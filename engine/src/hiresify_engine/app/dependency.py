# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the reusable dependencies for FastAPI endpoints."""

import typing as ty

from fastapi import Depends, FastAPI, Request

from hiresify_engine.db.repository import Repository


async def get_repository(request: Request) -> Repository:
    """Retrieve the repository object from the state."""
    app: FastAPI = request.app
    repository: Repository = app.state.repository
    return repository


RepositoryDep = ty.Annotated[Repository, Depends(get_repository)]
