# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend upload-related endpoints."""

import typing as ty
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import PlainTextResponse

from hiresify_engine.dep import BlobServiceDep, RepositoryDep
from hiresify_engine.envvar import BLOB_TTL
from hiresify_engine.type import ImageFormat, VideoFormat

from .const import jwt
from .util import verify_access_token

router = APIRouter(prefix="/blob")


@router.get("/upload")
async def start_upload(
    file_fmt: ty.Annotated[ImageFormat | VideoFormat, Form(..., max_length=8)],
    file_name: str = Form(..., max_length=256),
    blob_key: str = Form(..., max_length=256),
    *,
    blob: BlobServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> PlainTextResponse:
    """Start a multipart upload of the given file."""
    user_uid = verify_access_token(request, jwt)

    creator = (
        repo.create_image
        if file_fmt in ty.get_args(ImageFormat)
        else repo.create_video
    )

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(days=BLOB_TTL)

    await creator(
        user_uid,
        file_name=file_name,
        blob_key=blob_key,
        format=file_fmt,  # type: ignore[arg-type]
        created_at=created_at,
        valid_thru=valid_thru,
    )

    async with blob.start_session() as session:
        upload_id = await session.start_upload(blob_key)

    return PlainTextResponse(upload_id, status_code=status.HTTP_201_CREATED)
