# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TrainingMethodDpo"]


class TrainingMethodDpo(BaseModel):
    method: Literal["dpo"]

    dpo_beta: Optional[float] = None
