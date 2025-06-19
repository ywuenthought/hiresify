# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the reusable dependencies for FastAPI endpoints."""

import typing as ty

from fastapi import Depends, FastAPI, Request
from redis.asyncio import Redis

from hiresify_engine.db.repository import Repository


async def get_repository(request: Request) -> Repository:
    """Retrieve the repository object from the state."""
    app: FastAPI = request.app
    repo: Repository = app.state.repo
    return repo


async def get_redis(request: Request) -> Redis:
    """Retrieve the in-memory database client from the state."""
    app: FastAPI = request.app
    redis: Redis = app.state.redis
    return redis


RepositoryDep = ty.Annotated[Repository, Depends(get_repository)]
RedisDep = ty.Annotated[Redis, Depends(get_redis)]
