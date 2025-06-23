# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import typing as ty

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from ..main import app


@pytest.fixture(scope="session", autouse=True)
async def start_lifespan() -> ty.AsyncGenerator[None, None]:
    """Start the lifespan of the testing app."""
    async with LifespanManager(app=app):
        yield


@pytest.fixture(scope="function")
async def client() -> ty.AsyncGenerator[AsyncClient, None]:
    """Create an async client against the app in memory."""
    transport = ASGITransport(app=app)
    base_url = "https://hiresify"

    async with AsyncClient(transport=transport, base_url=base_url) as client:
        yield client
