# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the endpoint schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UserAuthSchema(BaseModel):
    """The endpoint schema for user authentication."""

    #: The unique user name of a user.
    username: str = Field(..., max_length=30)

    #: The hashed password associated with the user name.
    password: str | None = Field(None, max_length=128)

    #: The refresh tokens associated with this user.
    refresh_tokens: list["RefreshTokenSchema"] | None = None

    # Allow for instantiating from the database model.
    model_config = {"from_attributes": True}


class RefreshTokenSchema(BaseModel):
    """The endpoint schema for a user's refresh token."""

    #: The hashed refresh token.
    token: str = Field(..., max_length=128)

    #: The date and time when the token was issued.
    issued_at: datetime = Field(...)

    #: The date and time when the token was set to expire.
    expire_at: datetime = Field(...)

    #: A boolean flag for whether the token has been revoked.
    revoked: bool = False

    #: The user agent or device name for this token.
    device: str | None = Field(None, max_digits=128)

    #: The IP address where this token was requested.
    ip: str | None = Field(None, max_digits=45)

    #: The platform used when requesting this token.
    platform: str | None = Field(None, max_digits=32)

    #: The user that this refresh token belongs to.
    user: UserAuthSchema | None = None

    # Allow for instantiating from the database model.
    model_config = {"from_attributes": True}

    @field_validator("issued_at", "expire_at")
    @classmethod
    def has_timezone(cls, v: datetime) -> datetime:
        """Validate the timezone-awareness of `issued_at` and `expire_at`."""
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("The timezone information is missing.")
        return v
