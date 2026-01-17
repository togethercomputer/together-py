from __future__ import annotations

import re
import json
from typing import Union, Literal
from pathlib import Path

import click

from together import NOT_GIVEN, NotGiven, Together
from together.lib import DownloadManager
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
def download(
    ctx: click.Context,
    fine_tune_id: str,
    output_dir: str | None = None,
    checkpoint_step: Union[int, NotGiven] = NOT_GIVEN,
    checkpoint_type: Literal["default", "merged", "adapter"] | NotGiven = NOT_GIVEN,
) -> None:
    """Download fine-tuning checkpoint"""
    client: Together = ctx.obj

    if re.match(_FT_JOB_WITH_STEP_REGEX, fine_tune_id) is not None:
        if checkpoint_step is NOT_GIVEN:
            checkpoint_step = int(fine_tune_id.split(":")[1])
            fine_tune_id = fine_tune_id.split(":")[0]
        else:
            raise ValueError(
                "Fine-tuning job ID {fine_tune_id} contains a colon to specify the step to download, but `checkpoint_step` "
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

        if checkpoint_type not in {
            "merged",
            "adapter",
        }:
            raise ValueError(f"Invalid checkpoint type for LoRATrainingType: {checkpoint_type}")

    remote_name = ft_job.x_model_output_name

    url = f"/finetune/download?ft_id={fine_tune_id}&checkpoint={loosely_typed_checkpoint_type}"
    output: Path | None = None
    if isinstance(output_dir, str):
        output = Path(output_dir)

    file_path, file_size = DownloadManager(client).download(
        url=url,
        output=output,
        remote_name=remote_name,
        fetch_metadata=True,
    )

    click.echo(json.dumps({"object": "local", "id": fine_tune_id, "filename": file_path, "size": file_size}, indent=4))
