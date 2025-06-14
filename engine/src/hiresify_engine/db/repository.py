# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""
Exports the repository layer around the database.
"""

import contextlib
import json
import typing as ty
from collections import abc

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hiresify_engine.type import FilePath

from .models import Base


class Repository:
    """
    A wrapper class providing APIs to manage the database.
    """

    def __init__(self, url: str, **configs: dict[str, ty.Any]) -> None:
        self._engine = create_async_engine(url, **configs)
        self._create_session = async_sessionmaker(bind=self._engine)

    @classmethod
    def from_config_file(cls, url: str, *, config_file: FilePath) -> "Repository":
        """
        Create a Repository instance from a JSON configuration file. 
        """
        with open(config_file) as fp:
            configs = json.load(fp)

        return cls(url, **configs)

    @contextlib.asynccontextmanager
    async def session(self) -> abc.AsyncGenerator[AsyncSession, None]:
        """
        Provide an async context-managed database session.
        """
        async with self._create_session() as session:
            yield session

    async def init_schema(self) -> None:
        """
        Initialize all the tables based on a pre-defined schema.
        """
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        """
        Dispose of the database engine and close all pooled connections.
        """
        await self._engine.dispose()
