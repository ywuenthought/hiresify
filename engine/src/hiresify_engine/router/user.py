# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend user-related endpoints."""

from fastapi import APIRouter, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from hiresify_engine.db.exception import EntityConflictError, EntityNotFoundError
from hiresify_engine.templates import LOGIN_HTML

from .dependency import CCHManagerDep, PWDManagerDep, RepositoryDep

_templates = Jinja2Templates(directory=LOGIN_HTML.parent)

router = APIRouter(prefix="/user")


@router.post("/register")
async def register_user(
    username: str = Form(..., max_length=30),
    password: str = Form(..., max_length=128),
    *,
    pwd: PWDManagerDep,
    repo: RepositoryDep,
) -> None:
    """Register a user using the given user name."""
    hashed_password = pwd.hash(password)

    try:
        await repo.register_user(username, hashed_password)
    except EntityConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.get("/authorize")
async def authorize_user(
    client_id: str = Query(..., max_length=32, min_length=32),
    code_challenge: str = Query(..., max_length=43, min_length=43),
    code_challenge_method: str = Query(..., max_length=10, min_length=4),
    redirect_uri: str = Query(..., max_length=2048, pattern="^https://"),
    response_type: str = Query(..., max_length=20, min_length=4),
    state: str = Query(..., max_length=32, min_length=32),
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
    session = await cch.get_session(session_id) if session_id else None
    code = await cch.set_code(
        session.user_uid,
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        redirect_uri=redirect_uri,
    ) if session else None

    if code:
        url = f"{redirect_uri}?code={code}&state={state}"
    else:
        request_id = await cch.set_url(str(request.url))
        url = f"/user/login?request_id={request_id}"

    return RedirectResponse(url=url)


@router.get("/login")
async def login_user_page(
    request_id: str = Query(..., max_length=32, min_length=32),
    *,
    cch: CCHManagerDep,
    request: Request,
) -> HTMLResponse:
    """Render the login form with an anonymous session."""
    response = _templates.TemplateResponse(
        LOGIN_HTML.name,
        dict(request=request, request_id=request_id),
    )

    session = await cch.set_session()
    session.set_cookie_on(response)

    return response


@router.post("/login")
async def login_user(
    username: str = Form(..., max_length=30),
    password: str = Form(..., max_length=128),
    request_id: str = Query(..., max_length=32, min_length=32),
    *,
    cch: CCHManagerDep,
    pwd: PWDManagerDep,
    repo: RepositoryDep,
    request: Request,
) -> RedirectResponse:
    """Verify a user's credentials and set up a login session."""
    if not (session_id := request.cookies.get("session_id")) or not (
        session := await cch.get_session(session_id)
    ):
        raise HTTPException(
            detail=f"{session_id=} is invalid or timed out.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

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

    session = await cch.set_session(db_user.uid)
    session.set_cookie_on(response)

    return response
