# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from uuid import uuid4

from ..service import JWTTokenService


def test_round_trip(service: JWTTokenService) -> None:
    # Given
    user_uid = uuid4().hex

    # When
    token = service.generate(user_uid)

    # Then
    assert len(token.token) == 160

    # When
    sub = service.verify(token.token)

    # Then
    assert sub == user_uid
