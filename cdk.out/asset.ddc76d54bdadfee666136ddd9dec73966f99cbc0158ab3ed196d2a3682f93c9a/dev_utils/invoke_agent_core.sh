#!/bin/bash

RUNTIME_ID=exampletwo_agent_runtime-QAGEyu4L9K
PAYLOAD='{"prompt": ["Hello world"]}'

aws bedrock-agent-runtime invoke-agent-runtime \
  --agent-runtime-id "$RUNTIME_ID" \
  --cli-binary-format raw-in-base64-out \
  --payload "$PAYLOAD"
