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

K3S_URL = "https://get.k3s.io"

SERVER = "server"

LOAD_BALANCER = "balancer"

FASTAPI = "fastapi"

REDIS = "redis"

POSTGRES = "postgres"

NODE_CONFIGS = {
    SERVER: dict(cpus=1, disk="4G", memory="1G"),
    LOAD_BALANCER: dict(cpus=1, disk="4G", memory="1G"),
    FASTAPI: dict(cpus=2, disk="4G", memory="1G"),
    REDIS: dict(cpus=2, disk="4G", memory="2G"),
    POSTGRES: dict(cpus=2, disk="8G", memory="1G"),
}


@click.group()
def cli() -> None:
    """CLI tool for Hiresify developers."""


@cli.group()
def cluster() -> None:
    """Manage a local cluster for deploying this project."""


@cluster.command("create")
@click.option(
    "-t",
    "--token",
    envvar="K3S_TOKEN",
    help="The K3S token used to register agent nodes.",
    required=True,
)
def cluster_create(token: str) -> None:
    """Create the node cluster for a local deployment."""

    # -- create the server node.

    _create_k3s_node(name=SERVER, **NODE_CONFIGS[SERVER])

    # -- launch the K3s server on the server node.

    _launch_k3s_server(node=SERVER, token=token)

    # -- get the server node URL.

    cmd = ["multipass", "info", "server"]

    process = subprocess.run(cmd, capture_output=True, check=False, text=True)

    if process.returncode:
        raise ClickException("Failed to get the server node info.")

    server_url = None
    for line in process.stdout.splitlines():
        if line.strip().startswith("IPv4"):
            ip = line.split(":", 1)[1].strip()
            # 6443 is the default port.
            server_url = f"https://{ip}:6443"

    if server_url is None:
        raise ClickException("Failed to get the K3s server URL.")

    # -- create the agent nodes and register them to the K3s server.

    for name, config in NODE_CONFIGS.items():
        if name == SERVER:
            continue

        _create_k3s_node(name=name, **config)
        _launch_k3s_agent(node=name, server=server_url, token=token)


@cluster.command("up")
def cluster_spin_up() -> None:
    """Spin up the node cluster for a local deployment."""
    failed_nodes = []

    for name in NODE_CONFIGS:
        cmd = ["multipass", "start", name]

        if subprocess.run(cmd, check=False).returncode:
            failed_nodes.append(name)

    if failed_nodes:
        raise ClickException(f"Failed to spin up nodes: {', '.join(failed_nodes)}.")


@cluster.command("down")
@click.option(
    "--purge/--no-purge",
    default=False,
    help="Remove nodes from disk to free up space.",
    is_flag=True,
)
def cluster_spin_down(purge: bool) -> None:
    """Spin down the node cluster for a local deployment."""
    failed_nodes = []

    for name in NODE_CONFIGS:
        # Note: Use this aggressive global operation until a better solution is figured.
        cmd = ["multipass", "delete", "--purge", name] if purge else [
            "multipass", "stop", name
        ]

        if subprocess.run(cmd, check=False).returncode:
            failed_nodes.append(name)

    if failed_nodes:
        raise ClickException(f"Failed to spin down nodes: {', '.join(failed_nodes)}.")


# -- helper functions


def _create_k3s_node(*, cpus: int, disk: str, memory: str, name: str) -> None:
    """Create a node in the local K3s cluster."""

    # -- launch the node from scratch.

    cmd = [
        "multipass",
        "launch",
        "24.04",
        "--cloud-init",
        CLOUD_INIT,
        "--cpus",
        f"{cpus}",
        "--disk",
        f"{disk}",
        "--memory",
        f"{memory}",
        "--name",
        f"{name}",
    ]

    if subprocess.run(cmd, check=False).returncode:
        raise ClickException(f"Failed to create node {name}.")

    # -- reboot the node due to package upgrades.

    cmd = ["multipass", "restart", "server"]

    if subprocess.run(cmd, check=False).returncode:
        raise ClickException(f"Failed to reboot node {name}.")


def _launch_k3s_server(node: str, token: str) -> None:
    """Launch a K3s server on the specified node."""
    cmd = [
        "multipass",
        "exec",
        node,
        "--",
        "sh",
        "-c",
        f'curl -sfL {K3S_URL} | sh -s - --token {token}',
    ]

    if subprocess.run(cmd, check=False).returncode:
        raise ClickException(f"Failed to launch the K3s server on node {node}.")


def _launch_k3s_agent(node: str, server: str, token: str) -> None:
    """Launch a K3s agent on the specified node."""
    cmd = [
        "multipass",
        "exec",
        node,
        "--",
        "sh",
        "-c",
        f'curl -sfL {K3S_URL} | K3S_URL={server} sh -s - agent --token {token}',
    ]

    if subprocess.run(cmd, check=False).returncode:
        raise ClickException(f"Failed to launch the K3s agent on node {node}.")


if __name__ == "__main__":
    cli()
