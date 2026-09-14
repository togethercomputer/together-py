from __future__ import annotations

import re

from together.lib.cli.utils.config import CLIConfigParameter
from together.types.beta.models.config import Config
from together.types.beta.supported_model_deployment_profile import SupportedModelDeploymentProfile

_CONFIG_PATH_RE = re.compile(r"^projects/([^/]+)/configs/([^/]+)$")


async def resolve_configs(config: CLIConfigParameter, model_id: str) -> list[Config]:
    configs = await config.client.beta.models.configs.list(reference_model_id=model_id)
    return configs.data


def resolve_config(configs: list[Config], config_id: str | None, *, model: str) -> Config:
    """Pick a config from the model's config list, validating an explicit --config when given."""
    if config_id is None:
        if len(configs) > 1:
            from together.lib.cli.api.beta.models._utils import print_configs_table

            print_configs_table(configs, empty_message="")
            raise ValueError(
                "Multiple configs found for model. Please specify a config id using the --config flag. "
                "You can use `tg beta models configs <model-id>` to list configs that can be used."
            )
        if len(configs) == 0:
            raise ValueError(f"No configs found for model {model}.")
        return configs[0]

    for candidate in configs:
        if _config_id_matches(candidate, config_id):
            return candidate
    raise ValueError(
        f"Config {config_id} is not valid for model {model}. Use `tg beta models configs <model-id>` to list configs."
    )


def _config_id_matches(config: Config, config_id: str) -> bool:
    if config.id == config_id:
        return True
    if config.id and config_id.endswith(f"/configs/{config.id}"):
        return True
    if config.project_id and config.id and config_id == f"projects/{config.project_id}/configs/{config.id}":
        return True
    return False


def validate_requested_config(config: Config, config_id: str | None, *, model: str) -> Config:
    """Re-check the resolved config against an explicit CLI --config, when provided."""
    if config_id is None:
        return config
    if _config_id_matches(config, config_id):
        return config
    raise ValueError(f"Config {config_id} is not valid for model {model}. Resolved config id is {config.id}.")


def config_from_profile(profile: SupportedModelDeploymentProfile) -> Config:
    """Build a Config stub from a public supported-model deployment profile.

    Only ``id`` / ``project_id`` are populated — enough for ``construct_config_path``.
    Full config bodies come from the configs API for private models.
    """
    if profile.config:
        match = _CONFIG_PATH_RE.match(profile.config)
        if match:
            return Config.construct(id=match.group(2), projectId=match.group(1))

    config_id = profile.certified_config_revision_id
    if config_id and profile.model:
        project_match = re.match(r"^projects/([^/]+)/models/", profile.model)
        if project_match:
            return Config.construct(id=config_id, projectId=project_match.group(1))

    raise ValueError(f"Deployment profile has no usable config path: {profile.to_json()}")


def construct_config_path(config: Config) -> str:
    return f"projects/{config.project_id}/configs/{config.id}"
