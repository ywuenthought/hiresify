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
from base64 import b64encode
from pathlib import Path

import click

ROOT_DIR = Path(__file__).parent

DEPLOY_DIR = ROOT_DIR / "deploy"

MANIFEST = DEPLOY_DIR / "manifest.yaml"

ENGINE_CHART = DEPLOY_DIR / "engine"

CLIENT_CHART = DEPLOY_DIR / "client"

K3S_NAMESPACE = "hiresify"

K3S_URL = "https://get.k3s.io"

K3S_VERSION = "1.33.3+k3s1"

K3S_PREFIX = f"curl -sfL {K3S_URL} | INSTALL_K3S_VERSION=v{K3S_VERSION} sh -s -"

DOCKER_HUB = "registry-1.docker.io"

BITNAMI_OCI = f"oci://{DOCKER_HUB}/bitnamicharts"

HELM_URL = "https://get.helm.sh"

HELM_VERSION = "3.18.6"

HELM_PLATFORM = "linux-amd64"

HELM_ARCHIVE = f"helm-v{HELM_VERSION}-{HELM_PLATFORM}.tar.gz"


@click.group()
def cli() -> None:
    """CLI tool for Hiresify developers."""


@cli.group()
def cluster() -> None:
    """Manage a local cluster for deploying this project."""


@cluster.command("create")
def cluster_create() -> None:
    """Create the node cluster for a local deployment."""
    cmd = (
        f"{K3S_PREFIX} server --write-kubeconfig-mode=644 && "
        "mkdir -p ~/.kube && "
        "cp /etc/rancher/k3s/k3s.yaml ~/.kube/config"
    )

    if subprocess.run(cmd, check=False, shell=True).returncode:
        click.secho("Failed to launch the K3s server.", fg="red")

    cmd = (
        f"curl -sfL -o {HELM_ARCHIVE} {HELM_URL}/{HELM_ARCHIVE} && "
        f"tar -zxvf {HELM_ARCHIVE} && "
        f"sudo cp {HELM_PLATFORM}/helm /usr/local/bin && "
        f"rm -rf {HELM_ARCHIVE} {HELM_PLATFORM}"
    )

    if subprocess.run(cmd, check=False, shell=True).returncode:
        click.secho("Failed to install and configure helm.", fg="red")


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
    MANIFEST.write_text(template.format(docker_config=docker_config))
    cmd = ["kubectl", "apply", "-f", MANIFEST]

    try:
        if subprocess.run(cmd, check=False).returncode:
            click.secho(f"Failed to apply manifest {MANIFEST}.", fg="red")
    finally:
        MANIFEST.write_text(template)


@cli.group()
def deploy() -> None:
    """Manage a local deployment of this project."""


@deploy.command("up")
def deploy_up() -> None:
    """Spin up the local deployment."""
    cmd = " && ".join(
        [
            _build_helm_command(f"upgrade --install {chart.name} {chart}")
            for chart in (ENGINE_CHART, CLIENT_CHART)
        ]
    )

    if subprocess.run(cmd, check=False, shell=True).returncode:
        click.secho("Failed to spin up the local deployment.", fg="red")


@deploy.command("down")
def deploy_down() -> None:
    """Spin down the local deployment."""
    cmd = " && ".join(
        [
            _build_helm_command(f"uninstall {chart.name}")
            for chart in (ENGINE_CHART, CLIENT_CHART)
        ]
    )

    if subprocess.run(cmd, check=False, shell=True).returncode:
        click.secho("Failed to spin down the local deployment.", fg="red")


# -- helper functions


def _encode_text(text: str) -> str:
    """Encode the given text in base64."""
    return b64encode(text.encode()).decode()


def _build_helm_command(cmd: str) -> str:
    """Build the full Helm command with the given subcommand."""
    return f"sudo helm {cmd} -n {K3S_NAMESPACE} --kubeconfig ~/.kube/config"


if __name__ == "__main__":
    cli()
