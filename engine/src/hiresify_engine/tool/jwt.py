# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the token manager for user authentication."""

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from jose import jwt


class TokenManager:
    """A manager class for generating and verifying an access token."""

    def __init__(self, ttl: int, algorithm: str = "HS256") -> None:
        """Initialize a new instance of TokenManager."""
        self._ttl = ttl
        self._algorithm = algorithm

        self._secret_key = token_urlsafe(32)

    def generate(self, user_id: str) -> str:
        """Generate an access token for a user with the given user ID."""
        issued_at = datetime.now(UTC)
        expire_at = issued_at + timedelta(seconds=self._ttl)

        return jwt.encode(
            dict(
                exp=int(expire_at.timestamp()),
                iat=int(issued_at.timestamp()),
                scope="read write",
                sub=user_id,
            ),
            self._secret_key,
            algorithm=self._algorithm,
        )

    def verify(self, token: str) -> bool:
        """Verify the given access token."""
        payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        return payload["sub"]
