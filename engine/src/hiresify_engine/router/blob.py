# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend upload-related endpoints."""

import logging
import typing as ty
from datetime import UTC, datetime, timedelta

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Path,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import PlainTextResponse

from hiresify_engine.db.exception import EntityNotFoundError
from hiresify_engine.dep import BlobServiceDep, RepositoryDep
from hiresify_engine.envvar import UPLOAD_TTL

from .const import jwt
from .util import generate_blob_key, verify_access_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/blob")


@router.get("/upload/{ffmt}")
async def start_upload(
    ffmt: ty.Literal["jpg", "mp4", "png"] = Path(..., max_length=8),
    *,
    blob: BlobServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> PlainTextResponse:
    """Start a multipart upload of the given file."""
    user_uid = verify_access_token(request, jwt)
    blob_key = generate_blob_key(user_uid, ffmt)

    async with blob.start_session() as session:
        uploadid = await session.start_upload(blob_key)

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(days=UPLOAD_TTL)

    await repo.start_upload(
        user_uid,
        uploadid=uploadid,
        blob_key=blob_key,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    return PlainTextResponse(uploadid, status_code=status.HTTP_201_CREATED)


@router.post("/upload/{part}")
async def upload_chunk(
    file: UploadFile = File(...),  # noqa: B008
    part: int = Path(..., examples=[1], ge=1),
    upload_id: str = Form(..., max_length=128),
    *,
    blob: BlobServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> None:
    """Receive, process, and upload a chunk of blob."""
    verify_access_token(request, jwt)

    try:
        upload = await repo.find_upload(upload_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail=f"{upload_id=} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e

    chunk = await file.read()

    async with blob.start_session() as session:
        await session.upload_chunk(
            blob_key=upload.blob_key,
            data_chunk=chunk,
            part_index=part,
            upload_id=upload_id,
        )
