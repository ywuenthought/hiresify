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
from hiresify_engine.db.repository import Repository
from hiresify_engine.tool import CCHManager, JWTManager, PKCEManager, PWDManager
from hiresify_engine.util import get_envvar


@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    # Load the access token TTL and default to 900 seconds.
    access_ttl = get_envvar(const.ACCESS_TTL, int, 900)

    # Load the database URL and default to an empty string.
    db_url = get_envvar(const.DATABASE_URL, str, "")

    # Load the database config file path and default to an empty string.
    db_config = get_envvar(const.DATABASE_CONFIG, str, "")

    # Load the redis server URL and default to an empty string.
    redis_url = get_envvar(const.REDIS_URL, str, "")

    # Load the refresh token TTL and default to 30 days.
    refresh_ttl = get_envvar(const.REFRESH_TTL, int, 30)

    # Load the regular cache entry TTL and default to 300 seconds.
    regular_ttl = get_envvar(const.REGULAR_TTL, int, 300)

    # Load the session TTL and default to 1800 seconds.
    session_ttl = get_envvar(const.SESSION_TTL, int, 1800)

    with open(db_config) as fp:
        configs = json.load(fp)

    # Initialize the cache store manager.
    app.state.cch = CCHManager(redis_url, regular_ttl, session_ttl)

    # Initialize the JWT access token manager.
    app.state.jwt = JWTManager(access_ttl)

    # Initialize the PKCE code manager.
    app.state.pkce = PKCEManager()

    # Initialize the user password manager.
    app.state.pwd = PWDManager()

    # Initialize the database repository.
    app.state.repo = Repository(db_url, refresh_ttl, **configs)

    yield

    await app.state.cch.dispose()
    await app.state.repo.dispose()
