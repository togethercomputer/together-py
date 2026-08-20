from __future__ import annotations

from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.types.beta.supported_model import SupportedModel
from together.types.beta.supported_model_deployment_profile import SupportedModelDeploymentProfile
from together.lib.cli.api.beta.endpoints._utils._resolve_model import MODEL_PATH_RE


def _profile_model_id(profile: SupportedModelDeploymentProfile) -> str | None:
    match = MODEL_PATH_RE.match(profile.model or "")
    if match:
        return match.group(2)
    return None


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

    supported = await show_loading_status(
        "Resolving base model...",
        config.client.beta.models.list_supported(search=base_model),
    )

    candidates: list[tuple[str, str, str]] = []
    exact_ids: dict[str, str] = {}

    for model in supported.data or []:
        for profile in model.deployment_profiles or []:
            model_id = _profile_model_id(profile)
            if not model_id:
                continue
            display_name = _profile_display_name(profile, model)
            candidates.append((display_name, model_id, profile.quantization or ""))
            if profile.api_model_name and profile.api_model_name == base_model:
                exact_ids[model_id] = profile.api_model_name

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
            f"  tg beta models create <name> --base-model {next(iter(exact_ids))}"
        )

    if candidates:
        _print_base_model_candidates(candidates, title=f'No exact match for "{base_model}"')
        example_id = candidates[0][1]
        raise ValueError(
            f'No exact match for base model "{base_model}".\n'
            "Possible matches:\n"
            f"{_format_candidate_lines(candidates)}\n\n"
            "Re-run with an exact model name or model id, for example:\n"
            f"  tg beta models create <name> --base-model {example_id}"
        )

    raise ValueError(
        f'Base model "{base_model}" not found.\n'
        "Search supported models with:\n"
        f"  tg beta models public --search {base_model}"
    )
