# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ...._models import BaseModel
from .rl_supported_model import RlSupportedModel

__all__ = ["RlSupportedModels"]


class RlSupportedModels(BaseModel):
    """List of base models supported by the RL service"""

    data: List[RlSupportedModel]
    """Supported base models for RL"""
