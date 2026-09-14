from __future__ import annotations

import sys
from typing import Any, Literal, Optional, Annotated, cast

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._prompt import PromptParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.types.model_upload_response import ModelUploadResponse


async def upload(
    model_name: Annotated[
        str,
        Parameter(required=True, help="The name to give to your uploaded model"),
        PromptParameter(instructions="What model name identifier would you like to use?", message="Model Name"),
    ],
    model_source: Annotated[
        str,
        Parameter(required=True, help="The source location of the model (Hugging Face repo or S3 path)"),
        PromptParameter(
            instructions="What is the source location of the model (Hugging Face repo or S3 path)?",
            message="Model Source",
        ),
    ],
    model_type: Annotated[
        Optional[Literal["model", "adapter"]], Parameter(help="Whether the model is a full model or an adapter")
    ] = None,
    hf_token: Annotated[Optional[str], Parameter(help="Hugging Face token (if uploading from Hugging Face)")] = None,
    description: Annotated[Optional[str], Parameter(help="A description of your model")] = None,
    base_model: Annotated[
        Optional[str],
        Parameter(help="Base model to use for an adapter against a serverless pool (model_type `adapter` only)"),
    ] = None,
    lora_model: Annotated[
        Optional[str],
        Parameter(help="LoRA pool to use for an adapter against a dedicated pool (model_type `adapter` only)"),
    ] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Upload a custom model or adapter from Hugging Face or S3."""
    response: ModelUploadResponse = await show_loading_status(
        "Uploading model...",
        config.client.models.upload(
            model_name=model_name,
            model_source=model_source,
            model_type=model_type or omit,
            hf_token=hf_token or omit,
            description=description or omit,
            base_model=base_model or omit,
            lora_model=lora_model or omit,
            extra_body={"allow_unsupported": True},
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    # This API has some weird behavior where certain failure cases return a 200 response with no data and a message
    # (schema always has `data`, but responses may omit it — check via cast for mypy).
    if cast(Any, response).data is None:
        console.print(f"[red]X[/red] [bold]Error[/bold]")
        console.print(f"  [white]{escape_rich_markup(response.message)}[/white]")
        sys.exit(1)

    console.print("[bold green]Model upload job created successfully![/bold green]")
    table = ListTable("Upload Job")
    table.add_column("Field")
    table.add_primary_column("Value")
    if response.data.job_id:
        table.add_row("Job ID", response.data.job_id)
    if response.data.x_model_name:
        table.add_row("Model Name", response.data.x_model_name)
    if response.data.x_model_id:
        table.add_row("Model ID", response.data.x_model_id)
    if response.data.x_model_source:
        table.add_row("Model Source", response.data.x_model_source)
    if response.message:
        table.add_row("Message", response.message)
    console.print(table)
