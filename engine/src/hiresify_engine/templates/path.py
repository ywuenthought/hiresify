# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the paths to the data files or directories."""

import pathlib

_TEMPLATES_PATH = pathlib.Path(__file__).parent

LOGIN_HTML_PATH = _TEMPLATES_PATH / "login.html"
