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
# user regex
############

USERNAME_REGEX = r"^[a-zA-Z][a-zA-Z0-9_]*$"

PASSWORD_REGEX = r"^[A-Za-z\d!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]+$"

############
# JWT tokens
############

ACCESS_TOKEN_NAME = "hiresify-access"

REFRESH_TOKEN_NAME = "hiresify-refresh"

TOKEN_ALGORITHM = "HS256"

TOKEN_AUDIENCE = "hiresify-app"

TOKEN_ISSUER = "hiresify-oauth2"
