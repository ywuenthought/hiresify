# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import shutil
import subprocess

import click
from click.exceptions import ClickException

from .const import (
    DEV_DOCKER_COMPOSE,
    DOCKER_FILE,
    DOCKER_REGISTRY,
    PROJECT_ROOT,
    REQUIREMENTS_FILE,
)


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


@cli.command()
def ip() -> None:
    """Show the IP address of the host."""
    click.echo(_get_host_ip())


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
    "--local",
    help="To push the image to the local registry.",
    is_flag=True,
)
@click.option(
    "-t",
    "--tag",
    default="latest",
    envvar="TAG",
)
def push(local: bool, tag: str) -> None:
    """Push the Docker image of this project."""
    image = f"hiresify:{tag}"

    if local:
        port = DOCKER_REGISTRY["port"]
        registry_url = f"{_get_host_ip()}:{port}"
        target_image = f"{registry_url}/{image}"
        cmd = f"docker tag {image} {target_image} && docker push {target_image}"

        if subprocess.run(
            cmd,
            check=False,
            shell=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        ).returncode:
            raise ClickException("Failed to push the image to the local registry.")


@docker.group()
def registry() -> None:
    """Manage a local Docker registry hosting this project."""


@registry.command("up")
def registry_up() -> None:
    """Spin up the local Docker registry."""
    port = DOCKER_REGISTRY["port"]
    cmd = [
        "docker",
        "run",
        "-d",
        "-p",
        f"0.0.0.0:{port}:{port}",
        "--restart=always",
        "--name",
        DOCKER_REGISTRY["name"],
        "registry:latest",
    ]

    if subprocess.run(
        cmd,
        check=False,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    ).returncode:
        raise ClickException("Failed to start the local Docker registry.")


@registry.command("down")
def registry_down() -> None:
    """Spin down the local Docker registry."""
    name = DOCKER_REGISTRY["name"]
    cmd = f"docker stop {name} && docker rm {name}"

    if subprocess.run(
        cmd,
        check=False,
        shell=True,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    ).returncode:
        raise ClickException("Failed to stop the local Docker registry.")


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


# -- helper functions


def _get_host_ip() -> str:
    """Get the IP address of the host."""
    process = subprocess.run(
        "ip -4 addr show dev mpqemubr0 | grep inet | awk '{print $2}' | cut -d/ -f1",
        capture_output=True,
        check=False,
        shell=True,
        text=True,
    )

    if process.returncode:
        raise ClickException("Failed to get the host IP.")

    return process.stdout.rstrip()


if __name__ == "__main__":
    cli()
