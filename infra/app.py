#!/usr/bin/env python3
import aws_cdk as cdk

import constants
from pipeline import Pipeline

app = cdk.App()

# Pipeline
pipeline = Pipeline(app, f"{constants.CDK_APP_NAME}-Pipeline",
                    env=constants.AWS_PIPELINE_ENV)

app.synth()
