# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide utility functions used across the routers."""

from fastapi import HTTPException, Request, Response, status

from hiresify_engine.envvar import PRODUCTION
from hiresify_engine.jwt.service import JWTTokenService

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


def verify_access_token(request: Request, jwt: JWTTokenService) -> str:
    """Verify the access token and return the user UID if ok."""
    if not (access_token := request.cookies.get("access_token")):
        raise HTTPException(
            detail="No access token was found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if not (user_uid := jwt.verify(access_token)):
        raise HTTPException(
            detail="The access token is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return user_uid


def _format_csp_items(csp_items: dict[str, list[str]]) -> str:
    """Format the given CSP items into a string."""
    formatted_items = []
    for key, values in csp_items.items():
        value_string = " ".join([f"{value!r}" for value in values])
        formatted_items.append(f"{key} {value_string};")

    return " ".join(formatted_items)
