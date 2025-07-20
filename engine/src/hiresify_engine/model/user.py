# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the domain model for user management."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Wrap user-facing fields and methods for a user."""

    #: The UID of this user.
    uid: str

    #: The username of this user.
    username: str

    #: The hashed password of this user.
    password: str
