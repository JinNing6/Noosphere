# syntax=docker/dockerfile:1

FROM python:3.12-slim-bookworm

LABEL org.opencontainers.image.title="Noosphere MCP"
LABEL org.opencontainers.image.description="Live, review-gated shared Skills for coding agents"
LABEL org.opencontainers.image.source="https://github.com/JinNing6/Noosphere"
LABEL org.opencontainers.image.licenses="Apache-2.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NOOSPHERE_REPO=JinNing6/Noosphere

WORKDIR /opt/noosphere

COPY README.md LICENSE ./
COPY sdk/pyproject.toml ./sdk/pyproject.toml
COPY sdk/noosphere ./sdk/noosphere

RUN python -m pip install --disable-pip-version-check --no-cache-dir ./sdk \
    && useradd --create-home --uid 10001 noosphere

USER noosphere

CMD ["noosphere-mcp"]
