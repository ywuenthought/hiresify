# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide utility functions used across the routers."""

import os
from uuid import uuid4

from fastapi import HTTPException, Request, Response, status

from hiresify_engine.const import ACCESS_TOKEN_NAME
from hiresify_engine.envvar import PRODUCTION
from hiresify_engine.model import JWTToken

_CSP_ITEMS = {
    "connect-src": ["self"],
    "default-src": ["self"],
    "img-src": ["self"],
    "script-src": ["self"],
    "style-src": ["self"],
}

_STS_ITEMS = [
    "includeSubDomains",
    "max-age=63072000",
    "preload",
]


def add_secure_headers(response: Response) -> None:
    """Add secure headers to the given response."""
    response.headers.update(
        {
            # Prevent loading any external resources.
            "Content-Security-Policy": _format_csp_items(_CSP_ITEMS),

            # Disable access to sensitive APIs.
            "Permissions-Policy": "geolocation=(), camera=()",

            # Prevent leaking the referrer URL.
            "Referrer-Policy": "no-referrer",

            # Disallow MIME-sniff the response content.
            "X-Content-Type-Options": "nosniff",

            # Prevent the page from being embedded in frames.
            "X-Frame-Options": "DENY",
        },
    )

    if PRODUCTION:
        # Force browsers to use HTTPS for all future requests.
        response.headers["Strict-Transport-Security"] = "; ".join(_STS_ITEMS)


def generate_blob_key(user_uid: str, mime_type: str) -> str:
    """Generate a blob key with the given user UID and MIME type."""
    main, sub = mime_type.split("/")
    return f"{user_uid}/{main}/{uuid4().hex}.{sub}"


def restore_mime_type(blob_key: str) -> str:
    """Rstore the MIME type from the given blob key."""
    _, main, name = blob_key.split("/")
    _, ext = os.path.splitext(name)
    return f"{main}/{ext[1:]}"


def verify_access_token(request: Request) -> str:
    """Verify the access token and return the user UID if ok."""
    if not (token := request.cookies.get(ACCESS_TOKEN_NAME)):
        raise HTTPException(
            detail="No access token was found.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if not (access_token := JWTToken.from_token(token)):
        raise HTTPException(
            detail="The access token is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return access_token.user_uid


def _format_csp_items(csp_items: dict[str, list[str]]) -> str:
    """Format the given CSP items into a string."""
    formatted_items = []
    for key, values in csp_items.items():
        value_string = " ".join([f"{value!r}" for value in values])
        formatted_items.append(f"{key} {value_string};")

    return " ".join(formatted_items)
