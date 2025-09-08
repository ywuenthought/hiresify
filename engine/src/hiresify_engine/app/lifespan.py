# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the app lifespan and service initialization."""

import typing as ty
from contextlib import asynccontextmanager

from fastapi import FastAPI

from hiresify_engine.config import AppConfig
from hiresify_engine.db.repository import Repository
from hiresify_engine.service import BlobService, CacheService, QueueService

##########
# lifespan
##########

@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    config: AppConfig = app.state.config

    # Initialize the blob store manager.
    app.state.blob = blob = BlobService(
        config.blob_store_url,
        region_tag=config.blob_store_region,
        access_key=config.blob_access_key,
        secret_key=config.blob_secret_key,
    )

    # Initialize the broker service for compute jobs.
    app.state.broker = broker = QueueService(config.redis_url)

    # Initialize the cache store manager.
    app.state.cache = cache = CacheService(config.redis_url)

    # Initialize the database repository.
    app.state.repo = repo = Repository(config.database_url, **config.database_config)

    # Initialize the blob bucket.
    async with blob.start_session(config.production) as session:
        await session.init_bucket()

    # Initialize the job queue.
    await broker.init_queue()

    # Initialize the database schema.
    await repo.init_schema()

    yield

    async with blob.start_session(config.production) as session:
        await session.dispose()

    await broker.dispose()
    await cache.dispose()
    await repo.dispose()
