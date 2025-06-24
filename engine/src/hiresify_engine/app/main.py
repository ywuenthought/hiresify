# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the application entry point."""

from fastapi import FastAPI

from hiresify_engine.router import routers

from .lifespan import lifespan

app = FastAPI(lifespan=lifespan)

for router in routers:
    app.include_router(router)
