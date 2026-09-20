FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm
USER root
RUN python -m venv /opt/storage-venv && chown -R vscode:vscode /opt/storage-venv
ENV VIRTUAL_ENV=/opt/storage-venv
ENV PATH="/opt/storage-venv/bin:${PATH}"
USER vscode
