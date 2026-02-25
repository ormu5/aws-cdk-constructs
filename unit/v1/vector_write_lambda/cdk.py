from aws_cdk.aws_s3vectors import CfnIndex
from aws_cdk import aws_lambda as lambda_, aws_logs as logs, Duration
from constructs import Construct
import boto3

from cloudformation_ import inject_canonical_id

s3_vectors_client = boto3.client("s3vectors")

@inject_canonical_id
class VectorWriteLambda(Construct):
    """Given structured data, converts to semantic text based on config,
    performs embedding, and submits embedding and metadata to vector store
    at the given index."""
    def __init__(
            self, scope: Construct, id: str, *,
            name: str,
            index: CfnIndex,  # Index to write to
            **kwargs
    ) -> None:
        super().__init__(scope, f"{id}-{name}")

        self.function = lambda_.Function(
            self,
            f"{id}-{name}",
            function_name=name,
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset("unit/v1/vector_write_lambda"),
            handler="handler.handler",
            retry_attempts=2,  # Max
            timeout=Duration.seconds(10),
            memory_size=128,
            environment={
                "VECTOR_BUCKET_NAME": index.vector_bucket_name,
                "INDEX_NAME": index.index_name
            },
            log_retention=logs.RetentionDays(60)
        )




