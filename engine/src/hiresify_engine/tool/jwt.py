# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the token manager for user authentication."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from jose import JWTError, jwt


@dataclass(frozen=True)
class AccessToken:
    """The data model for an access token."""

    #: The encoded access token.
    token: str

    #: When the access token expires.
    expires_in: int

    #: The refresh token.
    refresh_token: str | None = None

    #: The permissions granted by this token.
    scope: str = "read write"

    #: The type of this token.
    token_type: str = "bearer"


class JWTTokenManager:
    """A wrapper class for managing access tokens."""

    def __init__(self, ttl: int, algorithm: str = "HS256") -> None:
        """Initialize a new instance of TokenManager."""
        self._ttl = ttl
        self._algorithm = algorithm

        self._key = token_urlsafe(64)

    def generate(
        self, user_uid: str, refresh_token: str | None = None,
    ) -> AccessToken:
        """Generate a token response for the user UID and refresh token."""
        issued_at = datetime.now(UTC)
        expire_at = issued_at + timedelta(seconds=self._ttl)

        claims = dict(
            exp=int(expire_at.timestamp()),
            iat=int(issued_at.timestamp()),
            scope="read write",
            sub=user_uid,
        )

        return AccessToken(
            token=jwt.encode(claims, self._key, self._algorithm),
            expires_in=self._ttl,
            refresh_token=refresh_token,
        )

    def verify(self, token: str) -> str | None:
        """Verify the given access token and return the subscriber."""
        try:
            payload = jwt.decode(token, self._key, algorithms=[self._algorithm])
            return payload["sub"]
        except JWTError:
            return None
