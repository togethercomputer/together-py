# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["WandbMetadata"]


class WandbMetadata(BaseModel):
    """Details that associate a training session with a Weights & Biases run"""

    entity: Optional[str] = None
    """Weights & Biases username or team that owns the project"""

    group: Optional[str] = None
    """Weights & Biases group used to organize related runs"""

    project: Optional[str] = None
    """Weights & Biases project containing the run"""

    run_id: Optional[str] = None
    """Unique identifier assigned to the run by Weights & Biases"""

    run_name: Optional[str] = None
    """Human-readable name of the Weights & Biases run"""

    url: Optional[str] = None
    """HTTPS URL for the Weights & Biases run"""
