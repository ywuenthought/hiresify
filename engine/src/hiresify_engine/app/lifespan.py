# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the app lifespan and service initialization."""

import json
import typing as ty
from contextlib import asynccontextmanager

from fastapi import FastAPI

from hiresify_engine.cache.service import CacheService
from hiresify_engine.db.repository import Repository
from hiresify_engine.envvar import CACHE_TTL, DATABASE_CONFIG, DATABASE_URL, REDIS_URL

##########
# lifespan
##########

@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    with open(DATABASE_CONFIG) as fp:
        configs = json.load(fp)

    # Initialize the cache store manager.
    app.state.cache = cache = CacheService(REDIS_URL, ttl=CACHE_TTL)

    # Initialize the database repository.
    app.state.repo = repo = Repository(DATABASE_URL, **configs)

    # Initialize the database schema.
    await repo.init_schema()

    yield

    await cache.dispose()
    await repo.dispose()
