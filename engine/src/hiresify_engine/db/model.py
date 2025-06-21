# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the database schema."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """The base for all database models to inherit from."""


class User(Base):
    """The database model for identifying a user."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)

    #: The UID of a user, used externally.
    uid: Mapped[str] = mapped_column(
        String(32), default=lambda: uuid4().hex, unique=True,
    )

    #: The unique user name of a user.
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    #: The hashed password associated with the user name.
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    # A user can have many refresh tokens.
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan",
    )


class RefreshToken(Base):
    """The database model for a user's refresh token."""

    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(primary_key=True)

    #: The UID of a refresh token, used externally.
    uid: Mapped[str] = mapped_column(
        String(32), default=lambda: uuid4().hex, unique=True,
    )

    #: A string representation of the refresh token.
    token: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)

    #: The date and time when the token was issued.
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    #: The date and time when the token was set to expire.
    expire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    #: A boolean flag for whether the token has been revoked.
    revoked: Mapped[bool] = mapped_column(default=False, nullable=False)

    #: The user agent or device name for this token.
    device: Mapped[str] = mapped_column(String(128), nullable=True)

    #: The IP address where this token was requested.
    ip: Mapped[str] = mapped_column(String(45), nullable=True)

    #: The platform used when requesting this token.
    platform: Mapped[str] = mapped_column(String(32), nullable=True)

    #: The user ID that this refresh token is associated with.
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    # Each refresh token belongs to one user.
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
