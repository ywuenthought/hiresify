# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the JWT token manager."""

import typing as ty
from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from jose import JWTError, jwt


class JWTTokenManager:
    """A wrapper class for managing access tokens."""

    def __init__(self, ttl: int, algorithm: str = "HS256") -> None:
        """Initialize a new instance of TokenManager."""
        self._ttl = ttl
        self._algorithm = algorithm

        self._key = token_urlsafe(64)

    def generate(
        self, user_uid: str,
        *,
        refresh_token: str | None = None,
    ) -> dict[str, ty.Any]:
        """Generate a token response for the given user UID.

        Note that if `refresh_token` is given, it will also be sent to the client to
        exchange for a fresh access token.
        """
        issued_at = datetime.now(UTC)
        expire_at = issued_at + timedelta(seconds=self._ttl)

        claims = dict(
            exp=int(expire_at.timestamp()),
            iat=int(issued_at.timestamp()),
            scope="read write",
            sub=user_uid,
        )

        return dict(
            token=jwt.encode(claims, self._key, self._algorithm),
            expires_in=self._ttl,
            refresh_token=refresh_token,
            scope="read write",
            token_type="bearer",
        )

    def verify(self, token: str) -> str | None:
        """Verify the given access token and return the user UID."""
        try:
            payload = jwt.decode(token, self._key, algorithms=[self._algorithm])
            return payload["sub"]
        except JWTError:
            return None
