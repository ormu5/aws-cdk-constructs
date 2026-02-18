from constructs import Construct

from aws_cdk import Stack, RemovalPolicy, aws_s3 as s3

class S3BucketStack(Stack):
    """One S3 bucket per stack ('alone' in stack)."""
    def __init__(
            self, scope: Construct, *,
            bucket_name: str,
            removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
            versioned: bool = False,
            event_bridge_enabled: bool = False,
            lifecycle_rules: list[s3.LifecycleRule] | None = None,
            **kwargs
    ) -> None:
        stack_id = "-".join([bucket_name, "stack"])
        super().__init__(scope, stack_id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            "bucket",
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=removal_policy,
            versioned=versioned,
            event_bridge_enabled=event_bridge_enabled,
            lifecycle_rules=lifecycle_rules,
        )
