from constructs import Construct
from aws_cdk import (
    Stack, Duration,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    SecretValue
)
import aws_cdk.aws_iam as iam


class Pipeline(Stack):

    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="Source",
            owner="Big-Vi",
            repo="php-ci-cd",
            branch="main",
            oauth_token=SecretValue.secrets_manager(
                "git", json_field='access-token'),
            output=source_output,
        )

        cb_docker_build = codebuild.PipelineProject(
            self, "DockerBuild",
            project_name=f"{props['namespace']}-Docker-Build",
            environment=codebuild.BuildEnvironment(
                privileged=True,
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0
            ),
            description='Pipeline for CodeBuild',
            timeout=Duration.minutes(60),
        )
        
        cb_docker_build.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW, 
            actions= [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetRepositoryPolicy",
                "ecr:DescribeRepositories",
                "ecr:ListImages",
                "ecr:DescribeImages",
                "ecr:BatchGetImage",
                "ecr:GetLifecyclePolicy",
                "ecr:GetLifecyclePolicyPreview",
                "ecr:ListTagsForResource",
                "ecr:DescribeImageScanFindings",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
            ],
            resources=["*"]
        ))

        pipeline = codepipeline.Pipeline(
            self,
            "Pipeline",
            pipeline_name=f"{props['namespace']}",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source", actions=[source_action]),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="Build",
                            project=cb_docker_build,
                            input=source_output,
                        )
                    ]
                )
            ]
        )
