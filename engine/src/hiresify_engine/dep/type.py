# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the types of endpoint dependencies."""

import typing as ty

from fastapi import Depends

from hiresify_engine.config import AppConfig
from hiresify_engine.db.repository import Repository
from hiresify_engine.service import BlobService, CacheService, QueueService

from .getter import get_blob, get_cache, get_config, get_queue, get_repo

# The type for the app configuration dependency.
AppConfigDep = ty.Annotated[AppConfig, Depends(get_config)]

# The type for the blob service dependency.
BlobServiceDep = ty.Annotated[BlobService, Depends(get_blob)]

# The type for the job queue service dependency.
QueueServiceDep = ty.Annotated[QueueService, Depends(get_queue)]

# The type for the cache service dependency.
CacheServiceDep = ty.Annotated[CacheService, Depends(get_cache)]

# The type for the database repository dependency.
RepositoryDep = ty.Annotated[Repository, Depends(get_repo)]
