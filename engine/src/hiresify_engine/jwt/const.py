# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the constants used by JWT service."""

import typing as ty

TokenName = ty.Literal["access_token", "refresh_token"]

ACCESS_TOKEN: TokenName = "access_token"

REFRESH_TOKEN: TokenName = "refresh_token"
