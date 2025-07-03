# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the application entry point."""

from functools import partial

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from hiresify_engine import const
from hiresify_engine.router import api_routers, routers
from hiresify_engine.router.util import add_secure_headers
from hiresify_engine.tool import JWTTokenManager
from hiresify_engine.util import get_envvar

from .lifespan import lifespan
from .middleware import HTTPSOnlyMiddleware

##########
# env vars
##########

# Load the access token TTL and default to 900 seconds.
access_ttl = get_envvar(const.ACCESS_TTL, int, 900)

# Load the deployment type and default to "development".
deployment = get_envvar(const.DEPLOYMENT, str, const.DEVELOPMENT)

##########
# main app
##########

app = FastAPI(lifespan=lifespan)

# Initialize the callable to add secure headers to a response.
app.state.add_secure_headers = partial(add_secure_headers, deployment=deployment)

# Initialize the JWT access token manager.
app.state.jwt = JWTTokenManager(access_ttl)

if deployment == const.PRODUCTION:
    app.add_middleware(HTTPSOnlyMiddleware)

for router in routers:
    app.include_router(router)

#########
# API app
#########

api_app = FastAPI()

for api_router in api_routers:
    api_app.include_router(api_router)

app.mount("/api", api_app)
app.mount("/static", StaticFiles(directory=const.STATIC_DIR))
