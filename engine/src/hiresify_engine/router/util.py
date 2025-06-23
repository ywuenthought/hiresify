# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide utility functions used in the endpoints."""

import base64
import hashlib


def compute_challenge_s256(verifier: str) -> str:
    """Compute the code challenge given the code verifier via s256."""
    hashed = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(hashed).rstrip(b"=").decode()
    return challenge


def is_pkce_valid(verifier: str, challenge: str, *, method: str | None = None) -> bool:
    """Match the code_verifier with the code_challenge via the given PKCE method."""
    result = verifier

    if method == "s256":
        result = compute_challenge_s256(verifier)

    return result == challenge
