# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide utility functions used across the routers."""

from fastapi import HTTPException, status

from hiresify_engine.model import JWTToken


def verify_token(
    cookies: dict[str, str], *, token_name: str, secret_key: str,
) -> JWTToken:
    """Verify the specified token received from the request."""
    if not (token := cookies.get(token_name)):
        raise HTTPException(
            detail=f"No {token_name} token was found.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if not (jwt_token := JWTToken.from_token(token, secret_key=secret_key)):
        raise HTTPException(
            detail=f"{token_name} token is invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return jwt_token
