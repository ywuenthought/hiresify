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
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from hiresify_engine.type import FilePath

from .exception import EntityNotFoundError
from .models import Base, RefreshToken, UserAuth
from .util import abbreviate_token


class Repository:
    """
    A wrapper class providing APIs to manage the database.
    """

    def __init__(self, url: str, **configs: ty.Any) -> None:
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

    async def find_user(self, username: str) -> UserAuth:
        """
        Find the user with the given user name.
        """
        where_clause = UserAuth.username == username

        async with self.session() as session:
            stmt = select(UserAuth).where(where_clause)
            result = await session.execute(stmt)

            if (user := result.scalar_one_or_none()) is None:
                raise EntityNotFoundError(UserAuth, username=username)

            return user

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

    ###############
    # refresh token
    ###############

    async def find_token(self, token: str) -> RefreshToken:
        """
        Find the refresh token with the given hashed token.
        """
        where_clause = RefreshToken.token == token

        async with self.session() as session:
            stmt = select(RefreshToken).where(where_clause)
            result = await session.execute(stmt)

            if (refresh_token := result.scalar_one_or_none()) is None:
                # Do not log the entire token for security.
                raise EntityNotFoundError(
                    RefreshToken, token=abbreviate_token(token, 6)
                )

            return refresh_token

    async def find_tokens(self, username: str) -> ty.Sequence[RefreshToken]:
        """
        Find all the refresh tokens for a user with the given user name.
        """
        user = await self.find_user(username)

        where_clause = RefreshToken.user_id == user.id

        async with self.session() as session:
            stmt = select(RefreshToken).where(where_clause)
            result = await session.execute(stmt)

            return result.scalars().all()

    async def create_token(
        self, username: str, token: str, issued_at: datetime, expires_at: datetime
    ) -> RefreshToken:
        """Create a refresh token for a user with the given user name."""
        user = await self.find_user(username)

        refresh_token = RefreshToken(
            token=token,
            issued_at=issued_at,
            expires_at=expires_at,
            user_id=user.id,
        )

        async with self.session() as session:
            async with session.begin():
                session.add(refresh_token)

            await session.refresh(refresh_token)
            return refresh_token

    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a refresh token given its hashed token.
        """
        where_clause = RefreshToken.token == token

        async with self.session() as session:
            async with session.begin():
                stmt = select(RefreshToken).where(where_clause)
                result = await session.execute(stmt)

                if refresh_token := result.scalar_one_or_none():
                    refresh_token.revoked = True
                    return True

                return False

    async def revoke_tokens(self, username: str) -> int:
        """
        Revoke all the refresh tokens for a user with the given user name.
        """
        user = await self.find_user(username)

        where_clauses = [
            RefreshToken.user_id == user.id,
            RefreshToken.revoked.is_(False),
        ]

        async with self.session() as session:
            stmt = select(RefreshToken).where(*where_clauses)
            result = await session.execute(stmt)

            if not (refresh_tokens := result.scalars().all()):
                return 0

            async with session.begin():
                for refresh_token in refresh_tokens:
                    refresh_token.revoked = True

            return len(refresh_tokens)

    async def purge_tokens(self, retention_days: int) -> int:
        """
        Purge (delete) all the refresh tokens expired for longer than `retention_days`.
        """
        cutoff = datetime.now(UTC) - timedelta(days=retention_days)
        where_clause = RefreshToken.expires_at < cutoff

        async with self.session() as session:
            async with session.begin():
                stmt = delete(RefreshToken).where(where_clause)
                result = await session.execute(stmt)

                return result.rowcount
