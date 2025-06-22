# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the cache store manager for user authentication."""

import json
import typing as ty
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

    #: A token sent by the client to avoid CSRF attacks.
    state: str | None = None


@dataclass(frozen=True)
class _SessionMetadata:
    """Wrap the metadata associated with a user's session."""

    #: When the session expires.
    expires: datetime

    #: The duration when the session is valid.
    max_age: int

    #: The actual value stored in the cookie.
    # This is the session ID by default.
    value: str

    #: The protective token used against CSRF attacks.
    csrf_token: str = field(default_factory=lambda: uuid4().hex)

    #: Whether only sent via HTTP requests.
    httponly: bool = True

    #: The cookie name.
    key: str = "session_id"

    #: Whether the cookie is sent with cross-site requests.
    # "lax" allows sending cookies on top-level navigation GET requests.
    samesite: ty.Literal["lax", "strict", "none"] | None = "lax"

    #: Whether only sent over HTTPS connections.
    secure: bool = True

    #: The user UID linked to this session.
    # The session is anonymous with user_uid=None.
    user_uid: str | None = None

    def set_cookie_on(self, response: Response) -> None:
        """Set a cookie on the given response using the metadata."""
        response.set_cookie(
            expires=self.expires,
            httponly=self.httponly,
            key=self.key,
            max_age=self.max_age,
            samesite=self.samesite,
            secure=self.secure,
            value=self.value,
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

    async def generate_code(
        self,
        session_id: str,
        *,
        client_id: str,
        code_challenge: str,
        code_challenge_method: str,
        redirect_uri: str,
        state: str | None = None,
    ) -> str | None:
        """Generate an authentication code for a user login session."""
        if not (session := await self.get_session(session_id)) or not session.user_uid:
            return None

        code = uuid4().hex
        code_meta = dict(
            client_id=client_id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            redirect_uri=redirect_uri,
            user_uid=session.user_uid,
            state=state,
        )

        await self._store.setex(f"code:{code}", self._ttl, json.dumps(code_meta))

        return code

    async def get_codemeta(self, code: str) -> _CodeMetadata | None:
        """Get the metadata associated with the given authentication code."""
        if not (raw := await self._store.get(f"code:{code}")):
            return None

        return _CodeMetadata(**json.loads(raw))

    async def delete_code(self, code: str) -> None:
        """Delete the given authentication code from the cache store."""
        await self._store.delete(f"code:{code}")

    ##############
    # user session
    ##############

    async def generate_session(self, user_uid: str | None = None) -> _SessionMetadata:
        """Generate a session cookie for a user with the given user UID."""
        session = _SessionMetadata(
            expires=datetime.now(UTC) + timedelta(seconds=self._session_ttl),
            max_age=self._session_ttl,
            value=(session_id := uuid4().hex),
            user_uid=user_uid,
        )

        serialized = json.dumps(asdict(session))
        await self._store.setex(f"session:{session_id}", self._session_ttl, serialized)

        return session

    async def get_session(self, session_id: str) -> _SessionMetadata | None:
        """Get the session metadata given the corresponding session ID."""
        if not (raw := await self._store.get(f"session:{session_id}")):
            return None

        return _SessionMetadata(**json.loads(raw))

    async def delete_session(self, session_id: str) -> None:
        """Delete the session from the cache store given the session ID."""
        await self._store.delete(f"session:{session_id}")

    #############
    # request URL
    #############

    async def cache_url(self, url: str) -> str:
        """Cache a request URL by assigning it a request ID."""
        request_id = uuid4().hex
        await self._store.setex(f"request:{request_id}", self._ttl, url)

        return request_id

    async def get_url(self, request_id: str) -> str | None:
        """Get the request URL associated with the request ID."""
        return await self._store.get(f"request:{request_id}")
