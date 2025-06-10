# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["Autoscaling"]


class Autoscaling(BaseModel):
    max_replicas: int
    """The maximum number of replicas to scale up to under load"""

    min_replicas: int
    """The minimum number of replicas to maintain, even when there is no load"""
