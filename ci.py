# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

# /// script
# requires-python = ">=3.11"
# dependencies = ["click"]
# ///

import json
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

API_NODE = "api"

APP_NODE = "app"

APP_NAME = "hiresify"

APP_CHART = ROOT_DIR / APP_NAME

API_RESOURCES = dict(cpus=2, disk="8G", memory="2G")

APP_RESOURCES = dict(cpus=4, disk="64G", memory="4G")


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

    # -- create the API node.

    if _create_k3s_node(**API_RESOURCES, name=API_NODE):
        click.secho(f"Failed to launch node {API_NODE}.", fg="red")
        return

    if _exec(f"{K3S_PREFIX} server --token {token} --write-kubeconfig-mode=644"):
        click.secho("Failed to launch the K3s server.", fg="red")
        return

    # -- install helm from a binary release.

    helm_cmd = (
        f"curl -sfL -o {HELM_ARCHIVE} {HELM_URL}/{HELM_ARCHIVE} && "
        f"tar -zxvf {HELM_ARCHIVE} && "
        f"mv {HELM_PLATFORM}/helm /usr/local/bin && "
        f"rm -rf {HELM_ARCHIVE} {HELM_PLATFORM}"
    )

    if _exec(helm_cmd, admin=True):
        click.secho("Failed to install and configure helm.", fg="red")
        return

    # -- create the app node.

    if (ip := _get_node_ip()) is None:
        click.secho("Failed to get the K3s server IP.", fg="red")
        return

    if _create_k3s_node(**APP_RESOURCES, name=APP_NODE):
        click.secho(f"Failed to launch node {APP_NODE}.", fg="red")
        return

    if _exec(
        # 6443 is the default port.
        f"{K3S_PREFIX} agent --server https://{ip}:6443 --token {token}",
        node=APP_NODE,
    ):
        click.secho("Failed to launch the K3s agent.", fg="red")
        return


@cluster.command("up")
def cluster_up() -> None:
    """Spin up the node cluster for a local deployment."""
    failed_nodes = []

    for node in (API_NODE, APP_NODE):
        if _start(node):
            failed_nodes.append(node)

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
    cmd_prefix = ["multipass", "delete", "--purge"] if purge else ["multipass", "stop"]

    failed_nodes = []
    for node in (API_NODE, APP_NODE):
        cmd_prefix.append(node)
        if subprocess.run(cmd_prefix, check=False).returncode:
            failed_nodes.append(node)
        cmd_prefix.pop()

    if failed_nodes:
        raise ClickException(f"Failed to spin down nodes: {', '.join(failed_nodes)}.")


@cli.command()
def ip() -> None:
    """Display the IP address to the app server."""
    click.echo(_get_node_ip(APP_NODE))


@cli.group()
def predeploy() -> None:
    """Perform pre-deployment operations on the local cluster."""


@predeploy.command("config")
@click.option(
    "--docker-username",
    envvar="DOCKER_USERNAME",
    help="The username used to log in Docker Hub",
    required=True,
)
@click.option(
    "--docker-password",
    envvar="DOCKER_PASSWORD",
    help="The password used to log in Docker Hub",
    required=True,
)
def predeploy_config(docker_username: str, docker_password: str) -> None:
    """Set up the pre-deployment configuration."""
    docker_config = _encode_text(
        json.dumps(
            {
                "auths": {
                    "docker.io": {
                        "username": docker_username,
                        "password": docker_password,
                        "auth": _encode_text(f"{docker_username}:{docker_password}"),
                    }
                }
            }
        )
    )

    template = MANIFEST.read_text(encoding="utf-8")

    try:
        MANIFEST.write_text(template.format(docker_config=docker_config))

        _copy(MANIFEST)
        _exec(f"kubectl apply -f {MANIFEST.name}")
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
    cmd = (
        "mkdir -p ~/.kube && cp /etc/rancher/k3s/k3s.yaml ~/.kube/config && "
        f"helm upgrade --install {APP_NAME} {APP_CHART.name} -n {APP_NAME}"
    )

    _copy(APP_CHART, recursive=True)
    _exec(cmd, admin=True)


@deploy.command("down")
def deploy_down() -> None:
    """Spin down the local deployment."""
    cmd = (
        "mkdir -p ~/.kube && cp /etc/rancher/k3s/k3s.yaml ~/.kube/config && "
        f"helm uninstall {APP_NAME} -n {APP_NAME}"
    )

    _exec(cmd, admin=True)


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
        return code

    return _restart(name)


def _encode_text(text: str) -> str:
    """Encode the given text in base64."""
    return b64encode(text.encode()).decode()


def _exec(
    cmd: str,
    *,
    node: str = API_NODE,
    quiet: bool = False,
    admin: bool = False
) -> int:
    """Execute a command on the specified node."""
    cmd = ["multipass", "exec", node, "--"] + (
        ["sudo"] if admin else []
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


def _get_node_ip(node: str = API_NODE) -> str | None:
    """Get the IP address to the specified node."""
    result = subprocess.run(
        ["multipass", "info", node],
        capture_output=True,
        check=False,
        text=True,
    ).stdout

    for line in result.splitlines():
        if line.strip().startswith("IPv4"):
            return line.split(":", 1)[1].strip()

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


def _copy(
    source: Path,
    target: ty.Optional[Path] = None,
    recursive: bool = False,
) -> int:
    """Copy the source from the host to the target in the multipass instance."""
    if target is not None:
        _exec(f"mkdir -p {target.parent}", admin=True)

    cmd = ["multipass", "transfer"] + (
        ["-r"] if recursive else []
    ) + [source, f"{API_NODE}:{'' if target is None else target}"]

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
