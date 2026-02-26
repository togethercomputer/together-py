from typing import Annotated, Literal, Optional

import typer
from rich.console import Console

from together import Together, TogetherError, omit
from together._response import APIResponse as APIResponse
from together._utils._json import openapi_dumps
from together.types import ModelUploadResponse

console = Console()

def upload(
    ctx: typer.Context,
    model_name: Annotated[str, typer.Option("--model-name", help="The name to give to your uploaded model")],
    model_source: Annotated[str, typer.Option("--model-source", help="The source location of the model (Hugging Face repo or S3 path)")],
    model_type: Optional[Literal["model", "adapter"]] = typer.Option("model", "--model-type", help="Whether the model is a full model or an adapter"),
    hf_token: Optional[str] = typer.Option(None, "--hf-token", help="Hugging Face token (if uploading from Hugging Face)"),
    description: Optional[str] = typer.Option(None, "--description", help="A description of your model"),
    base_model: Optional[str] = typer.Option(None, "--base-model", help="The base model to use for an adapter if setting it to run against a serverless pool. Only used for model_type 'adapter'."),
    lora_model: Optional[str] = typer.Option(None, "--lora-model", help="The lora pool to use for an adapter if setting it to run against, say, a dedicated pool. Only used for model_type 'adapter'."),
    json: bool = typer.Option(False, "--json", help="Output in JSON format"),
) -> None:
    """Upload a custom model or adapter from Hugging Face or S3"""
    client: Together = ctx.obj

    response: ModelUploadResponse = client.models.upload(
        model_name=model_name,
        model_source=model_source,
        model_type=model_type or omit,
        hf_token=hf_token or omit,
        description=description or omit,
        base_model=base_model or omit,
        lora_model=lora_model or omit,
    )

    if json:
        print(openapi_dumps(response))
    else:
        # If the model weights already exist, the api is returning 200 but with no data
        if response.data is None:  # type: ignore
            raise TogetherError(response.message)


        console.print("[green]Model upload job created.[/green]")
        if response.data.job_id:
            console.print(f"Upload job ID: [bold]{response.data.job_id}[/bold]")
