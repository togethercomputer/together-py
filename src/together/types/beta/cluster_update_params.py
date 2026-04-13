# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ClusterUpdateParams"]


class ClusterUpdateParams(TypedDict, total=False):
    cluster_type: Literal["KUBERNETES", "SLURM"]
    """Type of cluster to update."""

    num_gpus: int
    """Number of GPUs to allocate in the cluster.

    This must be multiple of 8. For example, 8, 16 or 24
    """

    reservation_end_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Timestamp at which the cluster should be decommissioned.

    Only accepted for prepaid clusters.
    """
