from aws_cdk import (
    aws_ecr as ecr,
    aws_secretsmanager as secretsmanager,
    App, RemovalPolicy, Stack
)
from constructs import Construct
from typing import Any

import constants


class Base(Stack):

    def __init__(self, scope: Construct, id_: str, **kwargs: Any):
        super().__init__(scope, id_, **kwargs)

        # ecr repo
        ecr.Repository(
            self, "ECR",
            repository_name=constants.CDK_APP_NAME,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Secret for git commit hash - needed for CloudFormation dynamically pull it.
        # secretsmanager.Secret(
        #     self, "secret-git-commit-hash",
        #     secret_name = "php-ci-cd/git"
        # )
