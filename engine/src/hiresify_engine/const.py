# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the constants shared among modules."""

import pathlib

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
