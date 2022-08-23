from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    Stack, RemovalPolicy, CfnOutput
)
from constructs import Construct
from aws_cdk.aws_secretsmanager import Secret


class Database(Construct):

    def __init__(self, scope: Construct, id: str, instance_type: ec2.InstanceType, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        @property
        def db_endpoint(self):
            return self._db_endpoint

        @property
        def secret_name(self):
            return self._secret_name

        vpc = ec2.Vpc.from_lookup(
            self, "VPC",
            vpc_id="vpc-0a2eb88f37dd4d313",
        )

        vpc_subnets = ec2.SubnetSelection(
            subnets=[
                ec2.Subnet.from_subnet_id(
                    self, "subnet1", "subnet-025da55a2ea069297"),
                ec2.Subnet.from_subnet_id(
                    self, "subnet2", "subnet-090a11611b7237db6")
            ]
        )

        security_group = ec2.SecurityGroup.from_lookup_by_id(
            self, "SG", "sg-0cf6eb022d5597677")

        # db_secret = Secret.from_secret_name_v2(
        #     self, "DBSecret", "prod/php-app")

        dbInstance = rds.DatabaseInstance(
            self, "RDS",
            database_name="php_ci_cd",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_5_7_37
            ),
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=[security_group],
            port=3306,
            instance_type=instance_type,
            # instance_type=ec2.InstanceType.of(
            #     ec2.InstanceClass.BURSTABLE3,
            #     ec2.InstanceSize.MICRO
            # ),
            credentials=rds.Credentials.from_generated_secret("admin"),
            publicly_accessible=True,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False
        )

        # self._db_endpoint = CfnOutput(self, "dbEndpoint",
        #                               value=dbInstance.instance_endpoint.hostname, export_name="dbEndpoint")
        # self._secret_name = CfnOutput(self, "secretName",
        #                               value=dbInstance.secret.secret_name, export_name="secretName")

        self._secret_name = dbInstance.secret.secret_name
