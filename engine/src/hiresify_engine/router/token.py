# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend token-related endpoints."""

import json
import typing as ty
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Form, HTTPException, status
from jose import jwt

from hiresify_engine import const
from hiresify_engine.db.exception import EntityConflictError, EntityNotFoundError
from hiresify_engine.util import get_envvar

from .dependency import RedisDep, RepositoryDep
from .model import CodeMetadata
from .util import is_pkce_valid

JWT_ALGORITHM = get_envvar(const.JWT_ALGORITHM, str, "HS256")

JWT_SECRET_KEY = get_envvar(const.JWT_SECRET_KEY, str, "")

JWT_TTL = get_envvar(const.JWT_TTL, int, 1800)

router = APIRouter(prefix="/token")


@router.post("", status_code=status.HTTP_201_CREATED)
async def issue_token(
    client_id: str = Form(..., max_length=32, min_length=32),
    code: str = Form(..., max_length=32, min_length=32),
    code_verifier: str = Form(..., max_length=32, min_length=32),
    redirect_uri: str = Form(..., max_length=128, pattern="^https://"),
    device: str | None = Form(None, max_length=128),
    ip: str | None = Form(None, max_length=45),
    platform: str | None = Form(None, max_length=32),
    *,
    redis: RedisDep,
    repo: RepositoryDep,
) -> dict[str, ty.Any]:
    """Issue an access token to a user identified by the given metadata."""
    if not (raw := await redis.get(f"code:{code}")):
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

    issued_at = datetime.now(UTC)
    expire_at = issued_at + timedelta(days=30)

    access_token = jwt.encode(
        dict(
            exp=int(expire_at.timestamp()),
            iat=int(issued_at.timestamp()),
            scope="read write",
            sub=code_meta.user_uid,
        ),
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    try:
        await repo.create_token(
            code_meta.user_uid,
            refresh_token := uuid4().hex,
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

    await redis.delete(f"code:{code}")

    return dict(
        access_token=access_token,
        expires_in=JWT_TTL,
        refresh_token=refresh_token,
        scope="read write",
        token_type="bearer",
    )
