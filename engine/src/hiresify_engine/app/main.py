# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from hiresify_engine import const
from hiresify_engine.config import AppConfig
from hiresify_engine.router import api_routers, routers

from .lifespan import lifespan
from .middleware import HTTPSOnlyMiddleware

app = FastAPI(lifespan=lifespan)

app.state.config = config = AppConfig()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=[config.allowed_origin],
)

if config.production:
    app.add_middleware(HTTPSOnlyMiddleware)

app.mount("/static", StaticFiles(directory=const.STATIC_DIR))

for router in routers + api_routers:
    app.include_router(router)
