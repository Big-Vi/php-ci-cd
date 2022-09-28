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
GITHUB_OWNER = "Big-Vi"
GITHUB_REPO = "php-ci-cd"
GITHUB_TRUNK_BRANCH = "main"

DEV_DATABASE_INSTANCE_TYPE = ec2.InstanceType.of(
    ec2.InstanceClass.BURSTABLE3,
    ec2.InstanceSize.MICRO
)

PROD_DATABASE_INSTANCE_TYPE = ec2.InstanceType.of(
    ec2.InstanceClass.BURSTABLE3,
    ec2.InstanceSize.MICRO
)

INFRA_DEV = {
    "DB_NAME": "php_ci_cd_dev",
    "SECRET_ENV": "dev/php_ci_cd",
    "DATABASE_INSTANCE_TYPE": DEV_DATABASE_INSTANCE_TYPE,
    "ELASTICACHE_NODE_TYPE": "cache.t3.micro",
    "DOMAIN_NAME": "test.resumeonthefly.com",
    "CERTIFICATE_ARN": "arn:aws:acm:ap-southeast-2:090426658505:certificate/68449ec6-263b-415d-aaad-3035434d83f3"
}
INFRA_PROD = {
    "DB_NAME": "php_ci_cd_prod",
    "SECRET_ENV": "prod/php_ci_cd",
    "DATABASE_INSTANCE_TYPE": PROD_DATABASE_INSTANCE_TYPE,
    "ELASTICACHE_NODE_TYPE": "cache.t3.micro",
    "DOMAIN_NAME": "resumeonthefly.com",
    "CERTIFICATE_ARN": "arn:aws:acm:ap-southeast-2:090426658505:certificate/68449ec6-263b-415d-aaad-3035434d83f3"
}

AWS_PIPELINE_ENV = Environment(account="090426658505", region="ap-southeast-2")

AWS_DEV_ENV = Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])

AWS_PROD_ENV = Environment(account="090426658505", region="ap-southeast-2")
