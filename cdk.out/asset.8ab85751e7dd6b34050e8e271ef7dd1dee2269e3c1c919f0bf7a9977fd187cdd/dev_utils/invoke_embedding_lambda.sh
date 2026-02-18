#!/bin/bash

PAYLOAD='{"sentences": ["sentence one"]}'

aws lambda invoke \
  --function-name exampletwo-embedding-lambda \
  --payload '"$PAYLOAD"' \
  --cli-binary-format raw-in-base64-out \
  response.json
