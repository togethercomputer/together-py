# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .model_parameters import ModelParameters

__all__ = ["ModelWeights"]


class ModelWeights(BaseModel):
    """
    Architecture, size, precision, and speculative-decoding metadata for model weights.
    """

    architecture: Optional[str] = None
    """Model architecture detected from the weight metadata."""

    context_length: Optional[str] = FieldInfo(alias="contextLength", default=None)
    """Maximum context length reported by the model metadata."""

    draft_speculator_type: Optional[Literal["DRAFT_SPECULATOR_TYPE_EAGLE", "DRAFT_SPECULATOR_TYPE_PHOENIX"]] = (
        FieldInfo(alias="draftSpeculatorType", default=None)
    )
    """Draft-model speculator family for draft speculative decoding."""

    parameters: Optional[ModelParameters] = None
    """Total parameter count and breakdown by numerical data type."""

    speculator_mechanism: Optional[
        Literal["SPECULATOR_MECHANISM_DRAFT", "SPECULATOR_MECHANISM_LOOKAHEAD", "SPECULATOR_MECHANISM_MTP"]
    ] = FieldInfo(alias="speculatorMechanism", default=None)
    """Speculative decoding mechanism for speculator weights."""

    type: Optional[Literal["WEIGHTS_TYPE_DEFAULT", "WEIGHTS_TYPE_SPECULATOR", "WEIGHTS_TYPE_ADAPTER"]] = None
    """Role of the weights: full model, speculative draft model, or LoRA adapter."""
