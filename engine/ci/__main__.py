# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import subprocess

import click
from click.exceptions import ClickException

from .const import DOCKER_FILE, PROJECT_ROOT


@click.group()
def cli() -> None:
    """Manage CI tasks for this project."""


@cli.group()
def docker() -> None:
    """Manage Docker-related CI tasks."""


@docker.command()
@click.option(
    "-t",
    "--tag",
    default="latest",
    envvar="TAG",
)
def build(tag: str) -> None:
    """Build the Docker image of this project."""
    cmd = [
        "docker",
        "build",
        "-f",
        str(DOCKER_FILE),
        "-t",
        tag,
        str(PROJECT_ROOT),
    ]
    if subprocess.run(cmd, check=False).returncode:
        raise ClickException("Failed to build the Docker image.")


if __name__ == "__main__":
    cli()
