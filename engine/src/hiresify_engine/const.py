# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the constants shared among modules."""

import pathlib

#############
# envvar keys
#############

# The access token TTL (sec).
ACCESS_TTL = "ACCESS_TTL"

# The database URL.
DATABASE_URL = "DATABASE_URL"

# The database config file.
DATABASE_CONFIG = "DATABASE_CONFIG"

# The long TTL for a cache entry (sec).
LONG_CACHE_TTL = "LONG_CACHE_TTL"

# The redis server URL.
REDIS_URL = "REDIS_URL"

# The refresh token TTL (day).
REFRESH_TTL = "REFRESH_TTL"

# The short TTL for a cache entry (sec).
SHORT_CACHE_TTL = "SHORT_CACHE_TTL"

################
# dir/file paths
################

PACKAGE_ROOT = pathlib.Path(__file__).parent

STATIC_DIR = PACKAGE_ROOT / "static"
