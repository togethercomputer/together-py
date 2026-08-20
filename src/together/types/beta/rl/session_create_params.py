# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .lora_config_param import LoraConfigParam
from .session_metadata_param import SessionMetadataParam

__all__ = ["SessionCreateParams"]


class SessionCreateParams(TypedDict, total=False):
    model_resources_id: Required[str]
    """Model resource to attach the session to.

    The session runs on that resource's GPU pods.
    """

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
    """Checkpoint ID to resume from"""

    resume_from_hf_checkpoint: str
    """HuggingFace repo (or hf://) to resume model weights from.

    Accepts either a full model or a PEFT adapter directory. Mutually exclusive with
    resume_from_checkpoint_id.
    """
