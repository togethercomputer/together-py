from __future__ import annotations

from together import omit
from together._types import Omit
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._json_mode import exit_with_message
from together.types.beta.clusters.remediation import Remediation


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

    exit_with_message(
        f"[red]Error:[/red] Remediation not found: {remediation_id}",
        error=f"Remediation not found: {remediation_id}",
        diagnostic=f"Remediation not found: {remediation_id}",
    )
