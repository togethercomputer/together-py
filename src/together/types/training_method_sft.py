# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TrainingMethodSft"]


class TrainingMethodSft(BaseModel):
    method: Literal["sft"] = "sft"

    train_on_inputs: Union[bool, Literal["auto"]]
    """
    Whether to mask the user messages in conversational data or prompts in
    instruction data.
    """
