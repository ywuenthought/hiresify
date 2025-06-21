# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import tempfile
import typing as ty

import pytest

from ..repository import Repository


@pytest.fixture(scope="session")
async def repository() -> ty.AsyncGenerator[Repository, None]:
    """Create a temporary file-based repository for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
        db_url = f"sqlite+aiosqlite:///{temp_db.name}"
        repository = Repository(db_url, 30)
        await repository.init_schema()
        yield repository
        await repository.dispose()


@pytest.fixture(scope="function", autouse=True)
async def purge_tables(repository: Repository) -> None:
    """Purge all the tables in-between tests."""
    await repository.purge_tables()
