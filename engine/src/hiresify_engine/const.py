# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the constants shared among modules."""

import pathlib

ACCESS_TOKEN_NAME = "hiresify-access"

BUCKET_NAME = "hiresify-bucket"

DEVELOPMENT = "development"

PACKAGE_ROOT = pathlib.Path(__file__).parent

PASSWORD_REGEX = r"^[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$"

PRODUCTION = "production"

REFRESH_TOKEN_NAME = "hiresify-refresh"

SESSION_NAME = "hiresify-session"

STATIC_DIR = PACKAGE_ROOT / "static"

TESTING = "testing"

TOKEN_ALGORITHM = "HS256"

TOKEN_AUDIENCE = "hiresify-app"

TOKEN_ISSUER = "hiresify-auth"

USERNAME_REGEX = r"^[a-zA-Z][a-zA-Z0-9_]*$"

config_files = {
    deployment: PACKAGE_ROOT / f".env.{deployment}"
    for deployment in (DEVELOPMENT, PRODUCTION, TESTING)
}
