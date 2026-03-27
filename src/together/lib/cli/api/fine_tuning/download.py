from __future__ import annotations

import os
import re
from typing import Union, Literal
from pathlib import Path

import click

from together import NOT_GIVEN, APIError, NotGiven, Together, APIStatusError
from together.lib import DownloadManager
from together._utils._json import openapi_dumps
from together.lib.cli._track_cli import auto_track_command
from together.lib.cli.api._utils import handle_api_errors
from together.types.finetune_response import TrainingTypeFullTrainingType, TrainingTypeLoRaTrainingType

_FT_JOB_WITH_STEP_REGEX = r"^ft-[\dabcdef-]+:\d+$"


@click.command()
@click.pass_context
@click.argument("fine_tune_id", type=str, required=True)
@click.option(
    "--output_dir",
    "-o",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=False,
    default=None,
    help="Output directory",
)
@click.option(
    "--checkpoint-step",
    "-s",
    type=int,
    required=False,
    default=None,
    help="Download fine-tuning checkpoint. Defaults to latest.",
)
@click.option(
    "--checkpoint-type",
    type=click.Choice(["merged", "adapter", "default"]),
    required=False,
    default="merged",
    help="Specifies checkpoint type. 'merged' and 'adapter' options work only for LoRA jobs.",
)
@click.option("--json", is_flag=True, help="Print output in JSON format")
@handle_api_errors("Fine-tuning")
@auto_track_command
def download(
    ctx: click.Context,
    fine_tune_id: str,
    output_dir: str | None = None,
    checkpoint_step: Union[int, NotGiven] = NOT_GIVEN,
    checkpoint_type: Literal["default", "merged", "adapter"] | NotGiven = NOT_GIVEN,
    json: bool = False,
) -> None:
    """Download fine-tuning checkpoint"""
    client: Together = ctx.obj

    if re.match(_FT_JOB_WITH_STEP_REGEX, fine_tune_id) is not None:
        if checkpoint_step is NOT_GIVEN:
            checkpoint_step = int(fine_tune_id.split(":")[1])
            fine_tune_id = fine_tune_id.split(":")[0]
        else:
            raise ValueError(
                f"Fine-tuning job ID {fine_tune_id} contains a colon to specify the step to download, but `checkpoint_step` "
                "was also set. Remove one of the step specifiers to proceed."
            )

    ft_job = client.fine_tuning.retrieve(fine_tune_id)

    loosely_typed_checkpoint_type: str | NotGiven = checkpoint_type
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
    if checkpoint_step is not NOT_GIVEN:
        url = f"{url}&checkpoint_step={checkpoint_step}"
    output: Path | None = None
    if isinstance(output_dir, str):
        output = Path(output_dir)

    # Disable tqdm for json mode
    if json:
        os.environ.setdefault("TOGETHER_DISABLE_TQDM", "true")

    try:
        file_path, file_size = DownloadManager(client).download(
            url=url,
            output=output,
            remote_name=remote_name,
            fetch_metadata=True,
        )

        click.echo(
            openapi_dumps({"object": "local", "id": fine_tune_id, "filename": file_path, "size": file_size}).decode(
                "utf-8"
            )
        )
    except APIStatusError as e:
        raise APIError(
            "Training job is not downloadable. This may be because the job is not in a completed state.",
            request=e.request,
            body=None,
        ) from e
