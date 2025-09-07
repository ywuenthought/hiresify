# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the cache service layer for user authorization."""

import asyncio
import json
import typing as ty
from uuid import uuid4

from redis.asyncio import Redis

from hiresify_engine.model import CSRFSession, UserSession
from hiresify_engine.util import get_interval_from_now

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
        ttl: int,
        client_id: str,
        code_challenge: str,
        code_challenge_method: str,
        redirect_uri: str,
    ) -> str:
        """Set an authorization for the given user UID."""
        code = uuid4().hex

        await self._store.set(
            f"auth:{code}",
            json.dumps(
                dict(
                    client_id=client_id,
                    code_challenge=code_challenge,
                    code_challenge_method=code_challenge_method,
                    redirect_uri=redirect_uri,
                    user_uid=user_uid,
                ),
            ),
            ex=ttl,
        )

        return code

    async def get_authorization(self, code: str) -> dict[str, str] | None:
        """Get the authorization with the given code."""
        if not (serialized := await self._store.get(f"auth:{code}")):
            return None

        return json.loads(serialized)

    async def del_authorization(self, code: str) -> None:
        """Delete the authorization with the given code."""
        await self._store.delete(f"auth:{code}")

    ##############
    # CSRF session
    ##############

    async def set_csrf_session(self, csrf_token: str, ttl: int) -> CSRFSession:
        """Set a CSRF session for the given CSRF token."""
        return await self._set_session(CSRFSession, ttl, csrf_token=csrf_token)

    async def get_csrf_session(self, session_id: str) -> CSRFSession | None:
        """Get the CSRF session with the given session ID."""
        return await self._get_session(CSRFSession, session_id)

    ##############
    # user session
    ##############

    async def set_user_session(self, user_uid: str, ttl: int) -> UserSession:
        """Set a user session for the given user UID."""
        return await self._set_session(UserSession, ttl, user_uid=user_uid)

    async def get_user_session(self, session_id: str) -> UserSession | None:
        """Get the user session with the given session ID."""
        return await self._get_session(UserSession, session_id)

    ##############
    # job progress
    ##############

    async def set_job_progress(self, job_id: str, progress: float) -> None:
        """Set the current progress of a job with the given ID.

        The numerical range of a normal progress is [0, 1]. But there are two special
        numbers -1 and 2. -1 is used when a job is aborted abnormally. 2 is used when
        a job result has been synced to the blob store and database.
        """
        await self._store.set(f"job:{job_id}", str(progress))

    async def get_job_progress(self, job_id: str) -> float | None:
        """Get the current progress of a job with the given ID."""
        progress = await self._store.get(f"job:{job_id}")
        return None if progress is None else float(progress)

    async def pub_job_progress(self, job_id: str, progress: float) -> None:
        """Publish the progress of a job with the given ID."""
        await self._store.publish(f"job:{job_id}", str(progress))

    async def sub_job_progress(
        self,
        job_id: str,
        *,
        returning_timeout: int = 1,
        heartbeat_timeout: int = 1,
    ) -> ty.AsyncGenerator[float, None]:
        """Subscribe to a real-time progress stream for a job with the given ID."""
        key = f"job:{job_id}"

        subscriber = self._store.pubsub()
        await subscriber.subscribe(key)

        try:
            while True:
                message = await subscriber.get_message(
                    ignore_subscribe_messages=True,
                    timeout=float(returning_timeout),
                )

                if message is None:
                    await asyncio.sleep(float(heartbeat_timeout))
                    continue

                yield float(message["data"])
        finally:
            await subscriber.unsubscribe(key)
            await subscriber.aclose()

    async def delete_job(self, job_id: str) -> None:
        """Delete the job with the given ID from the cache store."""
        await self._store.delete(f"job:{job_id}")

    # -- helper functions

    async def _set_session(self, cls: type[T], ttl: int, **metadata: ty.Any) -> T:
        """Set a session with the given cls (class) and metadata."""
        issued_at, expire_at = get_interval_from_now(ttl)

        session = cls(
            issued_at=issued_at,
            expire_at=expire_at,
            **metadata,
        )

        serialized = session.serialize()
        await self._store.set(f"{cls.type}:{session.id}", serialized, ex=ttl)

        return session

    async def _get_session(self, cls: type[T], session_id: str) -> T | None:
        """Get the session specified by the given cls (class) and session ID."""
        if not (serialized := await self._store.get(f"{cls.type}:{session_id}")):
            return None

        return cls.from_serialized(serialized)
