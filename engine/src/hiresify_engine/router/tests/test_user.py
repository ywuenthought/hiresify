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
from hiresify_engine.tool import PKCEManager, PWDManager

from .util import get_query_params

###############
# authorization
###############

async def test_register_user(client: AsyncClient) -> None:
    # Given
    endpoint = "/user/register"

    username = "ywu"
    password = "12345678"

    data = dict(username=username, password=password)

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 201

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 409
    assert response.json()["detail"] == "The input username already exists."


async def test_authorize_user(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/user/authorize"

    client_id = uuid4().hex
    redirect_uri = "https://localhost/callback"
    state = uuid4().hex

    code_verifier = token_urlsafe(64)
    code_challenge_method = "s256"

    pkce: PKCEManager = app.state.pkce
    code_challenge = pkce.compute(code_verifier, code_challenge_method)

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
    assert response.status_code == 307

    url: str = response.headers.get("location")
    assert url.startswith("/user/login")

    query_params = get_query_params(url)
    assert list(query_params.keys()) == ["request_id"]

    # Given
    cache: CacheService = app.state.cache
    session = await cache.set_session("user-uid")
    client.cookies.set("session_id", session.id)

    # When
    response = await client.get(endpoint, params=prms)

    # Then
    assert response.is_redirect
    assert response.status_code == 307

    url = response.headers.get("location")
    assert url.startswith(redirect_uri)

    query_params = get_query_params(url)
    assert list(query_params.keys()) == ["code", "state"]


async def test_login_user(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/user/login"

    username = "ewu"
    password = "12345678"
    request_id = uuid4().hex

    data = dict(username=username, password=password)
    prms = dict(request_id=request_id)

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == "session_id=None is invalid or timed out."

    # Given
    cache: CacheService = app.state.cache
    session = await cache.set_session()
    client.cookies.set("session_id", session.id)

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.status_code == 404
    assert response.json()["detail"] == "The input username was not found."

    # Given
    pwd: PWDManager = app.state.pwd
    hashed_password = pwd.hash(password)

    repo: Repository = app.state.repo
    await repo.register_user(username, hashed_password)

    # The input password is incorrect.
    data.update(password="456")

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
    assert response.status_code == 400
    assert response.json()["detail"] == f"{request_id=} is invalid or timed out."

    # Given
    url = "https://hiresify/user/authorize"
    prms.update(request_id=await cache.set_url(url))

    # When
    response = await client.post(endpoint, data=data, params=prms)

    # Then
    assert response.is_redirect
    assert response.status_code == 302

    session_id = response.cookies.get("session_id")
    assert session_id is not None
    assert session_id != session.id
