# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend upload-related endpoints."""

import logging

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from magic import from_buffer

from hiresify_engine.const import ACCESS_TOKEN_NAME
from hiresify_engine.db.exception import EntityNotFoundError
from hiresify_engine.dep import AppConfigDep, BlobServiceDep, RepositoryDep
from hiresify_engine.model import Blob, Upload
from hiresify_engine.util import generate_blob_key, get_interval_from_now

from .util import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/blob")

_mime_types = {"image/jpeg", "image/png", "video/mp4"}


@router.post("/upload/init", status_code=status.HTTP_201_CREATED)
async def start_upload(
    file: UploadFile = File(...),  # noqa: B008
    *,
    blob: BlobServiceDep,
    config: AppConfigDep,
    repo: RepositoryDep,
    request: Request,
) -> str:
    """Start a multipart upload of the given file."""
    token = verify_token(
        request.cookies,
        token_name=ACCESS_TOKEN_NAME,
        secret_key=config.jwt_secret_key,
    )

    try:
        head = await file.read(4096)
    except (OSError, ValueError) as e:
        raise HTTPException(
            detail=f"Failed to read file chunk: {e!s}",
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from e
    finally:
        await file.close()

    if (mime_type := from_buffer(head, mime=True)) not in _mime_types:
        raise HTTPException(
            detail=f"{mime_type=} is not supported",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )

    blob_key = generate_blob_key(token.user_uid, mime_type)

    async with blob.start_session(config.production) as session:
        upload_id = await session.start_upload(blob_key)

    created_at, valid_thru = get_interval_from_now(86400 * config.upload_ttl)
    await repo.start_upload(
        token.user_uid,
        uid=upload_id,
        blob_key=blob_key,
        created_at=created_at,
        valid_thru=valid_thru,
    )

    return upload_id


@router.post("/upload")
async def upload_chunk(
    file: UploadFile = File(...),  # noqa: B008
    part: int = Query(1, examples=[1], ge=1),
    upload_id: str = Form(..., max_length=128),
    *,
    blob: BlobServiceDep,
    config: AppConfigDep,
    repo: RepositoryDep,
    request: Request,
) -> None:
    """Receive, process, and upload a chunk of blob."""
    token = verify_token(
        request.cookies,
        token_name=ACCESS_TOKEN_NAME,
        secret_key=config.jwt_secret_key,
    )

    upload = await _verify_upload(token.user_uid, upload_id, repo=repo)
    async with blob.start_session(config.production) as session:
        await session.upload_chunk(
            blob_key=upload.blob_key,
            data_chunk=await file.read(),
            part_index=part,
            upload_id=upload_id,
        )


@router.put("/upload", response_model=Blob)
async def finish_upload(
    upload_id: str = Form(..., max_length=128),
    file_name: str = Form(..., max_length=256),
    *,
    blob: BlobServiceDep,
    config: AppConfigDep,
    repo: RepositoryDep,
    request: Request,
) -> Blob:
    """Finish the upload specified by the given upload ID."""
    token = verify_token(
        request.cookies,
        token_name=ACCESS_TOKEN_NAME,
        secret_key=config.jwt_secret_key,
    )

    upload = await _verify_upload(token.user_uid, upload_id, repo=repo)
    async with blob.start_session(config.production) as session:
        await session.finish_upload(upload.blob_key, upload_id)

    await repo.remove_upload(upload_id)

    created_at, valid_thru = get_interval_from_now(86400 * config.upload_ttl)
    return await repo.create_blob(
        token.user_uid,
        blob_key=upload.blob_key,
        file_name=file_name,
        created_at=created_at,
        valid_thru=valid_thru,
    )


@router.delete("/upload", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_upload(
    upload_id: str = Query(..., max_length=128),
    *,
    blob: BlobServiceDep,
    config: AppConfigDep,
    repo: RepositoryDep,
    request: Request,
) -> None:
    """Finish the upload specified by the given upload ID."""
    token = verify_token(
        request.cookies,
        token_name=ACCESS_TOKEN_NAME,
        secret_key=config.jwt_secret_key,
    )

    upload = await _verify_upload(token.user_uid, upload_id, repo=repo)
    async with blob.start_session(config.production) as session:
        await session.cancel_upload(upload.blob_key, upload_id)

    await repo.remove_upload(upload_id)


@router.get("/fetch", response_model=list[Blob])
async def fetch_blobs(
    *, config: AppConfigDep, repo: RepositoryDep, request: Request,
) -> list[Blob]:
    """Fetch all the blobs associated with a user from the database."""
    token = verify_token(
        request.cookies,
        token_name=ACCESS_TOKEN_NAME,
        secret_key=config.jwt_secret_key,
    )
    return await repo.find_blobs(token.user_uid)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blob(
    blob_uid: str = Query(..., max_length=32, min_length=32),
    *,
    blob: BlobServiceDep,
    config: AppConfigDep,
    repo: RepositoryDep,
    request: Request,
) -> None:
    """Finish the upload specified by the given upload ID."""
    token = verify_token(
        request.cookies,
        token_name=ACCESS_TOKEN_NAME,
        secret_key=config.jwt_secret_key,
    )

    try:
        obj, key = await repo.find_blob(token.user_uid, blob_uid=blob_uid)
    except EntityNotFoundError as e:
        raise HTTPException(
            detail=f"{blob_uid=} was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from e

    if not obj.is_valid():
        raise HTTPException(
            detail=f"{blob_uid=} has timed out.",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )

    async with blob.start_session(config.production) as session:
        await session.delete_blob(key)

    await repo.delete_blob(blob_uid)


# -- helper functions


async def _verify_upload(
    user_uid: str, upload_id: str, *, repo: RepositoryDep,
) -> Upload:
    """Verify the specified upload for the given user UID."""
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

    return upload
