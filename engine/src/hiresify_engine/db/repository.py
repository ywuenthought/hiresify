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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hiresify_engine.type import FilePath

from .models import Base, UserAuth


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

    #################
    # user management
    #################

    async def find_user(self, username: str) -> UserAuth | None:
        """
        Find the user with the given user name.
        """
        where_clause = UserAuth.username == username

        async with self.session() as session:
            stmt = select(UserAuth).where(where_clause)
            result = await session.execute(stmt)

            return result.scalar_one_or_none()

    async def register_user(self, username: str, password: str) -> UserAuth:
        """
        Register a user given a user name and a hashed password.
        """
        user = UserAuth(username=username, password=password)

        async with self.session() as session:
            async with session.begin():
                session.add(user)

            await session.refresh(user)
            return user

    async def update_password(self, username: str, password: str) -> bool:
        """
        Update a user's password given the user name and the new hashed password.
        """
        where_clause = UserAuth.username == username

        async with self.session() as session:
            async with session.begin():
                stmt = select(UserAuth).where(where_clause)
                result = await session.execute(stmt)

                if user := result.scalar_one_or_none():
                    user.password = password
                    return True

                return False

    async def delete_user(self, username: str) -> bool:
        """
        Delete a user by the given user name.
        """
        where_clause = UserAuth.username == username

        async with self.session() as session:
            async with session.begin():
                stmt = select(UserAuth).where(where_clause)
                result = await session.execute(stmt)

                if user := result.scalar_one_or_none():
                    await session.delete(user)
                    return True

                return False
