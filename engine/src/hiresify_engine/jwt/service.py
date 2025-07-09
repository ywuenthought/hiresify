# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the JWT token service."""

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from jose import JWTError, jwt

from .model import AccessToken


class JWTTokenService:
    """A wrapper class for managing access tokens."""

    def __init__(self, ttl: int, algorithm: str = "HS256") -> None:
        """Initialize a new instance of JWTTokenService."""
        self._ttl = ttl
        self._algorithm = algorithm

        self._key = token_urlsafe(64)

    def generate(self, user_uid: str) -> AccessToken:
        """Generate an access token for the given user UID."""
        issued_at = datetime.now(UTC)
        expire_at = issued_at + timedelta(seconds=self._ttl)

        claims = dict(exp=int(expire_at.timestamp()), sub=user_uid)

        token = jwt.encode(claims, self._key, self._algorithm)
        return AccessToken(issued_at=issued_at, expire_at=expire_at, token=token)

    def verify(self, token: str) -> str | None:
        """Verify the given token and return the user UID."""
        try:
            payload = jwt.decode(token, self._key, algorithms=[self._algorithm])
            return payload["sub"]
        except JWTError:
            return None
