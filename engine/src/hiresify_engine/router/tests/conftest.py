# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import typing as ty

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from hiresify_engine.envvar import CACHE_TTL, REFRESH_TTL
from hiresify_engine.jwt.service import JWTTokenService
from hiresify_engine.router.util import add_secure_headers
from hiresify_engine.testing import TestCacheService, test_repository

from ...router import routers


@pytest.fixture(scope="session", autouse=True)
async def app() -> ty.AsyncGenerator[FastAPI, None]:
    """Create an app using the testing tool stack."""
    app = FastAPI()

    for router in routers:
        app.include_router(router)

    # Initialize the callable to add secure response headers.
    app.state.add_secure_headers = add_secure_headers

    # Initialize the JWT token manager.
    app.state.jwt = JWTTokenService()

    # Initialize the test cache manager.
    app.state.cache = TestCacheService(ttl=CACHE_TTL)

    # Initialize the test database repository.
    async with test_repository(REFRESH_TTL) as repo:
        app.state.repo = repo
        yield app


@pytest.fixture(scope="session", autouse=True)
async def start_lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Start the lifespan of the testing app."""
    async with LifespanManager(app=app):
        yield


@pytest.fixture(scope="function")
async def client(app: FastAPI) -> ty.AsyncGenerator[AsyncClient, None]:
    """Create an async client against the app in memory."""
    transport = ASGITransport(app=app)
    base_url = "https://hiresify"

    async with AsyncClient(transport=transport, base_url=base_url) as client:
        yield client
