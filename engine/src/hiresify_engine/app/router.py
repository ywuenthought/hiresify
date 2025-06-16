# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the backend endpoints."""

from fastapi import APIRouter, HTTPException, status

from hiresify_engine.db.exception import EntityConflictError

from .dependency import RepositoryDep
from .schema import UserAuthSchema
from .util import hash_password

router = APIRouter()


@router.post("/user")
async def register_user(user: UserAuthSchema, repository: RepositoryDep):
    """Register a user using the given user name."""
    hashed_password = hash_password(user.password)

    try:
        await repository.register_user(user.username, hashed_password)
    except EntityConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT) from e
