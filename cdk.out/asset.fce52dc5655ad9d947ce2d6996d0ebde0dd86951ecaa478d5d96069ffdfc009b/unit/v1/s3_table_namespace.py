from constructs import Construct
from aws_cdk import aws_s3tables as s3tables

from cloudformation_ import inject_canonical_id


@inject_canonical_id
class S3TableNamespace(Construct):
    """
    Represents a single S3 Tables namespace (equivalent to a Glue database)
    within a table bucket.
    NOTE: may want to maintain via DDL (Athena) or SDK (PyIceberg), depending on
    governance particulars.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        name: str,
        table_bucket_arn: str,
    ) -> None:
        super().__init__(scope, f"{id}-{name}")

        self.name = name
        self.resource = s3tables.CfnNamespace(
            self,
            name,
            namespace=name,
            table_bucket_arn=table_bucket_arn,
        )
