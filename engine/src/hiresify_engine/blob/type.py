# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the types used by the blob service layer."""

import typing as ty

Uploader = ty.Callable[[bytes], ty.Awaitable[None]]
