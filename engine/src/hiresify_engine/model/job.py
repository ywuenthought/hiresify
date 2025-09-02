# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the domain model for a compute job."""

import typing as ty
from datetime import datetime

from pydantic.dataclasses import dataclass

from hiresify_engine.util import check_tz

from .config import DEFAULT_CONFIG

JobStatus = ty.Literal["canceled", "crashed", "finished", "pending", "started"]


@dataclass(frozen=True, config=DEFAULT_CONFIG)
class ComputeJob:
    """Wrap user-facing fields and methods for a compute job."""

    #: The UID of this job.
    uid: str

    #: The UID of the blob that's worked on.
    blob_uid: str

    #: The current status of this job.
    status: JobStatus

    #: The date and time when the job was requested.
    requested_at: datetime

    #: The date and time when the job was completed.
    # This does not mean that the job was finished successfully.
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        """Perform post init checks."""
        check_tz(self.requested_at)
