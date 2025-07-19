# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the domain models used on the backend."""

from datetime import datetime

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Blob:
    """The domain model for a persisted blob file."""

    #: The UID of this blob.
    uid: str

    #: The name of this blob file.
    file_name: str

    #: The MIME type of this blob file.
    mime_type: str

    #: The date and time when the blob was created.
    created_at: datetime

    #: The date and time when the blob is valid through.
    valid_thru: datetime
