import aws_cdk as cdk
from constructs import Construct

from unit.v1.agent_core_stack.cdk import AgentCoreRuntimeStack
from unit.v1.embedding_stack.cdk import EmbeddingStack
from unit.v1.firehose import Firehose
from unit.v1.s3_bucket_stack import S3BucketStack
from unit.v1.s3_table_bucket_stack import S3TableBucketStack
from unit.v1.s3_table_namespace import S3TableNamespace
from unit.v1.firehose_iceberg_destination import FirehoseIcebergDestination
from unit.v1.s3_vector_store_stack import S3VectorBucketStack

NAME_FOR_EVERYTHING = "exampletwo"

app = cdk.App()

table_bucket_stack = S3TableBucketStack(app, table_bucket_name=NAME_FOR_EVERYTHING, removal_policy=cdk.RemovalPolicy.DESTROY)

class TestStack(cdk.Stack):
    """Test stack to hold test resources."""

    def __init__(self, scope: Construct, **kwargs) -> None:
        super().__init__(scope, "test-stack", **kwargs)

        bucket_stack = S3BucketStack(self, bucket_name=NAME_FOR_EVERYTHING + "bucketr4ndom1shstrng", removal_policy=cdk.RemovalPolicy.DESTROY)
        namespace = S3TableNamespace(self, name=NAME_FOR_EVERYTHING, table_bucket_arn=table_bucket_stack.table_bucket.table_bucket_arn)
        firehose = Firehose(self, name=NAME_FOR_EVERYTHING)

        iceberg_destination_configuration = FirehoseIcebergDestination(
            self, firehose=firehose, table_name="daily_sales",
            namespace_name=namespace.name, table_bucket_name=table_bucket_stack.table_bucket_name,
            errors_output_bucket=bucket_stack.bucket, buffer_interval_secs=30
        )
        firehose.add_destination(
            {"iceberg_destination_configuration": iceberg_destination_configuration.destination_configuration}
        )
        vector_bucket_stack = S3VectorBucketStack(self, vector_bucket_name=NAME_FOR_EVERYTHING)
        cdk.aws_s3vectors.CfnIndex(
            self,
            "my-vector-index",
            vector_bucket_name=vector_bucket_stack.vector_bucket.vector_bucket_name,
            index_name="docs-minilm-384-cosine",
            data_type="float32",
            dimension=384,
            distance_metric="cosine",
            # Optional: configure which metadata keys are filterable
            metadata_configuration=cdk.aws_s3vectors.CfnIndex.MetadataConfigurationProperty(
                non_filterable_metadata_keys=["sales_amount"],
            )
            # Optionally override encryption at the index level
            # encryption_configuration=...
        )
        embedding_stack = EmbeddingStack(self, name=f"{NAME_FOR_EVERYTHING}-embedding")
        agent_runtime = AgentCoreRuntimeStack(
            self,
            runtime_name="_".join([NAME_FOR_EVERYTHING,"agent_runtime"]),
            embedding_lambda=embedding_stack.embedding_lambda
        )


TestStack(app)

cdk.Tags.of(app).add("ENV", NAME_FOR_EVERYTHING)

app.synth()
