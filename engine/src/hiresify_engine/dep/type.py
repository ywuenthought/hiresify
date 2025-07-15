# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the types of endpoint dependencies."""

import typing as ty

from fastapi import Depends

from hiresify_engine.blob.service import BlobService
from hiresify_engine.cache.service import CacheService
from hiresify_engine.db.repository import Repository

from .getter import get_cache, get_repo

# The type for the blob service dependency.
BlobServiceDep = ty.Annotated[BlobService, Depends(get_cache)]

# The type for the cache service dependency.
CacheServiceDep = ty.Annotated[CacheService, Depends(get_cache)]

# The type for the database repository dependency.
RepositoryDep = ty.Annotated[Repository, Depends(get_repo)]
