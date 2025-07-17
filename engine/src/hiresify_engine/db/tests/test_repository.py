# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from ..exception import EntityConflictError, EntityNotFoundError
from ..repository import Repository

#################
# user management
#################

async def test_register_user(repository: Repository) -> None:
    # Given
    username = "ywu"

    # When/Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"User with username={username} was not found.",
    ):
        await repository.find_user(username)

    # Given
    password = "123"
    await repository.register_user(username, password)

    # When
    user = await repository.find_user(username)

    # Then
    assert user.username == username
    assert user.password == password

    # When/Then
    with pytest.raises(
        EntityConflictError,
        check=lambda e: str(e) == (
            f"User with username={username} conflicts with an existing entity."
        ),
    ):
        await repository.register_user(username, password)


async def test_update_password(repository: Repository) -> None:
    # Given
    username = "ywu"
    updated_password = "456"

    # When/Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"User with username={username} was not found.",
    ):
        await repository.update_password(username, updated_password)

    # Given
    await repository.register_user(username, "123")

    # When
    await repository.update_password(username, updated_password)
    updated_user = await repository.find_user(username)

    # Then
    assert updated_user.username == username
    assert updated_user.password == updated_password


async def test_delete_user(repository: Repository) -> None:
    # Given
    username = "ywu"

    # When/Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"User with username={username} was not found.",
    ):
        await repository.delete_user(username)

    # Given
    await repository.register_user(username, "123")

    # When
    await repository.delete_user(username)

    # Then
    with pytest.raises(
        EntityNotFoundError,
        check=lambda e: str(e) == f"User with username={username} was not found.",
    ):
        await repository.find_user(username)

###############
# refresh token
###############

async def test_create_token(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    token = "xyz123"
    issued_at = datetime.now(UTC)
    expire_at = issued_at + timedelta(seconds=1)

    # When
    refresh_token = await repository.create_token(
        user.uid,
        token=token,
        issued_at=issued_at,
        expire_at=expire_at,
    )

    # Then
    assert refresh_token.expire_at > refresh_token.issued_at
    assert not refresh_token.revoked


async def test_revoke_token(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    token = "xyz123"
    issued_at = datetime.now(UTC)
    expire_at = issued_at + timedelta(seconds=1)

    # When
    refresh_token = await repository.create_token(
        user.uid,
        token=token,
        issued_at=issued_at,
        expire_at=expire_at,
    )

    # Then
    assert not refresh_token.revoked

    # When
    token = refresh_token.token
    await repository.revoke_token(token)
    refresh_token = await repository.find_token(token)

    # Then
    assert refresh_token.revoked


async def test_revoke_tokens(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    # When
    refresh_tokens = await repository.find_tokens(user.uid)

    # Then
    assert not refresh_tokens

    # Given
    issued_at = datetime.now(UTC)
    tokens = [f"token{i}" for i in range(1, 4)]

    pre_tokens = []
    for token in tokens:
        expire_at = issued_at + timedelta(seconds=1)
        pre_tokens.append(
            await repository.create_token(
                user.uid,
                token=token,
                issued_at=issued_at,
                expire_at=expire_at,
            ),
        )
        issued_at = expire_at

    # Then
    for refresh_token in pre_tokens:
        assert not refresh_token.revoked

    # When
    await repository.revoke_tokens(user.uid)
    cur_tokens = await repository.find_tokens(user.uid)

    # Then
    assert len(cur_tokens) == len(pre_tokens)

    for cur_token, pre_token in zip(cur_tokens, pre_tokens, strict=False):
        assert cur_token.token == pre_token.token
        assert cur_token.revoked


async def test_purge_tokens(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")
    
    issued_at = datetime.now(UTC)
    tokens = [f"token{i}" for i in range(1, 4)]

    refresh_tokens = []
    for token in tokens:
        expire_at = issued_at + timedelta(seconds=1)
        refresh_tokens.append(
            await repository.create_token(
                user.uid,
                token=token,
                issued_at=issued_at,
                expire_at=expire_at,
            ),
        )
        issued_at = expire_at

    # When
    *_, refresh_token = refresh_tokens
    await repository.purge_tokens(1, refresh_token.expire_at + timedelta(days=2))
    refresh_tokens = await repository.find_tokens(user.uid)

    # Then
    assert not refresh_tokens

#############
# image files
#############

async def test_create_image(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    image = await repository.create_image(
        user.uid,
        blob_key=uuid4().hex,
        filename="image.jpg",
        file_fmt="jpg",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert image.valid_thru > image.created_at
    assert not image.finished
    assert not image.deleted


async def test_bump_image_index(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    image = await repository.create_image(
        user.uid,
        blob_key=uuid4().hex,
        filename="image.jpg",
        file_fmt="jpg",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert image.next_index == 1

    # When
    index = await repository.bump_image_next(image.uid)
    image = await repository.find_image(image.uid)

    # Then
    assert index == 2
    assert image.next_index == 2


async def test_finish_image_upload(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    image = await repository.create_image(
        user.uid,
        blob_key=uuid4().hex,
        filename="image.jpg",
        file_fmt="jpg",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert image.uploadid is None
    assert not image.finished

    # Given
    uploadid = uuid4().hex

    # When
    await repository.start_image_upload(image.uid, uploadid)
    image = await repository.find_image(image.uid)

    # Then
    assert image.uploadid == uploadid
    assert not image.finished

    # When
    await repository.finish_image_upload(image.uid)
    image = await repository.find_image(image.uid)

    # Then
    assert image.uploadid is None
    assert image.finished


async def test_delete_image(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    image = await repository.create_image(
        user.uid,
        blob_key=uuid4().hex,
        filename="image.jpg",
        file_fmt="jpg",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert not image.deleted

    # When
    await repository.delete_image(image.uid)
    image = await repository.find_image(image.uid)

    # Then
    assert image.deleted


async def test_delete_images(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    # When
    images = await repository.find_images(user.uid)

    # Then
    assert not images

    # Given
    created_at = datetime.now(UTC)
    filenames = [f"image{i}.jpg" for i in range(1, 4)]

    pre_images = []
    for filename in filenames:
        valid_thru = created_at + timedelta(seconds=1)
        pre_images.append(
            await repository.create_image(
                user.uid,
                blob_key=uuid4().hex,
                filename=filename,
                file_fmt="jpg",
                created_at=created_at,
                valid_thru=valid_thru,
            ),
        )
        created_at = valid_thru

    # Then
    for image in pre_images:
        assert not image.deleted

    # When
    await repository.delete_images(user.uid)
    cur_images = await repository.find_images(user.uid)

    # Then
    assert len(cur_images) == len(pre_images)

    for cur_image, pre_image in zip(cur_images, pre_images, strict=False):
        assert cur_image.filename == pre_image.filename
        assert cur_image.deleted


async def test_purge_images(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")
    
    created_at = datetime.now(UTC)
    filenames = [f"image{i}.jpg" for i in range(1, 4)]

    images = []
    for filename in filenames:
        valid_thru = created_at + timedelta(seconds=1)
        images.append(
            await repository.create_image(
                user.uid,
                blob_key=uuid4().hex,
                filename=filename,
                file_fmt="jpg",
                created_at=created_at,
                valid_thru=valid_thru,
            ),
        )
        created_at = valid_thru

    # When
    *_, image = images
    await repository.purge_images(1, image.valid_thru + timedelta(days=2))
    images = await repository.find_images(user.uid)

    # Then
    assert not images

#############
# video files
#############

async def test_create_video(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    video = await repository.create_video(
        user.uid,
        blob_key=uuid4().hex,
        filename="video.mp4",
        file_fmt="mp4",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert video.valid_thru > video.created_at
    assert not video.finished
    assert not video.deleted


async def test_bump_video_index(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    video = await repository.create_video(
        user.uid,
        blob_key=uuid4().hex,
        filename="video.mp4",
        file_fmt="mp4",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert video.next_index == 1

    # When
    index = await repository.bump_video_next(video.uid)
    video = await repository.find_video(video.uid)

    # Then
    assert index == 2
    assert video.next_index == 2


async def test_finish_video_upload(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    video = await repository.create_video(
        user.uid,
        blob_key=uuid4().hex,
        filename="video.mp4",
        file_fmt="mp4",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert video.uploadid is None
    assert not video.finished

    # Given
    uploadid = uuid4().hex

    # When
    await repository.start_video_upload(video.uid, uploadid)
    video = await repository.find_video(video.uid)

    # Then
    assert video.uploadid == uploadid
    assert not video.finished

    # When
    await repository.finish_video_upload(video.uid)
    video = await repository.find_video(video.uid)

    # Then
    assert video.uploadid is None
    assert video.finished


async def test_delete_video(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(seconds=1)

    # When
    video = await repository.create_video(
        user.uid,
        blob_key=uuid4().hex,
        filename="video.mp4",
        file_fmt="mp4",
        created_at=created_at,
        valid_thru=valid_thru,
    )

    # Then
    assert not video.deleted

    # When
    await repository.delete_video(video.uid)
    video = await repository.find_video(video.uid)

    # Then
    assert video.deleted


async def test_delete_videos(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")

    # When
    videos = await repository.find_videos(user.uid)

    # Then
    assert not videos

    # Given
    created_at = datetime.now(UTC)
    filenames = [f"video{i}.mp4" for i in range(1, 4)]

    pre_videos = []
    for filename in filenames:
        valid_thru = created_at + timedelta(seconds=1)
        pre_videos.append(
            await repository.create_video(
                user.uid,
                blob_key=uuid4().hex,
                filename=filename,
                file_fmt="mp4",
                created_at=created_at,
                valid_thru=valid_thru,
            ),
        )
        created_at = valid_thru

    # Then
    for video in pre_videos:
        assert not video.deleted

    # When
    await repository.delete_videos(user.uid)
    cur_videos = await repository.find_videos(user.uid)

    # Then
    assert len(cur_videos) == len(pre_videos)

    for cur_video, pre_video in zip(cur_videos, pre_videos, strict=False):
        assert cur_video.filename == pre_video.filename
        assert cur_video.deleted


async def test_purge_videos(repository: Repository) -> None:
    # Given
    user = await repository.register_user("ywu", "123")
    
    created_at = datetime.now(UTC)
    filenames = [f"video{i}.mp4" for i in range(1, 4)]

    videos = []
    for filename in filenames:
        valid_thru = created_at + timedelta(seconds=1)
        videos.append(
            await repository.create_video(
                user.uid,
                blob_key=uuid4().hex,
                filename=filename,
                file_fmt="mp4",
                created_at=created_at,
                valid_thru=valid_thru,
            ),
        )
        created_at = valid_thru

    # When
    *_, video = videos
    await repository.purge_videos(1, video.valid_thru + timedelta(days=2))
    videos = await repository.find_videos(user.uid)

    # Then
    assert not videos
