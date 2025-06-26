FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install uv

RUN useradd --create-home --shell /bin/bash ywu

WORKDIR /home/ywu/app

RUN chown -R ywu:ywu /home/ywu/app

COPY --chown=ywu:ywu ci/configs/db.json ./
COPY --chown=ywu:ywu src/ ./
COPY --chown=ywu:ywu .python-version ./
COPY --chown=ywu:ywu pyproject.toml ./
COPY --chown=ywu:ywu uv.lock ./

USER ywu

ENV DATABASE_CONFIG=/home/ywu/app/db.json

RUN uv sync && uv pip install -e .

RUN rm -rf /home/ywu/.cache/uv
