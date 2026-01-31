import json as json_lib
from typing import Literal, Optional

import click

from together import Together, TogetherError, omit
from together._response import APIResponse as APIResponse
from together.lib.cli.api._utils import handle_api_errors
from together.types.model_upload_response import ModelUploadResponse


@click.command()
@click.option(
    "--model-name",
    required=True,
    help="The name to give to your uploaded model",
)
@click.option(
    "--model-source",
    required=True,
    help="The source location of the model (Hugging Face repo or S3 path)",
)
@click.option(
    "--model-type",
    type=click.Choice(["model", "adapter"]),
    default="model",
    help="Whether the model is a full model or an adapter",
)
@click.option(
    "--hf-token",
    help="Hugging Face token (if uploading from Hugging Face)",
)
@click.option(
    "--description",
    help="A description of your model",
)
@click.option(
    "--base-model",
    help="The base model to use for an adapter if setting it to run against a serverless pool. Only used for model_type 'adapter'.",
)
@click.option(
    "--lora-model",
    help="The lora pool to use for an adapter if setting it to run against, say, a dedicated pool. Only used for model_type 'adapter'.",
)
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Models")
def upload(
    ctx: click.Context,
    model_name: str,
    model_source: str,
    hf_token: Optional[str],
    description: Optional[str],
    base_model: Optional[str],
    lora_model: Optional[str],
    json: bool,
    model_type: Optional[Literal["model", "adapter"]] = "model",
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
        click.echo(json_lib.dumps(response.model_dump(), indent=2))
    else:
        # If the model weights already exist, the api is returning 200 but with no data
        if response.data is None: # type: ignore
            raise TogetherError(response.message)

        click.echo(f"Model upload job created successfully!")
        if response.data.job_id:
            click.echo(f"Job ID: {response.data.job_id}")
        if response.data.x_model_name:
            click.echo(f"Model Name: {response.data.x_model_name}")
        if response.data.x_model_id:
            click.echo(f"Model ID: {response.data.x_model_id}")
        if response.data.x_model_source:
            click.echo(f"Model Source: {response.data.x_model_source}")
        click.echo(f"Message: {response.message}")
