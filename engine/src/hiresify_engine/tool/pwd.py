# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the password manager for user authentication."""

from passlib.context import CryptContext


class PasswordManager:
    """A wrapper class for managing user passwords."""

    def __init__(self, *schemes: str) -> None:
        """Initialize a new instance of PasswordManager."""
        schemes = schemes if schemes else ("bcrypt", "argon2")
        self._context = CryptContext(schemes=schemes, deprecated="auto")

    def hash(self, password: str) -> str:
        """Hash the given password using the current preferred scheme."""
        return self._context.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        """Verify the given password with its hashed version."""
        return self._context.verify(plain, hashed)
