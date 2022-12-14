from typing import Dict
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    aws_secretsmanager as secretsmanager,
    aws_ecr_assets as ecr_assets,
    aws_certificatemanager as certificatemanager,
    aws_route53 as route53,
    aws_elasticloadbalancingv2 as elasticloadbalancing,
    CfnOutput
)
from constructs import Construct

import constants


class EcsCluster(Construct):

    def __init__(self, scope: Construct, id: str, elasticache_endpoint: str, infra: Dict[str, str], ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(
            self, "VPC",
            vpc_id=constants.INFRA_COMMON["VPC_ID"],
        )

        vpc_subnets = ec2.SubnetSelection(
            subnets=[
                ec2.Subnet.from_subnet_id(
                    self, "subnet1", constants.INFRA_COMMON["SUBNET_IDS_PUBLIC"]["SUBNET_ID_1"]),
                ec2.Subnet.from_subnet_id(
                    self, "subnet2", constants.INFRA_COMMON["SUBNET_IDS_PUBLIC"]["SUBNET_ID_2"])
            ]
        )

        fargate_security_group = ec2.SecurityGroup.from_lookup_by_id(
            self, "SG", constants.INFRA_COMMON["SG_ID"])

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

        secret = secretsmanager.Secret.from_secret_name_v2(
            self, "SecretFromName", infra["SECRET_ENV"])

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
                "REDIS_URL": elasticache_endpoint + ":6379"
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs_cron"),
            command=[elasticache_endpoint, "True"]
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
                "REDIS_URL": elasticache_endpoint + ":6379"
            },
            # New Relic Fluentbit Output configuration
            logging=ecs.LogDrivers.firelens(
                options={
                    "Name": "newrelic",
                    "region": "ap-southeast-2",
                    "delivery_stream": "ecs"
                },
                secret_options={
                    "apikey": ecs.Secret.from_secrets_manager(secret, "NEW_RELIC_API_KEY")
                }
            ),
            command=[elasticache_endpoint, "False"]
        )
        self.fargate_task_definition.add_firelens_log_router(
            "firelens-log-router",
            image=ecs.ContainerImage.from_registry(
                "533243300146.dkr.ecr.ap-southeast-2.amazonaws.com/newrelic/logging-firelens-fluentbit"),
            firelens_config=ecs.FirelensConfig(
                type=ecs.FirelensLogRouterType.FLUENTBIT,

                # the properties below are optional
                # options=ecs.FirelensOptions(
                #     config_file_value="configFileValue",
                #     enable_ecs_log_metadata=True
                # )
            ),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs"),
            memory_reservation_mib=50
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

        # self._cluster_name = CfnOutput(
        #     self, "ClusterName",
        #     value=self.cluster.cluster_name, export_name="ClusterName"
        # )
