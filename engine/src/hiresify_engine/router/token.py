# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend token-related endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Form, HTTPException, status

from hiresify_engine.db.exception import EntityConflictError, EntityNotFoundError
from hiresify_engine.dep import (
    CCHManagerDep,
    JWTManagerDep,
    PKCEManagerDep,
    RepositoryDep,
)
from hiresify_engine.tool.jwt import TokenResponse

router = APIRouter(prefix="/token")


@router.post(
    "/issue",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def issue_token(
    client_id: str = Form(..., max_length=32, min_length=32),
    code: str = Form(..., max_length=32, min_length=32),
    code_verifier: str = Form(..., max_length=43, min_length=128),
    redirect_uri: str = Form(..., max_length=128, pattern="^https://"),
    device: str | None = Form(None, max_length=128),
    ip: str | None = Form(None, max_length=45),
    platform: str | None = Form(None, max_length=32),
    *,
    cch: CCHManagerDep,
    jwt: JWTManagerDep,
    pkce: PKCEManagerDep,
    repo: RepositoryDep,
) -> TokenResponse:
    """Issue an access token to a user identified by the given metadata."""
    if not (meta := await cch.get_code(code)):
        raise HTTPException(
            detail=f"{code=} is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if client_id != meta.client_id:
        raise HTTPException(
            detail=f"{client_id=} is unauthorized.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if redirect_uri != meta.redirect_uri:
        raise HTTPException(
            detail=f"{redirect_uri=} is invalid.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not pkce.verify(
        code_verifier,
        meta.code_challenge,
        meta.code_challenge_method,
    ):
        raise HTTPException(
            detail=f"{code_verifier=} is invalid.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        refresh_token = await repo.create_token(
            meta.user_uid,
            device=device,
            ip=ip,
            platform=platform,
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    except EntityConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT) from e

    await cch.del_code(code)
    return jwt.generate(meta.user_uid, refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_token(
    token: str = Form(..., max_length=32, min_length=32),
    *,
    jwt: JWTManagerDep,
    repo: RepositoryDep,
) -> TokenResponse:
    """Refresh a user's access token if the given refresh token is active."""
    refresh_token = await repo.find_token(token, eager=True)

    if refresh_token.revoked or refresh_token.expire_at >= datetime.now(UTC):
        raise HTTPException(
            detail=f"{token=} was revoked or timed out.",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )

    user_uid = refresh_token.user.uid
    return jwt.generate(user_uid, token)
