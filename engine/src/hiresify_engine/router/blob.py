# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend upload-related endpoints."""

import logging
import typing as ty
from itertools import count

from fastapi import APIRouter, Form, HTTPException, Query, Request, status
from starlette.requests import ClientDisconnect

from hiresify_engine.dep import BlobServiceDep

from .const import jwt
from .util import generate_blob_key, verify_access_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/blob")


@router.get("/upload", status_code=status.HTTP_201_CREATED)
async def start_upload(
    file_fmt: ty.Literal["jpg", "mp4", "png"] = Query(..., max_length=8),
    *,
    blob: BlobServiceDep,
    request: Request,
) -> dict[str, str]:
    """Start a multipart upload of the given file."""
    user_uid = verify_access_token(request, jwt)
    blob_key = generate_blob_key(user_uid, file_fmt)

    async with blob.start_session() as session:
        uploadid = await session.start_upload(blob_key)

    return dict(blob_key=blob_key, uploadid=uploadid)


@router.post("/upload")
async def upload_bytes(
    blob_key: str = Form(..., max_length=256),
    uploadid: str = Form(..., max_length=128),
    *,
    blob: BlobServiceDep,
    request: Request,
) -> None:
    """Receive, process, and upload a stream of bytes."""
    user_uid = verify_access_token(request, jwt)
    dir_name, _ = blob_key.split("/")

    if dir_name != user_uid:
        raise HTTPException(
            detail="Mismatch was found between blob key and user UID.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    async with blob.start_session() as session:
        *_, last_part = await session.report_parts(blob_key, uploadid)
        counter = count(last_part.index)

        try:
            async for chunk in request.stream():
                part_index = next(counter)
                await session.upload_chunk(
                    blob_key=blob_key,
                    data_chunk=chunk,
                    part_index=part_index,
                    uploadid=uploadid,
                )
        except ClientDisconnect:
            logger.error("Upload stream disconnected.", exc_info=True)
        else:
            await session.finish_upload(blob_key, uploadid)
