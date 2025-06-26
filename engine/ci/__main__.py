# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import subprocess

import click
from click.exceptions import ClickException

from .const import DOCKER_COMPOSE, DOCKER_FILE, PROJECT_ROOT


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
        f"hiresify:{tag}",
        str(PROJECT_ROOT),
    ]
    if subprocess.run(cmd, check=False).returncode:
        raise ClickException("Failed to build the Docker image.")


@docker.group()
def stack() -> None:
    """Manage container stack-related CI tasks."""


@stack.command("up")
@click.option(
    "-t",
    "--tag",
    default="latest",
    envvar="TAG",
)
def stack_up(tag: str) -> None:
    """Launch the development container stack."""
    cmd = [
        "docker",
        "compose",
        "-f",
        str(DOCKER_COMPOSE),
        "-p",
        "hiresify",
        "up",
        "-d",
    ]
    if subprocess.run(cmd, check=False, env=dict(TAG=tag)).returncode:
        raise ClickException("Failed to launch the container stack.")


@stack.command("down")
@click.option(
    "-t",
    "--tag",
    default="latest",
    envvar="TAG",
)
def stack_down(tag: str) -> None:
    """Stop the development container stack."""
    cmd = [
        "docker",
        "compose",
        "-f",
        str(DOCKER_COMPOSE),
        "-p",
        "hiresify",
        "down",
        "--remove-orphans",
        "--volumes",
    ]
    if subprocess.run(cmd, check=False, env=dict(TAG=tag)).returncode:
        raise ClickException("Failed to stop the container stack.")


if __name__ == "__main__":
    cli()
