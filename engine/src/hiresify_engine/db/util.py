# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""
Provide utility functions used by the repository layer.
"""


def abbreviate_token(token: str, cutoff: int = 6) -> str:
    """
    Abbreviate the given token to make it partially visible.
    """
    if not token:
        return "<empty>"

    return f"{token[:cutoff]}***"
