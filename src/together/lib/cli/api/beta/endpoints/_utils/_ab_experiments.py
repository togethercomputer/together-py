from __future__ import annotations

from together import AsyncClient
from together.types.beta import AbMember, AbMemberParam
from together.types.beta.endpoints.ab_experiment import AbExperiment


async def find_ab_for_deployment(
    client: AsyncClient,
    endpoint_id: str,
    deployment_id: str,
) -> AbExperiment | None:
    async for experiment in client.beta.endpoints.ab_experiments.list(endpoint_id=endpoint_id):
        if any(m.deployment_id == deployment_id for m in experiment.members):
            return experiment
    return None


def build_ab_members_with_percent(
    members: list[AbMember],
    deployment_id: str,
    new_percent: int,
) -> list[AbMemberParam]:
    """Build AB member params with a variant percent adjusted against control.

    Rules:
    - ``deployment_id`` must identify a *variant* member (not control). Control
      percent is derived: ``100 - sum(variants)``.
    - Only the target variant and the control member change. All other variants
      keep their current percent.
    - Increasing a variant takes the delta from control.
    - Decreasing a variant returns the delta to control.
    - Control must remain >= 1% after the update.

    Examples (control=85, variant_a=5, variant_b=10):
    - Set variant_a to 20 → control=70, variant_a=20, variant_b=10
    - Set variant_a to 2  → control=88, variant_a=2,  variant_b=10
    - Set control to 80   → ValueError (control is not updatable)
    - Set variant_a to 95 → ValueError (control would be 0%)
    """
    target = next((m for m in members if m.deployment_id == deployment_id), None)
    if target is None:
        raise ValueError(f"Deployment {deployment_id} is not a member of the A/B experiment.")

    if target.role == "AB_EXPERIMENT_MEMBER_ROLE_CONTROL":
        raise ValueError("--ab-percent can only update variant deployments; control percent is derived from variants.")

    control = next((m for m in members if m.role == "AB_EXPERIMENT_MEMBER_ROLE_CONTROL"), None)
    if control is None:
        raise ValueError("Existing A/B experiment has no control member.")

    delta = new_percent - target.percent
    control_percent = control.percent - delta
    if control_percent < 1:
        raise ValueError(
            f"Cannot allocate {new_percent}% to deployment {deployment_id}: "
            f"control would be {control_percent}% (minimum 1%)."
        )

    result: list[AbMemberParam] = []
    for member in members:
        percent = member.percent
        if member.deployment_id == deployment_id:
            percent = new_percent
        elif member.deployment_id == control.deployment_id:
            percent = control_percent
        result.append(
            AbMemberParam(
                deployment_id=member.deployment_id,
                role=member.role,
                percent=percent,
            )
        )
    return result
