from __future__ import annotations

from typing import Annotated, Any, Dict, List

from tabulate import tabulate

from cyclopts import Parameter

from together import AsyncTogether

from together.lib.utils.tools import format_timestamp


async def list_checkpoints(
    fine_tune_id: str,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List available checkpoints for a fine-tuning job."""
    checkpoints = await client.fine_tuning.list_checkpoints(fine_tune_id)
    display_list: List[Dict[str, Any]] = []
    for checkpoint in checkpoints.data:
        name = (
            f"{fine_tune_id}:{checkpoint.step}"
            if "intermediate" in checkpoint.checkpoint_type.lower()
            else fine_tune_id
        )
        display_list.append(
            {
                "Type": checkpoint.checkpoint_type,
                "Timestamp": format_timestamp(checkpoint.created_at),
                "Name": name,
            }
        )
    if display_list:
        print(f"Job {fine_tune_id} contains the following checkpoints:")
        print(tabulate(display_list, headers="keys", tablefmt="grid"))
        print("\nTo download a checkpoint, use `together fine-tuning download`")
    else:
        print(f"No checkpoints found for job {fine_tune_id}")
