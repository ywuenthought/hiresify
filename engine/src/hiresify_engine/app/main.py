# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the application entry point."""

import typing as ty
from contextlib import asynccontextmanager

from fastapi import FastAPI

from hiresify_engine.db.repository import Repository

from .router import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> ty.AsyncGenerator[None, None]:
    """Wrap the lifespan events for the application."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
        db_url = f"sqlite+aiosqlite:///{temp_db.name}"
        app.state.repository = repository = Repository(db_url)
        await repository.init_schema()
        yield
        await repository.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
