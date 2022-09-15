import constants
from typing import Dict
from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticache as elasticache
)
from constructs import Construct


class Elasticache(Construct):

    def __init__(self, scope: Construct, id: str, infra: Dict[str, str], deploy_env=str, ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        redis_subnet_group = elasticache.CfnSubnetGroup(
            scope=self,
            id="redis_subnet_group",
            subnet_ids=[constants.INFRA_COMMON["SUBNET_IDS"]["SUBNET_ID_1"],
                        constants.INFRA_COMMON["SUBNET_IDS"]["SUBNET_ID_2"]],
            description="subnet group for redis"
        )

        elasticache_cluster = elasticache.CfnCacheCluster(
            self, "MyCfnCacheCluster",
            cache_node_type=infra["ELASTICACHE_NODE_TYPE"],
            engine="redis",
            num_cache_nodes=1,
            cache_subnet_group_name=redis_subnet_group.ref,
            vpc_security_group_ids=[constants.INFRA_COMMON["SG_ID"]]
        )

        self._elasticache_endpoint = elasticache_cluster.attr_redis_endpoint_address
