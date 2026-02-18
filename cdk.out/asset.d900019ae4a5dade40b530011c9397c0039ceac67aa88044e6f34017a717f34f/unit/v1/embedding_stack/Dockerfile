ARG MODEL_NAME="all-MiniLM-L6-v2"

##### Build container #####
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
WORKDIR /build

ARG MODEL_NAME
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
    SentenceTransformer('$MODEL_NAME').save('$MODEL_DIR/$MODEL_NAME')"


##### Runtime container #####
FROM public.ecr.aws/lambda/python:3.13

ARG MODEL_NAME
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false \
    MODEL_DIR=/opt/models \
    MODEL_NAME=$MODEL_NAME

COPY --from=builder /build/.venv/lib/python3.13/site-packages/ ${LAMBDA_TASK_ROOT}/
COPY unit/v1/embedding_stack/handler.py ${LAMBDA_TASK_ROOT}/handler.py
COPY --from=builder /build/models $MODEL_DIR

CMD ["handler.handler"]
