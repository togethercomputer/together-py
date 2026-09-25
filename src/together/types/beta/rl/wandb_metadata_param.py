# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["WandbMetadataParam"]


class WandbMetadataParam(TypedDict, total=False):
    """Details that associate a training session with a Weights & Biases run"""

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
