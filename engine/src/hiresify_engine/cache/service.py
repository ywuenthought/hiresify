# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the cache service layer for user authorization."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from redis.asyncio import Redis

from hiresify_engine.envvar import CACHE_TTL

from .model import Authorization, UserSession


class CacheService:
    """A wrapper class exposing APIs for cache service."""

    def __init__(self, db_url) -> None:
        """Initialize a new instance of CacheService."""
        self._store = Redis.from_url(db_url, decode_responses=True)

    async def dispose(self) -> None:
        """Dispose of the underlying cache store."""
        await self._store.aclose()

    ###############
    # authorization
    ###############

    async def set_authorization(
        self,
        user_uid: str,
        *,
        client_id: str,
        code_challenge: str,
        code_challenge_method: str,
        redirect_uri: str,
    ) -> Authorization:
        """Set an authorization with the given user UID."""
        auth = Authorization(
            client_id=client_id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            redirect_uri=redirect_uri,
            user_uid=user_uid,
        )

        serialized = auth.serialize()
        await self._store.set(f"auth:{auth.code}", serialized, ex=CACHE_TTL)

        return auth

    async def get_authorization(self, code: str) -> Authorization | None:
        """Get the authorization with the given code."""
        if not (serialized := await self._store.get(f"auth:{code}")):
            return None

        return Authorization.from_serialized(serialized)

    async def del_authorization(self, code: str) -> None:
        """Delete the authorization with the given code."""
        await self._store.delete(f"auth:{code}")

    ##############
    # user session
    ##############

    async def set_user_session(self, user_uid: str) -> UserSession:
        """Set a user session for the given user UID."""
        issued_at = datetime.now(UTC)
        expire_at = issued_at + timedelta(seconds=CACHE_TTL)

        session = UserSession(
            user_uid=user_uid,
            issued_at=issued_at,
            expire_at=expire_at,
        )

        serialized = session.serialize()
        await self._store.set(f"user:{session.id}", serialized, ex=CACHE_TTL)

        return session

    async def get_user_session(self, session_id: str) -> UserSession | None:
        """Get the user session with the given session ID."""
        if not (serialized := await self._store.get(f"user:{session_id}")):
            return None

        return UserSession.from_serialized(serialized)

    ############
    # CSRF token
    ############

    async def set_csrf_token(self, redirect_uri: str) -> str:
        """Set a CSRF token for the given redirect URI."""
        token = uuid4().hex
        await self._store.set(f"ruri:{redirect_uri}", token, ex=CACHE_TTL)
        return token

    async def get_csrf_token(self, redirect_uri: str) -> str | None:
        """Get the CSRF token with the given redirect URI."""
        return await self._store.get(f"ruri:{redirect_uri}")
