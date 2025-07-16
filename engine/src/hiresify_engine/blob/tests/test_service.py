# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

# ruff: noqa: B017

import asyncio
from itertools import count
from uuid import uuid4

import pytest

from ..service import BlobService


async def test_upload_file(media: str, service: BlobService) -> None:
    # Given
    chunk_size = 16 * 1024 * 1024  # bytes
    blob_key = uuid4().hex

    # When
    async with service.start_session() as session:
        upload_id = await session.start_upload(blob_key)

        tasks = []
        with open(media, "rb") as fp:
            counter = count(1)
            while chunk := fp.read(chunk_size):
                part_index = next(counter)
                task = asyncio.create_task(
                    session.upload_chunk(
                        blob_key=blob_key,
                        data_chunk=chunk,
                        part_index=part_index,
                        upload_id=upload_id,
                    ),
                )
                tasks.append(task)

        await asyncio.gather(*tasks)
        await session.finish_upload(blob_key, upload_id)

        # Then
        with pytest.raises(Exception):
            await session.report_parts(blob_key, upload_id)


async def test_abort_upload(media: str, service: BlobService) -> None:
    # Given
    chunk_size = 16 * 1024 * 1024  # bytes
    blob_key = uuid4().hex

    # When
    async with service.start_session() as session:
        upload_id = await session.start_upload(blob_key)

        with open(media, "rb") as fp:
            await session.upload_chunk(
                blob_key=blob_key,
                data_chunk=fp.read(chunk_size),
                part_index=1,
                upload_id=upload_id,
            )

        parts = await session.report_parts(blob_key, upload_id)

        # Then
        assert len(parts) == 1
        assert parts[0].index == 1

        # When
        await session.abort_upload(blob_key, upload_id)

        # Then
        with pytest.raises(Exception):
            await session.report_parts(blob_key, upload_id)
