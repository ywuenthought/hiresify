# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the repository layer around the database."""

import contextlib
import typing as ty
from collections import abc
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload, with_loader_criteria

from hiresify_engine.type import ImageFormat, VideoFormat

from .exception import EntityConflictError, EntityNotFoundError
from .model import Base, Image, RefreshToken, User, Video
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
        options = [selectinload(User.refresh_tokens)] if eager else []
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
        where_clause = RefreshToken.token == token
        stmt = select(RefreshToken).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (refresh_token := result.scalar_one_or_none()):
                raise EntityNotFoundError(RefreshToken, token=abbreviate_token(token))

            return refresh_token

    async def find_tokens(self, user_uid: str) -> list[RefreshToken]:
        """Find all the refresh tokens for the given user UID."""
        option = selectinload(User.refresh_tokens)
        where_clause = User.uid == user_uid
        stmt = select(User).options(option).where(where_clause)

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
        where_clause = RefreshToken.token == token
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
        where_clause = RefreshToken.expire_at < cutoff
        stmt = delete(RefreshToken).where(where_clause)

        async with self.session() as session:
            async with session.begin():
                result = await session.execute(stmt)

                return result.rowcount

    #############
    # image files
    #############

    async def find_image(self, image_uid: str, *, eager: bool = False) -> Image:
        """Find the image with the given image UID."""
        options = [selectinload(Image.user)] if eager else []
        where_clause = Image.uid == image_uid
        stmt = select(Image).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (image := result.scalar_one_or_none()):
                raise EntityNotFoundError(Image, uid=image_uid)

            return image

    async def find_images(self, user_uid: str) -> list[Image]:
        """Find all the images for the given user UID."""
        option = selectinload(User.images)
        where_clause = User.uid == user_uid
        stmt = select(User).options(option).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            return user.images

    async def create_image(
        self,
        user_uid: str,
        *,
        blob_key: str,
        filename: str,
        file_fmt: ImageFormat,
        created_at: datetime,
        valid_thru: datetime,
    ) -> Image:
        """Create an image for the given user UID."""
        where_clause = User.uid == user_uid
        stmt = select(User).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            image = Image(
                blob_key=blob_key,
                filename=filename,
                file_fmt=file_fmt,
                created_at=created_at,
                valid_thru=valid_thru,
                user_id=user.id,
            )

            async with session.begin():
                session.add(image)

            await session.refresh(image)
            return image

    async def bump_image_next(self, image_uid: str) -> int:
        """Bump the index of next part of the image with the given image UID."""
        where_clause = Image.uid == image_uid
        stmt = select(Image).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (image := result.scalar_one_or_none()):
                raise EntityNotFoundError(Image, uid=image_uid)

            async with session.begin():
                index = image.next_index + 1
                image.next_index = index
                return index

    async def finish_image(self, image_uid: str) -> None:
        """Finish the upload of the image with the given image UID."""
        where_clause = Image.uid == image_uid
        stmt = select(Image).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (image := result.scalar_one_or_none()):
                raise EntityNotFoundError(Image, uid=image_uid)

            async with session.begin():
                image.finished = True

    async def delete_image(self, image_uid: str) -> None:
        """Delete an image given the image UID."""
        where_clause = Image.uid == image_uid
        stmt = select(Image).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (image := result.scalar_one_or_none()):
                raise EntityNotFoundError(Image, uid=image_uid)

            async with session.begin():
                image.deleted = True

    async def delete_images(self, user_uid: str) -> int:
        """Delete all the images for the given user UID."""
        options = [
            selectinload(User.images),
            with_loader_criteria(Image, Image.deleted.is_(False)),
        ]

        where_clause = User.uid == user_uid
        stmt = select(User).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            async with session.begin():
                if not (images := user.images):
                    return 0

                for image in images:
                    image.deleted = True

                return len(images)

    async def purge_images(
        self, retention_days: int, now: datetime | None = None,
    ) -> int:
        """Purge all the images expired for longer than `retention_days`."""
        cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
        where_clause = Image.valid_thru < cutoff
        stmt = delete(Image).where(where_clause)

        async with self.session() as session:
            async with session.begin():
                result = await session.execute(stmt)

                return result.rowcount

    #############
    # video files
    #############

    async def find_video(self, video_uid: str, *, eager: bool = False) -> Video:
        """Find the video with the given video UID."""
        options = [selectinload(Video.user)] if eager else []
        where_clause = Video.uid == video_uid
        stmt = select(Video).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (video := result.scalar_one_or_none()):
                raise EntityNotFoundError(Video, uid=video_uid)

            return video

    async def find_videos(self, user_uid: str) -> list[Video]:
        """Find all the videos for the given user UID."""
        option = selectinload(User.videos)
        where_clause = User.uid == user_uid
        stmt = select(User).options(option).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            return user.videos

    async def create_video(
        self,
        user_uid: str,
        *,
        blob_key: str,
        filename: str,
        file_fmt: VideoFormat,
        created_at: datetime,
        valid_thru: datetime,
    ) -> Video:
        """Create an video for the given user UID."""
        where_clause = User.uid == user_uid
        stmt = select(User).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            video = Video(
                blob_key=blob_key,
                filename=filename,
                file_fmt=file_fmt,
                created_at=created_at,
                valid_thru=valid_thru,
                user_id=user.id,
            )

            async with session.begin():
                session.add(video)

            await session.refresh(video)
            return video

    async def bump_video_next(self, video_uid: str) -> int:
        """Bump the index of next part of the video with the given video UID."""
        where_clause = Video.uid == video_uid
        stmt = select(Video).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (video := result.scalar_one_or_none()):
                raise EntityNotFoundError(Video, uid=video_uid)

            async with session.begin():
                index = video.next_index + 1
                video.next_index = index
                return index

    async def finish_video(self, video_uid: str) -> None:
        """Finish the upload of the video with the given video UID."""
        where_clause = Video.uid == video_uid
        stmt = select(Video).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (video := result.scalar_one_or_none()):
                raise EntityNotFoundError(Video, uid=video_uid)

            async with session.begin():
                video.finished = True

    async def delete_video(self, video_uid: str) -> None:
        """Delete an video given the video UID."""
        where_clause = Video.uid == video_uid
        stmt = select(Video).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (video := result.scalar_one_or_none()):
                raise EntityNotFoundError(Video, uid=video_uid)

            async with session.begin():
                video.deleted = True

    async def delete_videos(self, user_uid: str) -> int:
        """Delete all the videos for the given user UID."""
        options = [
            selectinload(User.videos),
            with_loader_criteria(Video, Video.deleted.is_(False)),
        ]

        where_clause = User.uid == user_uid
        stmt = select(User).options(*options).where(where_clause)

        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()

            if not (user := result.scalar_one_or_none()):
                raise EntityNotFoundError(User, uid=user_uid)

            async with session.begin():
                if not (videos := user.videos):
                    return 0

                for video in videos:
                    video.deleted = True

                return len(videos)

    async def purge_videos(
        self, retention_days: int, now: datetime | None = None,
    ) -> int:
        """Purge all the videos expired for longer than `retention_days`."""
        cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
        where_clause = Video.valid_thru < cutoff
        stmt = delete(Video).where(where_clause)

        async with self.session() as session:
            async with session.begin():
                result = await session.execute(stmt)

                return result.rowcount
