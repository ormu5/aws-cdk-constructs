# Use uv's x86_64 Python base image
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    PYTHONPATH="/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# App deps
COPY unit/v1/agent_core_stack/pyproject.toml unit/v1/agent_core_stack/uv.lock ./

# Install deps, persist build artifacts
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY app.py config_query_rewrite.yaml ./

# Expose port
EXPOSE 8080

# Run application
CMD ["uv", "run", "python", "-m", "app"]
