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
        synth_codebuild_step = pipelines.CodeBuildStep(
            "Synth",
            input=codepipeline_source,
            build_environment=codebuild.BuildEnvironment(
                privileged=True,
            ),
            commands=[
                "cd infra",  # Installs the cdk cli on Codebuild
                "npm install -g aws-cdk",
                # Instructs Codebuild to install required packages
                "pip install -r requirements.txt",
                "cdk synth",
            ],
            primary_output_directory="infra/cdk.out",
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
        )
        dev_stage = ECSApplication(
            self,
            f"{constants.CDK_APP_NAME}-Dev",
            env=constants.AWS_PROD_ENV,
            infra=constants.INFRA_DEV
        )

        codepipeline.add_stage(dev_stage)

        # prod_stage = ECSApplication(
        #     self,
        #     f"{constants.CDK_APP_NAME}-Prod",
        #     env=constants.AWS_PROD_ENV,
        #     infra=constants.INFRA_PROD
        # )

        # codepipeline.add_stage(
        #     prod_stage,
        #     pre=[
        #         pipelines.ManualApprovalStep(
        #             "PromoteToProd")
        #     ]
        # )
