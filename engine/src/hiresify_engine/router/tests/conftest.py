# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import typing as ty

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from hiresify_engine.testing import TestCacheService, test_repository
from hiresify_engine.tool import JWTManager, PKCEManager, PWDManager

from ...router import routers


@pytest.fixture(scope="session", autouse=True)
async def app() -> ty.AsyncGenerator[FastAPI, None]:
    """Create an app using the testing tool stack."""
    app = FastAPI()

    for router in routers:
        app.include_router(router)

    # Initialize the JWT access token manager.
    app.state.jwt = JWTManager(300)

    # Initialize the PKCE code manager.
    app.state.pkce = PKCEManager()

    # Initialize the user password manager.
    app.state.pwd = PWDManager()

    # Initialize the test cache manager.
    app.state.cache = TestCacheService(ttl=300)

    # Initialize the test database repository.
    async with test_repository(30) as repo:
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
