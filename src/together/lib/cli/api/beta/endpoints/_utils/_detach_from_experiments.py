from __future__ import annotations

from together import omit
from together.types.beta.endpoint import Endpoint
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.endpoints._utils._ab_experiments import (
    find_ab_for_deployment,
    members_without_deployment,
)
from together.lib.cli.api.beta.endpoints._utils._shadow_experiments import find_shadow_for_deployment

# Can't trust this code right now as the server is not properly setting
# the traffic_mode for shadow deployments.
# def _experiment_checks_for_deployment(endpoint: Endpoint, deployment_id: str) -> tuple[bool, bool]:
#     """Return ``(check_shadow, check_ab)`` based on the deployment summary.

#     Shadow-mode deployments only need the shadow list. Live deployments only
#     need A/B — including members whose effective traffic share is 0 (weight
#     set to 0, stopped/scaled-to-zero variants, etc.). Membership is
#     authoritative; share is derived and can diverge.
#     """
#     deployment = next((d for d in (endpoint.deployments or []) if d.id == deployment_id), None)
#     if deployment is None:
#         return True, True
#     if deployment.traffic_mode == "TRAFFIC_MODE_SHADOW":
#         return True, False
#     # LIVE: only A/B is possible.
#     return False, True


async def detach_deployment_from_experiments(
    config: CLIConfig,
    *,
    endpoint: Endpoint,
    deployment_id: str,
) -> list[str]:
    """Remove a deployment from any shadow / A/B experiment membership.

    Always consults both experiment lists — ``traffic_mode`` on the deployment
    summary is not reliably populated for shadow deployments, so membership is
    the only authoritative signal.

    Returns human-readable action strings describing what was cleaned up.
    """
    endpoint_id = endpoint.id
    actions: list[str] = []
    # Can't trust this code right now as the server is not properly setting
    # check_shadow, check_ab = _experiment_checks_for_deployment(endpoint, deployment_id)

    shadow = await find_shadow_for_deployment(config.client, endpoint_id, deployment_id)  # if check_shadow else None
    if shadow is not None:
        target = next(t for t in (shadow.targets or []) if t.target_deployment_id == deployment_id)
        await show_loading_status(
            "Removing deployment from shadow experiment...",
            config.client.beta.endpoints.shadow_experiments.targets.delete(
                id=target.id,
                endpoint_id=endpoint_id,
                experiment_id=shadow.id,
                etag=target.etag or omit,
            ),
        )
        remaining = [t for t in (shadow.targets or []) if t.target_deployment_id != deployment_id]
        if remaining:
            actions.append(f"removed from shadow experiment {shadow.id}")
        else:
            await show_loading_status(
                "Deleting empty shadow experiment...",
                config.client.beta.endpoints.shadow_experiments.delete(
                    id=shadow.id,
                    endpoint_id=endpoint_id,
                    etag=shadow.etag or omit,
                ),
            )
            actions.append(f"deleted empty shadow experiment {shadow.id}")

    ab = await find_ab_for_deployment(config.client, endpoint_id, deployment_id)  # if check_ab else None
    if ab is not None:
        removed = next(m for m in ab.members if m.deployment_id == deployment_id)
        remaining_members = [m for m in ab.members if m.deployment_id != deployment_id]
        # A/B experiments require >= 2 members and a control; otherwise delete the experiment.
        if len(remaining_members) < 2 or removed.role == "AB_EXPERIMENT_MEMBER_ROLE_CONTROL":
            await show_loading_status(
                "Deleting A/B experiment...",
                config.client.beta.endpoints.ab_experiments.delete(
                    id=ab.id,
                    endpoint_id=endpoint_id,
                    etag=ab.etag or omit,
                ),
            )
            actions.append(f"deleted A/B experiment {ab.id}")
        else:
            members = members_without_deployment(ab.members, deployment_id)
            await show_loading_status(
                "Removing deployment from A/B experiment...",
                config.client.beta.endpoints.ab_experiments.update(
                    id=ab.id,
                    endpoint_id=endpoint_id,
                    update_mask="members",
                    members=members,
                    etag=ab.etag or omit,
                ),
            )
            actions.append(f"removed from A/B experiment {ab.id}")

    return actions
