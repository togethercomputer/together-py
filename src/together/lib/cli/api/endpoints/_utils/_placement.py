from __future__ import annotations

import asyncio
from typing import Any, Mapping, Sequence, cast
from collections.abc import Callable, Awaitable

from together import BaseModel, AsyncClient
from together.types.endpoint import Endpoint
from together.lib.cli.components.loader import show_loading_status
from together.types.endpoint_deployment import Placement as DeploymentPlacement
from together.types.deployment_placement_config_param import CompliancePolicy, DeploymentPlacementConfigParam
from together.lib.cli.api.endpoints._utils._parameters import PlacementModel, resolve_cli_placement
from together.types.endpoints.deployment_create_params import Placement, PlacementInline, PlacementProfile


def placement_from_response(placement: DeploymentPlacement | None) -> Placement | None:
    """Convert a retrieved deployment placement into a deployment-create placement."""
    data = _as_mapping(placement)
    if data is None:
        return None

    profile = data.get("profile")
    if isinstance(profile, str) and profile:
        return PlacementProfile(profile=profile)

    inline = _as_mapping(data.get("inline"))
    if inline is None:
        return None

    config: DeploymentPlacementConfigParam = {}
    regions = inline.get("regions")
    if isinstance(regions, list):
        raw_regions = cast(list[object], regions)
        names = [region for region in raw_regions if isinstance(region, str)]
        if names and len(names) == len(raw_regions):
            config["regions"] = names
    constraint = inline.get("constraint")
    if constraint == "ENFORCEMENT_REQUIRED" or constraint == "ENFORCEMENT_PREFERRED":
        config["constraint"] = constraint
    policy = _as_mapping(inline.get("compliance_policy"))
    if policy is not None and policy.get("hipaa") is not None:
        config["compliance_policy"] = {"hipaa": bool(policy["hipaa"])}
    if not config:
        return None
    return PlacementInline(inline=config)


def combine_placement(
    explicit: Placement | None,
    inherited: Placement | None,
    *,
    hipaa_specified: bool,
) -> Placement | None:
    """Use explicit flags, or the inherited placement when the command omitted them.

    Inline region and constraint flags replace the inherited placement, but a HIPAA
    requirement on that placement stays in force unless ``--placement.hipaa`` was
    passed. A placement profile is sent as given.
    """
    if explicit is None:
        return inherited
    if "inline" not in explicit:
        return explicit
    if hipaa_specified or not _requires_hipaa(inherited):
        return explicit

    source = explicit["inline"]  # type: ignore[typeddict-item]
    inline: DeploymentPlacementConfigParam = {}
    if regions := source.get("regions"):
        inline["regions"] = list(regions)
    if constraint := source.get("constraint"):
        inline["constraint"] = constraint
    policy: CompliancePolicy = {"hipaa": True}
    inline["compliance_policy"] = policy
    return PlacementInline(inline=inline)


async def resolve_deployment_placement(
    placement_id: str | None,
    placement: PlacementModel,
    load_inherited: Callable[[], Awaitable[Placement | None]],
) -> Placement | None:
    """Resolve the placement for a new A/B variant or shadow deployment.

    A profile, or any command that sets ``--placement.hipaa``, is sent as given.
    Otherwise the inherited placement is loaded so a HIPAA control is not replaced
    by a deployment that can never receive its traffic.
    """
    explicit = resolve_cli_placement(placement_id, placement)
    hipaa_specified = placement.hipaa is not None
    if explicit is not None and (hipaa_specified or "inline" not in explicit):
        return explicit
    return combine_placement(explicit, await load_inherited(), hipaa_specified=hipaa_specified)


async def inherit_live_placement(client: AsyncClient, endpoint: Endpoint) -> Placement | None:
    """Copy the placement shared by deployments that currently receive live traffic."""
    deployment_ids: list[str] = []
    for entry in endpoint.traffic_split:
        if entry.weight <= 0 or entry.deployment_id in deployment_ids:
            continue
        deployment_ids.append(entry.deployment_id)
    if not deployment_ids:
        return None

    deployments = await show_loading_status(
        "Loading live deployment placement...",
        asyncio.gather(
            *[
                client.endpoints.deployments.retrieve(deployment_id, endpoint_id=endpoint.id)
                for deployment_id in deployment_ids
            ]
        ),
    )
    found = [
        (deployment_id, placement_from_response(deployment.placement))
        for deployment_id, deployment in zip(deployment_ids, deployments, strict=True)
    ]
    return shared_placement(found)


def shared_placement(placements: Sequence[tuple[str, Placement | None]]) -> Placement | None:
    if not placements:
        return None
    first_id, first = placements[0]
    mismatches = [deployment_id for deployment_id, placement in placements[1:] if placement != first]
    if mismatches:
        raise ValueError(
            "Live deployments do not share a placement "
            f"({first_id} vs {', '.join(mismatches)}). "
            "Pass --placement.hipaa, --placement.regions, or --placement <profile-id> "
            "so the new deployment is scheduled where it can receive traffic."
        )
    return first


def _requires_hipaa(placement: Placement | None) -> bool:
    if placement is None or "inline" not in placement:
        return False
    policy = placement["inline"].get("compliance_policy") or {}  # type: ignore[typeddict-item]
    return policy.get("hipaa") is True


def _as_mapping(value: object) -> dict[str, Any] | None:
    if isinstance(value, BaseModel):
        return cast(dict[str, Any], value.to_dict(use_api_names=False, exclude_unset=True, exclude_none=True))
    if isinstance(value, Mapping):
        mapped = cast(Mapping[Any, Any], value)
        return {str(key): mapped[key] for key in mapped}
    return None
