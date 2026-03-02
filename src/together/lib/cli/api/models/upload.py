from __future__ import annotations

from typing import Annotated, Literal, Optional

from cyclopts import Parameter

from together import AsyncTogether, TogetherError, omit

from together.types.model_upload_response import ModelUploadResponse


async def upload(
    model_name: str,
    model_source: str,
    model_type: Literal["model", "adapter"] = "model",
    hf_token: Optional[str] = None,
    description: Optional[str] = None,
    base_model: Optional[str] = None,
    lora_model: Optional[str] = None,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Upload a custom model or adapter from Hugging Face or S3."""
    response: ModelUploadResponse = await client.models.upload(
        model_name=model_name,
        model_source=model_source,
        model_type=model_type or omit,
        hf_token=hf_token or omit,
        description=description or omit,
        base_model=base_model or omit,
        lora_model=lora_model or omit,
    )

    if json_output:
        import json as json_lib

        print(json_lib.dumps(response.model_dump(), indent=2))
        return

    if response.data is None:  # type: ignore
        raise TogetherError(response.message)

    print("Model upload job created successfully!")
    if response.data.job_id:
        print(f"Job ID: {response.data.job_id}")
    if response.data.x_model_name:
        print(f"Model Name: {response.data.x_model_name}")
    if response.data.x_model_id:
        print(f"Model ID: {response.data.x_model_id}")
    if response.data.x_model_source:
        print(f"Model Source: {response.data.x_model_source}")
    print(f"Message: {response.message}")
