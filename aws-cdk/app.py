#!/usr/bin/env python3
import aws_cdk as cdk

import constants
from pipeline import Pipeline
# from rds.RDSStack import RDSStack
# from ecs.EcsCluster import EcsCluster
from deployment import ECSApplication

app = cdk.App()

# env = Environment(account = "090426658505", region = "ap-southeast-2")

# rds_stack = RDSStack(
#     app, "RDS-Stack", env=env)
# ecs_stack = EcsCluster(
#     app, "ECS-Stack", env=env)

# pipeline = Pipeline(app, f"{props['namespace']}-pipeline", props,
#                     env=env)

# ecs_stack.node.add_dependency(rds_stack)
# pipeline.node.add_dependency(ecs_stack)

# Development
# ECSApplication(
#     app,
#     f"{constants.CDK_APP_NAME}-Dev",
#     env=constants.DEV_ENV,
#     instance_type=constants.DEV_DATABASE_INSTANCE_TYPE,
# )

# Production pipeline
Pipeline(app, f"{constants.CDK_APP_NAME}-Pipeline", env=constants.PIPELINE_ENV)

app.synth()
