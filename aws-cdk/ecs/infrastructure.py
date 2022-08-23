from typing import Dict
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    Stack, CfnOutput, Fn
)
from constructs import Construct

import constants


class EcsCluster(Construct):

    def __init__(self, scope: Construct, id: str, database_secret_name: str, infra: Dict[str, str], **kwargs) -> None:
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

        self.fargate_task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef",
            cpu=256,
            execution_role=ecsTaskExecutionRole,
            task_role=ecsTaskExecutionRole
        )
        my_secret_from_name = secretsmanager.Secret.from_secret_name_v2(
            self, "SecretFromName", database_secret_name)

        secrets = {
            "SS_DATABASE_NAME": ecs.Secret.from_secrets_manager(my_secret_from_name, "dbname"),
            "SS_DATABASE_PASSWORD": ecs.Secret.from_secrets_manager(my_secret_from_name, "password"),
            "SS_DATABASE_USERNAME": ecs.Secret.from_secrets_manager(my_secret_from_name, "username"),
            "SS_DATABASE_SERVER": ecs.Secret.from_secrets_manager(my_secret_from_name, "host"),
        }

        container = self.fargate_task_definition.add_container(
            constants.CDK_APP_NAME,
            # Use an image from ECR
            image=ecs.ContainerImage.from_registry(
                "090426658505.dkr.ecr.ap-southeast-2.amazonaws.com/" + constants.CDK_APP_NAME + ":latest"),
            port_mappings=[ecs.PortMapping(container_port=80)],
            secrets=secrets,
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ecs"),
        )

        self.fargate_service = ecs.FargateService(
            self, "CDKFargateService",
            service_name=constants.CDK_APP_NAME,
            cluster=self.cluster, task_definition=self.fargate_task_definition,
            vpc_subnets=vpc_subnets, assign_public_ip=True,
            security_groups=[security_group]
        )

        # fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
        #     self, "CDKFargateService", cluster=self.cluster, task_definition=fargate_task_definition,
        # )
        # fargate_service.service.connections.security_groups[0].add_ingress_rule(
        #     peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
        #     connection=ec2.Port.tcp(80),
        #     description="Allow http inbound from VPC"
        # )

        self._cluster_name = CfnOutput(
            self, "ClusterName",
            value=self.cluster.cluster_name, export_name="ClusterName"
        )
        self._service_name = CfnOutput(
            self, "FargateServiceName",
            value=self.fargate_service.service_name, export_name="FargateServiceName"
        )
        # self._fargate_task_definition = CfnOutput(
        #     self, "FargateTaskDefinitionName",
        #     value=self.fargate_task_definition, export_name="FargateTaskDefinitionName"
        # )
        # CfnOutput(
        #     self,
        #     "CDKFargateLoadBalancerDNS",
        #     value=fargate_service.load_balancer.load_balancer_dns_name,
        # )
