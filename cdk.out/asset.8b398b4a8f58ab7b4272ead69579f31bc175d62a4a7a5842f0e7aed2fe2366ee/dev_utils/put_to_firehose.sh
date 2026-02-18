#!/bin/bash
# For ad hoc putting of a record onto data firhose
#

aws firehose put-record \
    --delivery-stream-name exampletwo \
    --record '{"Data":"{\"sales_date\":\"2025-10-01\",\"product_category\":\"sports\",\"sales_amount\":\"6.13\"}"}' \
    --cli-binary-format raw-in-base64-out

#
#
# {\"hauling_site_id\":\"blah\", \"validation_contract\":\"test-entity\", \"validation_version\":\"1.0.13", \"product\":\"test-product\", \"validated_at\":\"2025-07-23T16:58:14.465749+00:00\"}
