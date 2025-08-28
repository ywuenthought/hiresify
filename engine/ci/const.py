# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

import pathlib

CI_DIR = pathlib.Path(__file__).parent

PROJECT_ROOT = CI_DIR.parent

DOCKER_DIR = PROJECT_ROOT / "docker"

DOCKER_FILE = DOCKER_DIR / "Dockerfile"

DEV_DOCKER_COMPOSE = DOCKER_DIR / "compose.dev.yml"

REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

DOCKER_REGISTRY = dict(name="registry", port=5000)
