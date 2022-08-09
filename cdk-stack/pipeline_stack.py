from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    SecretValue
)

class MyPipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="Source",
            owner="Big-Vi",
            repo="php-ci-cd",
            branch="main",
            oauth_token=SecretValue.secrets_manager("git", json_field='access-token'),
            output=source_output,
        )

        pipeline = codepipeline.Pipeline(
            self,
            "MyPipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source", actions=[source_action]),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="Build",
                            project=codebuild.PipelineProject(self, "CICD"),
                            input=source_output,
                        )
                    ]
                )
            ]
        )
    