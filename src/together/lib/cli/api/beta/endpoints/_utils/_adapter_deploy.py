from __future__ import annotations

import re
from typing import Any, cast

from together import NotFoundError
from together.types.beta import Model, EndpointDeployment
from together.lib.cli.utils.config import CLIConfigParameter
from together.types.beta.models.config import Config
from together.lib.cli.api.beta.endpoints._utils._resolve_model import MODEL_PATH_RE, load_model
from together.lib.cli.api.beta.endpoints._utils._resolve_config import (
    find_config,
    resolve_config,
    prompt_for_config,
)
from together.lib.cli.api.beta.endpoints._utils._hardware_pricing import selector_value

ADAPTER_WEIGHTS_TYPE = "WEIGHTS_TYPE_ADAPTER"
_LORA_ADAPTER_MODES = frozenset({"fixed", "dynamic"})
# Lower rank wins. Dynamic is preferred over fixed when both can host the adapter.
_ADAPTER_MODE_RANK = {"dynamic": 0, "fixed": 1}
_CONFIG_PATH_RE = re.compile(r"^projects/([^/]+)/configs/([^/]+)$")
_STATE_RANK = {
    "DEPLOYMENT_STATE_READY": 0,
    "DEPLOYMENT_STATE_SCALING": 1,
    "DEPLOYMENT_STATE_PROVISIONING": 2,
    "DEPLOYMENT_STATE_DEGRADED": 3,
    "DEPLOYMENT_STATE_STOPPED": 4,
    "DEPLOYMENT_STATE_STOPPING": 5,
    "DEPLOYMENT_STATE_FAILED": 6,
}


def is_adapter_model(model: Model) -> bool:
    return model.weights.type == ADAPTER_WEIGHTS_TYPE


def config_adapter_mode(model_config: Config) -> str | None:
    """Return ``fixed``, ``dynamic``, ``disabled``, or ``unspecified``.

    Public configs expose this as the ``adapter_mode`` selector (``fixed`` /
    ``dynamic`` / ``disabled``). Composite config payloads use ``adapterMode``
    with the ``ADAPTER_MODE_*`` enum. An unset mode is LoRA off.
    """
    raw = selector_value(model_config, "adapter_mode") or selector_value(model_config, "adapterMode")
    if not raw:
        extra_value = getattr(model_config, "model_extra", None) or getattr(model_config, "__pydantic_extra__", None)
        extra = cast(dict[str, Any], extra_value) if isinstance(extra_value, dict) else {}
        candidate = extra.get("adapterMode", extra.get("adapter_mode"))
        raw = candidate if isinstance(candidate, str) else None
    if not raw or not raw.strip():
        return None
    normalized = raw.strip().lower()
    if normalized.startswith("adapter_mode_"):
        normalized = normalized[len("adapter_mode_") :]
    if normalized in {"fixed", "dynamic", "disabled", "unspecified"}:
        return normalized
    return None


def config_serves_adapters(model_config: Config) -> bool:
    return config_adapter_mode(model_config) in _LORA_ADAPTER_MODES


def deployment_serves_model(deployment: EndpointDeployment, model: Model) -> bool:
    """True when the deployment is serving ``model``, including a pinned revision."""
    if model.id and deployment.api_model_id == model.id:
        return True
    path = deployment.model or ""
    match = MODEL_PATH_RE.match(path)
    if match is not None and model.id and match.group(2) == model.id:
        return True
    if model.project_id and model.id:
        base = f"projects/{model.project_id}/models/{model.id}"
        if path == base or path.startswith(base + "/"):
            return True
    return False


def select_lora_config(configs: list[Config], config_id: str | None, *, model: str) -> Config:
    """Pick a fixed or dynamic LoRA config.

    An explicit ``config_id`` must itself be fixed or dynamic. With no id, the only LoRA
    config is used. Several LoRA configs fail here; interactive deploy prompts instead.
    """
    if config_id is not None:
        selected = find_config(configs, config_id)
        if selected is None:
            raise ValueError(
                f"Config {config_id} is not valid for model {model}. "
                "Use `tg beta models configs <model-id>` to list configs."
            )
        if not config_serves_adapters(selected):
            mode = config_adapter_mode(selected) or "disabled"
            raise ValueError(
                f"Config {selected.id} has adapter_mode {mode} and cannot serve LoRA adapters. "
                "Use a config with adapter_mode fixed or dynamic."
            )
        return selected

    lora_configs = _ordered_lora_configs(configs)
    if not lora_configs:
        raise ValueError(
            f"No fixed or dynamic LoRA config found for {model}. "
            "An adapter can only deploy onto a config with adapter_mode fixed or dynamic. "
            f"List configs with `tg beta models configs {model}`."
        )
    if len(lora_configs) == 1:
        return lora_configs[0]
    return resolve_config(lora_configs, None, model=model)


async def select_lora_config_for_deploy(
    cli: CLIConfigParameter,
    configs: list[Config],
    config_id: str | None,
    *,
    model: str,
) -> Config:
    """Same as ``select_lora_config``, but prompt when several LoRA configs exist."""
    if config_id is not None or cli.non_interactive:
        return select_lora_config(configs, config_id, model=model)

    lora_configs = _ordered_lora_configs(configs)
    if len(lora_configs) <= 1:
        return select_lora_config(configs, None, model=model)
    return await prompt_for_config(lora_configs, model=model)


def _ordered_lora_configs(configs: list[Config]) -> list[Config]:
    """LoRA-capable configs, dynamic before fixed. Order is for display, not auto-selection."""
    lora_configs = [item for item in configs if config_serves_adapters(item)]
    return sorted(lora_configs, key=lambda item: (_adapter_mode_rank(config_adapter_mode(item)), item.id or ""))


def _adapter_mode_rank(mode: str | None) -> int:
    return _ADAPTER_MODE_RANK.get(mode or "", 9)


async def load_adapter_model(config: CLIConfigParameter, model_input: str) -> Model | None:
    """Load ``model_input`` when it is a LoRA adapter. Return None for every other model."""
    model = await load_model(config, model_input)
    if model is None or not is_adapter_model(model):
        return None
    return model


async def load_base_model(config: CLIConfigParameter, adapter: Model) -> Model:
    label = adapter.name or adapter.id
    if not adapter.base_model and not adapter.base_model_id:
        raise ValueError(f"Adapter {label} has no base model, so it cannot be deployed.")

    match = MODEL_PATH_RE.match(adapter.base_model or "")
    if match:
        try:
            return await config.client.beta.models.retrieve(id=match.group(2), project_id=match.group(1))
        except NotFoundError:
            raise ValueError(f"Base model {adapter.base_model} for adapter {label} was not found.") from None

    assert adapter.base_model_id is not None
    try:
        return await config.client.beta.models.retrieve(
            id=adapter.base_model_id,
            project_id=adapter.project_id,
        )
    except NotFoundError:
        raise ValueError(f"Base model {adapter.base_model_id} for adapter {label} was not found.") from None


async def list_model_configs(config: CLIConfigParameter, model_id: str) -> list[Config]:
    configs: list[Config] = []
    async for item in config.client.beta.models.configs.list(reference_model_id=model_id):
        configs.append(item)
    return configs


async def find_compatible_deployment(
    config: CLIConfigParameter,
    endpoint_id: str,
    *,
    base: Model,
    configs: list[Config],
    config_id: str | None,
    deployment_name: str | None = None,
) -> EndpointDeployment | None:
    """Pick a base-model deployment whose config is dynamic or fixed LoRA mode.

    Dynamic deployments are preferred over fixed ones. Within a mode, non-shadow deployments
    come first, then healthier state. When ``deployment_name`` is set, the deployment with that
    name is returned as-is when it exists; the API reports any incompatibility when the adapter
    is attached. Returns None when no such deployment exists, so the caller creates it.
    """
    deployments: list[EndpointDeployment] = []
    async for deployment in config.client.beta.endpoints.deployments.list(endpoint_id):
        deployments.append(deployment)

    if deployment_name is not None:
        return _find_deployment_by_name(deployments, deployment_name)

    by_id = {item.id: item for item in configs if item.id}
    matches: list[tuple[EndpointDeployment, Config]] = []
    for deployment in deployments:
        if not deployment_serves_model(deployment, base):
            continue
        model_config = await _config_for_deployment(config, deployment, by_id)
        if model_config is None or not config_serves_adapters(model_config):
            continue
        if config_id is not None and find_config([model_config], config_id) is None:
            continue
        matches.append((deployment, model_config))
    if not matches:
        return None
    deployment, _model_config = min(matches, key=lambda item: _deployment_preference(item[0], item[1]))
    return deployment


def _find_deployment_by_name(deployments: list[EndpointDeployment], name: str) -> EndpointDeployment | None:
    bare = name.rsplit("/", 1)[-1]
    for deployment in deployments:
        if deployment.name == name or (deployment.name or "").rsplit("/", 1)[-1] == bare:
            return deployment
    return None


def _lookup_config(deployment: EndpointDeployment, by_id: dict[str, Config]) -> Config | None:
    if deployment.config_id and deployment.config_id in by_id:
        return by_id[deployment.config_id]
    match = _CONFIG_PATH_RE.match(deployment.config or "")
    if match is not None and match.group(2) in by_id:
        return by_id[match.group(2)]
    return None


async def _config_for_deployment(
    config: CLIConfigParameter,
    deployment: EndpointDeployment,
    by_id: dict[str, Config],
) -> Config | None:
    cached = _lookup_config(deployment, by_id)
    if cached is not None:
        return cached

    match = _CONFIG_PATH_RE.match(deployment.config or "")
    if match is None:
        return None
    try:
        loaded = await config.client.beta.models.configs.retrieve(id=match.group(2), project_id=match.group(1))
    except NotFoundError:
        return None
    if loaded.id:
        by_id[loaded.id] = loaded
    return loaded


def _deployment_preference(deployment: EndpointDeployment, model_config: Config) -> tuple[int, int, int]:
    traffic_mode = getattr(deployment, "traffic_mode", None)
    shadow = 1 if traffic_mode == "TRAFFIC_MODE_SHADOW" else 0
    status = getattr(deployment, "status", None)
    state = getattr(status, "state", "") if status is not None else ""
    return (_adapter_mode_rank(config_adapter_mode(model_config)), shadow, _STATE_RANK.get(state, 9))
