# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend upload-related endpoints."""

import logging
import typing as ty
from datetime import UTC, datetime, timedelta
from itertools import count

from fastapi import APIRouter, Form, HTTPException, Query, Request, status
from starlette.requests import ClientDisconnect

from hiresify_engine.dep import BlobServiceDep, RepositoryDep
from hiresify_engine.envvar import BLOB_TTL
from hiresify_engine.model import Blob

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


@router.post("/upload", response_model=Blob)
async def upload_bytes(
    filename: str = Form(..., max_length=256),
    blob_key: str = Form(..., max_length=256),
    part_ind: int = Form(..., max_digits=100),
    uploadid: str = Form(..., max_length=128),
    *,
    blob: BlobServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> Blob:
    """Receive, process, and upload a stream of bytes."""
    user_uid = verify_access_token(request, jwt)
    dir_name, _ = blob_key.split("/")

    if dir_name != user_uid:
        raise HTTPException(
            detail="Mismatch was found between blob key and user UID.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    async with blob.start_session() as session:
        counter = count(part_ind)

        try:
            async for chunk in request.stream():
                part_index = next(counter)
                await session.upload_chunk(
                    blob_key=blob_key,
                    data_chunk=chunk,
                    part_index=part_index,
                    uploadid=uploadid,
                )

        except ClientDisconnect as e:
            await session.abort_upload(blob_key, uploadid)
            raise HTTPException(
                detail="Upload stream disconnected.",
                status_code=499,
            ) from e

        else:
            await session.finish_upload(blob_key, uploadid)

            created_at = datetime.now(UTC)
            valid_thru = created_at + timedelta(days=BLOB_TTL)

            await repo.create_blob(
                user_uid,
                blob_key=blob_key,
                filename=filename,
                created_at=created_at,
                valid_thru=valid_thru,
            )

            return Blob(
                blob_key=blob_key,
                filename=filename,
                created_at=created_at,
                valid_thru=valid_thru,
            )
