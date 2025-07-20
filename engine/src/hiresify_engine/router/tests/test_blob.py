# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import io
from uuid import uuid4

from fastapi import FastAPI
from httpx import AsyncClient

from hiresify_engine.const import ACCESS_TOKEN_NAME
from hiresify_engine.db.repository import Repository
from hiresify_engine.model import JWTToken
from hiresify_engine.service.blob import BlobService
from hiresify_engine.testing.data import PNG_STREAM
from hiresify_engine.tool import hash_password
from hiresify_engine.util import generate_blob_key, get_interval_from_now


async def test_start_upload(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/api/blob/upload/init"

    repo: Repository = app.state.repo
    user = await repo.register_user("ywu", hash_password("123"))

    issued_at, expire_at = get_interval_from_now(10)
    token = JWTToken(user_uid=user.uid, issued_at=issued_at, expire_at=expire_at)
    client.cookies.set(ACCESS_TOKEN_NAME, token.token)

    # When
    response = await client.post(
        endpoint, files=dict(file=("test.png", io.BytesIO(b""), "image/png")),
    )

    # Then
    assert response.status_code == 415
    assert response.json()["detail"] == (
        "mime_type='application/x-empty' is not supported"
    )

    # When
    response = await client.post(
        endpoint, files=dict(file=("test.png", PNG_STREAM, "image/png")),
    )

    upload_id = response.json()

    # Then
    assert response.status_code == 201
    assert upload_id

    upload = await repo.find_upload(user.uid, upload_id=upload_id)

    assert upload.uid == upload_id
    assert upload.blob_key
    assert upload.created_at < upload.valid_thru


async def test_upload_chunk(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/api/blob/upload"

    repo: Repository = app.state.repo
    user = await repo.register_user("ewu", hash_password("123"))

    issued_at, expire_at = get_interval_from_now(10)
    token = JWTToken(user_uid=user.uid, issued_at=issued_at, expire_at=expire_at)
    client.cookies.set(ACCESS_TOKEN_NAME, token.token)

    upload_id = uuid4().hex

    data = dict(upload_id=upload_id)
    file = ("test.png", PNG_STREAM, "image/png")

    # When
    response = await client.post(endpoint, data=data, files=dict(file=file))

    # Then
    assert response.status_code == 404
    assert response.json()["detail"] == f"upload={upload_id} was not found."

    # Given
    blob: BlobService = app.state.blob
    blob_key = generate_blob_key(user.uid, "image/png")

    async with blob.start_session() as session:
        upload_id = await session.start_upload(blob_key)

    created_at, valid_thru = get_interval_from_now(10)
    await repo.start_upload(
        user.uid,
        uid=upload_id,
        blob_key=blob_key,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    data.update(upload_id=upload_id)

    # When
    response = await client.post(endpoint, data=data, files=dict(file=file))

    # Then
    assert response.status_code == 200


async def test_finish_upload(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/api/blob/upload"

    repo: Repository = app.state.repo
    user = await repo.register_user("kwu", hash_password("123"))

    issued_at, expire_at = get_interval_from_now(10)
    token = JWTToken(user_uid=user.uid, issued_at=issued_at, expire_at=expire_at)
    client.cookies.set(ACCESS_TOKEN_NAME, token.token)

    blob: BlobService = app.state.blob
    blob_key = generate_blob_key(user.uid, "image/png")

    async with blob.start_session() as session:
        upload_id = await session.start_upload(blob_key)

    created_at, valid_thru = get_interval_from_now(10)
    await repo.start_upload(
        user.uid,
        uid=upload_id,
        blob_key=blob_key,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # When
    response = await client.put(
        endpoint, data=dict(upload_id=upload_id, file_name="test.png"),
    )

    # Then
    assert response.status_code == 200


async def test_cancel_upload(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/api/blob/upload"

    repo: Repository = app.state.repo
    user = await repo.register_user("swu", hash_password("123"))

    issued_at, expire_at = get_interval_from_now(10)
    token = JWTToken(user_uid=user.uid, issued_at=issued_at, expire_at=expire_at)
    client.cookies.set(ACCESS_TOKEN_NAME, token.token)

    blob: BlobService = app.state.blob
    blob_key = generate_blob_key(user.uid, "image/png")

    async with blob.start_session() as session:
        upload_id = await session.start_upload(blob_key)

    created_at, valid_thru = get_interval_from_now(10)
    await repo.start_upload(
        user.uid,
        uid=upload_id,
        blob_key=blob_key,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # When
    response = await client.delete(endpoint, params=dict(upload_id=upload_id))

    # Then
    assert response.status_code == 204


async def test_delete_blob(app: FastAPI, client: AsyncClient) -> None:
    # Given
    endpoint = "/api/blob/delete"

    repo: Repository = app.state.repo
    user = await repo.register_user("awu", hash_password("123"))

    issued_at, expire_at = get_interval_from_now(10)
    token = JWTToken(user_uid=user.uid, issued_at=issued_at, expire_at=expire_at)
    client.cookies.set(ACCESS_TOKEN_NAME, token.token)

    blob_uid = uuid4().hex

    # When
    response = await client.delete(endpoint, params=dict(blob_uid=blob_uid))

    # Then
    assert response.status_code == 404
    assert response.json()["detail"] == f"{blob_uid=} was not found."

    # Given
    blob: BlobService = app.state.blob
    blob_key = generate_blob_key(user.uid, "image/png")

    async with blob.start_session() as session:
        upload_id = await session.start_upload(blob_key)
        await session.finish_upload(blob_key, upload_id)

    created_at, valid_thru = get_interval_from_now(10)
    obj = await repo.create_blob(
        user.uid,
        blob_key=blob_key,
        file_name="test.png",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # When
    response = await client.delete(endpoint, params=dict(blob_uid=obj.uid))

    # Then
    assert response.status_code == 204
