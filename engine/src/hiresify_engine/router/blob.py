# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend upload-related endpoints."""

import logging
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
from magic import from_buffer

from hiresify_engine.db.exception import EntityNotFoundError
from hiresify_engine.dep import BlobServiceDep, RepositoryDep
from hiresify_engine.envvar import UPLOAD_TTL
from hiresify_engine.model import Blob

from .const import jwt, mime_types
from .util import generate_blob_key, verify_access_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/blob")


@router.get("/upload", status_code=status.HTTP_201_CREATED)
async def start_upload(
    file: UploadFile = File(...),  # noqa: B008
    *,
    blob: BlobServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> str:
    """Start a multipart upload of the given file."""
    user_uid = verify_access_token(request, jwt)

    try:
        head = await file.read(4096)
    except (OSError, ValueError) as e:
        raise HTTPException(
            detail=f"Failed to read file chunk: {e!s}",
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from e
    finally:
        await file.close()

    if (mime_type := from_buffer(head, mime=True)) not in mime_types:
        raise HTTPException(
            detail=f"{mime_type=} is not supported",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    blob_key = generate_blob_key(user_uid, mime_type)

    async with blob.start_session() as session:
        upload_id = await session.start_upload(blob_key)

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(days=UPLOAD_TTL)

    await repo.start_upload(
        user_uid,
        uid=upload_id,
        blob_key=blob_key,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    return upload_id


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
    user_uid = verify_access_token(request, jwt)

    try:
        upload = await repo.find_upload(user_uid, upload_id=upload_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail=f"upload={upload_id} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e

    if not upload.is_valid():
        raise HTTPException(
            detail=f"upload={upload_id} timed out.",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )

    chunk = await file.read()

    async with blob.start_session() as session:
        await session.upload_chunk(
            blob_key=upload.blob_key,
            data_chunk=chunk,
            part_index=part,
            upload_id=upload_id,
        )


@router.put("/upload", response_model=Blob)
async def finish_upload(
    upload_id: str = Form(..., max_length=128),
    file_name: str = Form(..., max_length=256),
    *,
    blob: BlobServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> Blob:
    """Finish the upload specified by the given upload ID."""
    user_uid = verify_access_token(request, jwt)

    try:
        upload = await repo.find_upload(user_uid, upload_id=upload_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail=f"upload={upload_id} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e

    if not upload.is_valid():
        raise HTTPException(
            detail=f"upload={upload_id} timed out.",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )

    blob_key = upload.blob_key
    async with blob.start_session() as session:
        await session.finish_upload(blob_key=blob_key, upload_id=upload_id)

    created_at = datetime.now(UTC)
    valid_thru = created_at + timedelta(days=UPLOAD_TTL)

    await repo.remove_upload(upload_id)
    return await repo.create_blob(
        user_uid,
        blob_key=blob_key,
        file_name=file_name,
        created_at=created_at,
        valid_thru=valid_thru,
    )


@router.delete("/upload", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_upload(
    upload_id: str = Form(..., max_length=128),
    *,
    blob: BlobServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> None:
    """Finish the upload specified by the given upload ID."""
    user_uid = verify_access_token(request, jwt)

    try:
        upload = await repo.find_upload(user_uid, upload_id=upload_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail=f"upload={upload_id} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e

    if not upload.is_valid():
        raise HTTPException(
            detail=f"upload={upload_id} timed out.",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )

    blob_key = upload.blob_key
    async with blob.start_session() as session:
        await session.cancel_upload(blob_key=blob_key, upload_id=upload_id)

    await repo.remove_upload(upload_id)


@router.get("/fetch", response_model=list[Blob])
async def fetch_blobs(*, repo: RepositoryDep, request: Request) -> list[Blob]:
    """Fetch all the blobs associated with a user from the database."""
    user_uid = verify_access_token(request, jwt)
    return await repo.find_blobs(user_uid)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blob(
    blob_uid: str = Form(..., max_length=32, min_length=32),
    *,
    blob: BlobServiceDep,
    repo: RepositoryDep,
    request: Request,
) -> None:
    """Finish the upload specified by the given upload ID."""
    user_uid = verify_access_token(request, jwt)

    try:
        blob_obj, blob_key = await repo.find_blob(user_uid, blob_uid=user_uid)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail=f"{blob_uid=} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e

    if not blob_obj.is_valid():
        raise HTTPException(
            detail=f"{blob_uid=} has timed out.",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )

    async with blob.start_session() as session:
        await session.delete_blob(blob_key)

    await repo.delete_blob(blob_uid)
