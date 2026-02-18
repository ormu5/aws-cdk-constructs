from __future__ import annotations

from constructs import Construct
from aws_cdk import Aws, aws_s3 as s3, aws_kinesisfirehose, aws_iam as iam, aws_lakeformation as lakeformation

import unit.v1.firehose
from cloudformation_ import inject_canonical_id


@inject_canonical_id
class FirehoseIcebergDestination(Construct):
    """
    Configures destination and associated additional IAM to interact with that
    destination.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        firehose: unit.v1.firehose.Firehose,  # That writes to the destination
        table_name: str,  # Must already exist
        namespace_name: str,  # Defer to caller for namespace maintenance (e.g., IaC vs DDL)
        table_bucket_name: str,
        errors_output_bucket: s3.Bucket,
        append_only: bool = True,
        buffer_interval_secs: int = 300,
        buffer_size_mb: int = 64,
        errors_output_prefix: str = ""
    ) -> None:
        super().__init__(scope, f"{id}-{table_name.replace('_', '-')}")

        # Access needed for firehose to destination, also common to *not* scope below
        # ARNs as Lake Formation will manage data permissions.
        # https://docs.aws.amazon.com/firehose/latest/dev/controlling-access.html#using-iam-s3
        self.inline_policy = iam.Policy(self, "firehose-inline-policy",
            statements=[
                iam.PolicyStatement(
                    sid="AllowReadFromCatalogViaS3TableGlueFederation",
                    effect=iam.Effect.ALLOW,
                    actions=["glue:GetTable", "glue:GetDatabase", "glue:UpdateTable"],
                    resources=[
                        f"arn:aws:glue:{Aws.REGION}:{Aws.ACCOUNT_ID}:catalog",
                        f"arn:aws:glue:{Aws.REGION}:{Aws.ACCOUNT_ID}:catalog/s3tablescatalog",
                        f"arn:aws:glue:{Aws.REGION}:{Aws.ACCOUNT_ID}:catalog/s3tablescatalog/*",
                        f"arn:aws:glue:{Aws.REGION}:{Aws.ACCOUNT_ID}:database/s3tablescatalog/{table_bucket_name}/{namespace_name}",
                        f"arn:aws:glue:{Aws.REGION}:{Aws.ACCOUNT_ID}:table/s3tablescatalog/{table_bucket_name}/{namespace_name}/{table_name}"
                    ],
                ),
                iam.PolicyStatement(
                    sid="WhenDoingMetadataReadsANDDataAndMetadataWriteViaLakeformation",
                    effect=iam.Effect.ALLOW,
                    actions=["lakeformation:GetDataAccess"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    sid="S3DeliveryErrorBucketPermission",
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:Get*",
                        "s3:List*",
                        "s3:AbortMultipartUpload",
                        "s3:PutObject",
                        "s3:DeleteObject",
                    ],
                    # Lock down below to error delivery bucket
                    resources=[
                        f"{errors_output_bucket.bucket_arn}",
                        f"{errors_output_bucket.bucket_arn}/{errors_output_prefix}*",
                    ],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["kms:Decrypt", "kms:GenerateDataKey"],
                    resources=[f"arn:aws:kms:{Aws.REGION}:{Aws.ACCOUNT_ID}:key/*"],
                    conditions={
                        "StringEquals": {"kms:ViaService": "s3.us-east-1.amazonaws.com"},
                        "StringLike": {
                            "kms:EncryptionContext:aws:s3:arn": f"{errors_output_bucket.bucket_arn}/{errors_output_prefix}*"
                        },
                    },
                ),
            ]
        )
        firehose.role.attach_inline_policy(self.inline_policy)

        # Needed when LakeFormation perms are enabled (which is best practice)
        lakeformation.CfnPermissions(
            self,
            f"{table_name.replace('_', '-')}-lf-table-permissions-for-firehose",
            permissions=["ALL"],
            permissions_with_grant_option=[],
            data_lake_principal=lakeformation.CfnPermissions.DataLakePrincipalProperty(
                data_lake_principal_identifier=firehose.role.role_arn
            ),
            resource=lakeformation.CfnPermissions.ResourceProperty(
                table_resource=lakeformation.CfnPermissions.TableResourceProperty(
                    catalog_id=f"{Aws.ACCOUNT_ID}:s3tablescatalog/{table_bucket_name}",
                    database_name=namespace_name,
                    name=table_name,
                )
            ),
        )

        # Now for actual destination config
        configuration = {
            "role_arn": firehose.role.role_arn,
            "catalog_configuration": aws_kinesisfirehose.CfnDeliveryStream.CatalogConfigurationProperty(
                catalog_arn=f"arn:aws:glue:{Aws.REGION}:{Aws.ACCOUNT_ID}:catalog/s3tablescatalog/{table_bucket_name}"
            ),
            "buffering_hints": aws_kinesisfirehose.CfnDeliveryStream.BufferingHintsProperty(
                interval_in_seconds=buffer_interval_secs, size_in_m_bs=buffer_size_mb
            ),
            "cloud_watch_logging_options": aws_kinesisfirehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                enabled=True,
                log_group_name=firehose.log_group.log_group_name,
                log_stream_name=firehose.log_stream.log_stream_name,
            ),
            "destination_table_configuration_list": [
                aws_kinesisfirehose.CfnDeliveryStream.DestinationTableConfigurationProperty(
                    destination_database_name=namespace_name,
                    destination_table_name=table_name,
                    # unique_keys=unique_keys,  # TODO: confirm inherited from table config
                )
            ],
            "append_only": append_only,
            "s3_backup_mode": "FailedDataOnly",
            # s3_configuraiton is not optional (at least w/ above line?)
            "s3_configuration": aws_kinesisfirehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
                    bucket_arn=errors_output_bucket.bucket_arn,
                    role_arn=firehose.role.role_arn,
                    error_output_prefix=errors_output_prefix,
                    compression_format="UNCOMPRESSED",
            )
        }
        if not append_only:
            configuration["processing_configuration"] = (
                aws_kinesisfirehose.CfnDeliveryStream.ProcessingConfigurationProperty(
                    enabled=True,
                    processors=[
                        aws_kinesisfirehose.CfnDeliveryStream.ProcessorProperty(
                            type="MetadataExtraction",
                            parameters=[
                                aws_kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                    parameter_name="MetadataExtractionQuery",
                                    parameter_value="{" '"operation": "update"' "}",
                                ),
                                aws_kinesisfirehose.CfnDeliveryStream.ProcessorParameterProperty(
                                    parameter_name="JsonParsingEngine", parameter_value="JQ-1.6"
                                ),
                            ],
                        )
                    ],
                )
            )
        self.destination_configuration = aws_kinesisfirehose.CfnDeliveryStream.IcebergDestinationConfigurationProperty(**configuration)





