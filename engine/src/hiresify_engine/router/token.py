# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend token-related endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Form, HTTPException, status

from hiresify_engine.db.exception import EntityNotFoundError
from hiresify_engine.dep import CacheServiceDep, JWTManagerDep, RepositoryDep
from hiresify_engine.tool import confirm_verifier

router = APIRouter(prefix="/token")


@router.post("/issue", status_code=status.HTTP_201_CREATED)
async def issue_token(
    client_id: str = Form(..., max_length=32, min_length=32),
    code: str = Form(..., max_length=32, min_length=32),
    code_verifier: str = Form(..., max_length=128, min_length=43),
    redirect_uri: str = Form(..., max_length=128),
    device: str | None = Form(None, max_length=128),
    ip: str | None = Form(None, max_length=45),
    platform: str | None = Form(None, max_length=32),
    *,
    cache: CacheServiceDep,
    jwt: JWTManagerDep,
    repo: RepositoryDep,
) -> dict[str, str]:
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

    try:
        refresh_token = await repo.create_token(
            auth.user_uid,
            device=device,
            ip=ip,
            platform=platform,
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            detail="The user account has been deleted.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e

    access_token = jwt.generate(auth.user_uid)
    await cache.del_authorization(code)

    return dict(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", status_code=status.HTTP_201_CREATED)
async def refresh_token(
    token: str = Form(..., max_length=32, min_length=32),
    *,
    jwt: JWTManagerDep,
    repo: RepositoryDep,
) -> dict[str, str]:
    """Refresh a user's access token if the given refresh token is active."""
    refresh_token = await repo.find_token(token, eager=True)

    if refresh_token.revoked or refresh_token.expire_at <= datetime.now(UTC):
        raise HTTPException(
            detail=f"{token=} was revoked or timed out.",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )

    user_uid = refresh_token.user.uid
    access_token = jwt.generate(user_uid)

    return dict(access_token=access_token)


@router.post("/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    token: str = Form(..., max_length=32, min_length=32),
    *,
    repo: RepositoryDep,
) -> None:
    """Revoke a user's refresh token."""
    try:
        await repo.revoke_token(token)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail="The refresh token was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e
