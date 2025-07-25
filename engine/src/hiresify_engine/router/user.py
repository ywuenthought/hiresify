# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend user-related endpoints."""

import typing as ty
from uuid import uuid4

from fastapi import APIRouter, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from hiresify_engine.const import PASSWORD_REGEX, SESSION_NAME, USERNAME_REGEX
from hiresify_engine.db.exception import EntityConflictError, EntityNotFoundError
from hiresify_engine.dep import AppConfigDep, CacheServiceDep, RepositoryDep
from hiresify_engine.templates import LOGIN_HTML, REGISTER_HTML
from hiresify_engine.tool import hash_password, verify_password

router = APIRouter(prefix="/user")

_templates = Jinja2Templates(directory=LOGIN_HTML.parent)


@router.get("/check")
async def check_username(
    username: str = Query(..., max_length=30, min_length=3, pattern=USERNAME_REGEX),
    *,
    repo: RepositoryDep,
) -> None:
    """Check if the given username already exists in the database."""
    try:
        await repo.find_user(username)
    except EntityNotFoundError:
        pass
    else:
        raise HTTPException(
            detail=f"{username=} already exists",
            status_code=status.HTTP_409_CONFLICT,
        )


@router.get("/register")
async def register_user_page(
    redirect_uri: str = Query(..., max_length=2048),
    *,
    cache: CacheServiceDep,
    config: AppConfigDep,
    request: Request,
) -> HTMLResponse:
    """Render the login form with a CSRF token."""
    csrf_token = uuid4().hex
    session = await cache.set_csrf_session(csrf_token, ttl=config.cache_ttl)

    response = _templates.TemplateResponse(
        request,
        REGISTER_HTML.name,
        dict(csrf_token=csrf_token, redirect_uri=redirect_uri),
    )

    response.set_cookie(**session.to_cookie(path="/user"))
    response.headers.update(_get_secure_headers(config.production))

    return response


@router.post("/register")
async def register_user(
    username: str = Form(..., max_length=30, min_length=3, pattern=USERNAME_REGEX),
    password: str = Form(..., max_length=128, min_length=8, pattern=PASSWORD_REGEX),
    csrf_token: str = Form(..., max_length=32, min_length=32),
    redirect_uri: str = Form(..., max_length=2048),
    *,
    cache: CacheServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> RedirectResponse:
    """Register a user using the given user name."""
    if (session_id := request.cookies.get(SESSION_NAME)) is None:
        raise HTTPException(
            detail="No session ID was found.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if (session := await cache.get_csrf_session(session_id)) is None:
        raise HTTPException(
            detail=f"{session_id=} is invalid or timed out.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if csrf_token != session.csrf_token:
        raise HTTPException(
            detail=f"{csrf_token=} is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    hashed_password = hash_password(password)

    try:
        await repo.register_user(username, hashed_password)
    except EntityConflictError as e:
        raise HTTPException(
            detail="The input username already exists.",
            status_code=status.HTTP_409_CONFLICT,
        ) from e

    return RedirectResponse(status_code=status.HTTP_303_SEE_OTHER, url=redirect_uri)


@router.get("/login")
async def login_user_page(
    redirect_uri: str = Query(..., max_length=2048),
    *,
    cache: CacheServiceDep,
    config: AppConfigDep,
    request: Request,
) -> HTMLResponse:
    """Render the login form with a CSRF token."""
    csrf_token = uuid4().hex
    session = await cache.set_csrf_session(csrf_token, ttl=config.cache_ttl)

    response = _templates.TemplateResponse(
        request,
        LOGIN_HTML.name,
        dict(csrf_token=csrf_token, redirect_uri=redirect_uri),
    )

    response.set_cookie(**session.to_cookie(path="/user"))
    response.headers.update(_get_secure_headers(config.production))

    return response


@router.post("/login")
async def login_user(
    username: str = Form(..., max_length=30),
    password: str = Form(..., max_length=128),
    csrf_token: str = Form(..., max_length=32, min_length=32),
    redirect_uri: str = Form(..., max_length=2048),
    *,
    cache: CacheServiceDep,
    config: AppConfigDep,
    repo: RepositoryDep,
    request: Request,
) -> RedirectResponse:
    """Verify a user's credentials and set up a login session."""
    if (session_id := request.cookies.get(SESSION_NAME)) is None:
        raise HTTPException(
            detail="No session ID was found.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if (csrf_session := await cache.get_csrf_session(session_id)) is None:
        raise HTTPException(
            detail=f"{session_id=} is invalid or timed out.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if csrf_token != csrf_session.csrf_token:
        raise HTTPException(
            detail=f"{csrf_token=} is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
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

    response = RedirectResponse(status_code=status.HTTP_302_FOUND, url=redirect_uri)

    session = await cache.set_user_session(db_user.uid, ttl=config.cache_ttl)
    response.set_cookie(**session.to_cookie(path="/user"))

    return response


@router.get("/authorize")
async def authorize_client(
    client_id: str = Query(..., max_length=32, min_length=32),
    code_challenge: str = Query(..., max_length=43, min_length=43),
    code_challenge_method: str = Query(..., max_length=10, min_length=4),
    redirect_uri: str = Query(..., max_length=2048),
    response_type: ty.Literal["code"] = Query(...),
    state: str = Query(..., max_length=32, min_length=32),
    *,
    cache: CacheServiceDep,
    config: AppConfigDep,
    request: Request,
) -> RedirectResponse:
    """Authorize a client on behalf of a verified user."""
    if (session_id := request.cookies.get(SESSION_NAME)) is None:
        raise HTTPException(
            detail="No session ID was found.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if (session := await cache.get_user_session(session_id)) is None:
        raise HTTPException(
            detail=f"{session_id=} is invalid or timed out.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    code = await cache.set_authorization(
        session.user_uid,
        ttl=config.cache_ttl,
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        redirect_uri=redirect_uri,
    )

    url = f"{redirect_uri}?code={code}&state={state}"
    response = RedirectResponse(status_code=status.HTTP_303_SEE_OTHER, url=url)
    response.headers.update(_get_secure_headers(config.production))

    return response


def _get_secure_headers(production: bool = False) -> dict[str, str]:
    """Get the secure headers depending on the deployment."""
    headers = {
        # Prevent loading any external resources.
        "Content-Security-Policy": "connect-src 'self'; default-src 'self'; img-src 'self'; script-src 'self'; style-src 'self';",  # noqa: E501

        # Disable access to sensitive APIs.
        "Permissions-Policy": "geolocation=(), camera=()",

        # Prevent leaking the referrer URL.
        "Referrer-Policy": "no-referrer",

        # Disallow MIME-sniff the response content.
        "X-Content-Type-Options": "nosniff",

        # Prevent the page from being embedded in frames.
        "X-Frame-Options": "DENY",
    }

    if production:
        # Force browsers to use HTTPS for all future requests.
        headers["Strict-Transport-Security"] = "includeSubDomains; max-age=63072000; preload"  # noqa: E501

    return headers
