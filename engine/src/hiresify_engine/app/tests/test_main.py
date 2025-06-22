# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

from httpx import AsyncClient

#################
# user management
#################

async def test_register_user(client: AsyncClient) -> None:
    # Given
    endpoint = "/user/register"

    username = "ywu"
    password = "123"

    data = dict(username=username, password=password)

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 200

    # Given
    expected_json = dict(
        detail=f"User with username={username} conflicts with an existing entity.",
    )

    # When
    response = await client.post(endpoint, data=data)

    # Then
    assert response.status_code == 409
    assert response.json() == expected_json
