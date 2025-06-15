# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import pytest

from ..exception import EntityConflictError, EntityNotFoundError
from ..repository import Repository


async def test_register_user(repository: Repository) -> None:
    # Given
    username = "ywu"
    password = "123"

    # When/Then
    with pytest.raises(
        EntityNotFoundError, match="UserAuth with username=ywu was not found.",
    ):
        await repository.find_user(username)

    # Given
    await repository.register_user(username, password)

    # When
    user = await repository.find_user(username)

    # Then
    assert user.username == username
    assert user.password == password

    # When/Then
    with pytest.raises(
        EntityConflictError,
        match="UserAuth with username=ywu conflicts with an existing entity.",
    ):
        await repository.register_user(username, password)
