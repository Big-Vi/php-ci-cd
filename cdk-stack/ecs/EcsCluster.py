from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_ecs_patterns as ecs_patterns,
    aws_kms as kms,
    Stack, CfnOutput,
)
from constructs import Construct


class EcsCluster(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(
            self, "VPC",
            vpc_id="vpc-0a2eb88f37dd4d313",
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

        fargate_task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef",
            cpu=256,
            execution_role=ecsTaskExecutionRole,
            task_role=ecsTaskExecutionRole
        )

        secrets = {
            "SS_DATABASE_NAME": ecs.Secret.from_secrets_manager(
                secretsmanager.Secret.from_secret_name_v2(self, 'SS_DATABASE_NAME', 'prod/php-app'), 'dbname'),
            "SS_DATABASE_PASSWORD": ecs.Secret.from_secrets_manager(
                secretsmanager.Secret.from_secret_name_v2(self, 'SS_DATABASE_PASSWORD', 'prod/php-app'), 'password')
        }

        container = fargate_task_definition.add_container(
            "WebContainer",
            # Use an image from ECR
            image=ecs.ContainerImage.from_registry(
                "090426658505.dkr.ecr.ap-southeast-2.amazonaws.com/php"),
            port_mappings=[ecs.PortMapping(container_port=8000)],
            secrets=secrets
        )

        fargate_service = ecs.FargateService(
            self, "CDKFargateService", cluster=self.cluster, task_definition=fargate_task_definition,
        )

        # fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
        #     self, "CDKFargateService", cluster=self.cluster, task_definition=fargate_task_definition,
        # )
        # fargate_service.service.connections.security_groups[0].add_ingress_rule(
        #     peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
        #     connection=ec2.Port.tcp(80),
        #     description="Allow http inbound from VPC"
        # )

        CfnOutput(
            self, "Cluster",
            value=self.cluster.cluster_name
        )
        # CfnOutput(
        #     self,
        #     "CDKFargateLoadBalancerDNS",
        #     value=fargate_service.load_balancer.load_balancer_dns_name,
        # )
