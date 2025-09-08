# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the compute callbacks used by compute workers."""

from pathlib import Path


async def callback(file_path: Path) -> Path:
    """Mock a real compute callback."""
    return file_path
