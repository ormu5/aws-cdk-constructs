from constructs import Construct
from aws_cdk.aws_s3tables_alpha import (
    TableBucket,
    UnreferencedFileRemoval,
    UnreferencedFileRemovalStatus,
    TableBucketEncryption,
)
from aws_cdk import Stack, RemovalPolicy, CfnOutput

class S3TableBucketStack(Stack):
    """One S3 table bucket per stack ('alone' in stack)."""
    def __init__(
            self, scope: Construct, *,
            table_bucket_name: str,
            removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
            **kwargs
    ) -> None:
        stack_id = "-".join([table_bucket_name, "stack"])
        super().__init__(scope, stack_id, **kwargs)

        # Some export weirdness when trying to reference name via TableBucket property
        self.table_bucket_name = table_bucket_name
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
