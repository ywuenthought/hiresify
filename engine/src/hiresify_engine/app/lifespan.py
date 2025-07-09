# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the app lifespan and service initialization."""

import json
import typing as ty
from contextlib import asynccontextmanager

from fastapi import FastAPI

from hiresify_engine import const
from hiresify_engine.cache.service import CacheService
from hiresify_engine.db.repository import Repository
from hiresify_engine.util import get_envvar

##########
# env vars
##########

# Load the database URL and default to an empty string.
db_url = get_envvar(const.DATABASE_URL, str, "")

# Load the database config file path and default to an empty string.
db_config = get_envvar(const.DATABASE_CONFIG, str, "")

# Load the redis server URL and default to an empty string.
redis_url = get_envvar(const.REDIS_URL, str, "")

# Load the refresh token TTL and default to 30 days.
refresh_ttl = get_envvar(const.REFRESH_TTL, int, 30)

# Load the cache TTL and default to 300 seconds.
cache_ttl = get_envvar(const.CACHE_TTL, int, 300)

##########
# lifespan
##########

@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    with open(db_config) as fp:
        configs = json.load(fp)

    # Initialize the cache store manager.
    app.state.cache = cache = CacheService(redis_url, ttl=cache_ttl)

    # Initialize the database repository.
    app.state.repo = repo = Repository(db_url, refresh_ttl=refresh_ttl, **configs)

    # Initialize the database schema.
    await repo.init_schema()

    yield

    await cache.dispose()
    await repo.dispose()
