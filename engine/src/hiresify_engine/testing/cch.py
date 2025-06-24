# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export a testing version of the cache store manager."""

import typing as ty
from datetime import UTC, datetime, timedelta

from hiresify_engine.tool import CCHManager


class _MockCacheStore:
    """A mock cache store that lives in memory."""

    def __init__(self) -> None:
        """Initialize a new instance of this class."""
        self._cache: dict[str, ty.Any] = {}
        self._timer: dict[str, datetime] = {}

    async def setex(self, key: str, ttl: int, value: ty.Any) -> None:
        """Set the value of a key with the given key, value, and TTL."""
        self._cache[key] = value
        self._timer[key] = datetime.now(UTC) + timedelta(seconds=ttl)

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


class TestCCHStoreManager(CCHManager):
    """A test cache store manager that uses a mock cache store."""

    def __init__(self, ttl, session_ttl) -> None:
        """Initialize a new instance of this class."""
        self._ttl = ttl
        self._session_ttl = session_ttl
        self._store = _MockCacheStore()
