# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the job queue service layer for compute jobs."""

from redis.asyncio import Redis


class QueueService:
    """A wrapper class exposing APIs for job queue service."""

    def __init__(
        self,
        db_url,
        *,
        queue_name: str = "job",
        max_length: int = 10000,
        group_name: str = "worker",
    ) -> None:
        """Initialize a new instance of QueueService."""
        self._store = Redis.from_url(db_url, decode_responses=True)

        self._queue_name = queue_name
        self._max_length = max_length
        self._group_name = group_name

    async def init_queue(self) -> None:
        """Initialize a job queue for compute workers."""
        groups = await self._store.xinfo_groups(self._queue_name)

        for group in groups:
            if group["name"] == self._group_name:
                break
        else:
            await self._store.xgroup_create(
                name=self._queue_name,
                groupname=self._group_name,
                id="$",
                mkstream=True,
            )

    async def dispose(self) -> None:
        """Dispose of the underlying cache store."""
        await self._store.aclose()

    async def enqueue_job(self, job_id: str) -> None:
        """Enqueue a compute job with the given job ID."""
        await self._store.xadd(
            name=self._queue_name,
            fields=dict(job_id=job_id),
            maxlen=self._max_length,
            approximate=True,
        )
