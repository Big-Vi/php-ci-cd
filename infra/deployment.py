from typing import Any, Dict

from aws_cdk import (
    aws_ec2 as ec2,
    Stack, Stage
)
from constructs import Construct

from coreapp import CoreApp


class ECSApplication(Stage):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        infra: Dict[str, str],
        **kwargs: Any,
    ):
        super().__init__(scope, id_, **kwargs)

        CoreApp(self, "CoreApp", infra=infra)
