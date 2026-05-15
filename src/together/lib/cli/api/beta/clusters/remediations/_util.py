from __future__ import annotations

import sys
from typing import List, Literal, TypeVar, Optional, cast, get_args
from datetime import datetime

from together import omit
from together._types import Omit
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.types.beta.clusters.remediation import Remediation

EMPTY_MESSAGE = "No remediations found for this cluster."

T = TypeVar("T")
RemediationState = Literal[
    "PENDING_APPROVAL", "PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", "AUTO_RESOLVED"
]
_REMEDIATION_STATES = set(get_args(RemediationState))


def omit_if_none(value: Optional[T]) -> T | Omit:
    return omit if value is None else value


def parse_states(state: Optional[str]) -> List[RemediationState] | Omit:
    if state is None:
        return omit
    states = [part.strip() for part in state.split(",") if part.strip()]
    if not states:
        return omit

    invalid_states = sorted(set(states) - _REMEDIATION_STATES)
    if invalid_states:
        console.print(f"[red]Error:[/red] Invalid remediation state: {', '.join(invalid_states)}")
        sys.exit(1)

    return cast(List[RemediationState], states)


def format_time(value: Optional[datetime]) -> str:
    if value is None:
        return "-"
    return value.isoformat()


def print_remediations(remediations: List[Remediation]) -> None:
    table = ListTable(title="Cluster Remediations", empty_message=EMPTY_MESSAGE)
    table.add_primary_column("ID")
    table.add_column("Instance")
    table.add_column("State")
    table.add_column("Mode")
    table.add_column("Trigger")
    table.add_column("Created")

    for remediation in remediations:
        table.add_row(
            remediation.id,
            remediation.instance_id,
            remediation.state,
            remediation.mode.replace("REMEDIATION_MODE_", ""),
            remediation.trigger.replace("REMEDIATION_TRIGGER_", ""),
            format_time(remediation.create_time),
        )

    console.print(table)


async def resolve_remediation(config: CLIConfigParameter, remediation_id: str) -> Remediation:
    clusters = await config.client.beta.clusters.list()

    for cluster in clusters.clusters:
        page_token: str | Omit = omit
        while True:
            response = await config.client.beta.clusters.remediations.list(
                "-",
                cluster_id=cluster.cluster_id,
                page_size=100,
                page_token=page_token,
            )
            for remediation in response.remediations:
                if remediation.id == remediation_id:
                    return remediation

            if not response.has_next or not response.next_page_token:
                break
            page_token = response.next_page_token

    console.print(f"[red]Error:[/red] Remediation not found: {remediation_id}")
    sys.exit(1)
