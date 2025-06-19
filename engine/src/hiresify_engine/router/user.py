# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend endpoints."""

import json
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from hiresify_engine.db.exception import EntityConflictError

from .dependency import RedisDep, RepositoryDep
from .schema import UserAuthSchema
from .util import hash_password

router = APIRouter(prefix="/user")


@router.post("")
async def register_user(user: UserAuthSchema, repo: RepositoryDep):
    """Register a user using the given user name."""
    hashed_password = hash_password(user.password)

    try:
        await repo.register_user(user.username, hashed_password)
    except EntityConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT) from e


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
):
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
        username := await redis.get(f"session:{session_id}")
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
        username=username,
    )
    # Store the authorization code and its metadata for 5 minutes.
    await redis.setex(f"code:{code}", 300, json.dumps(code_meta))

    redirect_url = f"{redirect_uri}?code={code}" + (f"&state={state}" if state else "")
    return RedirectResponse(url=redirect_url)
