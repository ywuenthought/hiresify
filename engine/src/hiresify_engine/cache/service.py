# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the cache service layer for user authorization."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from redis.asyncio import Redis

from .model import AuthorizationCode, UserSession


class CacheService:
    """A wrapper class exposing APIs for cache service."""

    def __init__(self, db_url, *, ttl: int, long_ttl: int) -> None:
        """Initialize a new instance of CacheService."""
        self._store = Redis.from_url(db_url, decode_responses=True)

        # The short-term TTL.
        self._ttl = ttl

        # The long-term TTL.
        self._long_ttl = long_ttl

    async def dispose(self) -> None:
        """Dispose of the underlying cache store."""
        await self._store.aclose()

    ###########
    # auth code
    ###########

    async def set_code(
        self,
        user_uid: str,
        *,
        client_id: str,
        code_challenge: str,
        code_challenge_method: str,
        redirect_uri: str,
    ) -> AuthorizationCode:
        """Set an authorization code for the given user UID."""
        code = AuthorizationCode(
            client_id=client_id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            redirect_uri=redirect_uri,
            user_uid=user_uid,
        )

        serialized = code.serialize()
        await self._store.set(f"code:{code.id}", serialized, ex=self._ttl)

        return code

    async def get_code(self, code_id: str) -> AuthorizationCode | None:
        """Get the code with the given code ID."""
        if not (serialized := await self._store.get(f"code:{code_id}")):
            return None

        return AuthorizationCode.from_serialized(serialized)

    async def del_code(self, code_id: str) -> None:
        """Delete the code with the given code ID."""
        await self._store.delete(f"code:{code_id}")

    ##############
    # user session
    ##############

    async def set_session(self, user_uid: str | None = None) -> UserSession:
        """Set a session for the given user UID.

        If `user_uid` is not given, the session will be anonymous.
        """
        issued_at = datetime.now(UTC)
        expire_at = issued_at + timedelta(seconds=self._long_ttl)

        session = UserSession(
            user_uid=user_uid,
            issued_at=issued_at,
            expire_at=expire_at,
        )

        serialized = session.serialize()
        await self._store.set(f"session:{session.id}", serialized, ex=self._long_ttl)

        return session

    async def get_session(self, session_id: str) -> UserSession | None:
        """Get the session with the given session ID."""
        if not (serialized := await self._store.get(f"session:{session_id}")):
            return None

        return UserSession.from_serialized(serialized)

    #############
    # request URL
    #############

    async def set_url(self, url: str) -> str:
        """Set a request ID for the given request URL."""
        request_id = uuid4().hex
        await self._store.set(f"request:{request_id}", url, ex=self._ttl)

        return request_id

    async def get_url(self, request_id: str) -> str | None:
        """Get the request URL for the given request ID."""
        return await self._store.get(f"request:{request_id}")
