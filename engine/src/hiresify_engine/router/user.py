# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend user-related endpoints."""

import typing as ty

from fastapi import APIRouter, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from hiresify_engine.const import PASSWORD_REGEX, USERNAME_REGEX
from hiresify_engine.db.exception import EntityConflictError, EntityNotFoundError
from hiresify_engine.dep import CacheServiceDep, RepositoryDep
from hiresify_engine.templates import LOGIN_HTML, REGISTER_HTML
from hiresify_engine.tool import hash_password, verify_password

_templates = Jinja2Templates(directory=LOGIN_HTML.parent)

router = APIRouter(prefix="/user")


@router.get("/register")
async def register_user_page(
    *,
    cache: CacheServiceDep,
    request: Request,
) -> HTMLResponse:
    """Render the login form with a CSRF token."""
    session = await cache.set_request_session(str(request.url))
    token = await cache.set_csrf_token(session.id)

    response = _templates.TemplateResponse(
        request,
        REGISTER_HTML.name,
        dict(csrf_token=token),
    )

    response.set_cookie(**session.to_cookie())
    return response


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    username: str = Form(..., max_length=30, min_length=3, pattern=USERNAME_REGEX),
    password: str = Form(..., max_length=128, min_length=8, pattern=PASSWORD_REGEX),
    csrf_token: str = Form(..., max_length=32, min_length=32),
    *,
    cache: CacheServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> None:
    """Register a user using the given user name."""
    session_id = request.cookies.get("session_id")

    if not session_id or not await cache.get_request_session(session_id):
        raise HTTPException(
            detail=f"{session_id=} is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if csrf_token != await cache.get_csrf_token(session_id):
        raise HTTPException(
            detail=f"{csrf_token=} is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    hashed_password = hash_password(password)

    try:
        await repo.register_user(username, hashed_password)
    except EntityConflictError as e:
        raise HTTPException(
            detail="The input username already exists.",
            status_code=status.HTTP_409_CONFLICT,
        ) from e


@router.get("/authorize")
async def authorize_client(
    client_id: str = Query(..., max_length=32, min_length=32),
    code_challenge: str = Query(..., max_length=43, min_length=43),
    code_challenge_method: str = Query(..., max_length=10, min_length=4),
    redirect_uri: str = Query(..., max_length=2048, pattern="^https://"),
    response_type: ty.Literal["code"] = Query(..., max_length=4, min_length=4),
    state: str = Query(..., max_length=32, min_length=32),
    *,
    cache: CacheServiceDep,
    request: Request,
) -> RedirectResponse:
    """Authorize a client on behalf of a verified user."""
    session_id = request.cookies.get("session_id")
    session = await cache.get_user_session(session_id) if session_id else None
    auth = await cache.set_authorization(
        session.user_uid,
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        redirect_uri=redirect_uri,
    ) if session and session.user_uid else None

    url = f"{redirect_uri}?code={auth.code}&state={state}" if auth else "/user/login"
    response = RedirectResponse(url=url)

    if not auth:
        req_session = await cache.set_request_session(str(request.url))
        response.set_cookie(**req_session.to_cookie())

    return response


@router.get("/login")
async def login_user_page(*, cache: CacheServiceDep, request: Request) -> HTMLResponse:
    """Render the login form with a CSRF token."""
    session_id = request.cookies.get("session_id")

    if not session_id or not await cache.get_request_session(session_id):
        raise HTTPException(
            detail=f"{session_id=} is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    token = await cache.set_csrf_token(session_id)
    response = _templates.TemplateResponse(
        request,
        LOGIN_HTML.name,
        dict(csrf_token=token),
    )

    return response


@router.post("/login")
async def login_user(
    username: str = Form(..., max_length=30),
    password: str = Form(..., max_length=128),
    csrf_token: str = Form(..., max_length=32, min_length=32),
    *,
    cache: CacheServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> RedirectResponse:
    """Verify a user's credentials and set up a login session."""
    session_id = request.cookies.get("session_id")

    if not session_id or not (session := await cache.get_request_session(session_id)):
        raise HTTPException(
            detail=f"{session_id=} is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if csrf_token != await cache.get_csrf_token(session_id):
        raise HTTPException(
            detail=f"{csrf_token=} is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        db_user = await repo.find_user(username)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail="The input username was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e

    if not verify_password(password, db_user.password):
        raise HTTPException(
            detail="The input password is incorrect.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    url = session.request_uri
    response = RedirectResponse(status_code=status.HTTP_302_FOUND, url=url)

    user_session = await cache.set_user_session(db_user.uid)
    response.set_cookie(**user_session.to_cookie())

    return response
