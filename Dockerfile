FROM python:3.13-slim AS python
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    build-essential \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*
# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash appuser
WORKDIR /app
RUN chown appuser:appuser /app


FROM python AS uv
# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.7.15 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN chown appuser:appuser pyproject.toml uv.lock
USER appuser
# Install dependencies only, skip local project installation
RUN --mount=type=cache,target=/home/appuser/.cache/uv,uid=1000,gid=1000 \
    uv sync --frozen --no-dev --no-install-project


FROM python AS runtime
# Copy the virtual environment
COPY --from=uv --chown=appuser:appuser /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app"
USER appuser
COPY --chown=appuser:appuser . /app/
