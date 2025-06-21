# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend user-related endpoints."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from hiresify_engine import const
from hiresify_engine.db.exception import EntityConflictError, EntityNotFoundError

from .dependency import AppEnvironDep, CCHManagerDep, PWDManagerDep, RepositoryDep

router = APIRouter(prefix="/user")


@router.post("")
async def register_user(
    username: str = Form(..., max_length=30),
    password: str = Form(..., max_length=128),
    *,
    pwd_manager: PWDManagerDep,
    repo: RepositoryDep,
) -> None:
    """Register a user using the given user name."""
    hashed_password = pwd_manager.hash(password)

    try:
        await repo.register_user(username, hashed_password)
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
    cch: CCHManagerDep,
    request: Request,
) -> RedirectResponse:
    """Authorize a verified user to log in the app."""
    if response_type != "code":
        raise HTTPException(
            detail='Only response_type="code" is supported.',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    session_id = request.cookies.get("session_id")
    code = await cch.generate_code(
        session_id,
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        redirect_uri=redirect_uri,
        state=state,
    ) if session_id else None

    if code:
        url = f"{redirect_uri}?code={code}"
    else:
        request_id = await cch.cache_url(str(request.url))
        url = f"/user/login?request_id={request_id}"

    return RedirectResponse(url=url)


@router.post("/login")
async def login_user(
    username: str = Form(..., max_length=30),
    password: str = Form(..., max_length=128),
    request_id: str = Form(..., max_length=32, min_length=32),
    *,
    cch: CCHManagerDep,
    env: AppEnvironDep,
    pwd: PWDManagerDep,
    repo: RepositoryDep,
) -> RedirectResponse:
    """Verify a user's credentials and set up a login session."""
    try:
        db_user = await repo.find_user(username)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    if not pwd.verify(password, db_user.password):
        raise HTTPException(
            detail=f"The input password for user {db_user.uid} is incorrect.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if not (url := await cch.get_url(request_id)):
        raise HTTPException(
            detail=f"{request_id=} is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    response = RedirectResponse(status_code=status.HTTP_302_FOUND, url=url)

    session_id = await cch.generate_session(db_user.uid)
    session_ttl: int = env[const.SESSION_TTL]

    response.set_cookie(
        expires=datetime.now(UTC) + timedelta(seconds=session_ttl),
        httponly=True,
        key="session_id",
        max_age=session_ttl,
        samesite="lax",
        secure=True,
        value=session_id,
    )

    return response
