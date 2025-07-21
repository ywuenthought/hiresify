FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl libmagic1 && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install uv

RUN useradd --create-home --shell /bin/bash ywu

WORKDIR /home/ywu/app

RUN chown -R ywu:ywu /home/ywu/app

COPY --chown=ywu:ywu src/ ./
COPY --chown=ywu:ywu .python-version ./
COPY --chown=ywu:ywu pyproject.toml ./
COPY --chown=ywu:ywu uv.lock ./

USER ywu

RUN uv sync && \
    uv pip install -e . && \
    rm -rf ../.cache/pip ../.cache/uv /tmp/*

USER root

RUN apt-get purge -y --auto-remove build-essential

USER ywu
