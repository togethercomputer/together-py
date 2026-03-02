from __future__ import annotations

import json
from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether



async def delete(
    fine_tune_id: str,
    force: bool = False,
    quiet: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Delete fine-tuning job."""
    if not quiet:
        confirm_response = input(
            f"Are you sure you want to delete fine-tuning job {fine_tune_id}? This action cannot be undone. [y/N] "
        )
        if confirm_response.lower() != "y":
            print("Deletion cancelled")
            return
    response = await client.fine_tuning.delete(fine_tune_id, force=force)
    print(json.dumps(response.model_dump(exclude_none=True), indent=4))
