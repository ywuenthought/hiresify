# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

# ruff: noqa: N803

"""Export a testing version of the blob service."""

import typing as ty
from contextlib import asynccontextmanager
from dataclasses import dataclass, field, replace
from uuid import uuid4

from hiresify_engine.service.blob import BlobService


@dataclass(frozen=True)
class _Store:

    buckets: dict[str, "_Bucket"] = field(default_factory=dict)


@dataclass(frozen=True)
class _Bucket:

    name: str

    blobs: dict[str, "_Blob"] = field(default_factory=dict)


@dataclass(frozen=True)
class _Blob:

    key: str

    deleted: bool = False

    uploads: dict[str, "_MultipartUpload"] = field(default_factory=dict)


@dataclass(frozen=True)
class _MultipartUpload:

    next_index: int = 1

    finished: bool = False

    aborted: bool = False

    id: str = field(default_factory=lambda: uuid4().hex)


class MockBlobStore:
    """A mock blob store that lives in memory."""

    def __init__(self) -> None:
        """Initialize a new instance of this class."""
        self._store = _Store()

    async def abort_multipart_upload(
        self, Bucket: str, Key: str, UploadId: str,
    ) -> None:
        """Abort a multipart upload of a blob file."""
        uploads = self._store.buckets[Bucket].blobs[Key].uploads
        uploads[UploadId] = replace(uploads[UploadId], aborted=True)

    async def complete_multipart_upload(
        self,
        Bucket: str,
        Key: str,
        MultipartUpload: dict[str, ty.Any],
        UploadId: str,
    ) -> None:
        """Complete a multipart upload of a blob file."""
        uploads = self._store.buckets[Bucket].blobs[Key].uploads
        uploads[UploadId] = replace(uploads[UploadId], finished=True)

    async def create_bucket(self, Bucket: str) -> None:
        """Create a bucket with the given bucket name."""
        self._store.buckets[Bucket] = _Bucket(name=Bucket)

    async def create_multipart_upload(self, Bucket: str, Key: str) -> dict[str, ty.Any]:
        """Initiate a multipart upload of a blob file."""
        blob = _Blob(key=Key)
        self._store.buckets[Bucket].blobs[Key] = blob

        upload = _MultipartUpload()
        blob.uploads[upload.id] = upload

        return dict(UploadId=upload.id)

    async def list_buckets(self) -> dict[str, ty.Any]:
        """List all the existing buckets."""
        return dict(Buckets=[dict(Name=name) for name in self._store.buckets])

    async def list_parts(
        self, Bucket: str, Key: str, UploadId: str,
    ) -> dict[str, ty.Any]:
        """List all the parts of a blob file that were already uploaded."""
        upload = self._store.buckets[Bucket].blobs[Key].uploads[UploadId]

        if upload.finished or upload.aborted:
            raise Exception(f"{UploadId=} does not exist.")

        return dict(
            Parts=[
                dict(ETag=uuid4().hex, PartNumber=index)
                for index
                in range(1, upload.next_index)
            ],
        )

    async def upload_part(
        self,
        Body: bytes,
        Bucket: str,
        Key: str,
        PartNumber: int,
        UploadId: str,
    ) -> None:
        """Upload an individual part of a blob file."""
        uploads = self._store.buckets[Bucket].blobs[Key].uploads
        uploads[UploadId] = replace(uploads[UploadId], next_index=PartNumber + 1)

    async def delete_object(self, Bucket: str, Key: str) -> None:
        """Delete the blob specified by the given bucket and blob key."""
        blobs = self._store.buckets[Bucket].blobs
        blobs[Key] = replace(blobs[Key], deleted=True)


class TestBlobService(BlobService):
    """A test blob service that uses a mock blob store."""

    def __init__(self) -> None:
        """Initialize a new instance of this class."""
        self._client = MockBlobStore()  # type: ignore[assignment]

    @asynccontextmanager
    async def start_session(
        self, production: bool = False,
    ) -> ty.AsyncGenerator["TestBlobService", None]:
        """Start a session for managing files."""
        try:
            yield self
        finally:
            pass
