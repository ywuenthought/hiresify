# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define custom database exceptions."""

import typing as ty


class EntityNotFoundError(Exception):
    """Raised when a database entity was not found."""

    def __init__(self, klass: type, **identifiers: ty.Any) -> None:
        """Initialize a new instance of EntityNotFoundError."""
        super().__init__(
            f"{klass.__name__} with "
            f"{' '.join(f'{key}={value}' for key, value in identifiers.items())} "
            "was not found.",
        )


class EntityConflictError(Exception):
    """Raised for a conflict with an existing database entity."""

    def __init__(self, klass: type, **identifiers: ty.Any) -> None:
        """Initialize a new instance of EntityConflictError."""
        super().__init__(
            f"{klass.__name__} with "
            f"{' '.join(f'{key}={value}' for key, value in identifiers.items())} "
            "conflicts with an existing entity.",
        )


class UploadConflictError(Exception):
    """Raised when starting an upload of a blob that's already being uploaded."""

    def __init__(self, blob_uid: str) -> None:
        """Initialize a new instance of UploadConflictError."""
        super().__init__(f"There is an existing upload for {blob_uid=}.")


class UploadNotFoundError(Exception):
    """Raised when aborting or finishing a nonexisting blob upload."""

    def __init__(self, blob_uid: str) -> None:
        """Initialize a new instance of UploadNotFoundError."""
        super().__init__(f"There is no upload for {blob_uid=}.")
