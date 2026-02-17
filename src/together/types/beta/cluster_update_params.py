# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["ClusterUpdateParams"]


class ClusterUpdateParams(TypedDict, total=False):
    cluster_type: Literal["KUBERNETES", "SLURM"]
    """Type of cluster to update."""

    num_gpus: int
    """Number of GPUs to allocate in the cluster.

    This must be multiple of 8. For example, 8, 16 or 24
    """
