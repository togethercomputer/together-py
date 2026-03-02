from __future__ import annotations

from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from tabulate import tabulate

from cyclopts import Parameter

from together import AsyncTogether, omit



async def list_(
    status: Optional[
        Literal["pending", "queued", "running", "completed", "error", "user_error"]
    ] = None,
    limit: Optional[int] = None,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List evals."""
    response = await client.evals.list(status=status or omit, limit=limit or omit)
    display_list: List[Dict[str, Any]] = []
    for job in response:
        if job.parameters:
            model = job.parameters.get("model_to_evaluate", "")
            model_a = job.parameters.get("model_a", "")
            model_b = job.parameters.get("model_b", "")
        else:
            model = ""
            model_a = ""
            model_b = ""
        display_list.append(
            {
                "Workflow ID": job.workflow_id or "",
                "Type": job.type,
                "Status": job.status,
                "Created At": job.created_at or 0,
                "Model": model,
                "Model A": model_a,
                "Model B": model_b,
            }
        )
    print(tabulate(display_list, headers="keys", tablefmt="grid", showindex=True))
