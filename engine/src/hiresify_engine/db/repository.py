# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the repository layer around the database."""

import contextlib
import typing as ty
from collections import abc
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from hiresify_engine.model import Blob, Upload

from .exception import EntityConflictError, EntityNotFoundError
from .mapper import to_blob, to_upload
from .model import Base, BlobORM, RefreshTokenORM, UploadORM, UserORM
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

    async def find_user(self, username: str, *, eager: bool = False) -> UserORM:
        """Find the user with the given user name."""
        options = [selectinload(UserORM.blobs)] if eager else []

        whereclause = UserORM.username == username
        stmt = select(UserORM).options(*options).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, username=username)

            return user

    async def register_user(self, username: str, password: str) -> UserORM:
        """Register a user given a user name and a hashed password."""
        user = UserORM(username=username, password=password)

        async with self.session() as session:
            try:
                async with session.begin():
                    session.add(user)
            except IntegrityError as e:
                raise EntityConflictError(UserORM, username=username) from e

            await session.refresh(user)
            return user

    async def update_password(self, username: str, password: str) -> None:
        """Update a user's password given the user name and the new hashed password."""
        whereclause = UserORM.username == username
        stmt = select(UserORM).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, username=username)

            async with session.begin():
                user.password = password

    async def delete_user(self, username: str) -> None:
        """Delete a user by the given user name."""
        whereclause = UserORM.username == username
        stmt = select(UserORM).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, username=username)

            async with session.begin():
                await session.delete(user)

    ###############
    # refresh token
    ###############

    async def find_token(self, token: str, *, eager: bool = False) -> RefreshTokenORM:
        """Find the refresh token with the given token string."""
        options = [selectinload(RefreshTokenORM.user)] if eager else []
        whereclause = RefreshTokenORM.token == token
        stmt = select(RefreshTokenORM).options(*options).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (refresh_token := result.scalar_one_or_none()):
                raise EntityNotFoundError(
                    RefreshTokenORM, token=abbreviate_token(token),
                )

            return refresh_token

    async def find_tokens(self, user_uid: str) -> list[RefreshTokenORM]:
        """Find all the refresh tokens for the given user UID."""
        option = selectinload(UserORM.refresh_tokens)
        whereclause = UserORM.uid == user_uid
        stmt = select(UserORM).options(option).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, uid=user_uid)

            return user.refresh_tokens

    async def create_token(
        self,
        user_uid: str,
        *,
        token: str,
        issued_at: datetime,
        expire_at: datetime,
        **metadata: ty.Any,
    ) -> RefreshTokenORM:
        """Create a refresh token for the given user UID."""
        whereclause = UserORM.uid == user_uid
        stmt = select(UserORM).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, uid=user_uid)

            refresh_token = RefreshTokenORM(
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
        whereclause = RefreshTokenORM.token == token
        stmt = delete(RefreshTokenORM).where(whereclause)

        async with self.session() as session:
            async with session.begin():
                await session.execute(stmt)

    async def revoke_tokens(self, user_uid: str) -> int:
        """Revoke all the refresh tokens for the given user UID."""
        whereclause = UserORM.uid == user_uid
        select_stmt = select(UserORM).where(whereclause)

        async with self.session() as session:
            result = await session.execute(select_stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, uid=user_uid)

            whereclause = RefreshTokenORM.user_id == user.id
            delete_stmt = delete(RefreshTokenORM).where(whereclause)

            async with session.begin():
                result = await session.execute(delete_stmt)

                return result.rowcount

    async def purge_tokens(
        self, retention_days: int, now: datetime | None = None,
    ) -> int:
        """Purge all the refresh tokens expired for longer than `retention_days`."""
        cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
        whereclause = RefreshTokenORM.expire_at < cutoff
        stmt = delete(RefreshTokenORM).where(whereclause)

        async with self.session() as session:
            async with session.begin():
                result = await session.execute(stmt)

                return result.rowcount

    #############
    # blob files
    #############

    async def find_blob(self, user_uid, *, blob_uid: str) -> tuple[Blob, str]:
        """Find the specified blob and its blob key for the given user UID."""
        option = selectinload(BlobORM.user)
        whereclause = and_(
            BlobORM.uid == blob_uid,
            BlobORM.user.has(UserORM.uid == user_uid),
        )
        stmt = select(BlobORM).join(BlobORM.user).options(option).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (blob := result.scalar_one_or_none()):
                raise EntityNotFoundError(BlobORM, uid=blob_uid)

            return to_blob(blob), blob.blob_key

    async def find_blobs(self, user_uid: str) -> list[Blob]:
        """Find all the blob for the given user UID."""
        option = selectinload(UserORM.blobs)
        whereclause = UserORM.uid == user_uid
        stmt = select(UserORM).options(option).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, uid=user_uid)

            return [to_blob(blob) for blob in user.blobs]

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
        whereclause = UserORM.uid == user_uid
        stmt = select(UserORM).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, uid=user_uid)

            blob = BlobORM(
                blob_key=blob_key,
                file_name=file_name,
                created_at=created_at,
                valid_thru=valid_thru,
                user_id=user.id,
            )

            async with session.begin():
                session.add(blob)

            await session.refresh(blob)
            return to_blob(blob)

    async def delete_blob(self, blob_uid: str) -> None:
        """Delete an blob given the blob UID."""
        whereclause = BlobORM.uid == blob_uid
        stmt = delete(BlobORM).where(whereclause)

        async with self.session() as session:
            async with session.begin():
                await session.execute(stmt)

    async def delete_blobs(self, user_uid: str) -> int:
        """Delete all the blobs for the given user UID."""
        whereclause = UserORM.uid == user_uid
        select_stmt = select(UserORM).where(whereclause)

        async with self.session() as session:
            result = await session.execute(select_stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, uid=user_uid)

            whereclause = BlobORM.user_id == user.id
            delete_stmt = delete(BlobORM).where(whereclause)

            async with session.begin():
                result = await session.execute(delete_stmt)

                return result.rowcount

    async def purge_blobs(
        self, retention_days: int, now: datetime | None = None,
    ) -> int:
        """Purge all the blobs expired for longer than `retention_days`."""
        cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
        whereclause = BlobORM.valid_thru < cutoff
        stmt = delete(BlobORM).where(whereclause)

        async with self.session() as session:
            async with session.begin():
                result = await session.execute(stmt)

                return result.rowcount

    ##############
    # blob uploads
    ##############

    async def find_upload(self, user_uid: str, *, upload_id: str) -> Upload:
        """Find the specified blob upload for the given user UID."""
        option = selectinload(UploadORM.user)
        whereclause = and_(
            UploadORM.uid == upload_id,
            UploadORM.user.has(UserORM.uid == user_uid),
        )
        stmt = select(UploadORM).join(UploadORM.user).options(option).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (upload := result.scalar_one_or_none()):
                raise EntityNotFoundError(UploadORM, uid=upload_id)

            return to_upload(upload)

    async def find_uploads(self, user_uid: str) -> list[Upload]:
        """Find all the uploads for the given user UID."""
        option = selectinload(UserORM.uploads)
        whereclause = UserORM.uid == user_uid
        stmt = select(UserORM).options(option).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, uid=user_uid)

            return [to_upload(upload) for upload in user.uploads]

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
        whereclause = UserORM.uid == user_uid
        stmt = select(UserORM).where(whereclause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(UserORM, uid=user_uid)

            upload = UploadORM(
                uid=uid,
                blob_key=blob_key,
                created_at=created_at,
                valid_thru=valid_thru,
                user_id=user.id,
            )

            async with session.begin():
                session.add(upload)

            await session.refresh(upload)
            return to_upload(upload)

    async def remove_upload(self, uid: str) -> None:
        """Remove an upload with the given upload ID.

        An upload is removable when it's either finished or canceled.
        """
        whereclause = and_(UploadORM.uid == uid)
        stmt = delete(UploadORM).where(whereclause)

        async with self.session() as session:
            async with session.begin():
                await session.execute(stmt)

    async def purge_uploads(
        self, retention_days: int, now: datetime | None = None,
    ) -> list[Upload]:
        """Purge all the uploads expired for longer than `retention_days`."""
        cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
        whereclause = UploadORM.valid_thru < cutoff
        select_stmt = select(UploadORM).where(whereclause)
        delete_stmt = delete(UploadORM).where(whereclause)

        async with self.session() as session:
            async with session.begin():
                result = await session.execute(select_stmt)
                uploads = result.scalars().all()
                await session.execute(delete_stmt)
                return [to_upload(upload) for upload in uploads]
