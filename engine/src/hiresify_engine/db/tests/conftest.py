# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import os
import tempfile
import typing as ty

import pytest

from ..repository import Repository


@pytest.fixture(scope="session")
async def repository() -> ty.AsyncGenerator[Repository, None]:
    """Create a temporary file-based repository for testing."""
    # delete=False prevents Python from exclusively opening this file.
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = temp_db.name
    # Close this file so SQLite can access it.
    temp_db.close()

    try:
        db_url = f"sqlite+aiosqlite:///{db_path}"
        repository = Repository(db_url)
        await repository.init_schema()
        yield repository
    finally:
        await repository.dispose()
        os.unlink(db_path)


@pytest.fixture(scope="function", autouse=True)
async def purge_tables(repository: Repository) -> None:
    """Purge all the tables in-between tests."""
    await repository.purge_tables()
