# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the password manager for user authentication."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class PasswordManager:
    """A wrapper class for managing user passwords."""

    def __init__(self) -> None:
        """Initialize a new instance of PasswordManager."""
        self._hasher = PasswordHasher()

    def hash(self, password: str) -> str:
        """Hash the given password using the current preferred scheme."""
        return self._hasher.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        """Verify the given password with its hashed version."""
        try:
            self._hasher.verify(hashed, plain)
        except VerifyMismatchError:
            return False

        return True
