# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide mapper functions to convert ORM objects to domain ones."""

from hiresify_engine.model import Blob, Upload

from .model import BlobORM, UploadORM
from .util import restore_mime_type


def to_blob(obj: BlobORM) -> Blob:
    """Convert a blob ORM object to a domain one."""
    return Blob(
        uid=obj.uid,
        file_name=obj.file_name,
        mime_type=restore_mime_type(obj.blob_key),
        created_at=obj.created_at,
        valid_thru=obj.valid_thru,
    )


def to_upload(obj: UploadORM) -> Upload:
    """Convert an upload ORM object to a domain one."""
    return Upload(
        uid=obj.uid,
        blob_key=obj.blob_key,
        created_at=obj.created_at,
        valid_thru=obj.valid_thru,
    )
