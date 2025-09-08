# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the compute worker layer to perform compute jobs."""

import asyncio
import signal
import typing as ty
from pathlib import Path

from hiresify_engine.db.repository import Repository
from hiresify_engine.service import BlobService, QueueService


class ComputeWorker:
    """A wrapper class exposing compute-related APIs."""

    def __init__(
        self,
        callback: ty.Callable[[Path], ty.Awaitable[Path]],
        *,
        index: int = 1,
        queue: QueueService,
        repo: Repository,
        blob: BlobService,
    ) -> None:
        """Initialize a new instance of ComputeService."""
        self._callback = callback

        self._index = index
        self._queue = queue
        self._repo = repo
        self._blob = blob

        self._stop = False

    async def run(self, production: bool = False) -> None:
        """Run the compute worker."""
        self._handle_signals()

        while not self._stop:
            if not (response := await self._queue.consume_job(self._index)):
                continue

            ((_, ((message_id, fields), )), ) = response

            job_id = fields["job_id"]
            blob_key = await self._repo.load_blob_key(job_id)
            file_path = Path(blob_key)
            file_path.parent.mkdir(exist_ok=True, parents=True)

            async with self._blob.start_session(production) as session:
                await session.download_blob(file_path, blob_key)

                try:
                    result_file_path = await self._callback(file_path)
                    result_blob_key = f"{job_id}{result_file_path.suffix}"

                    await session.upload_file(result_file_path, result_blob_key)
                    await self._repo.update_job(
                        job_id,
                        status="finished",
                        result_blob_key=result_blob_key,
                    )
                except RuntimeError:
                    await self._repo.update_job(job_id, status="aborted")

                await self._queue.acknowledge(message_id)

    def stop(self) -> None:
        """Stop the compute worker."""
        self._stop = True

    # -- helper functions

    def _handle_signals(self) -> None:
        """Handle signals to elegantly stop the compute worker."""
        try:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self.stop)
        # loop.add_signal_handler is not implemented on Windows.
        except NotImplementedError:
            pass
