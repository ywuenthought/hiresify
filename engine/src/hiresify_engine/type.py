# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""
Defines custom types used across modules.
"""

import os

# A type for file paths
FilePath = str | os.PathLike
