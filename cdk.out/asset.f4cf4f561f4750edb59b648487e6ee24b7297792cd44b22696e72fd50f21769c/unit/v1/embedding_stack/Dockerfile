##### Build container #####
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
WORKDIR /build

ENV UV_PROJECT_ENVIRONMENT=/build/.venv \
    MODEL_DIR=/build/models

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# App deps
COPY unit/v1/embedding_stack/pyproject.toml unit/v1/embedding_stack/uv.lock ./

# Install deps, persist build artifacts
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Fetch model for adding to image
RUN uv run python -c \
    "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('all-MiniLM-L6-v2').save('$MODEL_DIR/all-MiniLM-L6-v2')"


##### Runtime container #####
FROM public.ecr.aws/lambda/python:3.13

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_DIR=/opt/models

COPY --from=builder /build/.venv/lib/python3.13/site-packages/ ${LAMBDA_TASK_ROOT}/
COPY unit/v1/embedding_stack/handler.py ${LAMBDA_TASK_ROOT}/handler.py
COPY --from=builder /build/models $MODEL_DIR

CMD ["handler.handler"]
