from aws_cdk import (
    aws_ecr as ecr,
    App, RemovalPolicy, Stack
)
import constants

class Base(Stack):
    def __init__(self, app: App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # ecr repo to push docker container into
        # ecr repo to push docker container into
        app_ecr = ecr.Repository.from_repository_name(
            self, "ECR", constants.CDK_APP_NAME)
        if not app_ecr:
            ecr.Repository(
                self, "ECR",
                repository_name=constants.CDK_APP_NAME,
                removal_policy=RemovalPolicy.DESTROY
            )

        # codebuild permissions to interact with ecr
        # ecr.grant_pull_push(cb_docker_build)
