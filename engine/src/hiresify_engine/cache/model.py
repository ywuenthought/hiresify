# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the data models used by cache store."""

import json
from dataclasses import asdict, dataclass, field
from uuid import uuid4


@dataclass(frozen=True)
class Authorization:
    """The data model for an authorization."""

    #: The ID of the client to be authorized.
    client_id: str

    #: The code challenge sent by the client.
    code_challenge: str

    #: The method to be used against the code challenge.
    code_challenge_method: str

    #: The redirect URI.
    redirect_uri: str

    #: The UID of the user that granted the authorization.
    user_uid: str

    #: The authorization code that defaults to a random UUID.
    code: str = field(default_factory=lambda: uuid4().hex)

    @classmethod
    def from_serialized(cls, serialized: str) -> "Authorization":
        """Instantiate this class using the given serialized data."""
        raw = json.loads(serialized)
        return cls(**raw)

    def serialize(self) -> str:
        """Serialize this object into a string."""
        return json.dumps(asdict(self))
