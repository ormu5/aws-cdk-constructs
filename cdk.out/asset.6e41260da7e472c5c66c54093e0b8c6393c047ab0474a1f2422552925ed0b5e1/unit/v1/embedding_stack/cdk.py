from aws_cdk import Stack, aws_iam as iam, aws_lambda as lambda_, Duration
from aws_cdk.aws_ecr_assets import Platform
from aws_cdk.aws_lambda import Architecture

from constructs import Construct

class EmbeddingStack(Stack):
    """One agent per stack."""
    def __init__(
            self, scope: Construct, *,
            name: str,
            **kwargs
    ) -> None:
        stack_id = "-".join([name, "stack"])
        super().__init__(scope, stack_id, **kwargs)

        self.embedding_lambda = lambda_.DockerImageFunction(
            self,
            id="-".join([name, "lambda"]),
            function_name="-".join([name, "lambda"]),
            code=lambda_.DockerImageCode.from_image_asset(
                directory="./",  # Build context: project root
                cmd=["handler.handler"],
                platform=Platform.LINUX_AMD64,
                asset_name="-".join([name, "lambda"]),
                file="unit/v1/embedding_stack/Dockerfile",
            ),
            architecture=Architecture.X86_64,
            memory_size=1024,  # MB
            timeout=Duration.seconds(10),
        )
