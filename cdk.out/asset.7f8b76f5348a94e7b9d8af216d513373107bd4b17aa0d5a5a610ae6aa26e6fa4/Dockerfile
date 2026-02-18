# Use uv's x86_64 Python base image
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Copy uv files
COPY unit/v1/agent_core_stack/pyproject.toml unit/v1/agent_core_stack/uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

COPY app.py config_query_rewrite.yaml ./

# Set environment variables
ENV PYTHONPATH="/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run application
CMD ["uv", "run", "python", "-m", "app"]
