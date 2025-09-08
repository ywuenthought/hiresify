# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the compute callbacks used by compute workers."""

import shutil
import typing as ty
from pathlib import Path


async def callback(
    input_path: Path, output_path: Path,
) -> ty.AsyncGenerator[float, None]:
    """Mock a real compute callback.

    A callback should return a generator of the current progress of this compute job.
    """
    for progress_percent in range(0, 101):
        yield progress_percent / 100

    output_path.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(input_path, output_path)
