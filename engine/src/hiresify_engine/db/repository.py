# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the repository layer around the database."""

import contextlib
import json
import typing as ty
from collections import abc
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload, with_loader_criteria

from hiresify_engine.type import FilePath

from .exception import EntityConflictError, EntityNotFoundError
from .models import Base, RefreshToken, UserAuth
from .util import abbreviate_token


class Repository:
    """A wrapper class providing APIs to manage the database."""

    def __init__(self, url: str, **configs: ty.Any) -> None:
        """Initialize a new instance of Repository."""
        self._engine = create_async_engine(url, **configs)
        self._create_session = async_sessionmaker(
            bind=self._engine, expire_on_commit=False,
        )

    @classmethod
    def from_config_file(cls, url: str, *, config_file: FilePath) -> "Repository":
        """Create a Repository instance from a JSON configuration file."""
        with open(config_file) as fp:
            configs = json.load(fp)

        return cls(url, **configs)

    @contextlib.asynccontextmanager
    async def session(self) -> abc.AsyncGenerator[AsyncSession, None]:
        """Provide an async context-managed database session."""
        async with self._create_session() as session:
            yield session

    async def init_schema(self) -> None:
        """Initialize all the tables based on a pre-defined schema."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def purge_tables(self) -> None:
        """Purge all the tables (delete all the rows)."""
        async with self.session() as session:
            async with session.begin():
                for table in reversed(Base.metadata.sorted_tables):
                    await session.execute(table.delete())

    async def dispose(self) -> None:
        """Dispose of the database engine and close all pooled connections."""
        await self._engine.dispose()

    #################
    # user management
    #################

    async def find_user(self, username: str) -> UserAuth:
        """Find the user with the given user name."""
        where_clause = UserAuth.username == username

        async with self.session() as session:
            stmt = select(UserAuth).where(where_clause)
            result = await session.execute(stmt)

            try:
                return result.scalar_one()
            except NoResultFound as e:
                raise EntityNotFoundError(UserAuth, username=username) from e

    async def register_user(self, username: str, password: str) -> UserAuth:
        """Register a user given a user name and a hashed password."""
        user = UserAuth(username=username, password=password)

        async with self.session() as session:
            try:
                async with session.begin():
                    session.add(user)
            except IntegrityError as e:
                raise EntityConflictError(UserAuth, username=username) from e

            await session.refresh(user)
            return user

    async def update_password(self, username: str, password: str) -> None:
        """Update a user's password given the user name and the new hashed password."""
        where_clause = UserAuth.username == username

        async with self.session() as session:
            async with session.begin():
                stmt = select(UserAuth).where(where_clause)
                result = await session.execute(stmt)

                try:
                    user = result.scalar_one()
                    user.password = password
                except NoResultFound as e:
                    raise EntityNotFoundError(UserAuth, username=username) from e

    async def delete_user(self, username: str) -> None:
        """Delete a user by the given user name."""
        where_clause = UserAuth.username == username

        async with self.session() as session:
            async with session.begin():
                stmt = select(UserAuth).where(where_clause)
                result = await session.execute(stmt)

                try:
                    user = result.scalar_one()
                    await session.delete(user)
                except NoResultFound as e:
                    raise EntityNotFoundError(UserAuth, username=username) from e

    ###############
    # refresh token
    ###############

    async def find_token(self, token: str) -> RefreshToken:
        """Find the refresh token with the given hashed token."""
        where_clause = RefreshToken.token == token

        async with self.session() as session:
            stmt = select(RefreshToken).where(where_clause)
            result = await session.execute(stmt)

            try:
                return result.scalar_one()
            except NoResultFound as e:
                raise EntityNotFoundError(
                    # Do not log the entire token for security.
                    RefreshToken, token=abbreviate_token(token),
                ) from e

    async def find_tokens(self, username: str) -> list[RefreshToken]:
        """Find all the refresh tokens for a user with the given user name."""
        option = selectinload(UserAuth.refresh_tokens)
        where_clause = UserAuth.username == username

        async with self.session() as session:
            stmt = select(UserAuth).options(option).where(where_clause)
            result = await session.execute(stmt)

            try:
                user = result.scalar_one()
                return user.refresh_tokens
            except NoResultFound as e:
                raise EntityNotFoundError(UserAuth, username=username) from e

    async def create_token(
        self,
        username: str,
        token: str,
        *,
        issued_at: datetime,
        expire_at: datetime,
        **params: ty.Any,
    ) -> RefreshToken:
        """Create a refresh token for a user with the given user name."""
        user = await self.find_user(username)

        refresh_token = RefreshToken(
            token=token,
            issued_at=issued_at,
            expire_at=expire_at,
            user_id=user.id,
            **params,
        )

        async with self.session() as session:
            try:
                async with session.begin():
                    session.add(refresh_token)
            except IntegrityError as e:
                raise EntityConflictError(
                    RefreshToken, token=abbreviate_token(token),
                ) from e

            await session.refresh(refresh_token)
            return refresh_token

    async def revoke_token(self, token: str) -> None:
        """Revoke a refresh token given its hashed token."""
        where_clause = RefreshToken.token == token

        async with self.session() as session:
            async with session.begin():
                stmt = select(RefreshToken).where(where_clause)
                result = await session.execute(stmt)

                try:
                    refresh_token = result.scalar_one()
                    refresh_token.revoked = True
                except NoResultFound as e:
                    raise EntityNotFoundError(
                        RefreshToken, token=abbreviate_token(token),
                    ) from e

    async def revoke_tokens(self, username: str) -> int:
        """Revoke all the refresh tokens for a user with the given user name."""
        options = [
            selectinload(UserAuth.refresh_tokens),
            with_loader_criteria(RefreshToken, RefreshToken.revoked.is_(False)),
        ]

        where_clause = UserAuth.username == username

        async with self.session() as session:
            async with session.begin():
                stmt = select(UserAuth).options(*options).where(where_clause)
                result = await session.execute(stmt)

                try:
                    user = result.scalar_one()

                    if not (refresh_tokens := user.refresh_tokens):
                        return 0

                    for refresh_token in refresh_tokens:
                        refresh_token.revoked = True

                    return len(refresh_tokens)

                except NoResultFound as e:
                    raise EntityNotFoundError(UserAuth, username=username) from e

    async def purge_tokens(
        self, retention_days: int, now: datetime | None = None,
    ) -> int:
        """Purge all the refresh tokens expired for longer than `retention_days`."""
        cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
        where_clause = RefreshToken.expire_at < cutoff

        async with self.session() as session:
            async with session.begin():
                stmt = delete(RefreshToken).where(where_clause)
                result = await session.execute(stmt)

                return result.rowcount
