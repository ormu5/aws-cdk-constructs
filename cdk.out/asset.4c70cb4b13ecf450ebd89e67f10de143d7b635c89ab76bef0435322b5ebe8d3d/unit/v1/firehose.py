from aws_cdk import (
    Aws,
    aws_iam as iam,
    aws_kinesisfirehose as firehose,
    aws_logs as logs,
)
from constructs import Construct

from cloudformation_ import inject_canonical_id


@inject_canonical_id
class Firehose(Construct):
    """
    Firehose destinations should be passed as kwargs, exactly one is required.
    Pass a Cloudwatch alarms topic to surface alarms generated via Firehose errors.
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        name: str,
        type_: str = "DirectPut",  # or "KinesisStreamAsSource"
        **kwargs
    ) -> None:
        super().__init__(scope, f"{id}-{name}")

        self.id = id
        self.name = name
        self.type_ = type_
        self.kwargs = kwargs
        self.firehose_delivery_stream: firehose.CfnDeliveryStream | None = None

        # Trust policy for firehose principal
        self.role = iam.Role(
            self,
            f"{name}-firehose-role-v1",
            assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"),
        )

        # Logging and alarms

        self.log_group = logs.LogGroup(
            self,
            f"{name}-firehose-log-group-v1",
        )
        self.log_stream = logs.LogStream(
            self,
            f"{name}-firehose-log-stream-v1",
            log_group=self.log_group,
        )
        self.log_group.grant_write(self.role)

    def add_destination(self, destination_configuration: dict) -> None:
        """Allows for partial init of firehose to be passed to other CDK constructs (e.g.,
        destination configuration constructs themselves), accommodates additional keywords
        specific to firehose."""
        self.firehose_delivery_stream = firehose.CfnDeliveryStream(
            self,
            self.id,
            delivery_stream_name=self.name,
            delivery_stream_type=self.type_,
            **(self.kwargs | destination_configuration)
        )



