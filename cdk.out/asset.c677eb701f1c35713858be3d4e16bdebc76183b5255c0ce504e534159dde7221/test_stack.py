from aws_cdk import Stack, RemovalPolicy
from constructs import Construct
from aws_cdk.aws_s3tables_alpha import (
    TableBucket,
    UnreferencedFileRemoval,
    UnreferencedFileRemovalStatus,
    TableBucketEncryption,
)

class TestSTack(Stack):
    """One S3 table bucket per stack ('alone' in stack)."""
    def __init__(
            self, scope: Construct, *, **kwargs
    ) -> None:
        super().__init__(scope, "test-stack", **kwargs)

        namespace

        self.table_bucket = TableBucket(
            self,
            "table-bucket",
            table_bucket_name=table_bucket_name,
            unreferenced_file_removal=UnreferencedFileRemoval(
                status=UnreferencedFileRemovalStatus.ENABLED,
                unreferenced_days=30,
                noncurrent_days=30,
            ),
            removal_policy=removal_policy,
            encryption=TableBucketEncryption.S3_MANAGED,
        )