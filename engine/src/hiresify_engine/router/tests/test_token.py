# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from secrets import token_urlsafe
from uuid import uuid4

from fastapi import FastAPI
from httpx import AsyncClient

from hiresify_engine.config import AppConfig
from hiresify_engine.const import ACCESS_TOKEN_NAME, REFRESH_TOKEN_NAME
from hiresify_engine.db.repository import Repository
from hiresify_engine.model import JWTToken
from hiresify_engine.service.cache import CacheService
from hiresify_engine.tool import compute_challenge, hash_password
from hiresify_engine.util import get_interval_from_now


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
    code = await cache.set_authorization(
        user.uid,
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        redirect_uri=redirect_uri,
    )

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

    for key in (ACCESS_TOKEN_NAME, REFRESH_TOKEN_NAME):
        assert client.cookies.get(key) is not None

    # The authorization code has been removed from the cache store.
    assert await cache.get_authorization(code) is None


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
    assert response.status_code == 401
    assert response.json()["detail"] == f"No {REFRESH_TOKEN_NAME} token was found."

    # Given
    issued_at, expire_at = get_interval_from_now(10)
    refresh_token = JWTToken(
        issued_at=issued_at,
        expire_at=expire_at,
        user_uid=user.uid,
    )

    config: AppConfig = app.state.config
    token = refresh_token.get_token(config.jwt_secret_key)
    client.cookies.set(REFRESH_TOKEN_NAME, token)

    # When
    response = await client.post(endpoint)

    # Then
    assert response.status_code == 401
    assert response.json()["detail"] == f"token={refresh_token.uid} does not exist."

    # Given
    issued_at, expire_at = get_interval_from_now(10)
    refresh_token = await repo.create_token(
        user.uid,
        issued_at=issued_at,
        expire_at=expire_at,
    )


    token = refresh_token.get_token(config.jwt_secret_key)
    client.cookies.set(REFRESH_TOKEN_NAME, token)

    # When
    response = await client.post(endpoint)

    # Then
    assert response.status_code == 201
    assert client.cookies.get(ACCESS_TOKEN_NAME) is not None

    # Given
    await repo.revoke_token(refresh_token.uid)

    # When
    response = await client.post(endpoint)

    # Then
    assert response.status_code == 401
    assert response.json()["detail"] == f"token={refresh_token.uid} has been revoked."
