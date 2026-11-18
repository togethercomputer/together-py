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


def _catalog_target(model: SupportedModel) -> tuple[str | None, str | None]:
    project_id, path_model_id = _resource_ids(model.base_model)
    return project_id, path_model_id or model.base_model_id or model.id or None


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

    exact_ids, _catalog_ids, _projects, candidates = await show_loading_status(
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

    Deploy names (profile ``modelName``) win. Otherwise the catalog ``name`` — the
    string `tg models public` shows for serverless models that do not pin a
    separate quant profile — resolves through ``baseModel``.
    """
    exact_ids, catalog_ids, projects, candidates = await _search_supported_models(config, name)
    chosen = exact_ids or catalog_ids
    if len(chosen) == 1:
        return _located_model(name, next(iter(chosen)), projects)

    if len(chosen) > 1:
        ambiguous = [(display_name, model_id, "") for model_id, display_name in chosen.items()]
        example = _rerun_target(next(iter(chosen)), projects)
        _print_base_model_candidates(ambiguous, title=f'Multiple models named "{name}"')
        raise ValueError(
            f'Multiple models found for "{name}".\n'
            "Use a model path instead:\n"
            f"{_format_candidate_lines(ambiguous)}\n\n"
            "Re-run with a model path, for example:\n"
            f"  tg models get {example}"
        )

    if candidates:
        _print_base_model_candidates(candidates, title=f'No exact match for "{name}"')
        example = _rerun_target(candidates[0][1], projects)
        raise ValueError(
            f'No exact match for model "{name}".\n'
            "Possible matches:\n"
            f"{_format_candidate_lines(candidates)}\n\n"
            "Re-run with an exact model name or model path, for example:\n"
            f"  tg models get {example}"
        )

    raise ValueError(f'Model "{name}" not found.\nSearch supported models with:\n  tg models public --search {name}')


async def resolve_public_model_id(config: CLIConfig, model_id: str) -> tuple[str, str] | None:
    """Locate a public model id that is not in the caller's project or org."""
    exact_ids, catalog_ids, projects, _candidates = await _search_supported_models(config, model_id)
    if model_id not in exact_ids and model_id not in catalog_ids:
        return None
    project_id = projects.get(model_id)
    if not project_id:
        return None
    return project_id, model_id


def _located_model(name: str, model_id: str, projects: dict[str, str]) -> tuple[str, str]:
    project_id = projects.get(model_id)
    if not project_id:
        raise ValueError(
            f'Model "{name}" is in the public catalog but has no retrievable model path.\n'
            f"Search supported models with:\n  tg models public --search {name}"
        )
    return project_id, model_id


def _rerun_target(model_id: str, projects: dict[str, str]) -> str:
    project_id = projects.get(model_id)
    if project_id:
        return f"projects/{project_id}/models/{model_id}"
    return model_id


async def _search_supported_models(
    config: CLIConfig, query: str
) -> tuple[dict[str, str], dict[str, str], dict[str, str], list[tuple[str, str, str]]]:
    """Return deploy-name hits, catalog-name hits, ``model_id -> project_id``, and candidates.

    Deploy-name hits are profile ``modelName`` matches. Those stay exact for
    ``models create --base-model``. Catalog ``name`` / ``id`` hits are separate so
    ``models get`` can open the public model even when its profiles use another
    deploy name, or omit ``model`` because they do not pin weights.
    """
    supported = await config.client.models.list_supported(search=query)
    exact_ids: dict[str, str] = {}
    catalog_ids: dict[str, str] = {}
    projects: dict[str, str] = {}
    candidates: list[tuple[str, str, str]] = []

    for model in supported.data or []:
        _record_catalog_hit(model, query, catalog_ids, projects)
        profiles = model.deployment_profiles or []
        if not profiles:
            project_id, model_id = _catalog_target(model)
            if model_id and (model.name == query or model.id == query or model.base_model_id == query):
                exact_ids[model_id] = model.name or model.id
                if project_id:
                    projects[model_id] = project_id
            elif model_id and model.name:
                candidates.append((model.name, model_id, ""))
                if project_id:
                    projects.setdefault(model_id, project_id)
            continue

        catalog_project, catalog_model_id = _catalog_target(model)
        for profile in profiles:
            profile_model_id = _profile_model_id(profile)
            project_id, _path_model_id = _resource_ids(profile.model)
            display_name = _profile_display_name(profile, model)
            if profile_model_id:
                candidates.append((display_name, profile_model_id, profile.quantization or ""))
                if project_id:
                    projects.setdefault(profile_model_id, project_id)
            name_hit = bool(profile.api_model_name) and profile.api_model_name == query
            id_hit = bool(profile_model_id) and profile_model_id == query
            if not name_hit and not id_hit:
                continue
            matched_id = profile_model_id or catalog_model_id
            if not matched_id:
                continue
            exact_ids[matched_id] = profile.api_model_name or display_name or matched_id
            matched_project = project_id or catalog_project
            if matched_project:
                projects[matched_id] = matched_project

    return exact_ids, catalog_ids, projects, candidates


def _record_catalog_hit(
    model: SupportedModel,
    query: str,
    catalog_ids: dict[str, str],
    projects: dict[str, str],
) -> None:
    if query not in {model.name, model.id, model.base_model_id}:
        return
    project_id, model_id = _catalog_target(model)
    if not model_id:
        return
    catalog_ids[model_id] = model.name or model_id
    if project_id:
        projects[model_id] = project_id
