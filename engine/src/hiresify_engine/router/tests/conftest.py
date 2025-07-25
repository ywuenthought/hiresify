# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import typing as ty

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from hiresify_engine.config import AppConfig
from hiresify_engine.testing import TestBlobService, TestCacheService, test_repository

from ...router import api_routers, routers


@pytest.fixture(scope="module", autouse=True)
async def app() -> ty.AsyncGenerator[FastAPI, None]:
    """Create an app using the testing tool stack."""
    app = FastAPI()

    for router in routers + api_routers:
        app.include_router(router)

    yield app


@pytest.fixture(scope="module", autouse=True)
async def start_lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Start the lifespan of the testing app."""
    async with LifespanManager(app=app):
        # Initialize the app configuration.
        app.state.config = AppConfig()

        # Initialize the test blob service.
        app.state.blob = blob = TestBlobService()

        # Initialize the test cache manager.
        app.state.cache = TestCacheService()

        # Initialize the blob bucket.
        async with blob.start_session() as session:
            await session.init_bucket()

        # Initialize the test database repository.
        async with test_repository() as repo:
            app.state.repo = repo
            yield


@pytest.fixture(scope="function")
async def client(app: FastAPI) -> ty.AsyncGenerator[AsyncClient, None]:
    """Create an async client against the app in memory."""
    transport = ASGITransport(app=app)
    base_url = "https://hiresify"

    async with AsyncClient(transport=transport, base_url=base_url) as client:
        yield client
