# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DeploymentGetLogsParams"]


class DeploymentGetLogsParams(TypedDict, total=False):
    follow: bool
    """Stream logs in real-time (ndjson format)"""

    replica_id: str
    """Replica ID to filter logs"""
