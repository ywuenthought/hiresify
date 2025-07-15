# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the domain models used on the backend."""

from datetime import datetime

from pydantic.dataclasses import dataclass

from .type import ImageFormat, VideoFormat


@dataclass(frozen=True)
class User:
    """The domain model for identifying a user."""

    # A user can upload many images.
    images: list["Image"]

    # A user can upload many videos.
    videos: list["Video"]


class _BlobMixin:
    """The mixin for a blob domain model."""

    #: Name of this blob file.
    name: str

    #: The blob key to identify this blob in the blob store.
    key: str

    #: The date and time when the blob was created.
    created_at: datetime

    #: The date and time when the blob is valid through.
    valid_thru: datetime

    #: The index of the next part of this blob to be uploaded.
    next_index: int

    #: A boolean flag for whether the upload of this blob has been finished.
    finished: bool

    #: A user-facing boolean flag for whether the blob has been deleted.
    deleted: bool


@dataclass(frozen=True)
class Image(_BlobMixin):
    """The domain model for an image uploaded by a user."""

    #: The format of this image file.
    format: ImageFormat


@dataclass(frozen=True)
class Video(_BlobMixin):
    """The domain model for a video uploaded by a user."""

    #: The format of this video file.
    format: VideoFormat
