# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide the default configuration for Pydantic domain models."""

from pydantic import ConfigDict


def to_camel(s: str) -> str:
    """Convert the field names from snake case to camel case."""
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


DEFAULT_CONFIG = ConfigDict(alias_generator=to_camel, populate_by_name=True)
