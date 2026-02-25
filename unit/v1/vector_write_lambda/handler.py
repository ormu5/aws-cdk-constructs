import os
from typing import Any
import logging

import boto3
import yaml
from jsonpath_ng import parse
from jinja2 import Template

logger = logging.getLogger(__name__)
s3_vectors_client = boto3.client("s3vectors")

with open("unit/v1/vector_write_lambda/config.yaml") as fp:
    config = yaml.safe_load(fp)
id_component_delim: str = config["id"]["delim"]

def get_field_value(record: dict, field_definition: dict) -> Any:
    """Extract field value from record based on field definition."""
    expr = parse(field_definition["path"])
    matches = expr.find(record)
    if not matches:
        raise ValueError(f"{field_definition=} not found in {record=}")
    return matches[0].value

def build_record_id(record: dict) -> str:
    """Construct unique ID for given payload."""
    return id_component_delim.join(
        [get_field_value(record, field_definition)
         for field_definition in config["id"]["fields"]]
    )

def build_embedding_sentence(record: dict) -> str:
    """Construct embedding sentence for given payload."""
    return 

def handler(event, _context):
    """Intended for structured paylaods. Based on config:
    - Build unique record ID
    - Build semantic version of payload and embed
    - Assemble metadata fields
    Then submit to vector store index.
    """

    logger.debug(f"Received {event=}.")
    response = s3_vectors_client.put_vectors(
        vectorBucketName=os.environ["VECTOR_BUCKET_NAME"],
        indexName=os.environ["INDEX_NAME"],
        vectors=[
            {
                "id": build_record_id(payload),
                "values": [0.12, 0.98, -0.44, ...],  # embedding floats
                "metadata": {
                    "customer_id": "abc123",
                    "category": "routing"
                }
            }
        ]
    )