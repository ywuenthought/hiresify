# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend endpoints."""

import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, status
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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username={user.username} already exists.",
        ) from e


@router.get("/authorize")
async def authorize_user(
    client_id: str,
    code_challenge: str,
    code_challenge_method: str,
    redirect_uri: str,
    redis: RedisDep,
    request: Request,
    response_type: str,
    state: str | None = None,
) -> RedirectResponse:
    """Authorize a verified user to log in the app."""
    if response_type != "code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only response_type="code" is supported.',
        )

    if code_challenge_method.lower() != "s256":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only code_challenge_method="s256" is supported.',
        )

    if not (session_id := request.cookies.get("session_id")) or not (
        user_uid := await redis.get(f"session:{session_id}")
    ):
        request_id = uuid4().hex
        url = str(request.url)

        # Store the original URL for 5 minutes.
        await redis.setex(f"request:{request_id}", 300, url)

        return RedirectResponse(url=f"/user/login?request_id={request_id}")

    code = uuid4().hex
    code_meta = dict(
        client_id=client_id,
        code_challenge=code_challenge,
        redirect_uri=str,
        user_uid=user_uid,
    )
    # Store the authorization code and its metadata for 5 minutes.
    await redis.setex(f"code:{code}", 300, json.dumps(code_meta))

    redirect_url = f"{redirect_uri}?code={code}" + (f"&state={state}" if state else "")
    return RedirectResponse(url=redirect_url)


@router.post("/login")
async def login_user(
    user: UserSchema, redis: RedisDep, repo: RepositoryDep, request_id: str,
) -> RedirectResponse:
    """Verify a user's credentials and set up a login session."""
    try:
        db_user = await repo.find_user(user.username)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    if not verify_password(user.username, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"The password for user {db_user.uid} is incorrect.",
        )

    if not (auth_url := await redis.get(f"request:{request_id}")):
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="The authentication request timed out.",
        )

    session_id = uuid4().hex
    await redis.setex(f"session:{session_id}", 1800, db_user.uid)

    response = RedirectResponse(status_code=status.HTTP_302_FOUND, url=auth_url)
    response.set_cookie(
        expires=datetime.now(UTC) + timedelta(seconds=1800),
        httponly=True,
        key="session_id",
        max_age=1800,
        samesite="lax",
        secure=True,
        value=session_id,
    )

    return response
