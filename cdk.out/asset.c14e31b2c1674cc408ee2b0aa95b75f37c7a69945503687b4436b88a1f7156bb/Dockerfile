##### Build container #####
FROM python:3.12-slim AS builder
WORKDIR /build

# System
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python
COPY unit/v1/agent_core_stack/requirements.txt .
RUN pip install --upgrade pip \
  && pip install --no-cache-dir --target=/build/python \
    -r requirements.txt

##### Runtime container #####
FROM public.ecr.aws/lambda/python:3.12
WORKDIR /app

COPY --from=builder /build/python /usr/local/lib/python3.12/site-packages
COPY app.py /app/app.py

CMD ["python", "-m", "/app/app"]
