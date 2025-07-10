# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the JWT token service."""

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from jose import JWTError, jwt

from hiresify_engine.envvar import ACCESS_TTL, REFRESH_TTL

from .const import ACCESS_TOKEN, REFRESH_TOKEN, TokenName
from .model import JWTToken


class JWTTokenService:
    """A wrapper class for managing access tokens."""

    def __init__(self, algorithm: str = "HS256") -> None:
        """Initialize a new instance of JWTTokenService."""
        self._algorithm = algorithm
        self._key = token_urlsafe(64)

    def generate_access_token(self, user_uid: str) -> JWTToken:
        """Generate an access token for the given user UID."""
        return self._generate_token(user_uid, ACCESS_TOKEN)

    def generate_refresh_token(self, user_uid: str) -> JWTToken:
        """Generate a refresh token for the given user UID."""
        return self._generate_token(user_uid, REFRESH_TOKEN)

    def verify(self, token: str) -> str | None:
        """Verify the given token and return the user UID."""
        try:
            payload = jwt.decode(token, self._key, algorithms=[self._algorithm])
            return payload["sub"]
        except JWTError:
            return None

    def _generate_token(self, user_uid: str, name: TokenName) -> JWTToken:
        """Generate a JWT token by the given name."""
        ttl = ACCESS_TTL if name == ACCESS_TOKEN else REFRESH_TTL

        issued_at = datetime.now(UTC)
        expire_at = issued_at + timedelta(seconds=ttl)

        claims = dict(exp=int(expire_at.timestamp()), sub=user_uid)
        token = jwt.encode(claims, self._key, self._algorithm)

        return JWTToken(
            name=name,
            issued_at=issued_at,
            expire_at=expire_at,
            token=token,
        )
