from constructs import Construct
from aws_cdk import (
    aws_s3 as aws_s3,
    aws_ecr,
    aws_codebuild,
    App, CfnOutput, Duration, RemovalPolicy, Stack
)

class Base(Stack):
    def __init__(self, app: App, id: str, props, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # ecr repo to push docker container into
        ecr = aws_ecr.Repository(
            self, "ECR",
            repository_name=f"{props['namespace']}",
            removal_policy=RemovalPolicy.DESTROY
        )
        # codebuild project meant to run in pipeline
        cb_docker_build = aws_codebuild.PipelineProject(
            self, "DockerBuild",
            project_name=f"{props['namespace']}-Docker-Build",
            build_spec=aws_codebuild.BuildSpec.from_source_filename(
                filename='../buildspec.yml'),
            environment=aws_codebuild.BuildEnvironment(
                privileged=True,
            ),
            # pass the ecr repo uri into the codebuild project so codebuild knows where to push
            environment_variables={
                'ecr': aws_codebuild.BuildEnvironmentVariable(
                    value=ecr.repository_uri),
                'tag': aws_codebuild.BuildEnvironmentVariable(
                    value='cdk')
            },
            description='Pipeline for CodeBuild',
            timeout=Duration.minutes(60),
        )

        # codebuild permissions to interact with ecr
        ecr.grant_pull_push(cb_docker_build)

        CfnOutput(
            self, "ECRURI",
            description="ECR URI",
            value=ecr.repository_uri,
        )

        self.output_props = props.copy()
        self.output_props['cb_docker_build'] = cb_docker_build

    # pass objects to another stack
    @property
    def outputs(self):
        return self.output_props
