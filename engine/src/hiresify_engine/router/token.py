# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend token-related endpoints."""

from fastapi import APIRouter, Form, HTTPException, Request, Response, status

from hiresify_engine.const import ACCESS_TOKEN_NAME, REFRESH_TOKEN_NAME
from hiresify_engine.db.exception import EntityNotFoundError
from hiresify_engine.dep import AppConfigDep, CacheServiceDep, RepositoryDep
from hiresify_engine.envvar import ACCESS_TTL, REFRESH_TTL
from hiresify_engine.model import JWTToken
from hiresify_engine.tool import confirm_verifier
from hiresify_engine.util import get_interval_from_now

from .util import verify_token

router = APIRouter(prefix="/token")


@router.post("/issue", status_code=status.HTTP_201_CREATED)
async def issue_token(
    client_id: str = Form(..., max_length=32, min_length=32),
    code: str = Form(..., max_length=32, min_length=32),
    code_verifier: str = Form(..., max_length=128, min_length=43),
    redirect_uri: str = Form(..., max_length=2048),
    device: str | None = Form(None, max_length=128),
    ip: str | None = Form(None, max_length=45),
    platform: str | None = Form(None, max_length=32),
    *,
    cache: CacheServiceDep,
    config: AppConfigDep,
    repo: RepositoryDep,
    response: Response,
) -> None:
    """Issue an access token to a user identified by the given metadata."""
    if not (auth := await cache.get_authorization(code)):
        raise HTTPException(
            detail="The authorization code is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if client_id != auth["client_id"]:
        raise HTTPException(
            detail="The input client ID is unauthorized.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if redirect_uri != auth["redirect_uri"]:
        raise HTTPException(
            detail="The input redirect URI is invalid.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not confirm_verifier(
        code_verifier,
        auth["code_challenge"],
        auth["code_challenge_method"],
    ):
        raise HTTPException(
            detail="The input code verifier is invalid.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    issued_at, expire_at = get_interval_from_now(86400 * REFRESH_TTL)

    try:
        refresh_token = await repo.create_token(
            auth["user_uid"],
            issued_at=issued_at,
            expire_at=expire_at,
            device=device,
            ip=ip,
            platform=platform,
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            detail="The user account does not exist.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e

    response.set_cookie(
        **refresh_token.to_cookie(
            REFRESH_TOKEN_NAME,
            refresh_token.get_token(config.jwt_secret_key),
            path="/token",
            secure=config.production,
        ),
    )

    issued_at, expire_at = get_interval_from_now(ACCESS_TTL)
    access_token = JWTToken(
        issued_at=issued_at,
        expire_at=expire_at,
        user_uid=auth["user_uid"],
    )

    response.set_cookie(
        **access_token.to_cookie(
            ACCESS_TOKEN_NAME,
            access_token.get_token(config.jwt_secret_key),
            secure=config.production,
        ),
    )

    await cache.del_authorization(code)


@router.post("/refresh", status_code=status.HTTP_201_CREATED)
async def refresh_token(
    *,
    config: AppConfigDep,
    repo: RepositoryDep,
    request: Request,
    response: Response,
) -> None:
    """Refresh a user's access token if the given refresh token is active."""
    refresh_token = verify_token(
        request.cookies,
        token_name=REFRESH_TOKEN_NAME,
        secret_key=config.jwt_secret_key,
    )

    try:
        refresh_token = await repo.find_token(refresh_token.uid)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail=f"token={refresh_token.uid} does not exist.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from e

    if refresh_token.revoked:
        raise HTTPException(
            detail=f"token={refresh_token.uid} has been revoked.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    
    issued_at, expire_at = get_interval_from_now(ACCESS_TTL)
    access_token = JWTToken(
        issued_at=issued_at,
        expire_at=expire_at,
        user_uid=refresh_token.user_uid,
    )

    response.set_cookie(
        **access_token.to_cookie(
            ACCESS_TOKEN_NAME,
            access_token.get_token(config.jwt_secret_key),
            secure=config.production,
        ),
    )


@router.post("/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    *, config: AppConfigDep, repo: RepositoryDep, request: Request,
) -> None:
    """Revoke a user's refresh token."""
    refresh_token = verify_token(
        request.cookies,
        token_name=REFRESH_TOKEN_NAME,
        secret_key=config.jwt_secret_key,
    )

    try:
        await repo.revoke_token(refresh_token.uid)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail=f"token={refresh_token.uid} does not exist.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from e
