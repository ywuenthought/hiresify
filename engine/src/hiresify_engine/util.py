# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide utility functions used across the codebase."""

import os
import re
import typing as ty
from datetime import UTC, datetime, timedelta
from uuid import uuid4

T = ty.TypeVar("T")

BLOB_KEY_PATTERN = re.compile(
    r"^(?P<user_uid>[a-zA-Z0-9]{32})/(?P<main>[a-zA-Z0-9_-]+)"
    r"/(?P<blob_uid>[a-zA-Z0-9]{32})\.(?P<sub>[a-z0-9]+)$",
)


def abbreviate_token(token: str, cutoff: int = 6) -> str:
    """Abbreviate the given token to make it partially visible."""
    if not token:
        return "<empty>"

    return f"{token[:cutoff]}***"


def get_envvar(varname: str, caster: ty.Callable[[str], T], default: T) -> T:
    """Get the value of an environment variable."""
    if (value := os.getenv(varname)) is None:
        return default

    try:
        if caster is bool:
            return ty.cast(T, value.lower() in ("1", "true"))
        return caster(value)
    except (ValueError, TypeError) as e:
        raise RuntimeError(f"Failed to load the envvar {varname}") from e


def check_tz(dt: datetime) -> None:
    """Check if the given datetime object is timezone-aware."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise ValueError(f"{dt=} must be timezone-aware.")


def generate_blob_key(user_uid: str, mime_type: str) -> str:
    """Generate a blob key with the given user UID and MIME type."""
    main, sub = mime_type.split("/")
    return f"{user_uid}/{main}/{uuid4().hex}.{sub}"


def get_interval_from_now(ttl: int) -> tuple[datetime, datetime]:
    """Get a time interval from now with the given TTL.

    Note that the TTL is in seconds.
    """
    start = datetime.now(UTC)
    end = start + timedelta(seconds=ttl)
    return start, end


def parse_blob_key(blob_key: str) -> tuple[str, str, str]:
    """Parse the given blob key to get forming components."""
    if not (match := BLOB_KEY_PATTERN.match(blob_key)):
        raise ValueError(f"{blob_key=} is invalid.")

    user_uid, main, blob_uid, sub = match.groups()
    return user_uid, blob_uid, f"{main}/{sub}"
