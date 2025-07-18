# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the repository layer around the database."""

import contextlib
import typing as ty
from collections import abc
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload, with_loader_criteria

from .exception import EntityConflictError, EntityNotFoundError
from .model import Base, Blob, RefreshToken, Upload, User
from .util import abbreviate_token


class Repository:
    """A wrapper class providing APIs to manage the database."""

    def __init__(self, url: str, **configs: ty.Any) -> None:
        """Initialize a new instance of Repository."""
        self._engine = create_async_engine(url, **configs)
        self._create_session = async_sessionmaker(
            bind=self._engine, expire_on_commit=False,
        )

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

    async def find_user(self, username: str, *, eager: bool = False) -> User:
        """Find the user with the given user name."""
        options = [
            selectinload(User.blobs),
            with_loader_criteria(Blob, Blob.deleted.is_(False)),
        ] if eager else []

        where_clause = User.username == username
        stmt = select(User).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, username=username)

            return user

    async def register_user(self, username: str, password: str) -> User:
        """Register a user given a user name and a hashed password."""
        user = User(username=username, password=password)

        async with self.session() as session:
            try:
                async with session.begin():
                    session.add(user)
            except IntegrityError as e:
                raise EntityConflictError(User, username=username) from e

            await session.refresh(user)
            return user

    async def update_password(self, username: str, password: str) -> None:
        """Update a user's password given the user name and the new hashed password."""
        where_clause = User.username == username
        stmt = select(User).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, username=username)

            async with session.begin():
                user.password = password

    async def delete_user(self, username: str) -> None:
        """Delete a user by the given user name."""
        where_clause = User.username == username
        stmt = select(User).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, username=username)

            async with session.begin():
                await session.delete(user)

    ###############
    # refresh token
    ###############

    async def find_token(self, token: str, *, eager: bool = False) -> RefreshToken:
        """Find the refresh token with the given token string."""
        options = [selectinload(RefreshToken.user)] if eager else []
        where_clause = and_(
            RefreshToken.token == token,
            RefreshToken.revoked.is_(False),
        )
        stmt = select(RefreshToken).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (refresh_token := result.scalar_one_or_none()):
                raise EntityNotFoundError(RefreshToken, token=abbreviate_token(token))

            return refresh_token

    async def find_tokens(self, user_uid: str) -> list[RefreshToken]:
        """Find all the refresh tokens for the given user UID."""
        options = [
            selectinload(User.refresh_tokens),
            with_loader_criteria(RefreshToken, RefreshToken.revoked.is_(False)),
        ]
        where_clause = User.uid == user_uid
        stmt = select(User).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            return user.refresh_tokens

    async def create_token(
        self,
        user_uid: str,
        *,
        token: str,
        issued_at: datetime,
        expire_at: datetime,
        **metadata: ty.Any,
    ) -> RefreshToken:
        """Create a refresh token for the given user UID."""
        where_clause = User.uid == user_uid
        stmt = select(User).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            refresh_token = RefreshToken(
                token=token,
                issued_at=issued_at,
                expire_at=expire_at,
                user_id=user.id,
                **metadata,
            )

            async with session.begin():
                session.add(refresh_token)

            await session.refresh(refresh_token)
            return refresh_token

    async def revoke_token(self, token: str) -> None:
        """Revoke a refresh token given its token string."""
        where_clause = and_(
            RefreshToken.token == token,
            RefreshToken.revoked.is_(False),
        )
        stmt = select(RefreshToken).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (refresh_token := result.scalar_one_or_none()):
                raise EntityNotFoundError(RefreshToken, token=abbreviate_token(token))

            async with session.begin():
                refresh_token.revoked = True

    async def revoke_tokens(self, user_uid: str) -> int:
        """Revoke all the refresh tokens for the given user UID."""
        options = [
            selectinload(User.refresh_tokens),
            with_loader_criteria(RefreshToken, RefreshToken.revoked.is_(False)),
        ]

        where_clause = User.uid == user_uid
        stmt = select(User).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            async with session.begin():
                if not (refresh_tokens := user.refresh_tokens):
                    return 0

                for refresh_token in refresh_tokens:
                    refresh_token.revoked = True

                return len(refresh_tokens)

    async def purge_tokens(
        self, retention_days: int, now: datetime | None = None,
    ) -> int:
        """Purge all the refresh tokens expired for longer than `retention_days`."""
        cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
        where_clause = or_(
            RefreshToken.expire_at < cutoff,
            RefreshToken.revoked.is_(True),
        )
        stmt = delete(RefreshToken).where(where_clause)

        async with self.session() as session:
            async with session.begin():
                result = await session.execute(stmt)

                return result.rowcount

    #############
    # blob files
    #############

    async def find_blob(self, blob_uid: str, *, eager: bool = False) -> Blob:
        """Find the blob with the given blob UID."""
        options = [selectinload(Blob.user)] if eager else []
        where_clause = and_(Blob.uid == blob_uid, Blob.deleted.is_(False))
        stmt = select(Blob).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (blob := result.scalar_one_or_none()):
                raise EntityNotFoundError(Blob, uid=blob_uid)

            return blob

    async def find_blobs(self, user_uid: str) -> list[Blob]:
        """Find all the blobs for the given user UID."""
        options = [
            selectinload(User.blobs),
            with_loader_criteria(Blob, Blob.deleted.is_(False)),
        ]
        where_clause = User.uid == user_uid
        stmt = select(User).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            return user.blobs

    async def create_blob(
        self,
        user_uid: str,
        *,
        blob_key: str,
        file_name: str,
        created_at: datetime,
        valid_thru: datetime,
    ) -> Blob:
        """Create a blob for the given user UID."""
        where_clause = User.uid == user_uid
        stmt = select(User).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            blob = Blob(
                blob_key=blob_key,
                file_name=file_name,
                created_at=created_at,
                valid_thru=valid_thru,
                user_id=user.id,
            )

            async with session.begin():
                session.add(blob)

            await session.refresh(blob)
            return blob

    async def delete_blob(self, blob_uid: str) -> None:
        """Delete an blob given the blob UID."""
        where_clause = and_(Blob.uid == blob_uid, Blob.deleted.is_(False))
        stmt = select(Blob).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (blob := result.scalar_one_or_none()):
                raise EntityNotFoundError(Blob, uid=blob_uid)

            async with session.begin():
                blob.deleted = True

    async def delete_blobs(self, user_uid: str) -> int:
        """Delete all the blobs for the given user UID."""
        options = [
            selectinload(User.blobs),
            with_loader_criteria(Blob, Blob.deleted.is_(False)),
        ]

        where_clause = User.uid == user_uid
        stmt = select(User).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            async with session.begin():
                if not (blobs := user.blobs):
                    return 0

                for blob in blobs:
                    blob.deleted = True

                return len(blobs)

    async def purge_blobs(
        self, retention_days: int, now: datetime | None = None,
    ) -> int:
        """Purge all the blobs expired for longer than `retention_days`."""
        cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
        where_clause = or_(Blob.valid_thru < cutoff, Blob.deleted.is_(True))
        stmt = delete(Blob).where(where_clause)

        async with self.session() as session:
            async with session.begin():
                result = await session.execute(stmt)

                return result.rowcount

    ##############
    # upload blobs
    ##############

    async def find_upload(self, uid: str, *, eager: bool = False) -> Upload:
        """Find the upload with the given upload UID."""
        options = [selectinload(Upload.user)] if eager else []
        where_clause = Upload.uid == uid
        stmt = select(Upload).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (upload := result.scalar_one_or_none()):
                raise EntityNotFoundError(Upload, uid=uid)

            return upload

    async def start_upload(
        self,
        user_uid: str,
        *,
        uid: str,
        blob_key: str,
        created_at: datetime,
        valid_thru: datetime,
    ) -> Upload:
        """Start an upload of a blob for the given user UID."""
        where_clause = User.uid == user_uid
        stmt = select(User).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            upload = Upload(
                uid=uid,
                blob_key=blob_key,
                created_at=created_at,
                valid_thru=valid_thru,
                user_id=user.id,
            )

            async with session.begin():
                session.add(upload)

            await session.refresh(upload)
            return upload

    async def remove_upload(self, uid: str) -> None:
        """Remove an upload with the given upload ID.

        An upload is removable when it's either finished or canceled.
        """
        where_clause = and_(Upload.uid == uid)
        stmt = delete(Upload).where(where_clause)

        async with self.session() as session:
            async with session.begin():
                await session.execute(stmt)

    async def purge_uploads(
        self, retention_days: int, now: datetime | None = None,
    ) -> ty.Sequence[Upload]:
        """Purge all the uploads expired for longer than `retention_days`."""
        cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
        where_clause = Upload.valid_thru < cutoff
        stmt = delete(Upload).where(where_clause)

        async with self.session() as session:
            async with session.begin():
                result = await session.execute(stmt)
                return result.scalars().all()
