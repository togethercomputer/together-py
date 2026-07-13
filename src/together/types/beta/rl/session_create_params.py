# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .lora_config_param import LoraConfigParam

__all__ = ["SessionCreateParams"]


class SessionCreateParams(TypedDict, total=False):
    model_resources_id: Required[str]
    """Model resource to attach the session to.

    The session runs on that resource's GPU pods.
    """

    lora_config: LoraConfigParam
    """LoRA adapter configuration for the session"""

    resume_from_checkpoint_id: str
    """Checkpoint ID to resume from"""

    resume_from_hf_checkpoint: str
    """HuggingFace repo (or hf://) to resume model weights from.

    Accepts either a full model or a PEFT adapter directory. Mutually exclusive with
    resume_from_checkpoint_id.
    """
