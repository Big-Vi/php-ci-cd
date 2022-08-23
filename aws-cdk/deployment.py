from typing import Any

from aws_cdk import (
    aws_ec2 as ec2,
    Stack, Stage
)
from constructs import Construct

from database.infrastructure import Database
from ecs.infrastructure import EcsCluster


class ECSApplication(Stage):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        instance_type: ec2.InstanceType,
        **kwargs: Any,
    ):
        super().__init__(scope, id_, **kwargs)

        stateful = Stack(self, "Stateful")
        database = Database(
            stateful, "Database", instance_type = instance_type
        )

        stateless = Stack(self, "Stateless")
        ecs = EcsCluster(
            stateless,
            "ECS",
            database_secret_name = database._secret_name
        )
