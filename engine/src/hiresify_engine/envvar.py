# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Read and export environment variables."""

from .util import get_envvar

#############
# envvar keys
#############

# The access token TTL (sec).
ACCESS_TTL = get_envvar("ACCESS_TTL", int, 900)

# The TTL for a cache entry (sec).
CACHE_TTL = get_envvar("CACHE_TTL", int, 300)

# The database URL.
DATABASE_URL = get_envvar("DATABASE_URL", str, "")

# The database config file.
DATABASE_CONFIG = get_envvar("DATABASE_CONFIG", str, "")

# The current deployment type.
PRODUCTION = get_envvar("PRODUCTION", bool, False)

# The redis server URL.
REDIS_URL = get_envvar("REDIS_URL", str, "")

# The refresh token TTL (day).
REFRESH_TTL = get_envvar("REFRESH_TTL", int, 30)
