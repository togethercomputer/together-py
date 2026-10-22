ARG VARIANT="3.10"
FROM mcr.microsoft.com/devcontainers/python:3-${VARIANT}-trixie

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade ca-certificates \
    && rm -rf /var/lib/apt/lists/*

USER vscode

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN echo "[[ -d .venv ]] && source .venv/bin/activate || export PATH=\$PATH" >> /home/vscode/.bashrc
