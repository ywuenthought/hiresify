# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend compute-related endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, Query

from hiresify_engine.dep import BrokerServiceDep, RepositoryDep
from hiresify_engine.model import ComputeJob

router = APIRouter(prefix="/job")

@router.post("/submit", response_model=ComputeJob)
async def submit_job(
    blob_uid: str = Query(..., max_length=32, min_length=32),
    *,
    broker: BrokerServiceDep,
    repo: RepositoryDep,
) -> ComputeJob:
    """Submit a compute job for the given blob UID."""
    job = await repo.submit_job(blob_uid, requested_at=datetime.now(UTC))
    await broker.enqueue_job(job.uid)

    return job
