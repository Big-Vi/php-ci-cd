from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    Stack, RemovalPolicy, 
)
from constructs import Construct
from aws_cdk.aws_secretsmanager import Secret

class RDSStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(
            self, "VPC",
            vpc_id="vpc-0a2eb88f37dd4d313",
        )

        db_secret = Secret.from_secret_name_v2(
            self, "DBSecret", "prod/php-app")

        rds.DatabaseInstance(
            self, "RDS",
            database_name="php_ci_cd",
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_5_7_37
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            port=3306,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            credentials=rds.Credentials.from_secret(db_secret),
            publicly_accessible=True,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False
        )
