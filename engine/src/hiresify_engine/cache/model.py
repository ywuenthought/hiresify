# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the data models used by cache store."""

import copy
import json
import typing as ty
from dataclasses import asdict, dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class Authorization:
    """The data model for an authorization."""

    #: The ID of the client to be authorized.
    client_id: str

    #: The code challenge sent by the client.
    code_challenge: str

    #: The method to be used against the code challenge.
    code_challenge_method: str

    #: The redirect URI.
    redirect_uri: str

    #: The UID of the user that granted the authorization.
    user_uid: str

    #: The authorization code that defaults to a random UUID.
    code: str = field(default_factory=lambda: uuid4().hex)

    @classmethod
    def from_serialized(cls, serialized: str) -> "Authorization":
        """Instantiate this class using the given serialized data."""
        raw = json.loads(serialized)
        return cls(**raw)

    def serialize(self) -> str:
        """Serialize this object into a string."""
        return json.dumps(asdict(self))


class SessionMixin:
    """The mixin that injects methods to session data models."""

    #: When the session was issued.
    issued_at: datetime

    #: When the session expires.
    expire_at: datetime

    #: The session ID.
    id: str

    @classmethod
    def from_serialized(cls, serialized: str) -> ty.Self:
        """Instantiate this class using the given serialized data."""
        raw = json.loads(serialized)

        for key in ("issued_at", "expire_at"):
            raw[key] = datetime.fromisoformat(raw[key])

        return cls(**raw)

    def serialize(self) -> str:
        """Serialize this object into a string."""
        raw = copy.deepcopy(self.__dict__)

        for key in ("issued_at", "expire_at"):
            raw[key] = raw[key].isoformat()

        return json.dumps(raw)

    def to_cookie(self) -> dict[str, ty.Any]:
        """Convert the metadata to a cookie."""
        elapsed = self.expire_at - self.issued_at
        max_age = int(elapsed.total_seconds())

        return dict(
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


@dataclass(frozen=True)
class RequestSession(SessionMixin):
    """The data model for a request session.

    A request session is anonymous and only associated with a specific request.
    """

    #: The request URI linked to this session.
    request_uri: str

    #: When the session was issued.
    issued_at: datetime

    #: When the session expires.
    expire_at: datetime

    #: The session ID that defaults to a random UUID.
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass(frozen=True)
class UserSession(SessionMixin):
    """The data model for a user's session."""

    #: The user UID linked to this session.
    user_uid: str

    #: When the session was issued.
    issued_at: datetime

    #: When the session expires.
    expire_at: datetime

    #: The session ID that defaults to a random UUID.
    id: str = field(default_factory=lambda: uuid4().hex)
