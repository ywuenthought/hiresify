# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the PKCE tool functions."""

import base64
import hashlib


def compute_challenge(verifier: str, method: str) -> str:
    """Compute the code challenge using the preferred method."""
    if method == "s256":
        return _compute_challenge_s256(verifier)

    return verifier


def confirm_verifier(verifier: str, challenge: str, method: str) -> bool:
    """Confirm that the verifier matches the challenge."""
    return compute_challenge(verifier, method) == challenge


def _compute_challenge_s256(verifier: str) -> str:
    """Compute the code challenge given the code verifier via s256."""
    hashed = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(hashed).rstrip(b"=").decode()
    return challenge
