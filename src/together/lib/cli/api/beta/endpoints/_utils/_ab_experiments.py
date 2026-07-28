from __future__ import annotations

from together import AsyncClient
from together.types.beta import AbMember, AbMemberParam
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils._console import console
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


async def find_ab_experiment_by_name(
    client: AsyncClient,
    *,
    endpoint_id: str,
    name: str,
) -> AbExperiment | None:
    async for experiment in client.beta.endpoints.ab_experiments.list(endpoint_id=endpoint_id):
        if experiment.name == name:
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
    target = next(m for m in members if m.deployment_id == deployment_id)

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


def calculate_ab_members(
    *,
    control_deployment_id: str,
    new_deployment_id: str,
    new_percent: int,
    existing_members: list[AbMember] | None = None,
) -> list[AbMemberParam]:
    existing_variants: list[AbMember] = []

    if existing_members:
        control_member = next(
            (member for member in existing_members if member.role == "AB_EXPERIMENT_MEMBER_ROLE_CONTROL"),
            None,
        )
        if control_member is None:
            raise ValueError("Existing A/B experiment has no control member.")
        if control_member.deployment_id != control_deployment_id:
            raise ValueError(
                "Control deployment does not match the existing A/B experiment control member. "
                f"Expected {control_member.deployment_id}, got {control_deployment_id}."
            )
        existing_variants = [
            member for member in existing_members if member.role == "AB_EXPERIMENT_MEMBER_ROLE_VARIANT"
        ]

    existing_variant_total = sum(member.percent for member in existing_variants)
    control_percent = 100 - existing_variant_total - new_percent
    if control_percent < 1:
        raise ValueError(
            f"Cannot allocate {new_percent}% to the new variant: control would be {control_percent}% (minimum 1%)."
        )

    members: list[AbMemberParam] = [
        AbMemberParam(
            deployment_id=control_deployment_id,
            role="AB_EXPERIMENT_MEMBER_ROLE_CONTROL",
            percent=control_percent,
        ),
        *[
            AbMemberParam(
                deployment_id=member.deployment_id,
                role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
                percent=member.percent,
            )
            for member in existing_variants
        ],
        AbMemberParam(
            deployment_id=new_deployment_id,
            role="AB_EXPERIMENT_MEMBER_ROLE_VARIANT",
            percent=new_percent,
        ),
    ]
    return members


def print_ab_experiment_detail(experiment: AbExperiment | None) -> None:
    if experiment is None:
        console.print("A/B experiment not found.")
        return

    console.print(f"[dim][primary]Name:[/primary][/dim]\t\t[bold]{experiment.name}[/bold]")
    console.print(f"[dim][primary]ID:[/primary][/dim]\t\t{experiment.id}")
    console.print(f"[dim][primary]Endpoint:[/primary][/dim]\t{experiment.endpoint_id}")
    console.print(f"[dim][primary]Project:[/primary][/dim]\t{experiment.project_id}")
    if experiment.description:
        console.print(f"[dim][primary]Description:[/primary][/dim]\t{experiment.description}")
    console.print(f"[dim][primary]ETag:[/primary][/dim]\t\t{experiment.etag}")
    console.print("[dim][primary]Members:[/primary][/dim]")
    for member in experiment.members:
        role = format_member_role(member.role)
        console.print(f"\t\t{member.deployment_id} ({role}): {member.percent}%")
    console.print(f"[dim][primary]Created:[/primary][/dim]\t{format_datetime(experiment.created_at)}")
    console.print(f"[dim][primary]Updated:[/primary][/dim]\t{format_datetime(experiment.updated_at)}")


def format_member_role(role: str) -> str:
    if role.endswith("_CONTROL"):
        return "CONTROL"
    if role.endswith("_VARIANT"):
        return "VARIANT"
    return role
