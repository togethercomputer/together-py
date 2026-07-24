from __future__ import annotations

from together import AsyncClient, omit
from together.types.beta import AbMember, AbMemberParam
from together.types.beta.endpoints.ab_experiment import AbExperiment


async def find_ab_for_deployment(
    client: AsyncClient,
    endpoint_id: str,
    deployment_id: str,
    project_id: str | None,
) -> AbExperiment | None:
    cursor: str | None = None
    while True:
        page = await client.beta.endpoints.ab_experiments.list(
            endpoint_id=endpoint_id,
            project_id=project_id,
            after=cursor or omit,
        )
        for experiment in page.data:
            if any(m.deployment_id == deployment_id for m in experiment.members):
                return experiment
        if not page.next_cursor:
            break
        cursor = page.next_cursor
    return None


def update_ab_member_percent(
    members: list[AbMember],
    deployment_id: str,
    new_percent: int,
) -> list[AbMemberParam]:
    """Set a variant's AB percent by taking from or returning to control only."""
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
