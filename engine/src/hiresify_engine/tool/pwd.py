# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the password manager."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash the given password using the preferred scheme."""
    return _hasher.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify the given password with its hashed version."""
    try:
        _hasher.verify(hashed, plain)
    except VerifyMismatchError:
        return False

    return True
