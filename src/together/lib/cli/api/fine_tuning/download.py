from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Annotated, Literal, Optional

from cyclopts import Parameter

from together import APIError, APIStatusError, AsyncTogether, Together
from together.lib import DownloadManager

from together.types.finetune_response import TrainingTypeFullTrainingType, TrainingTypeLoRaTrainingType

_FT_JOB_WITH_STEP_REGEX = r"^ft-[\dabcdef-]+:\d+$"


async def download(
    fine_tune_id: str,
    output_dir: Optional[Path] = None,
    checkpoint_step: Optional[int] = None,
    checkpoint_type: Literal["merged", "adapter", "default"] = "merged",
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Download fine-tuning checkpoint."""
    if re.match(_FT_JOB_WITH_STEP_REGEX, fine_tune_id):
        if checkpoint_step is None:
            checkpoint_step = int(fine_tune_id.split(":")[1])
            fine_tune_id = fine_tune_id.split(":")[0]
        else:
            raise ValueError(
                f"Fine-tuning job ID {fine_tune_id} contains a colon to specify the step to download, "
                "but checkpoint_step was also set. Remove one of the step specifiers to proceed."
            )

    ft_job = await client.fine_tuning.retrieve(fine_tune_id)
    loosely_typed_checkpoint_type: str = checkpoint_type
    if isinstance(ft_job.training_type, TrainingTypeFullTrainingType):
        if checkpoint_type != "default":
            raise ValueError("Only DEFAULT checkpoint type is allowed for FullTrainingType")
        loosely_typed_checkpoint_type = "model_output_path"
    elif isinstance(ft_job.training_type, TrainingTypeLoRaTrainingType):
        if checkpoint_type == "default":
            loosely_typed_checkpoint_type = "merged"
        if checkpoint_type not in {"merged", "adapter"}:
            raise ValueError(f"Invalid checkpoint type for LoRATrainingType: {checkpoint_type}")

    url = f"/finetune/download?ft_id={fine_tune_id}&checkpoint={loosely_typed_checkpoint_type}"
    output = Path(output_dir) if output_dir else None
    sync_client = Together(
        api_key=client.api_key,
        base_url=client.base_url,
        timeout=client.timeout,
        max_retries=client.max_retries,
    )
    try:

        def _sync_download() -> tuple:
            return DownloadManager(sync_client).download(
                url=url,
                output=output,
                remote_name=ft_job.x_model_output_name,
                fetch_metadata=True,
            )

        file_path, file_size = await asyncio.to_thread(_sync_download)
        print(json.dumps({"object": "local", "id": fine_tune_id, "filename": str(file_path), "size": file_size}, indent=4))
    except APIStatusError as e:
        raise APIError(
            "Training job is not downloadable. This may be because the job is not in a completed state.",
            request=e.request,
            body=None,
        ) from e
