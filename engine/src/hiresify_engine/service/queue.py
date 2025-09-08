# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the job queue service layer for compute jobs."""

from redis.asyncio import Redis

Response = list[tuple[str, list[tuple[str, dict[str, str]]]]]


class QueueService:
    """A wrapper class exposing APIs for job queue service."""

    def __init__(
        self,
        db_url,
        *,
        block_time: int = 10,
        group_name: str = "worker",
        max_length: int = 10000,
        queue_name: str = "job",
    ) -> None:
        """Initialize a new instance of QueueService."""
        self._store = Redis.from_url(db_url, decode_responses=True)

        self._block_time = block_time * 1000  # s -> ms
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

    async def consume_job(self, worker_index: int) -> Response:
        """Consume the first-in job from the queue as the specified consumer."""
        return await self._store.xreadgroup(
            groupname=self._group_name,
            consumername=f"{self._group_name}:{worker_index}",
            streams={self._queue_name: ">"},
            block=self._block_time,
            count=1,
        )

    async def acknowledge(self, message_id: str) -> None:
        """Acknowledge successful processing of a message in the consumer group."""
        await self._store.xack(self._queue_name, self._group_name, message_id)
