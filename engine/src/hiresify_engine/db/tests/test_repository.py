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
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"User with username={username} was not found.",
    ):
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
    with pytest.raises(
        EntityConflictError,
        check=lambda e: str(e) == (
            f"User with username={username} conflicts with an existing entity."
        ),
    ):
        await repository.register_user(username, password)


async def test_update_password(repository: Repository) -> None:
    # Given
    username = "ywu"
    updated_password = "456"

    # When/Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"User with username={username} was not found.",
    ):
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
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"User with username={username} was not found.",
    ):
        await repository.delete_user(username)

    # Given
    await repository.register_user(username, "123")

    # When
    await repository.delete_user(username)

    # Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"User with username={username} was not found.",
    ):
        await repository.find_user(username)

###############
# refresh token
###############

async def test_create_token(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    token = "xyz123"
    issued_at = datetime.now(UTC)
    expire_at = issued_at + timedelta(seconds=1)

    # When
    refresh_token = await repository.create_token(
        user.uid,
        token=token,
        issued_at=issued_at,
        expire_at=expire_at,
    )

    # Then
    assert refresh_token.expire_at > refresh_token.issued_at
    assert not refresh_token.revoked


async def test_revoke_token(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    token = "xyz123"
    issued_at = datetime.now(UTC)
    expire_at = issued_at + timedelta(seconds=1)

    # When
    refresh_token = await repository.create_token(
        user.uid,
        token=token,
        issued_at=issued_at,
        expire_at=expire_at,
    )

    # Then
    assert not refresh_token.revoked

    # When
    token = refresh_token.token
    await repository.revoke_token(token)

    # Then
    with pytest.raises(EntityNotFoundError):
        await repository.find_token(token)


async def test_revoke_tokens(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    # When
    refresh_tokens = await repository.find_tokens(user.uid)

    # Then
    assert not refresh_tokens

    # Given
    issued_at = datetime.now(UTC)
    tokens = [f"token{i}" for i in range(1, 4)]

    pre_tokens = []
    for token in tokens:
        expire_at = issued_at + timedelta(seconds=1)
        pre_tokens.append(
            await repository.create_token(
                user.uid,
                token=token,
                issued_at=issued_at,
                expire_at=expire_at,
            ),
        )
        issued_at = expire_at

    # Then
    for refresh_token in pre_tokens:
        assert not refresh_token.revoked

    # When
    await repository.revoke_tokens(user.uid)
    cur_tokens = await repository.find_tokens(user.uid)

    # Then
    assert not cur_tokens


async def test_purge_tokens(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")
    
    issued_at = datetime.now(UTC)
    tokens = [f"token{i}" for i in range(1, 4)]

    refresh_tokens = []
    for token in tokens:
        expire_at = issued_at + timedelta(seconds=1)
        refresh_tokens.append(
            await repository.create_token(
                user.uid,
                token=token,
                issued_at=issued_at,
                expire_at=expire_at,
            ),
        )
        issued_at = expire_at

    # When
    *_, refresh_token = refresh_tokens
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
        blob_key=uuid4().hex,
        file_name="blob.bin",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert blob.valid_thru > blob.created_at
    assert not blob.deleted


async def test_delete_blob(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    blob = await repository.create_blob(
        user.uid,
        blob_key=uuid4().hex,
        file_name="blob.bin",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert not blob.deleted

    # When
    await repository.delete_blob(blob.uid)

    # Then
    with pytest.raises(EntityNotFoundError):
        await repository.find_blob(blob.uid)


async def test_delete_blobs(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    # When
    blobs = await repository.find_blobs(user.uid)

    # Then
    assert not blobs

    # Given
    created_at = datetime.now(UTC)
    file_names = [f"blob{i}.bin" for i in range(1, 4)]

    pre_blobs = []
    for file_name in file_names:
        valid_thru = created_at + timedelta(seconds=1)
        pre_blobs.append(
            await repository.create_blob(
                user.uid,
                blob_key=uuid4().hex,
                file_name=file_name,
                created_at=created_at,
                valid_thru=valid_thru,
            ),
        )
        created_at = valid_thru

    # Then
    for blob in pre_blobs:
        assert not blob.deleted

    # When
    await repository.delete_blobs(user.uid)
    cur_blobs = await repository.find_blobs(user.uid)

    # Then
    assert not cur_blobs


async def test_purge_blobs(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")
    
    created_at = datetime.now(UTC)
    file_names = [f"blob{i}.bin" for i in range(1, 4)]

    blobs = []
    for file_name in file_names:
        valid_thru = created_at + timedelta(seconds=1)
        blobs.append(
            await repository.create_blob(
                user.uid,
                blob_key=uuid4().hex,
                file_name=file_name,
                created_at=created_at,
                valid_thru=valid_thru,
            ),
        )
        created_at = valid_thru

    # When
    *_, blob = blobs
    await repository.purge_blobs(1, blob.valid_thru + timedelta(days=2))
    blobs = await repository.find_blobs(user.uid)

    # Then
    assert not blobs
