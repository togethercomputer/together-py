from __future__ import annotations

from typing import Literal, Optional, Annotated
from typing_extensions import override

from cyclopts import Group, Parameter
from cyclopts.validators import mutually_exclusive

from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._prompt import PromptParameter
from together.types.beta.deployment_placement_config_param import DeploymentPlacementConfigParam
from together.types.beta.endpoints.deployment_create_params import (
    Placement,
    PlacementInline,
)


class PlacementModel:
    regions: Optional[str] = None
    constraint: Optional[Literal["required", "preferred"]] = None
    # hipaa: Optional[bool] = None

    def __init__(
        self,
        regions: Annotated[Optional[str], Parameter(help="Comma-separated inline placement regions")] = None,
        constraint: Annotated[
            Optional[Literal["required", "preferred"]], Parameter(help="Inline placement enforcement")
        ] = None,
        # hipaa: Annotated[Optional[bool], Parameter(help="Require HIPAA-eligible placement", negative=())] = None,
    ):
        self.regions = regions
        self.constraint = constraint
        # self.hipaa = hipaa

    def to_json(self) -> Placement | None:
        if self.regions is None and self.constraint is None:  # and self.hipaa is None:
            return None

        inline: DeploymentPlacementConfigParam = {}

        if self.regions:
            inline["regions"] = self.regions.split(",")
        if self.constraint:
            inline["constraint"] = "ENFORCEMENT_REQUIRED" if self.constraint == "required" else "ENFORCEMENT_PREFERRED"
        # if self.hipaa:
        #     inline["hipaa"] = self.hipaa

        return PlacementInline(inline=inline)


placement_model = PlacementModel()


PlacementGroup = Group(validator=mutually_exclusive)


class ModelPromptParameter(PromptParameter):
    message = "Model:"
    instructions = "What model would you like to shadow traffic to?"

    @override
    async def preprompt(self, config: CLIConfig) -> None:
        models = await config.client.beta.models.list()
        public_models = await config.client.beta.models.list_supported()
        show_more = models.next_cursor is not None
        self.choices = [("/".join(model.name.split("/")[1:]), model.id) for model in models.data]
        for model in public_models.data:
            if model.deployment_profiles:
                profile_model = model.deployment_profiles[0].model
                if profile_model:
                    self.choices.append((model.name, profile_model))

        if show_more:
            self.choices.append(("Show more", "show_more"))


ModelParameter = Annotated[
    str,
    Parameter(
        help="""Model to deploy. Accepted forms:

- Public model name (for example, zai-org/GLM-5.2).
- Private model name, with or without the project slug.
- Private model ID (ml_...).
- Fully qualified model resource path returned by the API."""
    ),
    ModelPromptParameter(instructions="What model would you like to deploy to this endpoint?", message="Model"),
]


class EndpointPromptParameter(PromptParameter):
    message = "Endpoint ID:"
    instructions = "What endpoint are we adding a shadow to?"

    @override
    async def preprompt(self, config: CLIConfig) -> None:
        endpoints = await config.client.beta.endpoints.list()
        show_more = endpoints.next_cursor is not None
        self.choices = [("/".join(endpoint.name.split("/")[1:]), endpoint.id) for endpoint in endpoints.data]
        if show_more:
            self.choices.append(("Show more", "show_more"))
