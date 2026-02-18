#!/bin/bash

cdk deploy \
  --all \
  --app "python -m test_app" \
  --require-approval=never \
  --concurrency=4 \
  -v