# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import shutil
import subprocess

import click
from click.exceptions import ClickException

from .const import DEV_DOCKER_COMPOSE, DOCKER_FILE, PROJECT_ROOT, REQUIREMENTS_FILE


@click.group()
def cli() -> None:
    """Manage CI tasks for this project."""


@cli.command("build")
def build_wheel() -> None:
    """Build the wheel of this project."""
    if (build_dir := PROJECT_ROOT / "build").is_dir():
        shutil.rmtree(build_dir)

    cmd = ["uv", "build", ".", "-o", "build", "--wheel"]
    if subprocess.run(cmd, check=False, cwd=PROJECT_ROOT).returncode:
        raise ClickException("Failed to build the wheel.")


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
        "uv",
        "export",
        "--frozen",
        "--quiet",
        "-o",
        str(REQUIREMENTS_FILE),
        "--no-emit-project",
    ]
    if subprocess.run(cmd, check=False, cwd=PROJECT_ROOT).returncode:
        raise ClickException("Failed to export requirements.txt.")

    cmd = [
        "docker",
        "build",
        "-f",
        str(DOCKER_FILE),
        "-t",
        f"hiresify:{tag}",
        ".",
    ]
    if subprocess.run(cmd, check=False, cwd=PROJECT_ROOT).returncode:
        raise ClickException("Failed to build the Docker image.")


@docker.command()
@click.option(
    "-t",
    "--tag",
    default="latest",
    envvar="TAG",
)
def push(tag: str) -> None:
    """Push the Docker image of this project."""
    image = f"hiresify:{tag}"
    target_image = f"ywucontainer/{image}"
    cmd = f"docker tag {image} {target_image} && docker push {target_image}"

    if subprocess.run(
        cmd,
        check=False,
        shell=True,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    ).returncode:
        raise ClickException("Failed to push the app image.")


@docker.group()
@click.pass_context
def stack(ctx: click.Context) -> None:
    """Manage development container stack-related CI tasks."""
    ctx.ensure_object(dict)
    ctx.obj["compose_file"] = DEV_DOCKER_COMPOSE
    ctx.obj["project_name"] = "hiresify_dev"


@stack.command("up")
@click.option(
    "-t",
    "--tag",
    default="latest",
    envvar="TAG",
)
@click.pass_context
def stack_up(ctx: click.Context, tag: str) -> None:
    """Launch the development container stack."""
    cmd = [
        "docker",
        "compose",
        "-f",
        str(ctx.obj["compose_file"]),
        "-p",
        ctx.obj["project_name"],
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
@click.pass_context
def stack_down(ctx: click.Context, tag: str) -> None:
    """Stop the development container stack."""
    cmd = [
        "docker",
        "compose",
        "-f",
        str(ctx.obj["compose_file"]),
        "-p",
        ctx.obj["project_name"],
        "down",
        "--remove-orphans",
        "--volumes",
    ]
    if subprocess.run(cmd, check=False, env=dict(TAG=tag)).returncode:
        raise ClickException("Failed to stop the container stack.")


if __name__ == "__main__":
    cli()
