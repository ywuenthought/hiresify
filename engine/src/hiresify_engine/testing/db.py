# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export a testing version of the repository layer."""

import tempfile
import typing as ty
from contextlib import asynccontextmanager

from hiresify_engine.db.repository import Repository


@asynccontextmanager
async def test_repository(refresh_ttl: int) -> ty.AsyncGenerator[Repository, None]:
    """Create a test repository in the context of a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
        temp_db.close()

        db_url = f"sqlite+aiosqlite:///{temp_db.name}"
        repository = Repository(db_url, refresh_ttl)
        await repository.init_schema()
        yield repository
        await repository.dispose()
