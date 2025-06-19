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

from hiresify_engine.db.repository import Repository
from hiresify_engine.router import routers


@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
        # Initialize the database repository.
        db_url = f"sqlite+aiosqlite:///{temp_db.name}"
        app.state.repo = repo = Repository(db_url)
        await repo.init_schema()

        # Initialize the in-memory database client.
        app.state.redis = redis = Redis(
            host="localhost", port=6379, decode_responses=True,
        )

        yield

        await repo.dispose()
        await redis.aclose()


app = FastAPI(lifespan=lifespan)

for router in routers:
    app.include_router(router)
