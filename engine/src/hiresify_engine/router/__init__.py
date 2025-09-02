# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from .blob import router as blob_router
from .job import router as job_router
from .token import router as token_router
from .user import router as user_router

routers = [
    token_router,
    user_router,
]

api_routers = [
    blob_router,
    job_router,
]
