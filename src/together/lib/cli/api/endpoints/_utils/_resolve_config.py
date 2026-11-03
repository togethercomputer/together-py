from __future__ import annotations

import re

from together.types.models.config import Config
from together.lib.cli.utils.config import CLIConfigParameter
from together.types.supported_model_deployment_profile import SupportedModelDeploymentProfile

_CONFIG_PATH_RE = re.compile(r"^projects/([^/]+)/configs/([^/]+)$")


async def resolve_configs(config: CLIConfigParameter, model_id: str) -> list[Config]:
    configs = await config.client.models.configs.list(reference_model_id=model_id)
    return list(configs.data or [])


def find_config(configs: list[Config], config_id: str) -> Config | None:
    """Return the config matching ``config_id``, if any."""
    for candidate in configs:
        if _config_id_matches(candidate, config_id):
            return candidate
    return None


MULTIPLE_CONFIGS_MESSAGE = (
    "Multiple configs found for model. Please specify a config id using the --config flag. "
    "You can use `tg models configs <model-id>` to list configs that can be used."
)


def config_from_explicit_ref(config_id: str, *, project_id: str | None) -> Config:
    """Build a Config stub from an explicit ``--config`` value without membership checks.

    Fully-qualified ``projects/{projectId}/configs/{id}`` paths keep both fields.
    Bare ``cr_...`` ids are qualified with the CLI ``--project`` (required by deploy
    commands) so callers can always send the resource-name ``config`` field.
    """
    match = _CONFIG_PATH_RE.match(config_id)
    if match:
        return Config.construct(id=match.group(2), projectId=match.group(1))
    if not project_id:
        raise ValueError(
            f"Config {config_id} needs a project. Pass --project, or a fully-qualified "
            "path projects/<project-id>/configs/<config-id>."
        )
    return Config.construct(id=config_id, projectId=project_id)


def resolve_config(
    configs: list[Config],
    config_id: str | None,
    *,
    model: str,
    project_id: str | None = None,
) -> Config:
    """Pick a config from the model's config list.

    An explicit ``--config`` is preferred from the list when present (so we keep the
    owning ``projectId`` / selectors for pricing). If it is missing from the
    client-side list, forward it anyway — the API validates model/config
    compatibility. Auto-selection (no ``--config``) still requires a unique list hit.
    """
    if config_id is None:
        if len(configs) > 1:
            from together.lib.cli.api.models._utils import print_configs_table

            print_configs_table(configs, empty_message="")
            raise ValueError(MULTIPLE_CONFIGS_MESSAGE)
        if len(configs) == 0:
            raise ValueError(f"No configs found for model {model}.")
        return configs[0]

    selected = find_config(configs, config_id)
    if selected is not None:
        return selected
    return config_from_explicit_ref(config_id, project_id=project_id)


async def choose_config(
    cli: CLIConfigParameter,
    configs: list[Config],
    config_id: str | None,
    *,
    model: str,
) -> Config:
    """Use ``--config`` or the only config. Several configs prompt, or fail when non-interactive."""
    if config_id is None and len(configs) > 1 and not cli.non_interactive:
        return await prompt_for_config(configs, model=model)
    return resolve_config(configs, config_id, model=model, project_id=cli.project_id)


async def prompt_for_config(configs: list[Config], *, model: str) -> Config:
    """Ask which config to deploy. A cancelled or unavailable prompt fails like ``--non-interactive``."""
    from together.lib.cli.utils._prompt import PromptParameter
    from together.lib.cli.api.models._utils import print_configs_table

    print_configs_table(configs, empty_message="")
    choices: list[str | tuple[str, str]] = []
    for item in configs:
        if item.id:
            choices.append((item.id, item.id))
    try:
        selected_id = await PromptParameter(
            message="Which config should this deployment use?",
            instructions=f"{model} has more than one config. Pick one, or rerun with --config.",
            choices=choices,
        ).prompt("config")
    except ValueError:
        raise
    except Exception:
        raise ValueError(MULTIPLE_CONFIGS_MESSAGE) from None

    selected = find_config(configs, str(selected_id))
    if selected is None:
        raise ValueError(MULTIPLE_CONFIGS_MESSAGE)
    return selected


def _config_id_matches(config: Config, config_id: str) -> bool:
    if config.id == config_id:
        return True
    if config.id and config_id.endswith(f"/configs/{config.id}"):
        return True
    if config.project_id and config.id and config_id == f"projects/{config.project_id}/configs/{config.id}":
        return True
    return False


def validate_requested_config(
    config: Config,
    config_id: str | None,
    *,
    project_id: str | None = None,
) -> Config:
    """Prefer an explicit CLI ``--config`` over a resolved default.

    When the resolved config already matches, keep it (full body / owning project).
    Otherwise forward the explicit ref and let the API validate compatibility.
    """
    if config_id is None:
        return config
    if _config_id_matches(config, config_id):
        return config
    return config_from_explicit_ref(config_id, project_id=project_id)


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
