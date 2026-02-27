from __future__ import annotations

from typing_extensions import override

from rich import print
from clypi import Command, arg

from together import Together, omit
from together._response import APIResponse as APIResponse
from together._utils._json import openapi_dumps
from together.types.model_upload_response import ModelUploadResponse


class Upload(Command):
    """Upload a custom model or adapter from Hugging Face or S3"""

    model_name: str = arg(help="The name to give to your uploaded model")
    model_source: str = arg(help="The source location of the model (Hugging Face repo or S3 path)")
    hf_token: str | None = arg(None, help="Hugging Face token (if uploading from Hugging Face)")
    description: str | None = arg(None, help="A description of your model")
    base_model: str | None = arg(
        None,
        help="The base model to use for an adapter if setting it to run against a serverless pool. Only used for model_type 'adapter'.",
    )
    lora_model: str | None = arg(
        None,
        help="The lora pool to use for an adapter if setting it to run against, say, a dedicated pool. Only used for model_type 'adapter'.",
    )
    json: bool = arg(False, help="Output in JSON format")
    model_type: str | None = arg(None, help="Whether the model is a full model or an adapter")

    @override
    async def run(self):
        """Upload a custom model or adapter from Hugging Face or S3"""
        client = Together()

        response: ModelUploadResponse = client.models.upload(
            model_name=self.model_name,
            model_source=self.model_source,
            model_type=self.model_type or omit,
            hf_token=self.hf_token or omit,
            description=self.description or omit,
            base_model=self.base_model or omit,
            lora_model=self.lora_model or omit,
        )

        if self.json:
            print(openapi_dumps(response))
            return

        print(f"Model upload job created successfully!")
        print(f"Job ID: {response.data.job_id}")
        print(f"Model Name: {response.data.x_model_name}")
        print(f"Model ID: {response.data.x_model_id}")
        print(f"Model Source: {response.data.x_model_source}")
        print(f"Message: {response.message}")
