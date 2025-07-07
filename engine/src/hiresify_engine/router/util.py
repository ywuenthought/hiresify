# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide utility functions used across the routers."""

import typing as ty

from fastapi import Response

from hiresify_engine.const import DEVELOPMENT, PRODUCTION

# Argument `deployment` will be auto-filled on the app level.
AddSecureHeaders = ty.Callable[..., None]


def add_secure_headers(
    response: Response,
    *,
    nonces: list[str] | None = None,
    deployment: str = DEVELOPMENT,
) -> None:
    """Add secure headers to the given response."""
    script_srcs = ["self"] if nonces is None else [f"nonce-{nonce}" for nonce in nonces]
    script_srcs = [f"{src!r}" for src in script_srcs]

    response.headers.update(
        {
            # Prevent loading any external resources.
            "Content-Security-Policy": (
                "default-src 'none'; " +
                "img-src 'self'; " +
                f"script-src {' '.join(script_srcs)}; " +
                "style-src 'self';"
            ),

            # Disable access to sensitive APIs.
            "Permissions-Policy": (
                "geolocation=(), " +
                "camera=()"
            ),

            # Prevent leaking the referrer URL.
            "Referrer-Policy": "no-referrer",

            # Disallow MIME-sniff the response content.
            "X-Content-Type-Options": "nosniff",

            # Prevent the page from being embedded in frames.
            "X-Frame-Options": "DENY",
        },
    )

    if deployment == PRODUCTION:
        # Force browsers to use HTTPS for all future requests.
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; " +
            "includeSubDomains; " +
            "preload"
        )
