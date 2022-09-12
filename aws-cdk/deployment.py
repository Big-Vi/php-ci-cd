from typing import Any, Dict

from aws_cdk import (
    aws_ec2 as ec2,
    Stack, Stage
)
from constructs import Construct

from database.infrastructure import Database
from ecs.infrastructure import EcsCluster
from elasticache.infrastructure import Elasticache


class ECSApplication(Stage):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        deploy_env: str,
        infra: Dict[str, str],
        **kwargs: Any,
    ):
        super().__init__(scope, id_, **kwargs)

        stateful = Stack(self, "Stateful")
        database = Database(
            stateful, "Database", infra=infra, deploy_env=deploy_env
        )
        elasticache = Elasticache(
            stateful, "Elasticache", infra=infra, deploy_env=deploy_env
        )

        stateless = Stack(self, "Stateless")
        ecs = EcsCluster(
            stateless,
            "ECS",
            database_secret_name=database._secret_name,
            elasticache_endpoint=elasticache._elasticache_endpoint,
            infra=infra
        )
