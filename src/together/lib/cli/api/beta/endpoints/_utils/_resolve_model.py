from __future__ import annotations

import re
from typing import NamedTuple

from together import NotFoundError
from together.types.beta import Model, Endpoint
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.types.beta.models.config import Config
from together.types.beta.supported_model_deployment_profile import SupportedModelDeploymentProfile
from together.lib.cli.api.beta.endpoints._utils._resolve_config import (
    resolve_config,
    resolve_configs,
    config_from_profile,
    validate_requested_config,
)

# Logic for resolving a model + config from a user input string
#
# 1. Raw model id (e.g. ml_...)
#    → retrieve from --project when possible; config via baseModelId / id
#    → else GET /configs?referenceModelId=... (public / reference models)
# 2. Full model path (projects/.../models/...)
#    → retrieve that model (keep it as the deploy target), resolve config via
#      baseModelId (or the model id when it is itself a reference model).
#      Preserve an optional /revisions/... pin on the deploy path.
# 3. Named model (prefix/model-name)
#    a. prefix == project slug → list private models by name, resolve config via
#       baseModelId (path 1), but deploy the custom model path
#    b. otherwise → search supported-models (exactly one), resolve config from
#       deployment profiles
#
# Deployment-profile config selection:
#   - one profile + no --config → use that profile's config
#   - --config given → use the profile whose config matches
# After either path, re-validate against the user's --config when provided.
MODEL_PATH_RE = re.compile(r"^projects/([^/]+)/models/([^/]+)(?:/revisions/([^/]+))?$")


class ResolvedModelAndConfig(NamedTuple):
    model: Model
    config: Config
    revision_id: str | None = None


async def resolve_model(
    config: CLIConfigParameter,
    model_input: str,
    *,
    config_id: str | None = None,
) -> Model:
    resolved = await resolve_model_and_config(config, model_input, config_id=config_id)
    return resolved.model


async def resolve_model_and_config(
    config: CLIConfigParameter,
    model_input: str,
    *,
    config_id: str | None = None,
) -> ResolvedModelAndConfig:
    """Resolve a deployable model and the config revision to pair with it."""
    # 2. Full model path → keep the user's model; config from its base/reference.
    path_match = MODEL_PATH_RE.match(model_input)
    if path_match:
        project_id, model_id, revision_id = path_match.group(1), path_match.group(2), path_match.group(3)
        return await _resolve_explicit_model(
            config,
            model_id=model_id,
            project_id=project_id,
            config_id=config_id,
            model_input=model_input,
            revision_id=revision_id,
        )

    # 1. Raw model id
    if "/" not in model_input:
        if config.project_id:
            try:
                model = await config.client.beta.models.retrieve(id=model_input, project_id=config.project_id)
            except NotFoundError:
                pass
            else:
                reference_model_id = model.base_model_id or model.id
                assert reference_model_id is not None
                return await _resolve_config_for_model(
                    config,
                    model,
                    reference_model_id=reference_model_id,
                    config_id=config_id,
                    model_input=model_input,
                )
        return await _resolve_via_configs(config, model_input, config_id=config_id, model_input=model_input)

    # 3. Named model (prefix/model-name)
    me = await config.client.whoami()
    project_slug = me.project_slug
    prefix, _, _name = model_input.partition("/")

    if prefix == project_slug:
        model = await _find_private_model_by_name(config, model_input)
        reference_model_id = model.base_model_id or model.id
        assert reference_model_id is not None
        # Config comes from the base/reference model; deploy path stays the custom model.
        return await _resolve_config_for_model(
            config,
            model,
            reference_model_id=reference_model_id,
            config_id=config_id,
            model_input=model_input,
        )

    return await _resolve_public_model_and_config(config, model_input, config_id=config_id)


async def _resolve_explicit_model(
    config: CLIConfigParameter,
    *,
    model_id: str,
    project_id: str,
    config_id: str | None,
    model_input: str,
    revision_id: str | None = None,
) -> ResolvedModelAndConfig:
    """Load the user-specified model and pair it with a compatible config."""
    try:
        model = await config.client.beta.models.retrieve(id=model_id, project_id=project_id)
    except NotFoundError:
        raise ValueError(f"Model {model_input} not found.") from None

    reference_model_id = model.base_model_id or model.id
    assert reference_model_id is not None
    return await _resolve_config_for_model(
        config,
        model,
        reference_model_id=reference_model_id,
        config_id=config_id,
        model_input=model_input,
        revision_id=revision_id,
    )


async def _resolve_config_for_model(
    config: CLIConfigParameter,
    model: Model,
    *,
    reference_model_id: str,
    config_id: str | None,
    model_input: str,
    revision_id: str | None = None,
) -> ResolvedModelAndConfig:
    selected = resolve_config(
        await resolve_configs(config, reference_model_id),
        config_id,
        model=model_input,
    )
    selected = validate_requested_config(selected, config_id, model=model_input)
    return ResolvedModelAndConfig(model=model, config=selected, revision_id=revision_id)


async def _resolve_via_configs(
    config: CLIConfigParameter,
    reference_model_id: str,
    *,
    config_id: str | None,
    model_input: str,
) -> ResolvedModelAndConfig:
    """Resolve a public/reference model id through the configs API.

    The deploy target is the config's reference model — correct when the user
    passed a bare reference-model id that is not retrievable under --project.
    """
    selected = resolve_config(
        await resolve_configs(config, reference_model_id),
        config_id,
        model=model_input,
    )
    selected = validate_requested_config(selected, config_id, model=model_input)
    model = await _retrieve_model_from_reference(config, selected, model_input=model_input)
    return ResolvedModelAndConfig(model=model, config=selected)


async def _retrieve_model_from_reference(
    config: CLIConfigParameter,
    selected: Config,
    *,
    model_input: str,
) -> Model:
    """Load the named model via config.referenceModel (projects/.../models/...)."""
    path = selected.reference_model or ""
    match = MODEL_PATH_RE.match(path)
    if match:
        project_id, model_id = match.group(1), match.group(2)
    elif selected.reference_model_id and selected.project_id:
        project_id, model_id = selected.project_id, selected.reference_model_id
    else:
        raise ValueError(f"Config {selected.id} has no usable reference model path.")

    try:
        return await config.client.beta.models.retrieve(id=model_id, project_id=project_id)
    except NotFoundError:
        raise ValueError(f"Model {model_input} not found.") from None


async def _find_private_model_by_name(config: CLIConfigParameter, name: str) -> Model:
    bare = name.rsplit("/", 1)[-1]
    matches: list[Model] = []
    async for model in config.client.beta.models.list():
        if model.name == name or model.name == bare or model.name.rsplit("/", 1)[-1] == bare:
            matches.append(model)

    if not matches:
        raise ValueError(f"Model {name} not found.")
    if len(matches) > 1:
        raise ValueError(f"""Multiple models found for "{name}".
Please specify a more specific model ID. To find a more specific model variant to use, try this:

- tg beta models public --search {name}
""")
    return matches[0]


def _profile_matches_config(profile: SupportedModelDeploymentProfile, config_id: str) -> bool:
    if profile.certified_config_revision_id == config_id:
        return True
    if profile.profile_id == config_id:
        return True
    if profile.config and (profile.config == config_id or profile.config.endswith(f"/configs/{config_id}")):
        return True
    return False


def _profile_model_id(profile: SupportedModelDeploymentProfile) -> str:
    match = MODEL_PATH_RE.match(profile.model or "")
    if match:
        return match.group(2)
    if profile.model and "/" in profile.model:
        return profile.model.rsplit("/", 1)[-1]
    return profile.model or ""


def _profile_config_id(profile: SupportedModelDeploymentProfile) -> str:
    return profile.certified_config_revision_id or profile.profile_id or ""


def _profile_gpu(profile: SupportedModelDeploymentProfile) -> str:
    if profile.gpu_count or profile.gpu_type:
        return f"{profile.gpu_count or '?'}x {profile.gpu_type or '?'}"
    return ""


def _print_deployment_profiles(profiles: list[SupportedModelDeploymentProfile], *, model_input: str) -> None:
    from together.lib.cli.components.list import ListTable

    table = ListTable(f"Available configs for {model_input}")
    table.add_primary_column("Quant")
    table.add_column("GPUs")
    table.add_column("Parallelism")
    table.add_column("Model ID", ratio=2)
    table.add_column("Config", ratio=2)

    for profile in profiles:
        table.add_row(
            profile.quantization or "",
            _profile_gpu(profile),
            profile.parallelism or "",
            _profile_model_id(profile),
            _profile_config_id(profile),
        )
    console.print(table)

    example = profiles[0]
    example_model = _profile_model_id(example)
    example_config = _profile_config_id(example)
    console.print("\n[blue dim]Pick one and rerun with both flags, for example:[/blue dim]")
    console.print(
        f"  [dim]-[/dim] [white]tg beta endpoints deploy --model {example_model} "
        f"--config {example_config} --endpoint <ENDPOINT>[/white]"
    )


def _select_deployment_profile(
    profiles: list[SupportedModelDeploymentProfile],
    *,
    model_input: str,
    config_id: str | None,
) -> SupportedModelDeploymentProfile:
    if len(profiles) == 1:
        profile = profiles[0]
        if config_id is not None and not _profile_matches_config(profile, config_id):
            expected = _profile_config_id(profile)
            raise ValueError(f"Config {config_id} is not valid for model {model_input}. Expected {expected}.")
        return profile

    if config_id is None:
        _print_deployment_profiles(profiles, model_input=model_input)
        raise ValueError(f"Multiple configs found for {model_input}. Pass --model <model-id> and --config <config-id>.")

    matching = [profile for profile in profiles if _profile_matches_config(profile, config_id)]
    if len(matching) == 0:
        _print_deployment_profiles(profiles, model_input=model_input)
        raise ValueError(
            f"Config {config_id} is not valid for model {model_input}. Use a --config from the table above."
        )
    if len(matching) > 1:
        _print_deployment_profiles(matching, model_input=model_input)
        raise ValueError(
            f"Multiple profiles for {model_input} match config {config_id}. "
            "Pass a more specific --model <model-id> from the table above."
        )
    return matching[0]


async def _resolve_public_model_and_config(
    config: CLIConfigParameter,
    model_input: str,
    *,
    config_id: str | None = None,
) -> ResolvedModelAndConfig:
    supported_models = await config.client.beta.models.list_supported(search=model_input)
    if not supported_models.data:
        raise ValueError(f"Model {model_input} not found.")
    if len(supported_models.data) != 1:
        raise ValueError(f"""Multiple models found for "{model_input}".

Please specify a more specific model ID. To find a more specific model variant to use, try this:
- tg beta models public --search {model_input}""")

    public_model = supported_models.data[0]
    profiles = public_model.deployment_profiles or []
    if not profiles:
        raise ValueError(f"Model {model_input} has no deployment profiles.")

    profile = _select_deployment_profile(profiles, model_input=model_input, config_id=config_id)
    match = MODEL_PATH_RE.match(profile.model or "")
    if not match:
        raise ValueError(f"Invalid model path: {profile.model}")
    project_id, model_id, revision_id = match.group(1), match.group(2), match.group(3)

    selected_config = validate_requested_config(
        config_from_profile(profile),
        config_id,
        model=model_input,
    )
    model = Model.construct(id=model_id, projectId=project_id, name=public_model.name or model_id)
    return ResolvedModelAndConfig(model=model, config=selected_config, revision_id=revision_id)


def construct_model_path(model: Model, revision_id: str | None = None) -> str:
    path = f"projects/{model.project_id}/models/{model.id}"
    if revision_id:
        return f"{path}/revisions/{revision_id}"
    return path


async def resolve_endpoint(config: CLIConfigParameter, endpoint_id_or_name: str) -> Endpoint:
    if endpoint_id_or_name.startswith("ep_"):
        return await config.client.beta.endpoints.retrieve(id=endpoint_id_or_name)

    bare_name = endpoint_id_or_name.rsplit("/", 1)[-1]
    # Exact name filter avoids missing endpoints beyond the first list page.
    endpoints = await config.client.beta.endpoints.list(filter=f'name="{bare_name}"')

    me = await config.client.whoami()
    qualified_name = (
        endpoint_id_or_name
        if endpoint_id_or_name.startswith(f"{me.project_slug}/")
        else f"{me.project_slug}/{bare_name}"
    )

    for endpoint in endpoints.data or []:
        if endpoint.name == qualified_name or endpoint.name.rsplit("/", 1)[-1] == bare_name:
            return endpoint

    raise ValueError(f"Endpoint {endpoint_id_or_name} not found.")
