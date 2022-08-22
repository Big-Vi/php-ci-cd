# from constructs import Construct
# from aws_cdk import (
#     Stack, Duration,
#     aws_codepipeline as codepipeline,
#     aws_ecs as ecs,
#     aws_ec2 as ec2,
#     aws_s3 as s3,
#     aws_kms as kms,
#     aws_codepipeline_actions as codepipeline_actions,
#     aws_codebuild as codebuild,
#     SecretValue, Duration, Fn, RemovalPolicy, Arn, ArnComponents
# )
# import aws_cdk.aws_iam as iam


# class Pipeline(Stack):

#     def __init__(self, scope: Construct, id: str, **kwargs) -> None:
#         super().__init__(scope, id, **kwargs)

#         source_output = codepipeline.Artifact()

#         kms_key = kms.Key(
#             self, "Key",
#             removal_policy=RemovalPolicy.DESTROY
#         )

#         bucket = s3.Bucket(
#             self, 'ArtifactBucket',
#             bucket_name="php-artifact-bucket",
#             # encryption=s3.BucketEncryption.KMS,
#             encryption_key=kms_key,
#             auto_delete_objects=True,
#             removal_policy=RemovalPolicy.DESTROY
#         )

#         source_action = codepipeline_actions.GitHubSourceAction(
#             action_name="Source",
#             owner="Big-Vi",
#             repo="php-ci-cd",
#             branch="main",
#             oauth_token=SecretValue.secrets_manager(
#                 "prod/php-app", json_field='access_token'),
#             output=codepipeline.Artifact(bucket.bucket_name),
#         )

#         cb_docker_build = codebuild.PipelineProject(
#             self, "DockerBuild",
#             # project_name=f"{props['namespace']}-Docker-Build",
#             environment=codebuild.BuildEnvironment(
#                 privileged=True,
#                 build_image=codebuild.LinuxBuildImage.STANDARD_5_0
#             ),
#             description='Pipeline for CodeBuild',
#             timeout=Duration.minutes(60),
#         )

#         cb_docker_build.add_to_role_policy(iam.PolicyStatement(
#             effect=iam.Effect.ALLOW,
#             actions=[
#                 "ecr:GetAuthorizationToken",
#                 "ecr:BatchCheckLayerAvailability",
#                 "ecr:GetDownloadUrlForLayer",
#                 "ecr:GetRepositoryPolicy",
#                 "ecr:DescribeRepositories",
#                 "ecr:ListImages",
#                 "ecr:DescribeImages",
#                 "ecr:BatchGetImage",
#                 "ecr:GetLifecyclePolicy",
#                 "ecr:GetLifecyclePolicyPreview",
#                 "ecr:ListTagsForResource",
#                 "ecr:DescribeImageScanFindings",
#                 "ecr:InitiateLayerUpload",
#                 "ecr:UploadLayerPart",
#                 "ecr:CompleteLayerUpload",
#                 "ecr:PutImage"
#             ],
#             resources=["*"]
#         ))

#         vpc = ec2.Vpc.from_lookup(
#             self, "VPC",
#             vpc_id="vpc-0a2eb88f37dd4d313",
#         )
#         security_group = ec2.SecurityGroup.from_lookup_by_id(
#             self, "SG", "sg-0cf6eb022d5597677")

#         fargate_service = ecs.FargateService.from_fargate_service_attributes(
#             self, "Service",
#             cluster=ecs.Cluster.from_cluster_attributes(
#                 self, "Cluster",
#                 cluster_name=Fn.import_value("ClusterName"),
#                 vpc=vpc,
#                 security_groups=[security_group]
#             ),
#             service_name=Fn.import_value("FargateServiceName")
#         )

#         pipeline = codepipeline.Pipeline(
#             self,
#             "PipelinePHP",
#             artifact_bucket=bucket,
#             # pipeline_name=f"{props['namespace']}",
#             stages=[
#                 codepipeline.StageProps(
#                     stage_name="Source", actions=[source_action]),
#                 codepipeline.StageProps(
#                     stage_name="Build",
#                     actions=[
#                         codepipeline_actions.CodeBuildAction(
#                             action_name="Build",
#                             project=cb_docker_build,
#                             # input=source_output,
#                             input=codepipeline.Artifact(bucket.bucket_name),
#                         )
#                     ]
#                 ),
#                 codepipeline.StageProps(
#                     stage_name="Deploy",
#                     actions=[
#                         codepipeline_actions.EcsDeployAction(
#                             action_name="DeployAction",
#                             service=fargate_service,
#                             input=codepipeline.Artifact(bucket.bucket_name),
#                             deployment_timeout=Duration.minutes(60)
#                         )
#                     ]
#                 ),
#                 codepipeline.StageProps(
#                     stage_name="Approve",
#                     actions=[
#                         codepipeline_actions.ManualApprovalAction(
#                             action_name="DeployAction",
#                         )
#                     ]
#                 )
#             ]
#         )

#         # approve_stage = pipeline.add_stage(stage_name="Approve")

#         # manual_approval_action = codepipeline_actions.ManualApprovalAction(
#         #     action_name="Approve"
#         # )
#         # approve_stage.add_action(manual_approval_action)

#         # role = iam.Role.from_role_arn(self, "Admin", Arn.format(
#         #     ArnComponents(service="iam", resource="role", resource_name="Admin"), self))
#         # manual_approval_action.grant_manual_approval(role)

import json
import pathlib
from typing import Any

from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
    pipelines,
    Stack
)
from constructs import Construct

import constants

from deployment import UserManagementBackend


class Pipeline(Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs: Any):
        super().__init__(scope, id_, **kwargs)

        codepipeline_source = pipelines.CodePipelineSource.connection(
            f"{constants.GITHUB_OWNER}/{constants.GITHUB_REPO}",
            constants.GITHUB_TRUNK_BRANCH,
            connection_arn=constants.GITHUB_CONNECTION_ARN,
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
                        "REPO_NAME=php-" + constants.ENV,
                        "TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | head -c 8)",
                        "aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin \"$REPO_BASE\""
                    ]
                },
                "build": {
                    "commands": [
                        "docker build -t \"$REPO_BASE/$REPO_NAME:latest\" --build-arg env=" + constants.ENV + " .",
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
            partial_build_spec=codebuild.BuildSpec.from_object(
                synth_python_version),
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
                        "sts:AssumeRole"
                    ],
                    resources=["*"]
                )
            ]
        )
        codepipeline = pipelines.CodePipeline(
            self,
            "CodePipeline",
            # self_mutation=False,
            # cli_version=Pipeline._get_cdk_cli_version(),
            # cross_account_keys=True,
            synth=synth_codebuild_step,
            # docker_enabled_for_synth=True,
        )

        # self._add_prod_stage(codepipeline)

    @staticmethod
    def _get_cdk_cli_version() -> str:
        package_json_path = (
            pathlib.Path(__file__).resolve().parent.joinpath(
                "./aws-cdk/package.json")
        )
        with open(package_json_path) as package_json_file:
            package_json = json.load(package_json_file)
        cdk_cli_version = str(package_json["devDependencies"]["aws-cdk"])
        return cdk_cli_version

    def _add_prod_stage(self, codepipeline: pipelines.CodePipeline) -> None:
        prod_stage = UserManagementBackend(
            self,
            f"{constants.CDK_APP_NAME}-Prod",
            env=constants.PROD_ENV,
            instance_type=constants.PROD_DATABASE_INSTANCE_TYPE,
        )

        codepipeline.add_stage(prod_stage)
