# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide mapper functions to convert ORM objects to domain ones."""

import typing as ty

from hiresify_engine.model import Blob, ComputeJob, JWTToken, Upload, User
from hiresify_engine.util import parse_blob_key

from .model import BlobORM, ComputeJobORM, RefreshTokenORM, UploadORM, UserORM


def to_blob(obj: BlobORM) -> Blob:
    """Convert a blob ORM object to a domain one."""
    _, _, mime_type = parse_blob_key(obj.blob_key)

    return Blob(
        uid=obj.uid,
        file_name=obj.file_name,
        mime_type=mime_type,
        created_at=obj.created_at,
        valid_thru=obj.valid_thru,
    )


def to_token(obj: RefreshTokenORM, **kwargs: ty.Any) -> JWTToken:
    """Convert a refresh token ORM object to a domain one."""
    return JWTToken(
        issued_at=obj.issued_at,
        expire_at=obj.expire_at,
        revoked=obj.revoked,
        uid=obj.uid,
        **kwargs,
    )


def to_upload(obj: UploadORM) -> Upload:
    """Convert an upload ORM object to a domain one."""
    return Upload(
        uid=obj.uid,
        blob_key=obj.blob_key,
        created_at=obj.created_at,
        valid_thru=obj.valid_thru,
    )


def to_user(obj: UserORM) -> User:
    """Convert a user ORM object to a domain one."""
    return User(uid=obj.uid, username=obj.username, password=obj.password)


def to_job(obj: ComputeJobORM) -> ComputeJob:
    """Convert a compute job ORM object to a domain one."""
    return ComputeJob(
        uid=obj.uid,
        requested_at=obj.requested_at,
        completed_at=obj.completed_at,
        status=obj.status,  # type: ignore[arg-type]
    )
