# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the broker service layer for compute jobs."""

from redis.asyncio import Redis


class BrokerService:
    """A wrapper class exposing APIs for broker service."""

    def __init__(
        self,
        db_url,
        *,
        stream_key: str = "job",
        max_length: int = 10000,
        group_name: str = "worker",
    ) -> None:
        """Initialize a new instance of BrokerService."""
        self._store = Redis.from_url(db_url, decode_responses=True)

        self._stream_key = stream_key
        self._max_length = max_length
        self._group_name = group_name

    async def init_stream(self) -> None:
        """Initialize a stream for the consumer groups."""
        groups = await self._store.xinfo_groups(self._stream_key)

        for group in groups:
            if group["name"] == self._group_name:
                break
        else:
            await self._store.xgroup_create(
                name=self._stream_key,
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
            name=self._stream_key,
            fields=dict(job_id=job_id),
            maxlen=self._max_length,
            approximate=True,
        )
