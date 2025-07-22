# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the domain models for cache store."""

import copy
import json
import typing as ty
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from hiresify_engine.const import SESSION_NAME


@dataclass(frozen=True, kw_only=True)
class _BaseSession:
    """The base for a session domain model."""

    #: When the session was issued.
    issued_at: datetime

    #: When the session expires.
    expire_at: datetime

    #: The session ID that defaults to a random UUID.
    id: str = field(default_factory=lambda: uuid4().hex)

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

        for key, value in raw.items():
            if isinstance(value, datetime):
                raw[key] = value.isoformat()

        return json.dumps(raw)

    def to_cookie(self, *, path: str = "/", same: str = "lax") -> dict[str, ty.Any]:
        """Convert the metadata to a cookie."""
        elapsed = self.expire_at - self.issued_at
        max_age = int(elapsed.total_seconds())

        return dict(
            expires=self.expire_at,
            httponly=True,
            key=SESSION_NAME,
            max_age=max_age,
            path=path,
            samesite=same,
            secure=True,
            value=self.id,
        )


@dataclass(frozen=True, kw_only=True)
class UserSession(_BaseSession):
    """The domain model for a user session."""

    #: The user UID linked to this session.
    user_uid: str

    #: The type of this session.
    type: ty.ClassVar[str] = "user"


@dataclass(frozen=True, kw_only=True)
class CSRFSession(_BaseSession):
    """The domain model for a CSRF session."""

    #: The CSRF token linked to this session.
    csrf_token: str

    #: The type of this session.
    type: ty.ClassVar[str] = "csrf"
