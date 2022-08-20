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

CDK_APP_NAME = "UserManagementBackend"
CDK_APP_PYTHON_VERSION = "3.7"

# pylint: disable=line-too-long
GITHUB_CONNECTION_ARN = "arn:aws:codestar-connections:ap-southeast-2:090426658505:connection/62360df3-b12d-4a67-a60c-ccace1f34dc0"
GITHUB_OWNER = "big-vi"
GITHUB_REPO = "aws-cdk-python"
GITHUB_TRUNK_BRANCH = "main"

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

PIPELINE_ENV = Environment(account="090426658505", region="ap-southeast-2")

PROD_ENV = Environment(account="090426658505", region="ap-southeast-2")
