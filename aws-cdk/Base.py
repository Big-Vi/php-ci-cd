from aws_cdk import (
    Stack
)
from constructs import Construct
from typing import Any

class Base(Stack):

    def __init__(self, scope: Construct, id_: str, **kwargs: Any):
        super().__init__(scope, id_, **kwargs)
