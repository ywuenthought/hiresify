# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export a testing version of the cache store manager."""

import typing as ty
from datetime import UTC, datetime, timedelta

from hiresify_engine.cache.service import CacheService


class MockCacheStore:
    """A mock cache store that lives in memory."""

    def __init__(self) -> None:
        """Initialize a new instance of this class."""
        self._cache: dict[str, ty.Any] = {}
        self._timer: dict[str, datetime] = {}

    async def set(self, key: str, value: ty.Any, *, ex: int) -> None:
        """Set the value of a key with the given key, value, and TTL."""
        self._cache[key] = value
        self._timer[key] = datetime.now(UTC) + timedelta(seconds=ex)

    async def get(self, key: str) -> str | None:
        """Get the value of the given key."""
        if not (value := self._cache.get(key)):
            return None

        if datetime.now(UTC) >= self._timer[key]:
            self._cache.pop(key)
            self._timer.pop(key)
            return None

        return value

    async def delete(self, key: str) -> None:
        """Delete a key from the cache store."""
        self._cache.pop(key, None)
        self._timer.pop(key, None)

    async def aclose(self) -> None:
        """Close the connection to the cache store."""
        self._cache.clear()
        self._timer.clear()


class TestCacheService(CacheService):
    """A test cache service that uses a mock cache store."""

    def __init__(self, *, ttl, long_ttl) -> None:
        """Initialize a new instance of this class."""
        self._ttl = ttl
        self._long_ttl = long_ttl
        self._store = MockCacheStore()
