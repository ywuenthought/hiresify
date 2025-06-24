# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the app lifespan and service initialization."""

import typing as ty
from contextlib import asynccontextmanager

from fastapi import FastAPI

from hiresify_engine import const
from hiresify_engine.testing import TestCCHStoreManager, test_repository
from hiresify_engine.tool import JWTManager, PKCEManager, PWDManager
from hiresify_engine.util import get_envvar


@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    deployment = get_envvar(const.DEPLOYMENT, str, const.TESTING)

    if deployment not in (const.TESTING, const.DEVELOPMENT, const.PRODUCTION):
        raise ValueError(f"{deployment=} is invalid.")

    if deployment == const.PRODUCTION:
        raise NotImplementedError("The production deployment is not available.")

    # Initialize the PKCE code manager.
    app.state.pkce = PKCEManager()

    # Initialize the JWT access token manager.
    app.state.jwt = JWTManager(get_envvar(const.ACCESS_TTL, int, 900))

    # Initialize the user password manager.
    app.state.pwd = PWDManager()

    if deployment == const.TESTING:

        # Initialize the cache manager.
        app.state.cch = cache = TestCCHStoreManager(
            get_envvar(const.REGULAR_TTL, int, 300),
            get_envvar(const.SESSION_TTL, int, 1800),
        )

        async with test_repository(get_envvar(const.REFRESH_TTL, int, 30)) as repo:
            app.state.repo = repo
            yield


    if deployment == const.DEVELOPMENT:
        pass

    await cache.dispose()
