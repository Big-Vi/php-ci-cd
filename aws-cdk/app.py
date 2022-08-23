#!/usr/bin/env python3
import aws_cdk as cdk

import constants
from pipeline import Pipeline
from Base import Base

app = cdk.App()

# ECR
Base(app, f"{constants.CDK_APP_NAME}-Base")

# Pipeline
pipeline = Pipeline(app, f"{constants.CDK_APP_NAME}-Pipeline",
                 env=constants.PIPELINE_ENV)

app.synth()
