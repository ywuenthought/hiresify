# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the constants shared among modules."""

#############
# envvar keys
#############

# The access token TTL (sec).
ACCESS_TTL = "ACCESS_TTL"

# The database URL.
DATABASE_URL = "DATABASE_URL"

# The deployment type.
DEPLOYMENT = "DEPLOYMENT"

# The redis server host.
REDIS_HOST = "REDIS_HOST"

# The redis server port.
REDIS_PORT = "REDIS_PORT"

# The refresh token TTL (day).
REFRESH_TTL = "REFRESH_TTL"

# The regular cache entry TTL (sec).
REGULAR_TTL = "REGULAR_TTL"

# The HTTP session TTL (sec).
SESSION_TTL = "SESSION_TTL"

#############
# deployments
#############

TESTING = "testing"

DEVELOPMENT = "development"

PRODUCTION = "production"
