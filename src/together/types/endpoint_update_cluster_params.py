# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["EndpointUpdateClusterParams"]


class EndpointUpdateClusterParams(TypedDict, total=False):
    cluster_type: Literal["KUBERNETES", "SLURM"]

    num_gpus: int
