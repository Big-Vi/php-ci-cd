#!/usr/bin/env python3
import aws_cdk as cdk

from Pipeline import Pipeline

props = {'namespace': 'cdk-pipeline'}

app = cdk.App()

Pipeline(app, f"{props['namespace']}-pipeline", props)

app.synth()









