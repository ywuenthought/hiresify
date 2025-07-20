# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the cache service layer for user authorization."""

import typing as ty
from datetime import UTC, datetime, timedelta

from redis.asyncio import Redis

from hiresify_engine.envvar import CACHE_TTL
from hiresify_engine.model import CSRFSession, UserSession

from .model import Authorization

T = ty.TypeVar("T", CSRFSession, UserSession)


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
    # CSRF session
    ##############

    async def set_csrf_session(self, csrf_token: str) -> CSRFSession:
        """Set a CSRF session for the given CSRF token."""
        return await self._set_session(CSRFSession, csrf_token=csrf_token)

    async def get_csrf_session(self, session_id: str) -> CSRFSession | None:
        """Get the CSRF session with the given session ID."""
        return await self._get_session(CSRFSession, session_id)

    ##############
    # user session
    ##############

    async def set_user_session(self, user_uid: str) -> UserSession:
        """Set a user session for the given user UID."""
        return await self._set_session(UserSession, user_uid=user_uid)

    async def get_user_session(self, session_id: str) -> UserSession | None:
        """Get the user session with the given session ID."""
        return await self._get_session(UserSession, session_id)

    # -- helper functions

    async def _set_session(self, cls: type[T], **metadata: ty.Any) -> T:
        """Set a session with the given cls (class) and metadata."""
        issued_at = datetime.now(UTC)
        expire_at = issued_at + timedelta(seconds=CACHE_TTL)

        session = cls(
            issued_at=issued_at,
            expire_at=expire_at,
            **metadata,
        )

        serialized = session.serialize()
        await self._store.set(f"{cls.type}:{session.id}", serialized, ex=CACHE_TTL)

        return session

    async def _get_session(self, cls: type[T], session_id: str) -> T | None:
        """Get the session specified by the given cls (class) and session ID."""
        if not (serialized := await self._store.get(f"{cls.type}:{session_id}")):
            return None

        return cls.from_serialized(serialized)
