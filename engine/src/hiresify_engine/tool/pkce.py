# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the PKCE code manager for user authentication."""

import base64
import hashlib


class PKCECodeManager:
    """A wrapper class for managing PKCE codes."""

    def __init__(self) -> None:
        """Initialize a new instance of PKCECodeManager."""
        self._methods = {"s256": self._compute_challenge_s256}

    def compute(self, verifier: str, method: str) -> str:
        """Compute the code challenge using the given method."""
        if compute_func := self._methods.get(method):
            return compute_func(verifier)

        return verifier

    def verify(self, verifier: str, challenge: str, method: str) -> bool:
        """Verify that the verifier matches the challenge."""
        return self.compute(verifier, method) == challenge

    @staticmethod
    def _compute_challenge_s256(verifier: str) -> str:
        """Compute the code challenge given the code verifier via s256."""
        hashed = hashlib.sha256(verifier.encode()).digest()
        challenge = base64.urlsafe_b64encode(hashed).rstrip(b"=").decode()
        return challenge
