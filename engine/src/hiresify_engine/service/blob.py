# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the blob service layer for managing media files."""

import typing as ty
from contextlib import asynccontextmanager

from aioboto3 import Session
from aiobotocore.config import AioConfig
from types_aiobotocore_s3.client import S3Client

from hiresify_engine.const import BUCKET_NAME
from hiresify_engine.model import UploadPart


class BlobService:
    """A wrapper class providing APIs to manage the blob store."""

    def __init__(
        self,
        store_url: str,
        *,
        region_tag: str,
        access_key: str,
        secret_key: str,
    ) -> None:
        """Initialize a new instance of BlobService."""
        self._session = Session()

        self._store_url = store_url

        self._region_tag = region_tag
        self._access_key = access_key
        self._secret_key = secret_key

        self._client: S3Client | None = None

    @asynccontextmanager
    async def start_session(
        self, production: bool = False,
    ) -> ty.AsyncGenerator["BlobService", None]:
        """Start an AIOHTTP TCP session for managing files."""
        config = AioConfig(
            retries=dict(max_attempts=3),
            s3=dict(addressing_style="auto" if production else "path"),
            signature_version="s3v4",
        )

        async with self._session.client(
            "s3",
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            config=config,
            endpoint_url=self._store_url,
            region_name=self._region_tag,
            use_ssl=production,
        ) as client:
            self._client = client
            try:
                yield self
            finally:
                self._client = None

    async def init_bucket(self) -> None:
        """Initialize the bucket in the blob store."""
        if self._client is None:
            raise RuntimeError("S3 client has not been initialized.")

        resp = await self._client.list_buckets()
        if all(bucket["Name"] != BUCKET_NAME for bucket in resp["Buckets"]):
            await self._client.create_bucket(Bucket=BUCKET_NAME)

    async def dispose(self) -> None:
        """Dispose of resources held by the blob service."""
        if self._client is not None:
            raise RuntimeError("S3 client is still active.")

    #################
    # blob management
    #################

    async def start_upload(self, blob_key: str) -> str:
        """Start a session for a multipart upload of a file."""
        if self._client is None:
            raise RuntimeError("S3 client has not been initialized.")

        resp = await self._client.create_multipart_upload(
            Bucket=BUCKET_NAME,
            Key=blob_key,
        )

        return resp["UploadId"]

    async def upload_chunk(
        self,
        blob_key: str,
        data_chunk: bytes,
        part_index: int,
        upload_id: str,
    ) -> None:
        """Upload the given part of a media file."""
        if self._client is None:
            raise RuntimeError("S3 client has not been initialized.")

        await self._client.upload_part(
            Body=data_chunk,
            Bucket=BUCKET_NAME,
            Key=blob_key,
            PartNumber=part_index,
            UploadId=upload_id,
        )

    async def finish_upload(self, blob_key: str, upload_id: str) -> None:
        """Finish the session for a multipart upload of a file."""
        if self._client is None:
            raise RuntimeError("S3 client has not been initialized.")

        upload_parts = await self.report_parts(blob_key, upload_id)
        await self._client.complete_multipart_upload(
            Bucket=BUCKET_NAME,
            Key=blob_key,
            MultipartUpload=dict(
                Parts=[
                    dict(ETag=upload_part.etag, PartNumber=upload_part.index)
                    for upload_part
                    in upload_parts
                ],
            ),
            UploadId=upload_id,
        )

    async def cancel_upload(self, blob_key: str, upload_id: str) -> None:
        """Cancel the session for a multipart upload of a file."""
        if self._client is None:
            raise RuntimeError("S3 client has not been initialized.")

        await self._client.abort_multipart_upload(
            Bucket=BUCKET_NAME,
            Key=blob_key,
            UploadId=upload_id,
        )

    async def report_parts(self, blob_key: str, upload_id: str) -> list[UploadPart]:
        """Report the parts of a file that were already uploaded."""
        if self._client is None:
            raise RuntimeError("S3 client has not been initialized.")

        resp = await self._client.list_parts(
            Bucket=BUCKET_NAME,
            Key=blob_key,
            UploadId=upload_id,
        )

        parts = resp["Parts"]
        etags = [""] * len(parts)

        for part in parts:
            etags[part["PartNumber"] - 1] = part["ETag"]

        return [
            UploadPart(etag=etag, index=index)
            for index, etag
            in enumerate(etags, start=1)
        ]

    async def delete_blob(self, blob_key: str) -> None:
        """Delete the blob given its blob key."""
        if self._client is None:
            raise RuntimeError("S3 client has not been initialized.")

        await self._client.delete_object(Bucket=BUCKET_NAME, Key=blob_key)
