from __future__ import annotations

from typing import Annotated, Literal, Optional

from cyclopts import Parameter 
from rich.console import Console
from rich.theme import Theme

from together import TogetherError, omit

from together.lib.cli import Config
from together.lib.cli.logger.prompt import PromptParameter
from together.types.model_upload_response import ModelUploadResponse
from together._utils._json import openapi_dumps

custom_theme = Theme({
    # Text styles
    "primary": "#caaef5",       # Purple 300 ⭐ (lighter when bold)
    "secondary": "dim #caaef5",          # Purple 500 ⭐ (mid-tone without bold)
    "accent": "#ff68d4",             # Pink 500 ⭐
    "muted": "#98a0b3",              # Grey 400 ⭐
    "dim": "dim #626b84",            # Grey 600 ⭐

    # Semantic styles
    "success": "bold #0dce74",       # Green 400 ⭐
    "info": "#64afff",               # Blue 500 ⭐
    "warning": "bold #ff815d",       # Red 500 ⭐
    "error": "bold #c63800",         # Red 700 ⭐

    # UI elements
    "prompt": "#ba92ff",             # Purple 500 ⭐ (no bold)
    "prompt.choices": "#caaef5",     # Purple 300 ⭐
    "prompt.default": "dim #98a0b3", # Grey 400 ⭐

    # Table styles
    "table.header": "#414858",  # Purple 300 ⭐ (lighter when bold)
    "table.border": "#626b84",       # Grey 600 ⭐
    "table.row": "#c4c9d4",          # Grey 300 ⭐

    # Progress/Loading
    "progress.description": "#caaef5",     # Purple 300 ⭐
    "progress.percentage": "bold #caaef5", # Purple 300 ⭐ (lighter when bold)
    "bar.complete": "#ba92ff",             # Purple 500 ⭐ (no bold)
    "bar.finished": "#0dce74",             # Green 400 ⭐
    "bar.pulse": "#ff68d4",                # Pink 500 ⭐
})

console = Console(theme=custom_theme)

async def upload(
    model_name: Annotated[str, Parameter(required=True), PromptParameter(instructions="What model name identifier would you like to use?", message="Model Name")],
    model_source: Annotated[str, Parameter(required=True), PromptParameter(instructions="What is the source location of the model (Hugging Face repo or S3 path)?", message="Model Source")],
    model_type: Literal["model", "adapter"] = "model",
    hf_token: Optional[str] = None,
    description: Optional[str] = None,
    base_model: Optional[str] = None,
    lora_model: Optional[str] = None,
    *,
    config: Annotated[Config, Parameter(parse=False)],
) -> None:
    """Upload a custom model or adapter from Hugging Face or S3."""
    response: ModelUploadResponse = await config.client.models.upload(
        model_name=model_name,
        model_source=model_source,
        model_type=model_type or omit,
        hf_token=hf_token or omit,
        description=description or omit,
        base_model=base_model or omit,
        lora_model=lora_model or omit,
    )

    if config.json:
        print(openapi_dumps(response))
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