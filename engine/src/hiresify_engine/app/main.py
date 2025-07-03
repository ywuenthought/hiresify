# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the application entry point."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from hiresify_engine.const import STATIC_DIR
from hiresify_engine.router import api_routers, routers

from .lifespan import lifespan

##########
# main app
##########

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR))

for router in routers:
    app.include_router(router)

#########
# API app
#########

api_app = FastAPI()

for api_router in api_routers:
    api_app.include_router(api_router)

app.mount("/api", api_app)
