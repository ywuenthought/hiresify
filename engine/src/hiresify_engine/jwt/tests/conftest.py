# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import typing as ty

import pytest

from ..service import JWTTokenService


@pytest.fixture(scope="session", autouse=True)
def service() -> ty.Generator[JWTTokenService, None, None]:
    """Create an instance of JWTTokenService used in tests."""
    yield JWTTokenService()
