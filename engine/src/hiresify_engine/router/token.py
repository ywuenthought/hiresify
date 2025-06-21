# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend token-related endpoints."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Form, HTTPException, status

from hiresify_engine import const
from hiresify_engine.db.exception import EntityConflictError, EntityNotFoundError
from hiresify_engine.tool.jwt import TokenResponse
from hiresify_engine.util import get_envvar

from .dependency import CacheStoreDep, JWTManagerDep, RepositoryDep
from .util import is_pkce_valid

JWT_REFRESH_TTL = get_envvar(const.JWT_REFRESH_TTL, int, 30)

router = APIRouter(prefix="/token")


@dataclass(frozen=True)
class CodeMetadata:
    """Wrap the metadata associated with an authentication code."""

    #: The ID of the client.
    client_id: str

    #: The code challenge sent by the client.
    code_challenge: str

    #: The method to be used against the code challenge.
    code_challenge_method: str

    #: The redirect URI.
    redirect_uri: str

    #: The UID of the user to be authenticated.
    user_uid: str


@router.post(
    "/issue",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def issue_token(
    client_id: str = Form(..., max_length=32, min_length=32),
    code: str = Form(..., max_length=32, min_length=32),
    code_verifier: str = Form(..., max_length=32, min_length=32),
    redirect_uri: str = Form(..., max_length=128, pattern="^https://"),
    device: str | None = Form(None, max_length=128),
    ip: str | None = Form(None, max_length=45),
    platform: str | None = Form(None, max_length=32),
    *,
    cache: CacheStoreDep,
    jwt_manager: JWTManagerDep,
    repo: RepositoryDep,
) -> TokenResponse:
    """Issue an access token to a user identified by the given metadata."""
    if not (raw := await cache.get(f"code:{code}")):
        raise HTTPException(
            detail=f"{code=} is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    code_meta = CodeMetadata(**json.loads(raw))

    if client_id != code_meta.client_id:
        raise HTTPException(
            detail=f"{client_id=} is unauthorized.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if redirect_uri != code_meta.redirect_uri:
        raise HTTPException(
            detail=f"{redirect_uri=} is invalid.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not is_pkce_valid(
        code_verifier,
        code_meta.code_challenge,
        method=code_meta.code_challenge_method,
    ):
        raise HTTPException(
            detail=f"{code_verifier=} is invalid.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    refresh_token = uuid4().hex
    issued_at = datetime.now(UTC)
    expire_at = issued_at + timedelta(days=JWT_REFRESH_TTL)

    try:
        await repo.create_token(
            code_meta.user_uid,
            refresh_token,
            issued_at=issued_at,
            expire_at=expire_at,
            device=device,
            ip=ip,
            platform=platform,
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e
    except EntityConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT) from e

    await cache.delete(f"code:{code}")
    return jwt_manager.generate(code_meta.user_uid, refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_token(
    token: str = Form(..., max_length=32, min_length=32),
    *,
    jwt_manager: JWTManagerDep,
    repo: RepositoryDep,
) -> TokenResponse:
    """Refresh a user's access token if the given refresh token is active."""
    refresh_token = await repo.find_token(token, eager=True)

    if refresh_token.revoked or refresh_token.expire_at >= datetime.now(UTC):
        raise HTTPException(
            detail=f"{token=} was revoked or timed out.",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )

    user_id = refresh_token.user.uid
    return jwt_manager.generate(user_id, token)
