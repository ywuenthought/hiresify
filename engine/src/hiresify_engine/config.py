# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define the configuration of the application."""

import os
import typing as ty
from secrets import token_urlsafe

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from hiresify_engine.const import DEVELOPMENT, PRODUCTION, config_files

CONFIG_DIR = os.environ.get("CONFIG_DIR", "")

DEPLOYMENT = os.environ.get("DEPLOYMENT", DEVELOPMENT)


class AppConfig(BaseSettings):
    """The data model for the app configuration."""

    # The allowed origin for CORS.
    allowed_origin: str = ""

    # The access token TTL (sec).
    access_ttl: int = 900

    # The access key of the blob store.
    blob_access_key: str = ""

    # The secret key of the blob store.
    blob_secret_key: str = ""

    # The region name of the blob store.
    blob_store_region: str = "us-east-1"

    # The endpoint URL of the blob store.
    blob_store_url: str = ""

    # The TTL for persisting a blob file (day).
    blob_ttl: int = 30

    # The TTL for a cache entry (sec).
    cache_ttl: int = 300

    #: The database configuration.
    database_config: dict[str, ty.Any] = Field(default_factory=dict)

    # The database URL.
    database_url: str = ""

    # The heartbeat timeout (s) for streaming job progress.
    heartbeat_timeout: int = 1

    # The secret key used to encrypt and decrypt JWT tokens.
    jwt_secret_key: str = token_urlsafe(64)

    # The redis server URL.
    redis_url: str = ""

    # The refresh token TTL (day).
    refresh_ttl: int = 30

    # The returning timeout (s) for streaming job progress.
    returning_timeout: int = 1

    # The TTL for an upload of a blob file (day).
    upload_ttl: int = 7

    #: A boolean flag for whether the deployment is production.
    production: bool = DEPLOYMENT == PRODUCTION

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            CONFIG_DIR, config_files.get(DEPLOYMENT, config_files[DEVELOPMENT]),
        ),
        env_file_encoding="utf-8",
    )
