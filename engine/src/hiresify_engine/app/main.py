# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the application entry point."""

import tempfile
import typing as ty
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from hiresify_engine import const
from hiresify_engine.db.repository import Repository
from hiresify_engine.router import routers
from hiresify_engine.tool import JWTManager, PWDManager
from hiresify_engine.util import get_envvar


@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
        # Initialize the database repository.
        db_url = f"sqlite+aiosqlite:///{temp_db.name}"
        app.state.repo = repo = Repository(db_url)
        await repo.init_schema()

        # Initialize the in-memory database client.
        app.state.cache = cache = Redis(
            host="localhost", port=6379, decode_responses=True,
        )

        # Initialize the JWT access token manager.
        app.state.jwt_manager = JWTManager(
            ttl=get_envvar(const.JWT_ACCESS_TTL, int, 900),
        )

        # Initialize the user password manager.
        app.state.pwd_manager = PWDManager()

        # Initialize the environment variables.
        app.state.env = {
            const.CACHE_TTL: get_envvar(const.CACHE_TTL, int, 300),
            const.REFRESH_TTL: get_envvar(const.REFRESH_TTL, int, 30),
            const.SESSION_TTL: get_envvar(const.SESSION_TTL, int, 1800),
        }

        yield

        await repo.dispose()
        await cache.aclose()


app = FastAPI(lifespan=lifespan)

for router in routers:
    app.include_router(router)
