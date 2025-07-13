# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the data models used by the blob service."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MultipartUploadPart:
    """Wrap the metadata of a file's part in a multipart upload."""

    #: The E-Tag of this file part.
    etag: str

    #: The index of ordering among all the parts.
    index: int
