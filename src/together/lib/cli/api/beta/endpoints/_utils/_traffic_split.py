from __future__ import annotations

from together.types.beta import EndpointTrafficSplitEntry, EndpointTrafficSplitEntryParam


def upsert_traffic_weight(
    existing: list[EndpointTrafficSplitEntry] | None,
    *,
    deployment_id: str,
    weight: float,
) -> list[EndpointTrafficSplitEntryParam]:
    """Set one deployment's traffic weight while preserving all other entries."""
    if weight < 0:
        raise ValueError("Traffic weight must be non-negative.")

    updated: list[EndpointTrafficSplitEntryParam] = []
    found = False
    for entry in existing or []:
        if entry.deployment_id == deployment_id:
            updated.append(EndpointTrafficSplitEntryParam(deployment_id=deployment_id, weight=weight))
            found = True
        else:
            updated.append(EndpointTrafficSplitEntryParam(deployment_id=entry.deployment_id, weight=entry.weight))
    if not found:
        updated.append(EndpointTrafficSplitEntryParam(deployment_id=deployment_id, weight=weight))
    return updated
