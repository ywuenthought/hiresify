# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide utility functions used by the repository layer."""

import re

_BLOB_KEY_PATTERN = re.compile(
    r"^(?P<user_uid>[a-zA-Z0-9]{32})/(?P<main>[a-zA-Z0-9_-]+)"
    r"/(?P<blob_uid>[a-zA-Z0-9]{32})\.(?P<sub>[a-z0-9]+)$",
)


def restore_mime_type(blob_key: str) -> str | None:
    """Rstore the MIME type from the given blob key."""
    if not (match := _BLOB_KEY_PATTERN.match(blob_key)):
        return None

    _, main, _, sub = match.groups()
    return f"{main}/{sub}"
