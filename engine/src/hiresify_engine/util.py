# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide utility functions used across the codebase."""

import os
import typing as ty

T = ty.TypeVar("T")

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
