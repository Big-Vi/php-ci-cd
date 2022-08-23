#!/usr/bin/env python3
import aws_cdk as cdk

import constants
from pipeline import Pipeline

app = cdk.App()

# Pipeline
Pipeline(app, f"{constants.CDK_APP_NAME}-Pipeline", env=constants.PIPELINE_ENV)

app.synth()
