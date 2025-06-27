# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the data models used by cache store."""

import json
import typing as ty
from dataclasses import asdict, dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class AuthorizationCode:
    """The data model for an authorization code."""

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

    #: The code ID that defaults to a random UUID.
    id: str = field(default_factory=lambda: uuid4().hex)

    @classmethod
    def from_serialized(cls, serialized: str) -> "AuthorizationCode":
        """Instantiate this class using the given serialized data."""
        raw = json.loads(serialized)
        return cls(**raw)

    def serialize(self) -> str:
        """Serialize this object into a string."""
        return json.dumps(asdict(self))


@dataclass(frozen=True)
class UserSession:
    """The data model for a user session."""

    #: When the session was issued.
    issued_at: datetime

    #: When the session expires.
    expire_at: datetime

    #: The user UID linked to this session.
    # If not given, the session will be anonymous.
    user_uid: str | None = None

    #: The session ID that defaults to a random UUID.
    id: str = field(default_factory=lambda: uuid4().hex)

    @classmethod
    def from_serialized(cls, serialized: str) -> "UserSession":
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
