# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import typing as ty

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from hiresify_engine.db.repository import Repository

from ..main import app


@pytest.fixture(scope="session")
async def client() -> ty.AsyncGenerator[AsyncClient, None]:
    """Create an async client against the app in memory."""
    transport = ASGITransport(app=app)
    base_url = "https://hiresify"

    async with LifespanManager(app=app):
        async with AsyncClient(transport=transport, base_url=base_url) as client:
            yield client


@pytest.fixture(scope="function", autouse=True)
async def purge_tables() -> None:
    """Purge all the tables in-between tests."""
    repo: Repository = app.state.repo
    await repo.purge_tables()
