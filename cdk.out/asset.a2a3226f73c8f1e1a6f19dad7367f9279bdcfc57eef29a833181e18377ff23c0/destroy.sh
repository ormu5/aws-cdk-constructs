#!/bin/bash

cdk destroy \
  --all \
  --app "python -m test_app" \
  --require-approval=never \
  --concurrency=4 \
  -v