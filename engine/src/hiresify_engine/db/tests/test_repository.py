# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from ..exception import EntityConflictError, EntityNotFoundError
from ..repository import Repository

#################
# user management
#################

async def test_register_user(repository: Repository) -> None:
    # Given
    username = "ywu"

    # When/Then
    with pytest.raises(EntityNotFoundError):
        await repository.find_user(username)

    # Given
    password = "123"
    await repository.register_user(username, password)

    # When
    user = await repository.find_user(username)

    # Then
    assert user.username == username
    assert user.password == password

    # When/Then
    with pytest.raises(EntityConflictError):
        await repository.register_user(username, password)


async def test_update_password(repository: Repository) -> None:
    # Given
    username = "ywu"
    updated_password = "456"

    # When/Then
    with pytest.raises(EntityNotFoundError):
        await repository.update_password(username, updated_password)

    # Given
    await repository.register_user(username, "123")

    # When
    await repository.update_password(username, updated_password)
    updated_user = await repository.find_user(username)

    # Then
    assert updated_user.username == username
    assert updated_user.password == updated_password


async def test_delete_user(repository: Repository) -> None:
    # Given
    username = "ywu"

    # When/Then
    with pytest.raises(EntityNotFoundError):
        await repository.delete_user(username)

    # Given
    await repository.register_user(username, "123")

    # When
    await repository.delete_user(username)

    # Then
    with pytest.raises(EntityNotFoundError):
        await repository.find_user(username)

###############
# refresh token
###############

async def test_create_token(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    issued_at = datetime.now(UTC)
    expire_at = issued_at + timedelta(seconds=1)

    # When
    refresh_token = await repository.create_token(
        user.uid,
        issued_at=issued_at,
        expire_at=expire_at,
    )

    # Then
    assert refresh_token.expire_at > refresh_token.issued_at


async def test_revoke_token(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    issued_at = datetime.now(UTC)
    expire_at = issued_at + timedelta(seconds=1)

    refresh_token = await repository.create_token(
        user.uid,
        issued_at=issued_at,
        expire_at=expire_at,
    )

    # When
    refresh_token = await repository.find_token(refresh_token.uid)

    # Then
    assert not refresh_token.revoked

    # When
    await repository.revoke_token(refresh_token.uid)
    refresh_token = await repository.find_token(refresh_token.uid)

    # Then
    assert refresh_token.revoked


async def test_revoke_tokens(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    issued_at = datetime.now(UTC)
    for _ in range(3):
        expire_at = issued_at + timedelta(seconds=1)
        await repository.create_token(
            user.uid,
            issued_at=issued_at,
            expire_at=expire_at,
        )
        issued_at = expire_at

    # When
    refresh_tokens = await repository.find_tokens(user.uid)

    # Then
    for refresh_token in refresh_tokens:
        assert not refresh_token.revoked

    # When
    await repository.revoke_tokens(user.uid)
    refresh_tokens = await repository.find_tokens(user.uid)

    # Then
    for refresh_token in refresh_tokens:
        assert refresh_token.revoked


async def test_purge_tokens(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")
    
    issued_at = datetime.now(UTC)

    for _ in range(3):
        expire_at = issued_at + timedelta(seconds=1)
        refresh_token = await repository.create_token(
            user.uid,
            issued_at=issued_at,
            expire_at=expire_at,
        )
        issued_at = expire_at

    # When
    refresh_tokens = await repository.find_tokens(user.uid)

    # Then
    assert len(refresh_tokens) == 3

    # When
    await repository.purge_tokens(1, refresh_token.expire_at + timedelta(days=2))
    refresh_tokens = await repository.find_tokens(user.uid)

    # Then
    assert not refresh_tokens

############
# blob files
############

async def test_create_blob(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    blob = await repository.create_blob(
        user.uid,
        blob_key=f"{user.uid}/image/{uuid4().hex}.png",
        file_name="blob.png",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert blob.valid_thru > blob.created_at


async def test_delete_blob(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    blob_key = f"{user.uid}/image/{uuid4().hex}.png"
    file_name = "blob.png"

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    blob = await repository.create_blob(
        user.uid,
        blob_key=blob_key,
        file_name=file_name,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # When
    blob, key = await repository.find_blob(user.uid, blob_uid=blob.uid)

    # Then
    assert blob.file_name == file_name
    assert blob.mime_type == "image/png"

    assert blob.created_at == created_at
    assert blob.valid_thru == valid_thru

    assert key == blob_key

    # When
    await repository.delete_blob(blob.uid)

    # Then
    with pytest.raises(EntityNotFoundError):
        await repository.find_blob(user.uid, blob_uid=blob.uid)


async def test_delete_blobs(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    file_names = [f"blob{i}.png" for i in range(1, 4)]

    for file_name in file_names:
        valid_thru = created_at + timedelta(seconds=1)
        await repository.create_blob(
            user.uid,
            blob_key=f"{user.uid}/image/{uuid4().hex}.png",
            file_name=file_name,
            created_at=created_at,
            valid_thru=valid_thru,
        )
        created_at = valid_thru

    # When
    blobs = await repository.find_blobs(user.uid)

    # Then
    assert len(blobs) == len(file_names)

    # When
    await repository.delete_blobs(user.uid)
    blobs = await repository.find_blobs(user.uid)

    # Then
    assert not blobs


async def test_purge_blobs(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")
    
    created_at = datetime.now(UTC)
    file_names = [f"blob{i}.png" for i in range(1, 4)]

    for file_name in file_names:
        valid_thru = created_at + timedelta(seconds=1)
        blob = await repository.create_blob(
            user.uid,
            blob_key=f"{user.uid}/image/{uuid4().hex}.png",
            file_name=file_name,
            created_at=created_at,
            valid_thru=valid_thru,
        )
        created_at = valid_thru

    # When
    blobs = await repository.find_blobs(user.uid)

    # Then
    assert len(blobs) == len(file_names)

    # When
    await repository.purge_blobs(1, blob.valid_thru + timedelta(days=2))
    blobs = await repository.find_blobs(user.uid)

    # Then
    assert not blobs

##############
# upload blobs
##############

async def test_start_upload(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    upload_id = "upload-id"
    blob_key = f"{user.uid}/blob/{uuid4().hex}.png"

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    upload = await repository.start_upload(
        user.uid,
        uid=upload_id,
        blob_key=blob_key,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert upload.valid_thru > upload.created_at


async def test_remove_upload(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    upload_id = "upload-id"
    blob_key = f"{user.uid}/blob/{uuid4().hex}.png"

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    await repository.start_upload(
        user.uid,
        uid=upload_id,
        blob_key=blob_key,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # When
    upload = await repository.find_upload(user.uid, upload_id=upload_id)

    # Then
    assert upload.uid == upload_id
    assert upload.blob_key == blob_key
    assert upload.created_at == created_at
    assert upload.valid_thru == valid_thru

    # When
    await repository.remove_upload(upload_id)

    # Then
    with pytest.raises(EntityNotFoundError):
        await repository.find_upload(user.uid, upload_id=upload_id)


async def test_purge_uploads(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    upload_id = "upload-id"

    created_at = datetime.now(UTC)
    blob_keys = [f"{user.uid}/main/{uuid4().hex}.sub" for _ in range(1, 4)]

    for blob_key in blob_keys:
        valid_thru = created_at + timedelta(seconds=1)
        upload = await repository.start_upload(
            user.uid,
            uid=upload_id,
            blob_key=blob_key,
            created_at=created_at,
            valid_thru=valid_thru,
        )
        created_at = valid_thru

    # When
    uploads = await repository.find_uploads(user.uid)

    # Then
    assert len(uploads) == len(blob_keys)

    # When
    await repository.purge_uploads(1, upload.valid_thru + timedelta(days=2))
    uploads = await repository.find_uploads(user.uid)

    # Then
    assert not uploads

##############
# compute jobs
##############

async def test_start_job(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    blob_key = f"{user.uid}/image/{uuid4().hex}.png"
    file_name = "blob.png"

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    blob = await repository.create_blob(
        user.uid,
        blob_key=blob_key,
        file_name=file_name,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # When
    job = await repository.submit_job(blob.uid, requested_at=datetime.now(UTC))
    job = await repository.find_job(blob.uid, job_id=job.uid)

    # Then
    assert job.status == "pending"
    assert job.completed_at is None

    # When
    jobs = await repository.find_jobs(blob.uid)

    # Then
    assert len(jobs) == 1
    assert jobs[0] == job

async def test_update_job(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    blob_key = f"{user.uid}/image/{uuid4().hex}.png"
    file_name = "blob.png"

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    blob = await repository.create_blob(
        user.uid,
        blob_key=blob_key,
        file_name=file_name,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    job = await repository.submit_job(blob.uid, requested_at=datetime.now(UTC))

    # When
    await repository.update_job(job.uid, status="started")
    job = await repository.find_job(blob.uid, job_id=job.uid)

    # Then
    assert job.status == "started"
