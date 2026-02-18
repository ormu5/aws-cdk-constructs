import json
import os

from pyiceberg.catalog import load_catalog
from pyiceberg.partitioning import PartitionSpec, UNPARTITIONED_PARTITION_SPEC
from pyiceberg.schema import Schema

from lib.v1.dynamodb import put_item_to_ddb, delete_item_from_ddb
from lib.v1.logging_ import get_logger

# Configuration constants
ACCOUNT_ID = os.environ["ACCOUNT_ID"]
TARGET_DDB_TABLE_NAME = os.environ["TARGET_DDB_TABLE_NAME"]
REGION = os.environ["AWS_REGION"]  # e.g., 'us-east-1'
CATALOG_NAME = "s3tablescatalog"  # Requires s3 integraiton

logger = get_logger(__name__)


def handler(event, context):
    """
    """
    # Initialize the catalog
    table_bucket_name = event["table_bucket_name"]
    database_name = event["database_name"]
    table_name = event["table_name"]

    rest_catalog = load_catalog(
        CATALOG_NAME,
        **{
            "type": "rest",
            "warehouse": f"arn:aws:s3tables:{REGION}:{ACCOUNT_ID}:bucket/{table_bucket_name}",
            "uri": f"https://s3tables.{REGION}.amazonaws.com/iceberg",
            "rest.sigv4-enabled": "true",
            "rest.signing-name": "s3tables",
            "rest.signing-region": REGION,
        },
    )
    logger.info(f"Connected to catalog {CATALOG_NAME} for bucket {table_bucket_name}")
    table_properties = (
        json.loads(event.get("table_properties")) if event.get("table_properties") else None
    )

    match event["action"]:
        case "CREATE":
            # Create the Iceberg table
            schema: Schema = Schema(**json.loads(event["canonical_schema_json"]))
            partitioning_spec: PartitionSpec = UNPARTITIONED_PARTITION_SPEC
            if event.get("canonical_partitioning_spec_json"):
                partitioning_spec = PartitionSpec(
                    **json.loads(event["canonical_partitioning_spec_json"])
                )
            rest_catalog.create_table_if_not_exists(
                identifier=f"{database_name}.{table_name}",
                schema=schema,
                partition_spec=partitioning_spec,
                location=f"s3://{table_bucket_name}/{database_name}/{table_name}/",
            )
            # record contract metadata on table creatoin
            put_item_to_ddb(
                TARGET_DDB_TABLE_NAME, {"pk": database_name, "sk": table_name, **table_properties}
            )
            logger.info(f"Table metadata created with {table_properties}")
        case "UPDATE":
            put_item_to_ddb(
                TARGET_DDB_TABLE_NAME, {"pk": database_name, "sk": table_name, **table_properties}
            )
            logger.info(f"Table metadata updated with {table_properties}")
        case "DROP":
            rest_catalog.drop_table((database_name, table_name))
            delete_item_from_ddb(TARGET_DDB_TABLE_NAME, database_name, table_name)
        case "PURGE":
            rest_catalog.purge_table((database_name, table_name))
            delete_item_from_ddb(TARGET_DDB_TABLE_NAME, database_name, table_name)
        case _:
            logger.info("Action not a recognized action")
    logger.info("Iceberg DDL successfully executed.")
