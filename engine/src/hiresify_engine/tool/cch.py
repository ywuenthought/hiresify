# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the cache store manager for user authentication."""

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import Response
from redis.asyncio import Redis


@dataclass(frozen=True)
class _CodeMetadata:
    """Wrap the metadata associated with an authentication code."""

    #: The ID of the client.
    client_id: str

    #: The code challenge sent by the client.
    code_challenge: str

    #: The method to be used against the code challenge.
    code_challenge_method: str

    #: The redirect URI.
    redirect_uri: str

    #: The UID of the user to be authenticated.
    user_uid: str


@dataclass(frozen=True)
class _SessionMetadata:
    """Wrap the metadata associated with a user's session."""

    #: The user UID linked to this session.
    user_uid: str

    #: When the session was issued.
    issued_at: datetime

    #: When the session expires.
    expire_at: datetime

    #: The session ID that defaults to a random UUID.
    id: str = field(default_factory=lambda: uuid4().hex)

    @classmethod
    def from_serialized(cls, serialized: str) -> "_SessionMetadata":
        """Instantiate this class using the given serialized data."""
        raw = json.loads(serialized)

        for key in ("issued_at", "expire_at"):
            raw[key] = datetime.fromisoformat(raw[key])

        return cls(**raw)

    def serialize(self) -> str:
        """Serialize this object into a string."""
        raw = asdict(self)

        for key in ("issued_at", "expire_at"):
            raw[key] = raw[key].isoformat()

        return json.dumps(raw)

    def set_cookie_on(self, response: Response) -> None:
        """Set a cookie on the given response using the metadata."""
        elapsed = self.expire_at - self.issued_at
        max_age = int(elapsed.total_seconds())

        response.set_cookie(
            expires=self.expire_at,
            value=self.id,
            max_age=max_age,
            # Only send over HTTP requests, avoiding XSS attacks.
            httponly=True,
            # The hardcoded cookie name.
            key="session_id",
            # Forbidden cross-site requests.
            samesite="strict",
            # Only send over HTTPS connections.
            secure=True,
        )


class CCHStoreManager:
    """A wrapper class for managing a cache store."""

    def __init__(self,
        ttl: int,
        session_ttl: int,
        *,
        host: str = "localhost",
        port: int = 6379,
    ) -> None:
        """Initialize a new instance of CCHStoreManager."""
        self._ttl = ttl
        self._session_ttl = session_ttl

        self._store = Redis(host=host, port=port, decode_responses=True)

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
    ) -> str | None:
        """Set an authentication code for the given user UID."""
        code_meta = dict(
            client_id=client_id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            redirect_uri=redirect_uri,
            user_uid=user_uid,
        )

        code = uuid4().hex
        await self._store.setex(f"code:{code}", self._ttl, json.dumps(code_meta))

        return code

    async def get_code(self, code: str) -> _CodeMetadata | None:
        """Get the code metadata for with the given authentication code."""
        if not (raw := await self._store.get(f"code:{code}")):
            return None

        return _CodeMetadata(**json.loads(raw))

    async def del_code(self, code: str) -> None:
        """Delete the given authentication code from the cache store."""
        await self._store.delete(f"code:{code}")

    ##############
    # user session
    ##############

    async def set_session(self, user_uid: str = "null") -> _SessionMetadata:
        """Set a session for the given user UID.

        If `user_uid` is None, the session will be anonymous.
        """
        issued_at = datetime.now(UTC)
        expire_at = issued_at + timedelta(seconds=self._session_ttl)

        session = _SessionMetadata(
            user_uid=user_uid,
            issued_at=issued_at,
            expire_at=expire_at,
        )

        await self._store.setex(
            f"session:{session.id}",
            self._session_ttl,
            session.serialize(),
        )

        return session

    async def get_session(self, session_id: str) -> _SessionMetadata | None:
        """Get the session metadata for the given session ID."""
        if not (serialized := await self._store.get(f"session:{session_id}")):
            return None

        return _SessionMetadata.from_serialized(serialized)

    #############
    # request URL
    #############

    async def set_url(self, url: str) -> str:
        """Set a request ID for the given request URL."""
        request_id = uuid4().hex
        await self._store.setex(f"request:{request_id}", self._ttl, url)

        return request_id

    async def get_url(self, request_id: str) -> str | None:
        """Get the request URL for the given request ID."""
        return await self._store.get(f"request:{request_id}")
