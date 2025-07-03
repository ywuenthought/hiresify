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

# The TTL for a cache entry (sec).
CACHE_TTL = "CACHE_TTL"

# The database URL.
DATABASE_URL = "DATABASE_URL"

# The database config file.
DATABASE_CONFIG = "DATABASE_CONFIG"

# The current deployment type.
DEPLOYMENT = "DEPLOYMENT"

# The redis server URL.
REDIS_URL = "REDIS_URL"

# The refresh token TTL (day).
REFRESH_TTL = "REFRESH_TTL"

################
# dir/file paths
################

PACKAGE_ROOT = pathlib.Path(__file__).parent

STATIC_DIR = PACKAGE_ROOT / "static"

##############
# regular exps
##############

USERNAME_REGEX = r"^[a-zA-Z][a-zA-Z0-9_]*$"

PASSWORD_REGEX = r"^[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$"

##################
# deployment types
##################

DEVELOPMENT = "development"

PRODUCTION = "production"
