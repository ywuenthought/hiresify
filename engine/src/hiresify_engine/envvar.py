# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Read and export environment variables."""

from .util import get_envvar

# The access token TTL (sec).
ACCESS_TTL = get_envvar("ACCESS_TTL", int, 900)

# The access key of the blob store.
BLOB_ACCESS_KEY = get_envvar("BLOB_ACCESS_KEY", str, "")

# The secret key of the blob store.
BLOB_SECRET_KEY = get_envvar("BLOB_ACCESS_KEY", str, "")

# The region name of the blob store.
BLOB_STORE_REGION = get_envvar("BLOB_ACCESS_KEY", str, "")

# The endpoint URL of the blob store.
BLOB_STORE_URL = get_envvar("BLOB_ACCESS_KEY", str, "")

# The name of the bucket for blob storage.
BUCKET_NAME = get_envvar("BUCKET_NAME", str, "hiresify")

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
