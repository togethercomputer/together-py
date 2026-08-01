from __future__ import annotations

from typing import Literal
from typing_extensions import Annotated, override

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig, CLIConfigParameter
from together.lib.cli.utils._prompt import PromptParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.models._utils import print_model_detail
from together.lib.cli.utils._assert_explicit_project_id import assert_explicit_project_id
from together.lib.cli.api.beta.endpoints._utils._resolve_model import MODEL_PATH_RE


class PromptBaseModel(PromptParameter):
    message = "Compatible Base Model:"
    instructions = "Select a base model"

    @override
    async def preprompt(self, config: CLIConfig) -> None:
        # TODO: support pagination
        supported_models = await config.client.beta.models.list_supported()

        self.choices = []

        for model in supported_models.data:
            for profile in model.deployment_profiles:
                match = MODEL_PATH_RE.match(profile.model)
                if match:
                    model_id = match.group(2)
                    self.choices.append((f"{model.name} ({profile.quantization})", model_id))


async def create(
    name: Annotated[
        str,
        Parameter(help="Inference-addressable name for the new model or adapter record"),
        PromptParameter(message="Model Name", instructions="Give your model a name that can be referenced later."),
    ],
    *,
    base_model: Annotated[
        str,
        Parameter(help="Supported base model ID (ml_...); run `tg beta models public` to find it"),
        PromptBaseModel(),
    ],
    type: Annotated[
        Literal["model", "adapter"],
        Parameter(name="type", help="Record type: full model weights or a LoRA adapter"),
    ] = "model",
    config: CLIConfigParameter,
) -> None:
    """Register a model (does not upload files)"""

    await assert_explicit_project_id(config)

    response = await show_loading_status(
        "Creating beta model...",
        config.client.beta.models.create(name=name, base_model_id=base_model, type=type),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]√[/green] Beta model created.")
    await print_model_detail(response, config=config)
