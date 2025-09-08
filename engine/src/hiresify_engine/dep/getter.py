# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the getter functions for endpoint dependencies."""

from fastapi import FastAPI, Request

from hiresify_engine.config import AppConfig
from hiresify_engine.db.repository import Repository
from hiresify_engine.service import BlobService, CacheService, QueueService


def get_blob(request: Request) -> BlobService:
    """Get the blob service from app.state."""
    app: FastAPI = request.app
    service: BlobService = app.state.blob
    return service


def get_queue(request: Request) -> QueueService:
    """Get the job queue service from app.state."""
    app: FastAPI = request.app
    service: QueueService = app.state.queue
    return service


def get_cache(request: Request) -> CacheService:
    """Get the cache service from app.state."""
    app: FastAPI = request.app
    service: CacheService = app.state.cache
    return service


def get_config(request: Request) -> AppConfig:
    """Get the app configuration from app.state."""
    app: FastAPI = request.app
    config: AppConfig = app.state.config
    return config


def get_repo(request: Request) -> Repository:
    """Get the database repository from app.state."""
    app: FastAPI = request.app
    repository: Repository = app.state.repo
    return repository
