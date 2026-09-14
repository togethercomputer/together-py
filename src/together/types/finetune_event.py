# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .finetune_event_type import FinetuneEventType

__all__ = ["FinetuneEvent"]


class FinetuneEvent(BaseModel):
    created_at: str

    message: str

    object: Literal["fine-tune-event"]
    """The object type, which is always `fine-tune-event`."""

    type: FinetuneEventType

    checkpoint_path: Optional[str] = None

    early_stopping_best_metric_value: Optional[float] = None
    """For early_stopped events, the best validation loss observed.

    Null if no improving evaluation was recorded.
    """

    early_stopping_best_step: Optional[int] = None
    """
    For early_stopped events, the selected best-checkpoint step when a finite best
    metric exists. If early_stopping_best_metric_value is null, this is the halt
    step.
    """

    level: Optional[Literal["info", "warning", "error", "legacy_info", "legacy_iwarning", "legacy_ierror"]] = None

    x_model_path: Optional[str] = FieldInfo(alias="model_path", default=None)

    param_count: Optional[int] = None

    step: Optional[int] = None

    token_count: Optional[int] = None

    tokenized_dataset_path: Optional[str] = None
    """Storage path for the tokenized dataset archive associated with this event."""

    total_steps: Optional[int] = None

    wandb_url: Optional[str] = None
