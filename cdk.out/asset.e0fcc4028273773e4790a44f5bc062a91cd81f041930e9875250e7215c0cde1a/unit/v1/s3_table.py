from constructs import Construct
from aws_cdk.aws_s3tables_alpha import TableBucket, Namespace

from cloudformation_ import inject_canonical_id


@inject_canonical_id
class S3Table(Construct):
    """
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        name: str,
        table_bucket: TableBucket,
        namespace: Namespace
    ) -> None:
        super().__init__(scope, f"{id}-{name}")

        self.name = name
        # create a DDB table for tracking metadata
        # This table has a pk/sk of namespace/table
        ddb_table_name = construct_canonical_name("metadata-ddb-v1")
        ddb_table = ddb.TableV2(
            scope=self,
            id=ddb_table_name,
            table_name=ddb_table_name,
            dynamo_stream=ddb.StreamViewType.NEW_AND_OLD_IMAGES,
            table_class=ddb.TableClass.STANDARD,
            billing=ddb.Billing.on_demand(
                max_read_request_units=DDB_READ_CAPACITY,
                max_write_request_units=DDB_WRITE_CAPACITY,
            ),
            partition_key=ddb.Attribute(name="pk", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="sk", type=ddb.AttributeType.STRING),
            removal_policy=removal_policy,
        )