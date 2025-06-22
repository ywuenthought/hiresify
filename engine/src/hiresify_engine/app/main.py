# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the application entry point."""

import typing as ty
from contextlib import asynccontextmanager

from fastapi import FastAPI

from hiresify_engine import const
from hiresify_engine.router import routers
from hiresify_engine.testing import test_repository
from hiresify_engine.tool import CCHManager, JWTManager, PWDManager
from hiresify_engine.util import get_envvar


@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    async with test_repository(get_envvar(const.REFRESH_TTL, int, 30)) as repo:
        app.state.repo = repo

        # Initialize the cache manager.
        app.state.cch = cache = CCHManager(
            get_envvar(const.REGULAR_TTL, int, 300),
            get_envvar(const.SESSION_TTL, int, 1800),
        )

        # Initialize the JWT access token manager.
        app.state.jwt = JWTManager(get_envvar(const.ACCESS_TTL, int, 900))

        # Initialize the user password manager.
        app.state.pwd = PWDManager()

        yield

        await cache.dispose()


app = FastAPI(lifespan=lifespan)

for router in routers:
    app.include_router(router)
