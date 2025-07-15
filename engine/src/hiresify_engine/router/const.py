# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the constants used across backend endpoints."""

from fastapi.templating import Jinja2Templates

from hiresify_engine.jwt.service import JWTTokenService
from hiresify_engine.templates import LOGIN_HTML

jwt = JWTTokenService()

templates = Jinja2Templates(directory=LOGIN_HTML.parent)
