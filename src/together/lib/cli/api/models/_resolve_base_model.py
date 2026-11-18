from __future__ import annotations

from together.lib.cli.utils.config import CLIConfig
from together.types.supported_model import SupportedModel
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.types.supported_model_deployment_profile import SupportedModelDeploymentProfile
from together.lib.cli.api.endpoints._utils._resolve_model import MODEL_PATH_RE


def _resource_ids(resource: str | None) -> tuple[str | None, str | None]:
    match = MODEL_PATH_RE.match(resource or "")
    if not match:
        return None, None
    return match.group(1), match.group(2)


def _profile_model_id(profile: SupportedModelDeploymentProfile) -> str | None:
    return _resource_ids(profile.model)[1]


def _profile_display_name(profile: SupportedModelDeploymentProfile, model: SupportedModel) -> str:
    return profile.api_model_name or model.name or ""


def _print_base_model_candidates(
    candidates: list[tuple[str, str, str]],
    *,
    title: str,
) -> None:
    table = ListTable(title)
    table.add_primary_column("Model", ratio=3)
    table.add_column("Model ID")
    table.add_column("Quant")
    for name, model_id, quantization in candidates:
        table.add_row(name, model_id, quantization)
    console.print(table)


def _format_candidate_lines(candidates: list[tuple[str, str, str]]) -> str:
    return "\n".join(f"- {name} ({model_id})" for name, model_id, _quant in candidates)


async def resolve_base_model_id(config: CLIConfig, base_model: str) -> str:
    """Resolve a ``--base-model`` value to a model id for ``models.create``.

    Model ids (``ml_*``) are passed through. Any other string is treated as a
    deploy model name and resolved via ``list_supported(search=...)`` by exact
    match on deployment profile ``modelName``.
    """
    if base_model.startswith("ml_"):
        return base_model

    exact_ids, _projects, candidates = await show_loading_status(
        "Resolving base model...",
        _search_supported_models(config, base_model),
    )
    if len(exact_ids) == 1:
        return next(iter(exact_ids))

    if len(exact_ids) > 1:
        ambiguous = [(name, model_id, "") for model_id, name in exact_ids.items()]
        _print_base_model_candidates(ambiguous, title=f'Multiple models named "{base_model}"')
        raise ValueError(
            f'Multiple models found for "{base_model}".\n'
            "Use a model id instead:\n"
            f"{_format_candidate_lines(ambiguous)}\n\n"
            "Re-run with a model id, for example:\n"
            f"  tg models create <name> --base-model {next(iter(exact_ids))}"
        )

    if candidates:
        _print_base_model_candidates(candidates, title=f'No exact match for "{base_model}"')
        example_id = candidates[0][1]
        raise ValueError(
            f'No exact match for base model "{base_model}".\n'
            "Possible matches:\n"
            f"{_format_candidate_lines(candidates)}\n\n"
            "Re-run with an exact model name or model id, for example:\n"
            f"  tg models create <name> --base-model {example_id}"
        )

    raise ValueError(
        f'Base model "{base_model}" not found.\nSearch supported models with:\n  tg models public --search {base_model}'
    )


async def resolve_supported_model_location(config: CLIConfig, name: str) -> tuple[str, str]:
    """Resolve a public model string name to ``(project_id, model_id)``.

    Exact match is the deploy name printed by ``tg models public`` (deployment
    profile ``modelName``, or the catalog name when the model has no profiles).
    """
    exact_ids, projects, candidates = await _search_supported_models(config, name)
    if len(exact_ids) == 1:
        model_id = next(iter(exact_ids))
        project_id = projects.get(model_id)
        if not project_id:
            raise ValueError(
                f'Model "{name}" has no project path.\nUse the model id instead:\n  tg models get {model_id}'
            )
        return project_id, model_id

    if len(exact_ids) > 1:
        ambiguous = [(display_name, model_id, "") for model_id, display_name in exact_ids.items()]
        _print_base_model_candidates(ambiguous, title=f'Multiple models named "{name}"')
        raise ValueError(
            f'Multiple models found for "{name}".\n'
            "Use a model id instead:\n"
            f"{_format_candidate_lines(ambiguous)}\n\n"
            "Re-run with a model id, for example:\n"
            f"  tg models get {next(iter(exact_ids))}"
        )

    if candidates:
        _print_base_model_candidates(candidates, title=f'No exact match for "{name}"')
        example_id = candidates[0][1]
        raise ValueError(
            f'No exact match for model "{name}".\n'
            "Possible matches:\n"
            f"{_format_candidate_lines(candidates)}\n\n"
            "Re-run with an exact model name or model id, for example:\n"
            f"  tg models get {example_id}"
        )

    raise ValueError(f'Model "{name}" not found.\nSearch supported models with:\n  tg models public --search {name}')


async def _search_supported_models(
    config: CLIConfig, query: str
) -> tuple[dict[str, str], dict[str, str], list[tuple[str, str, str]]]:
    """Return exact ``model_id -> name``, ``model_id -> project_id``, and fuzzy candidates."""
    supported = await config.client.models.list_supported(search=query)
    exact_ids: dict[str, str] = {}
    projects: dict[str, str] = {}
    candidates: list[tuple[str, str, str]] = []

    for model in supported.data or []:
        profiles = model.deployment_profiles or []
        if not profiles and (model.name == query or model.id == query):
            project_id, path_model_id = _resource_ids(model.base_model)
            model_id = path_model_id or model.id
            if model_id:
                exact_ids[model_id] = model.name or model.id
                if project_id:
                    projects[model_id] = project_id
            continue

        for profile in profiles:
            profile_model_id = _profile_model_id(profile)
            if not profile_model_id:
                continue
            project_id, _path_model_id = _resource_ids(profile.model)
            display_name = _profile_display_name(profile, model)
            candidates.append((display_name, profile_model_id, profile.quantization or ""))
            if profile.api_model_name and profile.api_model_name == query:
                exact_ids[profile_model_id] = profile.api_model_name
                if project_id:
                    projects[profile_model_id] = project_id
            elif project_id:
                projects.setdefault(profile_model_id, project_id)

    return exact_ids, projects, candidates
