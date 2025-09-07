# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend compute-related endpoints."""

import typing as ty
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from hiresify_engine.db.exception import EntityNotFoundError
from hiresify_engine.dep import (
    AppConfigDep,
    BlobServiceDep,
    CacheServiceDep,
    QueueServiceDep,
    RepositoryDep,
)
from hiresify_engine.model import ComputeJob

router = APIRouter(prefix="/job")

@router.post("/submit", response_model=ComputeJob)
async def submit_job(
    blob_uid: str = Query(..., max_length=32, min_length=32),
    *,
    queue: QueueServiceDep,
    repo: RepositoryDep,
) -> ComputeJob:
    """Submit a compute job for the given blob UID."""
    job = await repo.submit_job(blob_uid, requested_at=datetime.now(UTC))
    await queue.enqueue_job(job.uid)

    return job


@router.get("/latest", response_model=ComputeJob)
async def get_latest_job(
    blob_uid: str = Query(..., max_length=32, min_length=32),
    *,
    repo: RepositoryDep,
) -> ComputeJob:
    """Get the latest compute job for a blob with the given UID."""
    try:
        job = await repo.find_latest_job(blob_uid)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blob {blob_uid} has no compute job at all.",
        ) from e

    return job


@router.get("/stream")
async def stream_job(
    job_id: str = Query(..., max_length=32, min_length=32),
    *,
    cache: CacheServiceDep,
    config: AppConfigDep,
) -> StreamingResponse:
    """Stream the real-time progress of a compute job."""
    async def generate() -> ty.AsyncGenerator[str, None]:
        """Generate the progress stream for the job."""
        async for progress in cache.sub_job_progress(
            job_id,
            returning_timeout=config.returning_timeout,
            heartbeat_timeout=config.heartbeat_timeout,
        ):
            yield f"data: {progress}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":"no-cache, no-transform",
            "Connection":"keep-alive",
        },
    )


@router.get("/download")
async def download_result(
    job_id: str = Query(..., max_length=32, min_length=32),
    *,
    blob: BlobServiceDep,
    config: AppConfigDep,
    repo: RepositoryDep,
) -> str:
    """Get a presigned URL to download the result for the given job ID."""
    try:
        blob_key = await repo.load_result_blob_key(job_id)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with {job_id=} was not found.",
        ) from e

    if not blob_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result for {job_id=} was not found.",
        )

    async with blob.start_session(config.production) as session:
        return await session.get_presigned_url(
            blob_key, expires_in=config.presigned_ttl,
        )
