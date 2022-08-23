# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os

from aws_cdk import (
    aws_ec2 as ec2,
    Environment
)

CDK_APP_NAME = "php-ci-cd"
CDK_APP_PYTHON_VERSION = "3.7"

# pylint: disable=line-too-long
GITHUB_CONNECTION_ARN = "arn:aws:codestar-connections:ap-southeast-2:090426658505:connection/62360df3-b12d-4a67-a60c-ccace1f34dc0"
GITHUB_OWNER = "big-vi"
GITHUB_REPO = "php-ci-cd"
GITHUB_TRUNK_BRANCH = "main"

ENV = "test"

DEV_ENV = Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]
)

DEV_DATABASE_INSTANCE_TYPE = ec2.InstanceType.of(
    ec2.InstanceClass.BURSTABLE3,
    ec2.InstanceSize.MICRO
)

PROD_DATABASE_INSTANCE_TYPE = ec2.InstanceType.of(
    ec2.InstanceClass.BURSTABLE3,
    ec2.InstanceSize.MICRO
)

INFRA = {
    "VPC_ID": "vpc-0a2eb88f37dd4d313",
    "SUBNET_IDS": {
        "SUBNET_ID_1": "subnet-025da55a2ea069297",
        "SUBNET_ID_2": "subnet-090a11611b7237db6"
    },
    "SG_ID": "sg-0cf6eb022d5597677",
    "DB_NAME": "php_ci_cd",
    "DEV_DATABASE_INSTANCE_TYPE": DEV_DATABASE_INSTANCE_TYPE,
    "PROD_DATABASE_INSTANCE_TYPE": PROD_DATABASE_INSTANCE_TYPE
}

PIPELINE_ENV = Environment(account="090426658505", region="ap-southeast-2")

PROD_ENV = Environment(account="090426658505", region="ap-southeast-2")
