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
from hiresify_engine.testing import TestCCHStoreManager, test_repository
from hiresify_engine.tool import CCHManager, JWTManager, PKCEManager, PWDManager
from hiresify_engine.util import get_envvar


@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    deployment = get_envvar(const.DEPLOYMENT, str, const.TESTING)

    if deployment not in (const.TESTING, const.DEVELOPMENT, const.PRODUCTION):
        raise ValueError(f"{deployment=} is invalid.")

    # Load the access token TTL and default to 900 seconds.
    access_ttl = get_envvar(const.ACCESS_TTL, int, 900)

    # Load the refresh token TTL and default to 30 days.
    refresh_ttl = get_envvar(const.REFRESH_TTL, int, 30)

    # Load the regular cache entry TTL and default to 300 seconds.
    regular_ttl = get_envvar(const.REGULAR_TTL, int, 300)

    # Load the session TTL and default to 1800 seconds.
    session_ttl = get_envvar(const.SESSION_TTL, int, 1800)

    # Load the database URL and default to an empty string.
    db_url = get_envvar(const.DATABASE_URL, str, "")

    # Load the database config file path and default to an empty string.
    db_config = get_envvar(const.DATABASE_CONFIG, str, "")

    # Load the redis host and default to localhost.
    host = get_envvar(const.REDIS_HOST, str, "localhost")

    # Load the redis port and default to 6379.
    port = get_envvar(const.REDIS_PORT, int, 6379)

    # Initialize the PKCE code manager.
    app.state.pkce = PKCEManager()

    # Initialize the JWT access token manager.
    app.state.jwt = JWTManager(access_ttl)

    # Initialize the user password manager.
    app.state.pwd = PWDManager()

    if deployment == const.TESTING:

        # Initialize the test cache manager.
        app.state.cch = TestCCHStoreManager(regular_ttl, session_ttl)

        # Initialize the test database repository.
        async with test_repository(refresh_ttl) as repo:
            app.state.repo = repo
            yield

    else:

        with open(db_config, "r") as fp:
            configs = json.load(fp)

        # Initialize the cache store manager.
        app.state.cch = CCHManager(regular_ttl, session_ttl, host=host, port=port)

        # Initialize the database repository.
        app.state.repo = Repository(db_url, refresh_ttl, **configs)

        yield

    await app.state.cch.dispose()
