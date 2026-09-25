# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .lora_config_param import LoraConfigParam
from .session_metadata_param import SessionMetadataParam

__all__ = ["SessionCreateParams"]


class SessionCreateParams(TypedDict, total=False):
    model_resources_id: Required[str]
    """ID of the model resource to use for this training session."""

    display_name: str
    """Optional display name used to identify the training session"""

    load_optimizer: bool
    """Whether to restore optimizer state and step from a training checkpoint.

    Omitted or true restores them; false loads weights only with a fresh optimizer
    and step 0. Not valid for inference or HuggingFace checkpoints, which have no
    optimizer state.
    """

    lora_config: LoraConfigParam
    """LoRA adapter configuration for the session"""

    metadata: SessionMetadataParam
    """Optional auxiliary metadata to associate with the training session"""

    resume_from_checkpoint_id: str
    """Checkpoint ID to resume from.

    LoRA training checkpoints may resume on another model resource with compatible
    base-model weights. Full-weight training checkpoints require the original base
    model.
    """

    resume_from_hf_checkpoint: str
    """HuggingFace repo (or hf://) to resume model weights from.

    Accepts either a full model or a PEFT adapter directory. Mutually exclusive with
    resume_from_checkpoint_id.
    """
