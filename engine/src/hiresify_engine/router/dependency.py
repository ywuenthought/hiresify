# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the reusable dependencies for FastAPI endpoints."""

import typing as ty

from fastapi import Depends, FastAPI, Request

from hiresify_engine.db.repository import Repository
from hiresify_engine.tool import CCHManager, JWTManager, PWDManager

T = ty.TypeVar("T")


def from_state(attr: str, _type: type[T]) -> ty.Callable[[Request], T]:
    """Create a dependency to fetch an object from app.state."""
    def dependency(request: Request) -> T:
        app: FastAPI = request.app
        return ty.cast(T, getattr(app.state, attr))
    return dependency


AppEnvironDep = ty.Annotated[dict, Depends(from_state("env", dict))]
CCHManagerDep = ty.Annotated[CCHManager, Depends(from_state("cch", CCHManager))]
JWTManagerDep = ty.Annotated[JWTManager, Depends(from_state("jwt", JWTManager))]
PWDManagerDep = ty.Annotated[PWDManager, Depends(from_state("pwd", PWDManager))]
RepositoryDep = ty.Annotated[Repository, Depends(from_state("repo", Repository))]
