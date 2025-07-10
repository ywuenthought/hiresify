# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the data models used by JWT service."""

import copy
import json
import typing as ty
from dataclasses import dataclass
from datetime import datetime

from .const import TokenName


@dataclass(frozen=True)
class JWTToken:
    """The data model for an access token."""

    #: The token name.
    name: TokenName

    #: When the session was issued.
    issued_at: datetime

    #: When the session expires.
    expire_at: datetime

    #: The token itself.
    token: str

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
            value=self.token,
            max_age=max_age,
            # Only send over HTTP requests, avoiding XSS attacks.
            httponly=True,
            # The hardcoded cookie name.
            key=self.name,
            # Forbidden cross-site requests.
            samesite="strict",
            # Only send over HTTPS connections.
            secure=True,
        )
