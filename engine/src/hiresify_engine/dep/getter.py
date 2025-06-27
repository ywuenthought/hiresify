# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the getter functions for endpoint dependencies."""

from fastapi import FastAPI, Request

from hiresify_engine.cache.service import CacheService
from hiresify_engine.db.repository import Repository
from hiresify_engine.tool import JWTManager, PKCEManager, PWDManager


def get_cache(request: Request) -> CacheService:
    """Get the cache service from app.state."""
    app: FastAPI = request.app
    service: CacheService = app.state.cache
    return service


def get_jwt(request: Request) -> JWTManager:
    """Get the JWT access token manager from app.state."""
    app: FastAPI = request.app
    manager: JWTManager = app.state.jwt
    return manager


def get_pkce(request: Request) -> PKCEManager:
    """Get the PKCE code manager from app.state."""
    app: FastAPI = request.app
    manager: PKCEManager = app.state.pkce
    return manager


def get_pwd(request: Request) -> PWDManager:
    """Get the user password manager from app.state."""
    app: FastAPI = request.app
    manager: PWDManager = app.state.pwd
    return manager


def get_repo(request: Request) -> Repository:
    """Get the database repository from app.state."""
    app: FastAPI = request.app
    repository: Repository = app.state.repo
    return repository
