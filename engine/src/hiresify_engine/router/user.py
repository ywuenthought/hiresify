# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend user-related endpoints."""

import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from hiresify_engine import const
from hiresify_engine.db.exception import EntityConflictError, EntityNotFoundError
from hiresify_engine.util import get_envvar

from .dependency import RedisDep, RepositoryDep
from .schema import UserSchema
from .util import hash_password, verify_password

REDIS_TTL = get_envvar(const.REDIS_TTL, int, 300)

SESSION_TTL = get_envvar(const.SESSION_TTL, int, 1800)

router = APIRouter(prefix="/user")


@router.post("")
async def register_user(user: UserSchema, repo: RepositoryDep) -> None:
    """Register a user using the given user name."""
    hashed_password = hash_password(user.password)

    try:
        await repo.register_user(user.username, hashed_password)
    except EntityConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT) from e


@router.get("/authorize")
async def authorize_user(
    client_id: str = Query(..., max_length=32, min_length=32),
    code_challenge: str = Query(..., max_length=43, min_length=43),
    code_challenge_method: str = Query(..., max_length=10, min_length=4),
    redirect_uri: str = Query(..., max_length=2048, pattern="^https://"),
    response_type: str = Query(..., max_length=20, min_length=4),
    state: str | None = Query(None, max_length=32, min_length=32),
    *,
    redis: RedisDep,
    request: Request,
) -> RedirectResponse:
    """Authorize a verified user to log in the app."""
    if response_type != "code":
        raise HTTPException(
            detail='Only response_type="code" is supported.',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not (session_id := request.cookies.get("session_id")) or not (
        user_uid := await redis.get(f"session:{session_id}")
    ):
        request_id = uuid4().hex
        url = str(request.url)

        # Store the original URL for 5 minutes.
        await redis.setex(f"request:{request_id}", REDIS_TTL, url)

        return RedirectResponse(url=f"/user/login?request_id={request_id}")

    code = uuid4().hex
    code_meta = dict(
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        redirect_uri=redirect_uri,
        user_uid=user_uid,
    )
    # Store the authorization code and its metadata for 5 minutes.
    await redis.setex(f"code:{code}", REDIS_TTL, json.dumps(code_meta))

    redirect_url = f"{redirect_uri}?code={code}" + (f"&state={state}" if state else "")
    return RedirectResponse(url=redirect_url)


@router.post("/login")
async def login_user(
    user: UserSchema,
    request_id: str = Query(..., max_length=32, min_length=32),
    *,
    redis: RedisDep,
    repo: RepositoryDep,
) -> RedirectResponse:
    """Verify a user's credentials and set up a login session."""
    try:
        db_user = await repo.find_user(user.username)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    if not verify_password(user.username, db_user.password):
        raise HTTPException(
            detail=f"The input password for user {db_user.uid} is incorrect.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if not (auth_url := await redis.get(f"request:{request_id}")):
        raise HTTPException(
            detail=f"{request_id=} is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    session_id = uuid4().hex
    await redis.setex(f"session:{session_id}", SESSION_TTL, db_user.uid)

    response = RedirectResponse(status_code=status.HTTP_302_FOUND, url=auth_url)
    response.set_cookie(
        expires=datetime.now(UTC) + timedelta(seconds=SESSION_TTL),
        httponly=True,
        key="session_id",
        max_age=SESSION_TTL,
        samesite="lax",
        secure=True,
        value=session_id,
    )

    return response
