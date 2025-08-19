# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

# /// script
# requires-python = ">=3.11"
# dependencies = ["click"]
# ///

import subprocess
from pathlib import Path

import click
from click import ClickException

ROOT_DIR = Path(__file__).parent

DEPLOY_DIR = ROOT_DIR / "deploy"

CLOUD_INIT = DEPLOY_DIR / "cloud_init.yaml"


@click.group()
def cli() -> None:
    """CLI tool for Hiresify developers."""


@cli.group()
def deploy() -> None:
    """Manage deployments of this project."""


@deploy.group("local")
def deploy_local() -> None:
    """Manage a local deployment of this project."""


@deploy_local.command("create")
@click.option(
    "-t",
    "--token",
    envvar="K3S_TOKEN",
    help="The K3S token used to register agent nodes.",
    required=True,
)
def local_create(token: str) -> None:
    """Create the node cluster for a local deployment."""
    server_cmd = [
        "multipass",
        "launch",
        "24.04",
        "--cloud-init",
        CLOUD_INIT,
        "--cpus",
        "2",
        "--disk",
        "10G",
        "--memory",
        "2G",
        "--name",
        "server",
    ]

    if subprocess.run(server_cmd, check=False).returncode:
        raise ClickException("Failed to create the server node.")

    server_cmd = ["multipass", "restart", "server"]

    if subprocess.run(server_cmd, check=False).returncode:
        raise ClickException("Failed to reboot the server node.")

    server_cmd = [
        "multipass",
        "exec",
        "server",
        "--",
        "sh",
        "-c",
        (
            "curl -sfL https://get.k3s.io | "
            f'INSTALL_K3S_EXEC="server" sh -s - --token {token}'
        ),
    ]

    if subprocess.run(server_cmd, check=False).returncode:
        raise ClickException("Failed to launch the K3s server.")


@deploy_local.command("up")
def local_spin_up() -> None:
    """Spin up the node cluster for a local deployment."""
    server_cmd = ["multipass", "start", "server"]

    if subprocess.run(server_cmd, check=False).returncode:
        raise ClickException("Failed to create the server node.")


@deploy_local.command("down")
@click.option(
    "--purge/--no-purge",
    default=False,
    help="Remove nodes from disk to free up space.",
    is_flag=True,
)
def local_spin_down(purge: bool) -> None:
    """Spin down the node cluster for a local deployment."""
    if purge:
        # Note: Use this aggressive global operation until a better solution is figured.
        cmd_factory = lambda name: ["multipass", "delete", "--purge", name]

        failed_nodes = []
        for name in ("server",):
            if subprocess.run(cmd_factory(name), check=False).returncode:
                failed_nodes.append(name)

        if failed_nodes:
            raise ClickException(f"Failed to purge nodes: {', '.join(failed_nodes)}.")

        return

    server_cmd = ["multipass", "stop", "server"]

    if subprocess.run(server_cmd, check=False).returncode:
        raise ClickException("Failed to spin down the server node.")


if __name__ == "__main__":
    cli()
