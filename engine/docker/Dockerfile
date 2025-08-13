FROM ghcr.io/astral-sh/uv:debian-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash ywu

WORKDIR /home/ywu

RUN chown -R ywu:ywu /home/ywu

COPY --chown=ywu:ywu .python-version ./
COPY --chown=ywu:ywu requirements.txt/ ./
COPY --chown=ywu:ywu build ./build

USER ywu

RUN uv venv hiresify

RUN uv pip install --python hiresify/bin/python -r requirements.txt && \
    rm requirements.txt

RUN uv pip install --python hiresify/bin/python build/*.whl && \
    rm -rf build

RUN rm -rf /home/ywu/.cache/pip /home/ywu/.cache/uv /tmp/*

CMD ["uv", "run", "--python", "hiresify/bin/python", \
     "uvicorn", "hiresify_engine.app.main:app", \
     "--access-log", \
     "--host", "0.0.0.0", \
     "--log-level", "debug", \
     "--port", "8000", \
     "--workers", "1"]
