# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the types of endpoint dependencies."""

import typing as ty

from fastapi import Depends

from hiresify_engine.cache.service import CacheService
from hiresify_engine.db.repository import Repository
from hiresify_engine.tool import JWTManager, PKCEManager, PWDManager

from .getter import get_cache, get_jwt, get_pkce, get_pwd, get_repo

# The type for the cache service dependency.
CacheServiceDep = ty.Annotated[CacheService, Depends(get_cache)]

# The type for the JWT access token manager dependency.
JWTManagerDep = ty.Annotated[JWTManager, Depends(get_jwt)]

# The type for the PKCE code manager dependency.
PKCEManagerDep = ty.Annotated[PKCEManager, Depends(get_pkce)]

# The type for the user password manager dependency.
PWDManagerDep = ty.Annotated[PWDManager, Depends(get_pwd)]

# The type for the database repository dependency.
RepositoryDep = ty.Annotated[Repository, Depends(get_repo)]
