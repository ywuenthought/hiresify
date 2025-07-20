# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the domain models for JWT service."""

import typing as ty
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import cached_property
from uuid import uuid4

from jose import JWTError, jwt

from hiresify_engine.const import TOKEN_ALGORITHM, TOKEN_AUDIENCE, TOKEN_ISSUER
from hiresify_engine.envvar import JWT_SECRET_KEY, PRODUCTION
from hiresify_engine.util import check_tz


@dataclass(frozen=True)
class JWTToken:
    """Wrap user-facing fields and methods for a JWT token."""

    #: The UID of the user that owns this token.
    user_uid: str

    #: When this token was issued.
    issued_at: datetime

    #: When this token expires.
    expire_at: datetime

    #: A boolean flag for whether this token has been revoked.
    revoked: bool = False

    #: The UID of this token.
    uid: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        """Perform post init checks."""
        check_tz(self.issued_at)
        check_tz(self.expire_at)

    def is_valid(self) -> bool:
        """Check if this upload is still valid or expired."""
        return self.expire_at > datetime.now(UTC)

    @classmethod
    def from_token(cls, token: str) -> ty.Optional["JWTToken"]:
        """Initialize a new instance of JWTToken by decrypting the JWT token."""
        try:
            payload = jwt.decode(
                token,
                key=JWT_SECRET_KEY,
                algorithms=[TOKEN_ALGORITHM],
                audience=TOKEN_AUDIENCE,
                issuer=TOKEN_ISSUER,
            )
        except JWTError:
            return None

        return cls(
            issued_at=datetime.fromtimestamp(payload["iat"], tz=UTC),
            expire_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
            uid=payload["jti"],
            user_uid=payload["sub"],
        )

    @cached_property
    def token(self) -> str:
        """Compute the JWT token by encrypting the token information."""
        return jwt.encode(
            dict(
                aud=TOKEN_AUDIENCE,
                exp=int(self.expire_at.timestamp()),
                iat=int(self.issued_at.timestamp()),
                iss=TOKEN_ISSUER,
                jti=self.uid,
                sub=self.user_uid,
            ),
            algorithm=TOKEN_ALGORITHM,
            key=JWT_SECRET_KEY,
        )

    def to_cookie(self, key: str, path: str = "/") -> dict[str, ty.Any]:
        """Generate a cookie with the available information."""
        elapsed = self.expire_at - self.issued_at
        max_age = int(elapsed.total_seconds())

        return dict(
            expires=self.expire_at,
            # Only send over HTTP requests, avoiding XSS attacks.
            httponly=True,
            # The cookie key.
            key=key,
            max_age=max_age,
            path=path,
            # Forbidden cross-site requests.
            samesite="strict",
            # Only send over HTTPS connections.
            secure=PRODUCTION,
            value=self.token,
        )
