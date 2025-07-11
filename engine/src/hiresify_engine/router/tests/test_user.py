# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from secrets import token_urlsafe
from uuid import uuid4

from fastapi import FastAPI
from httpx import AsyncClient

from hiresify_engine.cache.service import CacheService
from hiresify_engine.db.repository import Repository
from hiresify_engine.tool import compute_challenge, hash_password

from .util import get_query_params

###############
# user workflow
###############

async def test_register_user(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/user/register"
    redirect_uri = "http://localhost/callback"

    username = "ywu"
    password = "12345678"
    csrf_token = uuid4().hex

    data = dict(username=username, password=password, csrf_token=csrf_token)
    prms = dict(redirect_uri=redirect_uri)

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 404
    assert response.json()["detail"] == "No session ID was found in the cookies."

    # Given
    session_id = "session_id"
    client.cookies.set("session_id", session_id)

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == f"{session_id=} is invalid or timed out."

    # Given
    cache: CacheService = app.state.cache

    token = uuid4().hex
    session = await cache.set_csrf_session(token)
    client.cookies.set("session_id", session.id)

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == f"{csrf_token=} is invalid."

    # Given
    data.update(csrf_token=token)

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 303
    assert response.headers["location"] == redirect_uri

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 409
    assert response.json()["detail"] == "The input username already exists."


async def test_login_user(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/user/login"
    redirect_uri = "http://localhost/callback"

    username = "ewu"
    password = "12345678"
    csrf_token = uuid4().hex

    data = dict(username=username, password=password, csrf_token=csrf_token)
    prms = dict(redirect_uri=redirect_uri)

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 404
    assert response.json()["detail"] == "No session ID was found in the cookies."

    # Given
    session_id = "session_id"
    client.cookies.set("session_id", "session_id")

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == f"{session_id=} is invalid or timed out."

    # Given
    cache: CacheService = app.state.cache

    token = uuid4().hex
    session = await cache.set_csrf_session(token)
    client.cookies.set("session_id", session.id)

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == f"{csrf_token=} is invalid."

    # Given
    hashed_password = hash_password(password)

    repo: Repository = app.state.repo
    user = await repo.register_user(username, hashed_password)

    # The input password is incorrect.
    data.update(password="456")
    data.update(csrf_token=token)

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 401
    assert response.json()["detail"] == "The input password is incorrect."

    # Given
    data.update(password=password)

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 302

    sid = response.cookies.get("session_id")
    assert sid is not None

    user_session = await cache.get_user_session(sid)
    assert user_session is not None
    assert user_session.user_uid == user.uid


async def test_authorize_client(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/user/authorize"

    client_id = uuid4().hex
    redirect_uri = "http://localhost/callback"
    state = uuid4().hex

    code_verifier = token_urlsafe(64)
    code_challenge_method = "s256"
    code_challenge = compute_challenge(code_verifier, code_challenge_method)

    prms = dict(
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        redirect_uri=redirect_uri,
        response_type="code",
        state=state,
    )

    # When
    response = await client.get(endpoint, params=prms)

    # Then
    assert response.status_code == 404
    assert response.json()["detail"] == "No session ID was found in the cookies."

    # Given
    session_id = uuid4().hex
    client.cookies.set("session_id", session_id)

    # When
    response = await client.get(endpoint, params=prms)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == f"{session_id=} is invalid or timed out."

    # Given
    cache: CacheService = app.state.cache
    session = await cache.set_user_session("user-uid")
    client.cookies.set("session_id", session.id)

    # When
    response = await client.get(endpoint, params=prms)

    # Then
    assert response.status_code == 307

    url: str = response.headers.get("location")
    assert url.startswith(redirect_uri)

    query_params = get_query_params(url)
    assert list(query_params.keys()) == ["code", "state"]
