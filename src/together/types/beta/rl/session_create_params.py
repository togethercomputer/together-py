# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .lora_config_param import LoraConfigParam

__all__ = ["SessionCreateParams", "Metadata", "MetadataWandb"]


class SessionCreateParams(TypedDict, total=False):
    model_resources_id: Required[str]
    """Model resource to attach the session to.

    The session runs on that resource's GPU pods.
    """

    display_name: str
    """Optional display name used to identify the training session"""

    lora_config: LoraConfigParam
    """LoRA adapter configuration for the session"""

    metadata: Metadata
    """Optional auxiliary metadata to associate with the training session"""

    resume_from_checkpoint_id: str
    """Checkpoint ID to resume from"""

    resume_from_hf_checkpoint: str
    """HuggingFace repo (or hf://) to resume model weights from.

    Accepts either a full model or a PEFT adapter directory. Mutually exclusive with
    resume_from_checkpoint_id.
    """


class MetadataWandb(TypedDict, total=False):
    """Weights & Biases details associated with the training session"""

    entity: str
    """Weights & Biases username or team that owns the project"""

    group: str
    """Weights & Biases group used to organize related runs"""

    project: str
    """Weights & Biases project containing the run"""

    run_id: str
    """Unique identifier assigned to the run by Weights & Biases"""

    run_name: str
    """Human-readable name of the Weights & Biases run"""

    url: str
    """HTTPS URL for the Weights & Biases run"""


class Metadata(TypedDict, total=False):
    """Optional auxiliary metadata to associate with the training session"""

    wandb: MetadataWandb
    """Weights & Biases details associated with the training session"""
