# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the getter functions for endpoint dependencies."""

from fastapi import FastAPI, Request

from hiresify_engine.blob.service import BlobService
from hiresify_engine.cache.service import CacheService
from hiresify_engine.db.repository import Repository


def get_blob(request: Request) -> BlobService:
    """Get the blob service from app.state."""
    app: FastAPI = request.app
    service: BlobService = app.state.blob
    return service


def get_cache(request: Request) -> CacheService:
    """Get the cache service from app.state."""
    app: FastAPI = request.app
    service: CacheService = app.state.cache
    return service


def get_repo(request: Request) -> Repository:
    """Get the database repository from app.state."""
    app: FastAPI = request.app
    repository: Repository = app.state.repo
    return repository
