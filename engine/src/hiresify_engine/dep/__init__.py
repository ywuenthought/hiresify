# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the reusable dependency types for FastAPI endpoints."""

from .type import BlobServiceDep, CacheServiceDep, RepositoryDep

__all__ = ["BlobServiceDep", "CacheServiceDep", "RepositoryDep"]
