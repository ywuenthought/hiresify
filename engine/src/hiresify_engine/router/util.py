# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Provide utility functions used in the endpoints."""

import base64
import hashlib

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt", "argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash the given password using the bcrypt scheme."""
    return pwd_context.hash(password)


def is_pkce_valid(verifier: str, challenge: str, *, method: str) -> bool:
    """Match the code_verifier with the code_challenge via the given PKCE method."""
    if method != "s256":
        raise NotImplementedError(f"The PKCE method {method} is not implemented.")

    hashed = hashlib.sha256(verifier.encode()).digest()
    result = base64.urlsafe_b64encode(hashed).rstrip(b"=").decode()
    return result == challenge


def verify_password(plain: str, hashed: str) -> bool:
    """Verify the given password with its hashed version."""
    return pwd_context.verify(plain, hashed)
