# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from secrets import token_urlsafe
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from httpx import AsyncClient

from hiresify_engine.router.util import compute_challenge_s256
from hiresify_engine.tool import CCHManager

from ..main import app

################
# authentication
################

async def test_register_user(client: AsyncClient) -> None:
    # Given
    endpoint = "/user/register"

    username = "ywu"
    password = "123"

    data = dict(username=username, password=password)

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 200

    # Given
    expected_json = dict(
        detail=f"User with username={username} conflicts with an existing entity.",
    )

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 409
    assert response.json() == expected_json


async def test_authorize_user(client: AsyncClient) -> None:
    # Given
    endpoint = "/user/authorize"

    client_id = uuid4().hex
    code_verifier = token_urlsafe(64)
    code_challenge = compute_challenge_s256(code_verifier)
    redirect_uri = "https://localhost/callback"
    state = uuid4().hex

    params = dict(
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method="s256",
        redirect_uri=redirect_uri,
        response_type="code",
        state=state,
    )

    # When
    response = await client.get(endpoint, params=params)

    # Then
    assert response.status_code == 307

    redirect_url: str = response.headers.get("location")
    assert redirect_url.startswith("/user/login")

    parsed_url = urlparse(redirect_url)
    query_prms = parse_qs(parsed_url.query)
    assert list(query_prms.keys()) == ["request_id"]

    # Given
    cch: CCHManager = app.state.cch
    session = await cch.set_session()
    client.cookies.set("session_id", session.id)

    # When
    response = await client.get(endpoint, params=params)

    # Then
    assert response.is_redirect
    assert response.status_code == 307

    redirect_url = response.headers.get("location")
    assert redirect_url.startswith(redirect_uri)

    parsed_url = urlparse(redirect_url)
    query_prms = parse_qs(parsed_url.query)
    assert list(query_prms.keys()) == ["code", "state"]


async def test_login_user(client: AsyncClient) -> None:
    # Given
    endpoint = "/user/login"

    username = "ewu"
    password = "123"
    request_id = uuid4().hex

    data = dict(username=username, password=password)
    params = dict(request_id=request_id)

    expected_json = dict(detail="session_id=None is invalid or timed out.")

    # When
    response = await client.post(endpoint, data=data, params=params)

    # Then
    assert response.status_code == 400
    assert response.json() == expected_json

    # Given
    expected_json.update(detail=f"User with username={username} was not found.")

    cch: CCHManager = app.state.cch
    session = await cch.set_session()
    client.cookies.set("session_id", session.id)

    # When
    response = await client.post(endpoint, data=data, params=params)

    # Then
    assert response.status_code == 404
    assert response.json() == expected_json

    # Given
    await client.post("/user/register", data=data)

    # The input password is incorrect.
    data.update(password="456")

    expected_json.update(detail="The input password is incorrect.")

    # When
    response = await client.post(endpoint, data=data, params=params)

    # Then
    assert response.status_code == 401
    assert response.json() == expected_json

    # Given
    data.update(password=password)
    await client.post("user/register", data=data)

    expected_json.update(detail=f"{request_id=} is invalid or timed out.")

    # When
    response = await client.post(endpoint, data=data, params=params)

    # Then
    assert response.status_code == 400
    assert response.json() == expected_json

    # Given
    url = "https://hiresify/user/authorize"
    params.update(request_id=await cch.set_url(url))

    # When
    response = await client.post(endpoint, data=data, params=params)

    # Then
    assert response.is_redirect
    assert response.status_code == 302

    session_id = response.cookies.get("session_id")
    assert session_id is not None
    assert session_id != session.id
