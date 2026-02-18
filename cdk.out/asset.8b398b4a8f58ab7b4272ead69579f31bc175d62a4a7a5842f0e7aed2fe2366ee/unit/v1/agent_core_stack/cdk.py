from aws_cdk import Stack, aws_iam as iam
from constructs import Construct

import boto3
import aws_cdk.aws_bedrock_agentcore_alpha as agentcore

s3vectors_client = boto3.client("s3vectors")
bedrock_client = boto3.client("bedrock-runtime")

class AgentCoreRuntimeStack(Stack):
    """One agent per stack."""
    def __init__(
            self, scope: Construct, *,
            runtime_name: str,
            **kwargs
    ) -> None:
        stack_id = "-".join([runtime_name, "stack"])
        super().__init__(scope, stack_id, **kwargs)

        runtime = agentcore.Runtime(
            self,
            "agent-runtime",
            runtime_name=runtime_name,
            agent_runtime_artifact=agentcore.AgentRuntimeArtifact.from_asset("unit/v1/agent_core_stack"),
        )

        # TODO: tighten to specific vector store(s)
        runtime.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "s3vectors:QueryVectors",
                    # Required if you use metadata filters OR want metadata/vector data back
                    "s3vectors:GetVectors",
                ],
                resources=["*"],
            )
        )
        # TODO: tighten to specific model
        runtime.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                resources=["*"],
            )
        )