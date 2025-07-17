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
from hiresify_engine.jwt.service import JWTTokenService
from hiresify_engine.tool import compute_challenge, hash_password


async def test_issue_token(app: FastAPI, client: AsyncClient) -> None:
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
        "The authorization code is invalid or timed out."
    )

    # Given
    username = "kwu"
    password = "123"

    hashed_password = hash_password(password)

    repo: Repository = app.state.repo
    user = await repo.register_user(username, hashed_password)

    code_challenge_method = "s256"
    code_challenge = compute_challenge(code_verifier, code_challenge_method)

    cache: CacheService = app.state.cache
    auth = await cache.set_authorization(
        user.uid,
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        redirect_uri=redirect_uri,
    )

    # Use an incorrect client ID.
    data.update(client_id=uuid4().hex, code=auth.code)

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

    for key in ("access_token", "refresh_token"):
        assert client.cookies.get(key) is not None

    # The authorization code has been removed from the cache store.
    assert await cache.get_authorization(auth.code) is None


async def test_refresh_token(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/token/refresh"

    username = "swu"
    password = "123"

    hashed_password = hash_password(password)

    repo: Repository = app.state.repo
    user = await repo.register_user(username, hashed_password)

    # When
    response = await client.post(endpoint)

    # Then
    assert response.status_code == 404
    assert response.json()["detail"] == "No refresh token was found in the cookies."

    # Given
    token = uuid4().hex
    client.cookies.set("refresh_token", token)

    # When
    response = await client.post(endpoint)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == f"{token=} does not exist."

    # Given
    jwt: JWTTokenService = app.state.jwt
    refresh_token = jwt.generate_refresh_token(user.uid)
    await repo.create_token(
        user.uid,
        token=refresh_token.token,
        issued_at=refresh_token.issued_at,
        expire_at=refresh_token.expire_at,
    )


    token = refresh_token.token
    client.cookies.set("refresh_token", token)

    # When
    response = await client.post(endpoint)

    # Then
    assert response.status_code == 201
    assert client.cookies.get("access_token") is not None

    # Given
    await repo.revoke_token(token)

    # When
    response = await client.post(endpoint)

    # Then
    assert response.status_code == 400
    assert response.json()["detail"] == f"{token=} does not exist."
