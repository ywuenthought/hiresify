# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the application entry point."""

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from hiresify_engine import const
from hiresify_engine.config import AppConfig
from hiresify_engine.router import api_routers, routers

from .lifespan import lifespan
from .middleware import HTTPSOnlyMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


app = FastAPI(lifespan=lifespan)

app.state.config = config = AppConfig()

if config.production:
    app.add_middleware(HTTPSOnlyMiddleware)

app.mount("/static", StaticFiles(directory=const.STATIC_DIR))

for router in routers + api_routers:
    app.include_router(router)
