# aws-cdk-constructs
Goal: ready-to-rock AWS CDK constructs witih an emphasis on stubborn / poorly-documented patterns.

* No module in unit should ever directly import another module in unit

# Details

- for managed iceberg, S3 / analytics integration should be enabled in account
- cfn exec role should be given admin over any table bucket created. this may become available via CDK but was not at the time of this writing.