# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TrainingMethodDpo"]


class TrainingMethodDpo(BaseModel):
    method: Literal["dpo"] = "dpo"

    dpo_beta: Optional[float] = None

    dpo_normalize_logratios_by_length: Optional[bool] = None

    dpo_reference_free: Optional[bool] = None

    rpo_alpha: Optional[float] = None

    simpo_gamma: Optional[float] = None
