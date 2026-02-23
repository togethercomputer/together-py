from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_timestamp
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable


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

    table = ListTable(title="Checkpoints")
    table.add_column("ID")
    table.add_column("Timestamp")
    table.add_primary_column("Type")

    for checkpoint in checkpoints.data:
        name = (
            f"{fine_tune_id}:{checkpoint.step}"
            if "intermediate" in checkpoint.checkpoint_type.lower()
            else fine_tune_id
        )
        table.add_row(name, format_timestamp(checkpoint.created_at), checkpoint.checkpoint_type)

    if len(checkpoints.data) == 0:
        console.print(f"No checkpoints found for job {fine_tune_id}")
        return

    console.print(table)
    console.print(
        "\n[bold dim]To download a checkpoint, use `together fine-tuning download \\[checkpoint-id]`[/bold dim]"
    )
