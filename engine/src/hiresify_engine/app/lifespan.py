# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the app lifespan and service initialization."""

import json
import typing as ty
from contextlib import asynccontextmanager

from fastapi import FastAPI

from hiresify_engine.db.repository import Repository
from hiresify_engine.envvar import DATABASE_CONFIG, DATABASE_URL, REDIS_URL
from hiresify_engine.service.blob import BlobService
from hiresify_engine.service.cache import CacheService

##########
# lifespan
##########

@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    with open(DATABASE_CONFIG) as fp:
        configs = json.load(fp)

    # Initialize the blob store manager.
    app.state.blob = blob = BlobService()

    # Initialize the cache store manager.
    app.state.cache = cache = CacheService(REDIS_URL)

    # Initialize the database repository.
    app.state.repo = repo = Repository(DATABASE_URL, **configs)

    # Initialize the blob bucket.
    await blob.init_bucket()

    # Initialize the database schema.
    await repo.init_schema()

    yield

    await blob.dispose()
    await cache.dispose()
    await repo.dispose()
