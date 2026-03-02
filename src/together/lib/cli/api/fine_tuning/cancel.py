from __future__ import annotations

import json
from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether

from together.lib.utils.serializer import datetime_serializer

NON_CANCELLABLE_STATES = ["cancel_requested", "cancelled", "error", "completed", "user_error"]


async def cancel(
    fine_tune_id: str,
    quiet: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Cancel fine-tuning job."""
    job = await client.fine_tuning.retrieve(fine_tune_id)
    if job.status in NON_CANCELLABLE_STATES:
        print(f"Fine-tuning: Training is not currently cancellable. Current status is {job.status}")
        return
    if not quiet:
        confirm_response = input(
            "You will be billed for any completed training steps upon cancellation. "
            f"Do you want to cancel job {fine_tune_id}? [y/N]"
        )
        if "y" not in confirm_response.lower():
            print(json.dumps({"status": "Cancel not submitted"}))
            return
    response = await client.fine_tuning.cancel(fine_tune_id)
    print(json.dumps(response.model_dump(exclude_none=True), indent=4, default=datetime_serializer))
