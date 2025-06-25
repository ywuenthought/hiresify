# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from urllib.parse import parse_qs, urlparse


def get_query_params(url: str) -> dict[str, list[str]]:
    """Parse the given URL to get the query parameters."""
    parsed_url = urlparse(url)
    return parse_qs(parsed_url.query)
