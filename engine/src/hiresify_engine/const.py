# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the constants shared among modules."""

import pathlib

############
# file paths
############

PACKAGE_ROOT = pathlib.Path(__file__).parent

STATIC_DIR = PACKAGE_ROOT / "static"

############
# deployment
############

DEVELOPMENT = "development"

PRODUCTION = "production"

TESTING = "testing"

config_files = {
    deployment: PACKAGE_ROOT / f".env.{deployment}"
    for deployment in (DEVELOPMENT, PRODUCTION, TESTING)
}

############
# user regex
############

USERNAME_REGEX = r"^[a-zA-Z][a-zA-Z0-9_]*$"

PASSWORD_REGEX = r"^[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$"

############
# JWT tokens
############

TOKEN_ALGORITHM = "HS256"

TOKEN_AUDIENCE = "hiresify-app"

TOKEN_ISSUER = "hiresify-auth"

#############
# cookie keys
#############

ACCESS_TOKEN_NAME = "hiresify-access"

REFRESH_TOKEN_NAME = "hiresify-refresh"

SESSION_NAME = "hiresify-session"

############
# blob store
############

BUCKET_NAME = "hiresify-bucket"
