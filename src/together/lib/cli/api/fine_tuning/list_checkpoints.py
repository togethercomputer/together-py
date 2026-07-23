from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_timestamp
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable


def _format_registry_artifact(object_id: str | None, revision_id: str | None) -> str:
    if object_id and revision_id:
        return f"{object_id}@{revision_id}"
    return object_id or revision_id or ""


async def list_checkpoints(
    fine_tune_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """List available checkpoints for a fine-tuning job."""

    checkpoints = await config.client.fine_tuning.list_checkpoints(fine_tune_id)
    checkpoints.data = checkpoints.data or []

    if config.json:
        console.print_json(openapi_dumps(checkpoints.data).decode("utf-8"))
        return

    table = ListTable(
        title="Checkpoints",
        empty_message=f"No checkpoints found for job {fine_tune_id}",
    )
    table.add_column("Download ID")
    table.add_column("Timestamp")
    table.add_column("Registry Artifact", ratio=2)
    table.add_primary_column("Type")

    registry_artifacts: list[tuple[str, str]] = []
    for checkpoint in checkpoints.data:
        name = (
            f"{fine_tune_id}:{checkpoint.step}"
            if "intermediate" in checkpoint.checkpoint_type.lower()
            else fine_tune_id
        )
        registry_artifact = _format_registry_artifact(checkpoint.object_id, checkpoint.object_revision_id)
        if registry_artifact:
            registry_artifacts.append((name, registry_artifact))
        table.add_row(
            name,
            format_timestamp(checkpoint.created_at),
            registry_artifact,
            checkpoint.checkpoint_type,
        )

    console.print(table)
    if registry_artifacts:
        console.print("\n[dim]Registry artifacts:[/dim]")
        for name, registry_artifact in registry_artifacts:
            console.print(f"  [dim]{name}:[/dim] {registry_artifact}")

    if checkpoints.data:
        console.print(
            "\n[bold dim]To download a checkpoint, use `together fine-tuning download \\[checkpoint-id]`[/bold dim]"
        )
