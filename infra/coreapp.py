import constants
from typing import Dict
from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    aws_elasticache as elasticache,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    aws_secretsmanager as secretsmanager,
    aws_ecr_assets as ecr_assets,
    aws_certificatemanager as certificatemanager,
    aws_route53 as route53,
    aws_elasticloadbalancingv2 as elasticloadbalancing,
    RemovalPolicy,
    Stack
)
from constructs import Construct


class CoreApp(Stack):

    def __init__(self, scope: Construct, id: str, infra: Dict[str, str], ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self, "VPC",
            subnet_configuration=[ec2.SubnetConfiguration(
                cidr_mask=24,
                name="ingress",
                subnet_type=ec2.SubnetType.PUBLIC
            ), ec2.SubnetConfiguration(
                cidr_mask=28,
                name="rds",
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            )]
        )
        fargate_security_group = ec2.SecurityGroup(
            self, "fargate_security_group",
            security_group_name="fargate_security_group",
            vpc=vpc, allow_all_outbound=True
        )
        fargate_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("0.0.0.0/0"),
            description="Fargate Application",
            connection=ec2.Port.tcp(80),
        )
        fargate_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("0.0.0.0/0"),
            description="Fargate Application",
            connection=ec2.Port.tcp(443),
        )
        db_security_group = ec2.SecurityGroup(
            self, "db_security_group",
            security_group_name="db_security_group",
            vpc=vpc, allow_all_outbound=True
        )
        elasticache_security_group = ec2.SecurityGroup(
            self, "elasticache_security_group",
            security_group_name="elasticache_security_group",
            vpc=vpc, allow_all_outbound=True
        )

        # Add ingress rules to security group
        db_security_group.add_ingress_rule(
            peer=fargate_security_group,
            description="Allow MySQL connection",
            connection=ec2.Port.tcp(3306),
        )
        elasticache_security_group.add_ingress_rule(
            peer=fargate_security_group,
            description="Allow Redis connection",
            connection=ec2.Port.tcp(6379),
        )

        secret = secretsmanager.Secret.from_secret_name_v2(
            self, "SecretFromName", infra["SECRET_ENV"])

        dbInstance = rds.DatabaseInstance(
            self, "RDS",
            database_name=infra["DB_NAME"],
            engine=rds.DatabaseInstanceEngine.mysql(
                version=rds.MysqlEngineVersion.VER_5_7_37
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            port=3306,
            security_groups=[db_security_group],
            instance_type=infra["DATABASE_INSTANCE_TYPE"],
            credentials=rds.Credentials.from_secret(secret),
            publicly_accessible=True,
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False
        )
        selection = vpc.select_subnets(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
        )

        private_subnets_ids = [
            ps.subnet_id for ps in selection.subnets]

        redis_subnet_group = elasticache.CfnSubnetGroup(
            scope=self,
            id="redis_subnet_group",
            subnet_ids=private_subnets_ids,
            description="subnet group for redis"
        )

        elasticache_cluster = elasticache.CfnCacheCluster(
            self, "MyCfnCacheCluster",
            cache_node_type=infra["ELASTICACHE_NODE_TYPE"],
            engine="redis",
            num_cache_nodes=1,
            cache_subnet_group_name=redis_subnet_group.ref,
            vpc_security_group_ids=[
                elasticache_security_group.security_group_id],
        )

        vpc_subnets = ec2.SubnetSelection(
            one_per_az=False,
            subnet_type=ec2.SubnetType.PUBLIC
        )

        self.cluster = ecs.Cluster(
            self, 'EcsCluster',
            vpc=vpc
        )

        ecsTaskExecutionRole = iam.Role(
            self, "ecsTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        ecsTaskExecutionRole.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            "service-role/AmazonECSTaskExecutionRolePolicy"))

        ecrAsset = ecr_assets.DockerImageAsset(
            self, "buildImage",
            directory=(".././"),
        )

        self.fargate_task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef",
            cpu=256,
            execution_role=ecsTaskExecutionRole,
            task_role=ecsTaskExecutionRole,
        )
        self.fargate_cron_task_definition = ecs.FargateTaskDefinition(
            self, "CronTaskDef",
            cpu=256,
            execution_role=ecsTaskExecutionRole,
            task_role=ecsTaskExecutionRole,
        )

        secrets = {
            "SS_DATABASE_PASSWORD": ecs.Secret.from_secrets_manager(secret, "password"),
            "SS_DATABASE_USERNAME": ecs.Secret.from_secrets_manager(secret, "username"),
            "SS_DATABASE_NAME": ecs.Secret.from_secrets_manager(secret, "dbname"),
            "SS_DATABASE_SERVER": ecs.Secret.from_secrets_manager(secret, "host"),
            "SS_DEFAULT_ADMIN_USERNAME": ecs.Secret.from_secrets_manager(secret, "SS_DEFAULT_ADMIN_USERNAME"),
            "SS_DEFAULT_ADMIN_PASSWORD": ecs.Secret.from_secrets_manager(secret, "SS_DEFAULT_ADMIN_PASSWORD"),
        }

        self.fargate_cron_task_definition.add_container(
            constants.CDK_APP_NAME,
            # Use an image from ECR
            image=ecs.ContainerImage.from_docker_image_asset(ecrAsset),
            port_mappings=[ecs.PortMapping(container_port=80)],
            secrets=secrets,
            environment={
                "REDIS_URL": elasticache_cluster.attr_redis_endpoint_address + ":6379"
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs_cron"),
            command=[elasticache_cluster.attr_redis_endpoint_address, "True"]
        )
        self.fargate_cron_service = ecs.FargateService(
            self, "CronService",
            service_name=constants.CDK_APP_NAME + "_cron",
            cluster=self.cluster,
            task_definition=self.fargate_cron_task_definition,
            assign_public_ip=True, vpc_subnets=vpc_subnets,
            desired_count=1,
            enable_execute_command=True,
            security_groups=[fargate_security_group]
        )

        self.fargate_task_definition.add_container(
            constants.CDK_APP_NAME,
            image=ecs.ContainerImage.from_docker_image_asset(ecrAsset),
            port_mappings=[ecs.PortMapping(container_port=80)],
            secrets=secrets,
            environment={
                "REDIS_URL": elasticache_cluster.attr_redis_endpoint_address + ":6379"
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs"),
            command=[elasticache_cluster.attr_redis_endpoint_address, "False"]
        )

        domain_zone = route53.HostedZone.from_lookup(
            self, "Zone", domain_name=constants.INFRA_PROD["DOMAIN_NAME"])
        certificate = certificatemanager.Certificate.from_certificate_arn(
            self, "Cert", constants.INFRA_PROD["CERTIFICATE_ARN"])

        self.fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "CDKFargateService",
            service_name=constants.CDK_APP_NAME,
            cluster=self.cluster, task_definition=self.fargate_task_definition,
            certificate=certificate,
            ssl_policy=elasticloadbalancing.SslPolicy.RECOMMENDED,
            domain_name=infra["DOMAIN_NAME"],
            domain_zone=domain_zone,
            redirect_http=True,
            task_subnets=vpc_subnets, assign_public_ip=True,
            security_groups=[fargate_security_group]
        )

