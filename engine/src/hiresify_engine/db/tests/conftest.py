# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import typing as ty

import pytest

from hiresify_engine.testing import test_repository

from ..repository import Repository


@pytest.fixture(scope="session")
async def repository() -> ty.AsyncGenerator[Repository, None]:
    """Create a temporary file-based repository for testing."""
    async with test_repository(30) as repository:
        yield repository


@pytest.fixture(scope="function", autouse=True)
async def purge_tables(repository: Repository) -> None:
    """Purge all the tables in-between tests."""
    await repository.purge_tables()
