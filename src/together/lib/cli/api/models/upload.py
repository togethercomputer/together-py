from typing import Annotated, Literal, Optional

from cyclopts import Parameter
from rich import print

from together import TogetherError, omit
from together._response import APIResponse as APIResponse
# from together.lib.cli.api._utils import handle_api_errors
from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import Config
from together.types.model_upload_response import ModelUploadResponse

async def upload(
    model_name: Annotated[str, Parameter(name="--model-name", required=True, help="The name to give to your uploaded model")],
    model_source: Annotated[str, Parameter(name="--model-source", required=True, help="The source location of the model (Hugging Face repo or S3 path)")],
    hf_token: Annotated[Optional[str], Parameter(name="--hf-token", help="Hugging Face token (if uploading from Hugging Face)")],
    description: Annotated[Optional[str], Parameter(name="--description", help="A description of your model")],
    base_model: Annotated[Optional[str], Parameter(name="--base-model", help="The base model to use for an adapter if setting it to run against a serverless pool. Only used for model_type 'adapter'.")],
    lora_model: Annotated[Optional[str], Parameter(name="--lora-model", help="The lora pool to use for an adapter if setting it to run against, say, a dedicated pool. Only used for model_type 'adapter'.")],
    json: Annotated[bool, Parameter(name="--json", help="Output in JSON format")],
    model_type: Annotated[Optional[Literal["model", "adapter"]], Parameter(name="--model-type", show_choices=True, help="Whether the model is a full model or an adapter")],
    config: Annotated[Config, Parameter(name="*", group="General")] = Config(),
) -> None:
    """Upload a custom model or adapter from Hugging Face or S3"""
    client = config.client()

    response: ModelUploadResponse = await client.models.upload(
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

        print(f"Model upload job created successfully!")
        if response.data.job_id:
            print(f"Job ID: {response.data.job_id}")
        if response.data.x_model_name:
            print(f"Model Name: {response.data.x_model_name}")
        if response.data.x_model_id:
            print(f"Model ID: {response.data.x_model_id}")
        if response.data.x_model_source:
            print(f"Model Source: {response.data.x_model_source}")
        print(f"Message: {response.message}")
