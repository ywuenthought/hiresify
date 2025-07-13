# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import typing as ty
from tempfile import NamedTemporaryFile

import pytest

from ..service import BlobService


@pytest.fixture(scope="session")
async def service() -> ty.AsyncGenerator[BlobService, None]:
    service = BlobService()

    async with service.start_session() as session:
        await session.init_bucket()

    yield session


@pytest.fixture(scope="function")
def media() -> ty.Generator[str, None, None]:
    total_size = 32 * 1024 * 1024  # bytes

    with NamedTemporaryFile(suffix=".mp4") as media:
        media.write(b"\0" * total_size)
        yield media.name
