# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the application entry point."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from hiresify_engine import const
from hiresify_engine.envvar import PRODUCTION
from hiresify_engine.router import api_routers, routers

from .lifespan import lifespan
from .middleware import HTTPSOnlyMiddleware

##########
# main app
##########

app = FastAPI(lifespan=lifespan)

if PRODUCTION:
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
