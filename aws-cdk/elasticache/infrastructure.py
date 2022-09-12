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

        vpc = ec2.Vpc.from_lookup(
            self, "VPC",
            vpc_id=infra["VPC_ID"],
        )

        vpc_subnets = ec2.SubnetSelection(
            subnets=[
                ec2.Subnet.from_subnet_id(
                    self, "subnet1", infra["SUBNET_IDS"]["SUBNET_ID_1"]),
                ec2.Subnet.from_subnet_id(
                    self, "subnet2", infra["SUBNET_IDS"]["SUBNET_ID_2"])
            ]
        )

        security_group = ec2.SecurityGroup.from_lookup_by_id(
            self, "SG", infra["SG_ID"])

        elasticache_cluster = elasticache.CfnCacheCluster(
            self, "MyCfnCacheCluster",
            cache_node_type="cache.t3.micro",
            engine="redis",
            num_cache_nodes=1,
            vpc_security_group_ids=[infra["SG_ID"]]
        )

        self._elasticache_endpoint = elasticache_cluster.attr_redis_endpoint_address
