import json
import pathlib
from typing import Any

from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_ecr as ecr,
    pipelines,
    Stack, RemovalPolicy
)
from constructs import Construct

import constants

from deployment import ECSApplication


class Pipeline(Stack):
    def __init__(self, scope: Construct, id_: str, ** kwargs: Any):
        super().__init__(scope, id_, **kwargs)

        codepipeline_source = pipelines.CodePipelineSource.connection(
            f"{constants.GITHUB_OWNER}/{constants.GITHUB_REPO}",
            constants.GITHUB_TRUNK_BRANCH,
            connection_arn=constants.GITHUB_CONNECTION_ARN,
            trigger_on_push=True,
        )
        synth_python_version = {
            "phases": {
                "install": {
                    "runtime-versions": {"python": constants.CDK_APP_PYTHON_VERSION},
                    "commands": [
                        "nohup /usr/local/bin/dockerd --host=unix:///var/run/docker.sock --host=tcp://127.0.0.1:2375 --storage-driver=overlay2&",
                        "timeout 15 sh -c \"until docker info; do echo .; sleep 1; done\""
                    ]
                },
                "pre_build": {
                    "commands": [
                        "REPO_BASE=090426658505.dkr.ecr.ap-southeast-2.amazonaws.com",
                        "REPO_NAME=" + constants.CDK_APP_NAME,
                        "TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | head -c 8)",
                        "aws secretsmanager update-secret --secret-id " + constants.CDK_APP_NAME + "/git-hash \
                            --secret-string '{\"commit-hash\": \"'${TAG}'\"}'",
                        "aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin \"$REPO_BASE\"",
                    ]
                },
                "build": {
                    "commands": [
                        "docker build -t \"$REPO_BASE/$REPO_NAME:latest\" --build-arg env=" +
                        constants.ENV + " .",
                        "docker tag \"$REPO_BASE/$REPO_NAME:latest\" \"$REPO_BASE/$REPO_NAME:$TAG\""
                    ]
                },
                "post_build": {
                    "commands": [
                        "docker push $REPO_BASE/$REPO_NAME:$TAG",
                        "docker push $REPO_BASE/$REPO_NAME:latest",
                        "printf [{\"name\":\"$REPO_NAME\"\,\"imageUri\":\"090426658505.dkr.ecr.ap-southeast-2.amazonaws.com/$REPO_NAME:$TAG\"}] > imagedefinitions.json"
                    ]
                }
            },
            # "artifacts": {
            #     "files": ["imagedefinitions.json"]
            # }
        }
        synth_codebuild_step = pipelines.CodeBuildStep(
            "Synth",
            input=codepipeline_source,
            build_environment=codebuild.BuildEnvironment(
                privileged=True,
            ),
            # partial_build_spec=codebuild.BuildSpec.from_object(
            #     synth_python_version),
            # install_commands=["./scripts/install-deps.sh"],
            commands=[
                "cd aws-cdk",  # Installs the cdk cli on Codebuild
                "npm install -g aws-cdk",
                # Instructs Codebuild to install required packages
                "pip install -r requirements.txt",
                "cdk synth",
            ],
            primary_output_directory="aws-cdk/cdk.out",
            role_policy_statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
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
                        "ecr:PutImage",
                        "ecr:CreateRepository",
                        "sts:AssumeRole",
                        "secretsmanager:CreateSecret",
                        "secretsmanager:UpdateSecret"
                    ],
                    resources=["*"]
                )
            ]
        )
        codepipeline = pipelines.CodePipeline(
            self,
            "CodePipeline",
            # self_mutation=False,
            synth=synth_codebuild_step,
            # docker_enabled_for_self_mutation=True,
            # docker_enabled_for_synth=True,
        )

        self._add_dev_stage(codepipeline)

    def _add_dev_stage(self, codepipeline: pipelines.CodePipeline) -> None:
        prod_stage = ECSApplication(
            self,
            f"{constants.CDK_APP_NAME}-Dev",
            env=constants.AWS_DEV_ENV,
            infra=constants.INFRA_DEV
        )

        codepipeline.add_stage(prod_stage)
