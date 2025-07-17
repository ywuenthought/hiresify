# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend upload-related endpoints."""

import typing as ty
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import PlainTextResponse

from hiresify_engine.dep import BlobServiceDep, RepositoryDep
from hiresify_engine.envvar import BLOB_TTL
from hiresify_engine.type import ImageFormat, VideoFormat

from .const import jwt
from .util import verify_access_token

router = APIRouter(prefix="/blob")


@router.get("/upload")
async def start_upload(
    blob_key: str = Form(..., max_length=256),
    filename: str = Form(..., max_length=256),
    file_fmt: ty.Literal["jpg", "mp4", "png"] = Form(..., max_length=8),
    *,
    blob: BlobServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> PlainTextResponse:
    """Start a multipart upload of the given file."""
    user_uid = verify_access_token(request, jwt)

    creator = None
    if file_fmt in ty.get_args(ImageFormat):
        creator = repo.create_image
    if file_fmt in ty.get_args(VideoFormat):
        creator = repo.create_video  # type: ignore[assignment]

    if not creator:
        raise HTTPException(
            detail=f"{file_fmt=} is not supported.",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(days=BLOB_TTL)

    await creator(
        user_uid,
        blob_key=blob_key,
        filename=filename,
        file_fmt=file_fmt,  # type: ignore[arg-type]
        created_at=created_at,
        valid_thru=valid_thru,
    )

    async with blob.start_session() as session:
        upload_id = await session.start_upload(blob_key)

    return PlainTextResponse(upload_id, status_code=status.HTTP_201_CREATED)
