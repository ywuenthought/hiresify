# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the domain model for blob management."""

from datetime import UTC, datetime

from pydantic.dataclasses import dataclass

from hiresify_engine.util import check_tz


@dataclass(frozen=True)
class Blob:
    """Wrap user-facing fields and methods for a blob."""

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

    def __post_init__(self) -> None:
        """Perform post init checks."""
        check_tz(self.created_at)
        check_tz(self.valid_thru)

    def is_valid(self) -> bool:
        """Check if this blob is still valid or expired."""
        return self.valid_thru > datetime.now(UTC)
