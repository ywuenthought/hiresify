# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""
Exports the repository layer around the database.
"""

import json
import typing as ty

from sqlalchemy.ext.asyncio import create_async_engine

from hiresify_engine.type import FilePath


class Repository:
    """
    A wrapper class providing APIs to manage the database.
    """

    def __init__(self, url: str, **configs: dict[str, ty.Any]) -> None:
        self._engine = create_async_engine(url, **configs)

    @classmethod
    def from_config_file(cls, url: str, *, config_file: FilePath) -> "Repository":
        """
        Create a Repository instance from a JSON configuration file. 
        """
        with open(config_file) as fp:
            configs = json.load(fp)

        return cls(url, **configs)
