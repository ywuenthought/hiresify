# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide utility functions used across the codebase."""

import os
import typing as ty
from datetime import UTC, datetime, timedelta

T = ty.TypeVar("T")


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


def get_interval_from_now(ttl: int) -> tuple[datetime, datetime]:
    """Get a time interval from now with the given TTL.

    Note that the TTL is in seconds.
    """
    start = datetime.now(UTC)
    end = start + timedelta(seconds=ttl)
    return start, end
