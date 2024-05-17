# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["FineTuneEvent", "Data"]


class Data(BaseModel):
    checkpoint_path: str

    created_at: str

    hash: str

    message: str

    api_model_path: str = FieldInfo(alias="model_path")

    object: Literal["fine-tune-event"]

    param_count: int

    step: int

    token_count: int

    total_steps: int

    training_offset: int

    type: str

    wandb_url: str

    level: Optional[str] = None


class FineTuneEvent(BaseModel):
    data: List[Data]
