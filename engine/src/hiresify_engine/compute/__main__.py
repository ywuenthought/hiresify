# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Entry point for the compute worker layer."""

import argparse
import asyncio

from hiresify_engine.config import AppConfig
from hiresify_engine.db.repository import Repository
from hiresify_engine.service import BlobService, QueueService

from .callback import callback
from .worker import ComputeWorker

parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--index",
    default=1,
    help="Specify the worker index.",
    type=int,
)


async def main(index: int = 1) -> None:
    """Spin up an event loop with a compute worker."""
    config = AppConfig()

    # Initialize the blob store manager.
    blob = BlobService(
        config.blob_store_url,
        region_tag=config.blob_store_region,
        access_key=config.blob_access_key,
        secret_key=config.blob_secret_key,
    )

    # Initialize the queue service for compute jobs.
    queue = QueueService(config.redis_url)

    # Initialize the database repository.
    repo = Repository(config.database_url, **config.database_config)

    # Initialize the compute worker.
    worker = ComputeWorker(
        callback,
        index=index,
        queue=queue,
        repo=repo,
        blob=blob,
    )

    try:
        await worker.run()
    finally:
        async with blob.start_session(config.production) as session:
            await session.dispose()

        await queue.dispose()
        await repo.dispose()


if __name__ == "__main__":
    args = parser.parse_args()
    index: int = args.index

    asyncio.run(main(index))
