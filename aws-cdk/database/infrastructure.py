import constants
from typing import Dict
from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    RemovalPolicy,
)
from constructs import Construct


class Database(Construct):

    def __init__(self, scope: Construct, id: str, infra: Dict[str, str], ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(
            self, "VPC",
            vpc_id=constants.INFRA_COMMON["VPC_ID"],
        )

        vpc_subnets = ec2.SubnetSelection(
            subnets=[
                ec2.Subnet.from_subnet_id(
                    self, "subnet1", constants.INFRA_COMMON["SUBNET_IDS"]["SUBNET_ID_1"]),
                ec2.Subnet.from_subnet_id(
                    self, "subnet2", constants.INFRA_COMMON["SUBNET_IDS"]["SUBNET_ID_2"])
            ]
        )

        security_group = ec2.SecurityGroup.from_lookup_by_id(
            self, "SG", constants.INFRA_COMMON["SG_ID"])

        secret = secretsmanager.Secret.from_secret_name_v2(
            self, "SecretFromName", infra["SECRET_ENV"])

        dbInstance = rds.DatabaseInstance(
            self, "RDS",
            database_name=infra["DB_NAME"],
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_5_7_37
            ),
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=[security_group],
            port=3306,
            instance_type=infra["DATABASE_INSTANCE_TYPE"],
            credentials=rds.Credentials.from_secret(secret),
            publicly_accessible=True,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False
        )

        self.db_instance_endpoint_address = dbInstance.db_instance_endpoint_address
