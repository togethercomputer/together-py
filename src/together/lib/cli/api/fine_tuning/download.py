from __future__ import annotations

import os
import re
from typing import Literal, Optional, Annotated
from pathlib import Path

from cyclopts import Parameter

from together import APIError, Together, APIStatusError
from together.lib import DownloadManager
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.types.finetune_response import TrainingTypeFullTrainingType, TrainingTypeLoRaTrainingType
from together.lib.cli.components.loader import show_loading_status

_FT_JOB_WITH_STEP_REGEX = r"^ft-[\dabcdef-]+:\d+$"


# TODO: Validate path exists, is not a file, and resolve the path
#     type=click.Path(exists=True, file_okay=False, resolve_path=True),
OutputDirParam = Annotated[Optional[Path], Parameter(name=["--output-dir", "-o"], help="Output directory")]
CheckpointStepParam = Annotated[
    Optional[int],
    Parameter(name=["--checkpoint-step", "-s"], help="Download fine-tuning checkpoint. Defaults to latest."),
]
CheckpointTypeParam = Annotated[
    Literal["merged", "adapter", "default"],
    Parameter(
        name=["--checkpoint-type", "-c"],
        help="Specifies checkpoint type. 'merged' and 'adapter' options work only for LoRA jobs.",
    ),
]


async def download(
    fine_tune_id: str,
    output_dir: OutputDirParam = None,
    checkpoint_step: CheckpointStepParam = None,
    checkpoint_type: CheckpointTypeParam = "merged",
    *,
    config: CLIConfigParameter,
) -> None:
    """Download fine-tuning checkpoint."""
    if re.match(_FT_JOB_WITH_STEP_REGEX, fine_tune_id):
        if checkpoint_step is None:
            checkpoint_step = int(fine_tune_id.split(":")[1])
            fine_tune_id = fine_tune_id.split(":")[0]
        else:
            raise ValueError(
                f"Fine-tuning job ID {fine_tune_id} contains a colon to specify the step to download, but `checkpoint_step` "
                "was also set. Remove one of the step specifiers to proceed."
            )

    ft_job = await show_loading_status(
        "Retrieving fine-tuning job...", config.client.fine_tuning.retrieve(fine_tune_id)
    )
    loosely_typed_checkpoint_type: str = checkpoint_type
    if isinstance(ft_job.training_type, TrainingTypeFullTrainingType):
        if checkpoint_type != "default":
            raise ValueError("Only DEFAULT checkpoint type is allowed for FullTrainingType")
        loosely_typed_checkpoint_type = "model_output_path"
    elif isinstance(ft_job.training_type, TrainingTypeLoRaTrainingType):
        if checkpoint_type == "default":
            loosely_typed_checkpoint_type = "merged"

        if loosely_typed_checkpoint_type not in {
            "merged",
            "adapter",
        }:
            raise ValueError(f"Invalid checkpoint type for LoRATrainingType: {checkpoint_type}")

    remote_name = ft_job.x_model_output_name
    if remote_name is None:
        raise ValueError(
            "Job has no model output name yet. Ensure the job is completed or specify an output path with --output_dir."
        )

    url = f"/finetune/download?ft_id={fine_tune_id}&checkpoint={loosely_typed_checkpoint_type}"
    if checkpoint_step is not None:
        url = f"{url}&checkpoint_step={checkpoint_step}"
    output: Path | None = output_dir

    # Disable tqdm for json mode
    if config.json:
        os.environ.setdefault("TOGETHER_DISABLE_TQDM", "true")

    try:
        # TODO: This is a temporary hack,
        # We need to make the DownloadManager async so we can use the async client.
        sync_client = Together(
            api_key=config.client.api_key,
            base_url=config.client.base_url,
            timeout=config.client.timeout,
            max_retries=config.client.max_retries,
        )
        file_path, file_size = DownloadManager(sync_client).download(
            url=url,
            output=output,
            remote_name=ft_job.x_model_output_name,
            fetch_metadata=True,
        )

        if config.json:
            console.print_json(
                openapi_dumps(
                    {"object": "local", "id": fine_tune_id, "filename": str(file_path), "size": file_size}
                ).decode("utf-8")
            )
        else:
            console.print(f"File saved to {file_path}")
    except APIStatusError as e:
        raise APIError(
            "Training job is not downloadable. This may be because the job is not in a completed state.",
            request=e.request,
            body=None,
        ) from e
