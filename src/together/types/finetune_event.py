# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .finetune_event_type import FinetuneEventType

__all__ = ["FinetuneEvent"]


class FinetuneEvent(BaseModel):
    checkpoint_path: str

    created_at: str

    hash: str

    message: str

    x_model_path: str = FieldInfo(alias="model_path")

    object: Literal["fine-tune-event"]

    param_count: int

    step: int

    token_count: int

    total_steps: int

    training_offset: int

    type: FinetuneEventType

    wandb_url: str

    level: Optional[Literal["info", "warning", "error", "legacy_info", "legacy_iwarning", "legacy_ierror"]] = None
