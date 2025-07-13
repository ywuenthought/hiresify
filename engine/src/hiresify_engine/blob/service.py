# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Export the blob service layer for managing media files."""

import typing as ty
from contextlib import asynccontextmanager
from itertools import count

from aioboto3 import Session
from aiobotocore.config import AioConfig
from botocore.exceptions import BotoCoreError, ClientError
from types_aiobotocore_s3.client import S3Client

from hiresify_engine.envvar import (
    BLOB_ACCESS_KEY,
    BLOB_SECRET_KEY,
    BLOB_STORE_REGION,
    BLOB_STORE_URL,
    BUCKET_NAME,
    PRODUCTION,
)

from .type import Uploader


class BlobService:
    """A wrapper class providing APIs to manage the blob store."""

    def __init__(self) -> None:
        """Initialize a new instance of BlobService."""
        self._session = Session()
        self._config = AioConfig(
            retries=dict(max_attempts=3),
            s3=dict(addressing_style="auto" if PRODUCTION else "path"),
            signature_version="s3v4",
        )

    async def init_bucket(self) -> None:
        """Initialize the bucket in the blob store."""
        async with self._create_client() as client:
            resp = await client.list_buckets()
            if all(bucket["Name"] != BUCKET_NAME for bucket in resp["Buckets"]):
                await client.create_bucket(Bucket=BUCKET_NAME)

    async def dispose(self) -> None:
        """Dispose of resources held by the blob service."""

    @asynccontextmanager
    async def upload_by_parts(self, blob_key: str) -> ty.AsyncGenerator[Uploader, None]:
        """Upload a media (image or video) file to the blob store by parts."""
        parts: list[tuple[int, str]] = []
        index = count(1)
        upload_id = None

        async with self._create_client() as client:
            try:
                resp = await client.create_multipart_upload(
                    Bucket=BUCKET_NAME,
                    Key=blob_key,
                )
                upload_id = resp["UploadId"]

                async def uploader(body: bytes) -> None:
                    part_index = next(index)
                    resp = await client.upload_part(
                        Body=body,
                        Bucket=BUCKET_NAME,
                        Key=blob_key,
                        PartNumber=part_index,
                        UploadId=upload_id,
                    )
                    parts.append((part_index, resp["ETag"]))

                yield uploader

                parts.sort(key=lambda part: part[0])
                await client.complete_multipart_upload(
                    Bucket=BUCKET_NAME,
                    Key=blob_key,
                    MultipartUpload=dict(
                        Parts=[
                            dict(ETag=etag, PartNumber=part_index)
                            for part_index, etag
                            in parts
                        ],
                    ),
                    UploadId=upload_id,
                )

            except (BotoCoreError, ClientError) as upload_error:
                msg = f"The upload of media file {blob_key} failed."

                if upload_id:
                    try:
                        await client.abort_multipart_upload(
                            Bucket=BUCKET_NAME,
                            Key=blob_key,
                            UploadId=upload_id,
                        )
                    except (BotoCoreError, ClientError) as abort_error:
                        raise ExceptionGroup(
                            f"{msg} Aborting it also failed.",
                            [upload_error, abort_error],
                        ) from None

                raise RuntimeError(msg) from upload_error

    def _create_client(self) -> ty.AsyncContextManager[S3Client]:
        """Create an instance of S3 client as an async context manager."""
        return self._session.client(
            "s3",
            aws_access_key_id=BLOB_ACCESS_KEY,
            aws_secret_access_key=BLOB_SECRET_KEY,
            config=self._config,
            endpoint_url=BLOB_STORE_URL,
            region_name=BLOB_STORE_REGION,
            use_ssl=PRODUCTION,
        )
