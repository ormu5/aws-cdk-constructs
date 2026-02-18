from aws_cdk import (
    Stack,
    aws_s3vectors as s3v,
)
from constructs import Construct

class S3VectorBucketStack(Stack):
    """One S3 vector store bucket per stack ('alone' in stack)."""
    def __init__(
            self, scope: Construct, *,
            vector_bucket_name: str,
            # removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,  # Does not exist
            **kwargs
    ) -> None:
        stack_id = "-".join([vector_bucket_name, "stack"])
        super().__init__(scope, stack_id, **kwargs)

        self.vector_bucket = s3v.CfnVectorBucket(
            self,
            "vector-bucket",
            vector_bucket_name=vector_bucket_name,
            # encryption_configuration=...  # optional (SSE-S3 default)
        )  # :contentReference[oaicite:2]{index=2}
