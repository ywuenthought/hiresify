# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from datetime import datetime, timedelta

import pytest

from ..exception import EntityConflictError, EntityNotFoundError
from ..repository import Repository
from ..util import abbreviate_token

#################
# user management
#################

async def test_register_user(repository: Repository) -> None:
    # Given
    username = "ywu"

    # When/Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"UserAuth with username={username} was not found.",
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
            f"UserAuth with username={username} conflicts with an existing entity."
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
        check=lambda e: str(e) == f"UserAuth with username={username} was not found.",
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
        check=lambda e: str(e) == f"UserAuth with username={username} was not found.",
    ):
        await repository.delete_user(username)

    # Given
    await repository.register_user(username, "123")

    # When
    await repository.delete_user(username)

    # Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"UserAuth with username={username} was not found.",
    ):
        await repository.find_user(username)

###############
# refresh token
###############

async def test_create_token(repository: Repository) -> None:
    # Given
    username = "ywu"
    await repository.register_user(username, "123")

    token = "xyz"

    # When/Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == (
            f"RefreshToken with token={abbreviate_token(token)} was not found."
        ),
    ):
        refresh_token = await repository.find_token(token)

    # Given
    issued_at = datetime.now()
    expire_at = issued_at + timedelta(minutes=30)

    # When
    await repository.create_token(
        username, token, issued_at=issued_at, expire_at=expire_at,
    )
    refresh_token = await repository.find_token(token)

    # Then
    assert refresh_token.token == token
    assert refresh_token.issued_at == issued_at
    assert refresh_token.expire_at == expire_at
    assert not refresh_token.revoked


async def test_revoke_token(repository: Repository) -> None:
    # Given
    username = "ywu"
    await repository.register_user(username, "123")

    token = "xyz"

    # When/Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == (
            f"RefreshToken with token={abbreviate_token(token)} was not found."
        ),
    ):
        await repository.revoke_token(token)

    # Given
    token = "xyz"
    issued_at = datetime.now()
    expire_at = issued_at + timedelta(minutes=30)

    # When
    await repository.create_token(
        username, token, issued_at=issued_at, expire_at=expire_at,
    )
    refresh_token = await repository.find_token(token)

    # Then
    assert not refresh_token.revoked

    # When
    await repository.revoke_token(token)
    refresh_token = await repository.find_token(token)

    # Then
    assert refresh_token.revoked


async def test_revoke_tokens(repository: Repository) -> None:
    # Given
    username = "ywu"

    # When/Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"UserAuth with username={username} was not found.",
    ):
        await repository.revoke_tokens(username)

    # Given
    await repository.register_user(username, "123")

    # When
    refresh_tokens = await repository.find_tokens(username)

    # Then
    assert not refresh_tokens

    # Given
    tokens = ["xyz1", "xyz2", "xyz3"]

    # When
    for token in tokens:
        issued_at = datetime.now()
        await repository.create_token(
            username,
            token,
            issued_at=issued_at,
            expire_at=issued_at + timedelta(minutes=30),
        )
    refresh_tokens = await repository.find_tokens(username)

    # Then
    assert len(refresh_tokens) == len(tokens)
    for i, refresh_token in enumerate(refresh_tokens):
        assert refresh_token.token == tokens[i]
        assert not refresh_token.revoked

    # When
    await repository.revoke_tokens(username)
    refresh_tokens = await repository.find_tokens(username)

    # Then
    assert len(refresh_tokens) == len(tokens)
    for i, refresh_token in enumerate(refresh_tokens):
        assert refresh_token.token == tokens[i]
        assert refresh_token.revoked


async def test_purge_tokens(repository: Repository) -> None:
    # Given
    username = "ywu"
    await repository.register_user(username, "123")

    tokens = ["xyz1", "xyz2", "xyz3"]
    for token in tokens:
        issued_at = datetime.now()
        await repository.create_token(
            username,
            token,
            issued_at=issued_at,
            expire_at=issued_at + timedelta(minutes=30),
        )

    # When
    refresh_tokens = await repository.find_tokens(username)

    # Then
    assert len(refresh_tokens) == len(tokens)

    # When
    *_, refresh_token = refresh_tokens
    await repository.purge_tokens(1, refresh_token.expire_at + timedelta(days=2))
    refresh_tokens = await repository.find_tokens(username)

    # Then
    assert not refresh_tokens
