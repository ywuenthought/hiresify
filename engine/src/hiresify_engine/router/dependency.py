# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the reusable dependencies for FastAPI endpoints."""

import typing as ty

from fastapi import Depends, FastAPI, Request
from redis.asyncio import Redis

from hiresify_engine.db.repository import Repository
from hiresify_engine.tool import JWTManager, PWDManager

T = ty.TypeVar("T")


def from_state(attr: str, _type: type[T]) -> ty.Callable[[Request], T]:
    """Create a dependency to fetch an object from app.state."""
    def dependency(request: Request) -> T:
        app: FastAPI = request.app
        return ty.cast(T, getattr(app.state, attr))
    return dependency


CacheStoreDep = ty.Annotated[Redis, Depends(from_state("redis", Redis))]
JWTManagerDep = ty.Annotated[JWTManager, Depends(from_state("jwt_manager", JWTManager))]
PWDManagerDep = ty.Annotated[PWDManager, Depends(from_state("pwd_manager", PWDManager))]
RepositoryDep = ty.Annotated[Repository, Depends(from_state("repo", Repository))]
