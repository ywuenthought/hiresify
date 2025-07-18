# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend token-related endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Form, HTTPException, Request, Response, status

from hiresify_engine.db.exception import EntityNotFoundError
from hiresify_engine.dep import CacheServiceDep, RepositoryDep
from hiresify_engine.tool import confirm_verifier

from .const import jwt

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
    repo: RepositoryDep,
    response: Response,
) -> None:
    """Issue an access token to a user identified by the given metadata."""
    if not (auth := await cache.get_authorization(code)):
        raise HTTPException(
            detail="The authorization code is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if client_id != auth.client_id:
        raise HTTPException(
            detail="The input client ID is unauthorized.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if redirect_uri != auth.redirect_uri:
        raise HTTPException(
            detail="The input redirect URI is invalid.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not confirm_verifier(
        code_verifier,
        auth.code_challenge,
        auth.code_challenge_method,
    ):
        raise HTTPException(
            detail="The input code verifier is invalid.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    refresh_token = jwt.generate_refresh_token(auth.user_uid)

    try:
        await repo.create_token(
            auth.user_uid,
            token=refresh_token.token,
            issued_at=refresh_token.issued_at,
            expire_at=refresh_token.expire_at,
            device=device,
            ip=ip,
            platform=platform,
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            detail="The user account does not exist.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e

    response.set_cookie(**refresh_token.to_cookie())

    access_token = jwt.generate_access_token(auth.user_uid)
    response.set_cookie(**access_token.to_cookie())

    await cache.del_authorization(code)


@router.post("/refresh", status_code=status.HTTP_201_CREATED)
async def refresh_token(
    *,
    repo: RepositoryDep,
    request: Request,
    response: Response,
) -> None:
    """Refresh a user's access token if the given refresh token is active."""
    if (token := request.cookies.get("refresh_token")) is None:
        raise HTTPException(
            detail="No refresh token was found in the cookies.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        refresh_token = await repo.find_token(token, eager=True)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail=f"{token=} does not exist.",
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from e

    if refresh_token.expire_at <= datetime.now(UTC):
        raise HTTPException(
            detail=f"{token=} was revoked or timed out.",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )

    access_token = jwt.generate_access_token(refresh_token.user.uid)
    response.set_cookie(**access_token.to_cookie())


@router.post("/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(*, repo: RepositoryDep, request: Request) -> None:
    """Revoke a user's refresh token."""
    if (token := request.cookies.get("refresh_token")) is None:
        raise HTTPException(
            detail="No refresh token was found in the cookies.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    await repo.revoke_token(token)
