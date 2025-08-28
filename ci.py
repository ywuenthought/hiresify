# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

# /// script
# requires-python = ">=3.11"
# dependencies = ["click"]
# ///

import subprocess
import textwrap
import time
import typing as ty
from base64 import b64encode
from pathlib import Path

import click
from click import ClickException

ROOT_DIR = Path(__file__).parent

DEPLOY_DIR = ROOT_DIR / "deploy"

CLOUD_INIT = DEPLOY_DIR / "cloud_init.yaml"

MANIFEST = DEPLOY_DIR / "manifest.yaml"

K3S_URL = "https://get.k3s.io"

K3S_VERSION = "1.33.3+k3s1"

K3S_PREFIX = f"curl -sfL {K3S_URL} | INSTALL_K3S_VERSION=v{K3S_VERSION} sh -s -"

DOCKER_HUB = "registry-1.docker.io"

BITNAMI_OCI = f"oci://{DOCKER_HUB}/bitnamicharts"

HELM_URL = "https://get.helm.sh"

HELM_VERSION = "3.18.6"

HELM_PLATFORM = "linux-amd64"

HELM_ARCHIVE = f"helm-v{HELM_VERSION}-{HELM_PLATFORM}.tar.gz"

SERVER = "server"

LOAD_BALANCER = "balancer"

HIRESIFY = "hiresify"

NODE_CONFIGS = {
    SERVER: dict(cpus=2, disk="8G", memory="2G"),
    LOAD_BALANCER: dict(cpus=1, disk="8G", memory="1G"),
    HIRESIFY: dict(cpus=4, disk="64G", memory="4G"),
}

SERVICE_VALUES = {
    service: DEPLOY_DIR / f"{service}.yaml"
    for service
    in ("minio", "postgresql", "redis")
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

    if _create_k3s_node(name=SERVER, **NODE_CONFIGS[SERVER]):
        click.secho(f"Failed to launch node {SERVER}.", fg="red")
        return

    if _exec(f"{K3S_PREFIX} server --token {token} --write-kubeconfig-mode=644"):
        click.secho(f"Failed to launch the K3s server.", fg="red")
        return

    # -- install helm from a binary release.

    helm_cmd = (
        f"curl -sfL -o {HELM_ARCHIVE} {HELM_URL}/{HELM_ARCHIVE} && "
        f"tar -zxvf {HELM_ARCHIVE} && "
        f"mv {HELM_PLATFORM}/helm /usr/local/bin && "
        f"rm -rf {HELM_ARCHIVE} {HELM_PLATFORM} && "
        "mkdir -p ~/.kube && "
        "cp /etc/rancher/k3s/k3s.yaml ~/.kube/config"
    )

    if _exec(helm_cmd, with_root_permission=True):
        click.secho(f"Failed to install and configure helm.", fg="red")
        return

    # -- get the server node URL.

    if (server := _get_server_url()) is None:
        click.secho("Failed to get the K3s server URL.", fg="red")
        return

    # -- create the agent nodes and register them with labels and taints.

    for name, config in NODE_CONFIGS.items():
        if name == SERVER:
            continue

        if _create_k3s_node(name=name, **config):
            click.secho(f"Failed to launch node {name}.", fg="red")
            return

        if _exec(f"{K3S_PREFIX} agent --server {server} --token {token}", node=name):
            click.secho(f"Failed to launch the K3s agent {name}.", fg="red")
            return


@cluster.command("up")
def cluster_up() -> None:
    """Spin up the node cluster for a local deployment."""
    failed_nodes = []

    for name in NODE_CONFIGS:
        if _start(name):
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
def cluster_down(purge: bool) -> None:
    """Spin down the node cluster for a local deployment."""
    failed_nodes = []

    for name in NODE_CONFIGS:
        # Note: Use this aggressive global operation until a better solution is figured.
        if (_delete(name, purge=purge) if purge else _stop(name)):
            failed_nodes.append(name)

    if failed_nodes:
        raise ClickException(f"Failed to spin down nodes: {', '.join(failed_nodes)}.")


@cli.group()
def predeploy() -> None:
    """Perform pre-deployment operations on the local cluster."""


@predeploy.command("config")
@click.option(
    "--minio-password",
    envvar="MINIO_PASSWORD",
    help="The password used to access the MinIO database.",
    required=True,
)
@click.option(
    "--postgresql-password",
    envvar="POSTGRESQL_PASSWORD",
    help="The password used to access the PostgreSQL database.",
    required=True,
)
@click.option(
    "--redis-password",
    envvar="REDIS_PASSWORD",
    help="The password used to access the Redis server.",
    required=True,
)
def predeploy_config(
    minio_password: str,
    postgresql_password: str,
    redis_password: str
) -> None:
    """Set up the pre-deployment configuration."""
    template = MANIFEST.read_text(encoding="utf-8")

    try:
        MANIFEST.write_text(
            template.format(
                minio_username=_encode_text("user"),
                minio_password=_encode_text(minio_password),
                postgresql_password=_encode_text(postgresql_password),
                redis_password=_encode_text(redis_password),
            ),
            encoding="utf-8",
        )

        _transfer(MANIFEST)
        _exec(f"kubectl apply -f {MANIFEST.name}", node=SERVER)
    finally:
        MANIFEST.write_text(template)


@predeploy.command("login")
@click.option(
    "-u",
    "--username",
    envvar="DOCKER_USERNAME",
    help="The username used to log into Docker Hub.",
    required=True,
)
@click.option(
    "-p",
    "--password",
    envvar="DOCKER_PASSWORD",
    help="The password used to log into Docker Hub.",
    required=True,
)
def predeploy_login(username: str, password: str) -> None:
    """Log into Docker Hub using the given credentials."""
    _exec(
        f"echo {password} | helm registry login {DOCKER_HUB} "
        f"--username {username} --password-stdin"
    )


@cli.group()
def deploy() -> None:
    """Manage a local deployment of this project."""


@deploy.command("up")
def deploy_up() -> None:
    """Spin up the local deployment."""
    for service, values in SERVICE_VALUES.items():
        _transfer(values)
        _exec(
            f"helm upgrade --install {service} {BITNAMI_OCI}/{service} "
            f"-n {HIRESIFY} -f {values.name}",
            with_root_permission=True,
        )


@deploy.command("down")
def deploy_down() -> None:
    """Spin down the local deployment."""
    for service in SERVICE_VALUES:
        _exec(f"helm uninstall {service} -n {HIRESIFY}", with_root_permission=True)


# -- helper functions


def _create_k3s_node(*, cpus: int, disk: str, memory: str, name: str) -> int:
    """Create a node in the local K3s cluster."""
    if (network := _get_bridged_network()) is None:
        click.secho("Failed to get the bridged network.", fg="red")
        return

    launch_cmd = [
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
        "--network",
        network,
    ]

    if code := subprocess.run(launch_cmd, check=False).returncode:
        _delete(name, purge=True)
        return code

    _restart(name)

    return 0


def _delete(node: str, purge: bool = False) -> int:
    """Delete the specified multipass instance."""
    cmd = ["multipass", "delete"] + (["--purge"] if purge else []) + [node]

    return subprocess.run(cmd, check=False).returncode


def _encode_text(text: str) -> str:
    """Encode the given text in the base64 format."""
    return b64encode(text.encode("utf-8")).decode("utf-8")


def _exec(
    cmd: str,
    node: str = SERVER,
    quiet: bool = False,
    with_root_permission: bool = False,
) -> int:
    """Execute a command on the specified node."""
    cmd = ["multipass", "exec", node, "--"] + (
        ["sudo"] if with_root_permission else []
    ) + ["bash", "-lc", cmd]

    return subprocess.run(
        cmd,
        check=False,
        stderr=subprocess.DEVNULL if quiet else None,
        stdout=subprocess.DEVNULL if quiet else None,
    ).returncode


def _get_bridged_network() -> str | None:
    """Get the bridged network to be used by nodes."""
    result = subprocess.run(
        ["multipass", "networks"],
        capture_output=True,
        check=False,
        text=True,
    ).stdout

    _, *lines = result.strip().splitlines()
    for line in lines:
        name, network_type, *_ = line.split()
        if network_type == "bridge":
            return name

    return None


def _get_server_url() -> str | None:
    """Get the URL to the K3s server."""
    result = subprocess.run(
        ["multipass", "info", SERVER],
        capture_output=True,
        check=False,
        text=True,
    ).stdout

    for line in result.splitlines():
        if line.strip().startswith("IPv4"):
            ip = line.split(":", 1)[1].strip()
            # 6443 is the default port.
            return f"https://{ip}:6443"

    return None


def _restart(node: str) -> int:
    """Restart the specified multipass instance."""
    cmd = ["multipass", "restart", node]

    if code := subprocess.run(cmd, check=False).returncode:
        return code

    if code := _wait_for_exec(node):
        return code

    if code := _wait_for_init(node):
        return code

    if code := _wait_for_sshd(node):
        return code

    return 0


def _start(node: str) -> int:
    """Start the specified multipass instance."""
    cmd = ["multipass", "start", node]

    if code := subprocess.run(cmd, check=False).returncode:
        return code

    if code := _wait_for_exec(node):
        return code

    if code := _wait_for_init(node):
        return code

    if code := _wait_for_sshd(node):
        return code

    return 0


def _stop(node: str) -> int:
    """Stop the specified multipass instance."""
    cmd = ["multipass", "stop", node]

    return subprocess.run(cmd, check=False).returncode


def _transfer(file: Path, node: str = SERVER, path: ty.Optional[Path] = None) -> int:
    """Transfer a file from the host to the specified multipass instance."""
    if path is not None:
        _exec(f"mkdir -p {path.parent}", with_root_permission=True)

    cmd = ["multipass", "transfer", file, f"{node}:{'' if path is None else path}"]

    return subprocess.run(cmd, check=False).returncode


def _wait_for_exec(node: str, retries: int = 60) -> int:
    """Wait for the given node to accept exec."""
    code = 1

    while retries:
        if (code := _exec("true", node=node, quiet=True)) == 0:
            break

        time.sleep(1)

    return code


def _wait_for_init(node: str, retries: int = 60) -> int:
    """Wait for cloud-init to be ready inside the given node."""
    cmd = textwrap.dedent(
        f"""\
        for i in {{1..{retries}}}; do
          cloud-init status | grep -q 'done' && exit 0
          sleep 1
        done
        echo "init not ready" >&2; exit 1
        """
    )

    return _exec(cmd, node=node)


def _wait_for_sshd(node: str, retries: int = 60) -> int:
    """Wait for sshd to be ready inside the given node."""
    cmd = textwrap.dedent(
        f"""\
        for i in {{1..{retries}}}; do
          systemctl is-active --quiet ssh && exit 0
          sleep 1
        done
        echo "sshd not ready" >&2; exit 1
        """
    )

    return _exec(cmd, node=node)


if __name__ == "__main__":
    cli()
