# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the application entry point."""

from functools import partial

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from hiresify_engine import const
from hiresify_engine.envvar import ACCESS_TTL, PRODUCTION
from hiresify_engine.jwt.service import JWTTokenService
from hiresify_engine.router import api_routers, routers
from hiresify_engine.router.util import add_secure_headers

from .lifespan import lifespan
from .middleware import HTTPSOnlyMiddleware

##########
# main app
##########

app = FastAPI(lifespan=lifespan)

if PRODUCTION:
    app.add_middleware(HTTPSOnlyMiddleware)

# Initialize the callable to add secure headers to a response.
app.state.add_secure_headers = partial(add_secure_headers, production=PRODUCTION)

# Initialize the JWT access token service.
app.state.jwt = JWTTokenService(ACCESS_TTL)

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
