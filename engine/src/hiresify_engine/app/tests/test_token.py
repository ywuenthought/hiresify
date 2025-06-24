# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from secrets import token_urlsafe
from uuid import uuid4

from httpx import AsyncClient

from hiresify_engine.db.repository import Repository
from hiresify_engine.tool import CCHManager, PKCEManager, PWDManager

from ..main import app


async def test_issue_token(client: AsyncClient) -> None:
    # Given
    endpoint = "/token/issue"

    client_id = uuid4().hex
    code = uuid4().hex
    code_verifier = token_urlsafe(64)
    redirect_uri = "https://localhost/callback"

    data = dict(
        client_id=client_id,
        code=code,
        code_verifier=code_verifier,
        redirect_uri=redirect_uri,
    )

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "The authentication code is invalid or timed out."
    )

    # Given
    username = "kwu"
    password = "123"

    pwd: PWDManager = app.state.pwd
    hashed_password = pwd.hash(password)

    repo: Repository = app.state.repo
    user = await repo.register_user(username, hashed_password)

    code_challenge_method = "s256"
    pkce: PKCEManager = app.state.pkce
    code_challenge = pkce.compute(code_verifier, code_challenge_method)

    cch: CCHManager = app.state.cch
    code = await cch.set_code(
        user.uid,
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        redirect_uri=redirect_uri,
    )  # type: ignore[assignment]

    # Use an incorrect client ID.
    data.update(client_id=uuid4().hex, code=code)

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 401
    assert response.json()["detail"] == "The input client ID is unauthorized."

    # Given an incorrect redirect URI.
    data.update(client_id=client_id, redirect_uri="https://evil/callback")

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == "The input redirect URI is invalid."

    # Given an incorrect code verifier.
    data.update(code_verifier=token_urlsafe(64), redirect_uri=redirect_uri)

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == "The input code verifier is invalid."

    # Given
    data.update(code_verifier=code_verifier)

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 201

    # The authentication code has been removed from the cache store.
    assert await cch.get_code(code) is None


async def refresh_token(client: AsyncClient) -> None:
    # Given
    endpoint = "/token/refresh"

    username = "kwu"
    password = "123"

    pwd: PWDManager = app.state.pwd
    hashed_password = pwd.hash(password)

    repo: Repository = app.state.repo
    user = await repo.register_user(username, hashed_password)

    token = await repo.create_token(user.uid)
    data = dict(token=token)

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 201

    # Given
    await repo.revoke_token(token)

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 408
    assert response.json()["detail"] == f"{token=} was revoked or timed out."
