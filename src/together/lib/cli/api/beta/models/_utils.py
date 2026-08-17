from __future__ import annotations

from typing import Literal

from rich.rule import Rule
from rich.table import Table
from rich.padding import Padding

from together.lib.utils import convert_bytes
from together.lib.utils.tools import format_datetime
from together.types.beta.model import Model, Weights
from together.types.beta.models import Config
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.types.beta.model_list_files_response import ModelListFilesResponse
from together.lib.cli.api.beta.endpoints._utils._resolve_model import resolve_model

_DETAIL_LABEL_WIDTH = 17


def _short_name(fully_qualified_name: str) -> str:
    return fully_qualified_name.rsplit("/", 1)[-1]


def _print_detail_line(label: str, value: str) -> None:
    console.print(f"[dim]│{label:>{_DETAIL_LABEL_WIDTH}}[/dim] {value}")


def _print_detail_header(title: str, name: str) -> None:
    console.rule(
        f"[dim]╭─[/dim] {title} for [bold][primary]{name}[/primary][/bold]",
        style="dim",
        align="left",
    )


def _print_detail_footer() -> None:
    rule = Rule(style="dim")
    console.print("╰" + rule.characters[0] * (console.width - 1), style="dim")


def _readable_visibility(
    visibility: Literal["VISIBILITY_PUBLIC", "VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"] | None,
) -> str:
    if visibility is None:
        return "Unknown"
    return {
        "VISIBILITY_PUBLIC": "Public",
        "VISIBILITY_PRIVATE": "Private",
        "VISIBILITY_INTERNAL": "Internal",
    }[visibility]


def _format_enum_suffix(value: str, prefix: str) -> str:
    if value.startswith(prefix):
        return value[len(prefix) :].replace("_", " ").title()
    return value


def _format_count(count: str | None) -> str:
    if not count:
        return ""
    try:
        return f"{int(count):,}"
    except ValueError:
        return count


def _print_model_weights(weights: Weights) -> None:
    weights_table = ListTable(show_lines=False)
    weights_table.add_primary_column("Property", ratio=1)
    weights_table.add_column("Value", ratio=2)
    if weights.type:
        weights_table.add_row("Type", _format_enum_suffix(weights.type, "WEIGHTS_TYPE_"))
    if weights.architecture:
        weights_table.add_row("Architecture", weights.architecture)
    if weights.context_length:
        weights_table.add_row("Context length", weights.context_length)
    if weights.draft_speculator_type:
        weights_table.add_row(
            "Draft speculator",
            _format_enum_suffix(weights.draft_speculator_type, "DRAFT_SPECULATOR_TYPE_"),
        )
    if weights.speculator_mechanism:
        weights_table.add_row(
            "Speculator",
            _format_enum_suffix(weights.speculator_mechanism, "SPECULATOR_MECHANISM_"),
        )
    if weights.parameters:
        for entry in weights.parameters.by_dtype or []:
            if entry.dtype and entry.count:
                weights_table.add_row(f"Parameters - {entry.dtype}", _format_count(entry.count))
    if weights_table.table.row_count:
        console.print("\nWeights:")
        console.print(Padding(weights_table, (0, 0)))


async def print_model_detail(
    model: Model,
    *,
    config: CLIConfig | None = None,
    files: ModelListFilesResponse | None = None,
) -> None:
    _print_detail_header("Model Details", _short_name(model.name))
    _print_detail_line("Endpoint string", model.name)
    if model.id:
        _print_detail_line("ID", model.id)
    if model.base_model_id:
        base_model = model.base_model_id
        try:
            base_model = (
                (await resolve_model(config, model.base_model_id)).name if config is not None else model.base_model_id
            )
        except Exception:
            pass
        _print_detail_line("Base model", base_model)
    if model.description:
        _print_detail_line("Description", model.description)
    if model.visibility:
        _print_detail_line("Visibility", _readable_visibility(model.visibility))
    if files is not None:
        if files.revision_id:
            _print_detail_line("Current revision", files.revision_id)
        if files.revision_created_at:
            _print_detail_line("Revision created", format_datetime(files.revision_created_at))
        if files.total_size_bytes:
            size = convert_bytes(float(str(files.total_size_bytes)))
            if size is not None:
                _print_detail_line("Files size", size)
    _print_detail_footer()

    if model.weights:
        _print_model_weights(model.weights)


def print_models_table(models: list[Model], *, empty_message: str) -> None:
    table = ListTable("Models", empty_message=empty_message)
    table.add_primary_column("ID")
    table.add_column("Name", ratio=2)
    for model in models:
        table.add_row(
            model.id or "",
            model.name,
        )
    console.print(table)


def print_configs_table(configs: list[Config], *, empty_message: str) -> None:
    table = ListTable("Model Configs", empty_message=empty_message)
    table.add_primary_column("Config ID")
    table.add_column("Selectors")
    for config in configs:
        selector_table = Table(show_lines=False, show_header=False, box=None, expand=True)
        selector_table.add_column("Key", style="dim bold", justify="right", ratio=1)
        selector_table.add_column("Value", style="white", justify="left", ratio=2)
        for selector in config.selectors or []:
            selector_table.add_row(selector.key or "", selector.value or "")
        table.add_row(
            config.id or "",
            selector_table,
        )
    console.print(table)
