from __future__ import annotations

import shlex

from rich.markup import escape as escape_rich_markup

from together.lib.utils.tools import format_datetime
from together.types.beta.rl.session import Session
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.types.beta.rl.checkpoint import Checkpoint
from together.types.beta.rl.model_resources import ModelResources
from together.types.beta.rl.inference_checkpoint import InferenceCheckpoint

_STATUS_COLORS = {
    "ready": "green",
    "running": "green",
    "pending": "yellow",
    "creating": "yellow",
    "stopping": "yellow",
    "stopped": "yellow",
    "expired": "red",
    "error": "red",
}


def readable_enum(value: str, prefix: str) -> str:
    if value.startswith(prefix):
        return value[len(prefix) :].replace("_", " ").lower()
    return value


def status_markup(status: str, prefix: str) -> str:
    label = readable_enum(status, prefix)
    color = _STATUS_COLORS.get(label, "white")
    return f"[{color}]{escape_rich_markup(label)}[/{color}]"


def cell(value: object) -> str:
    if value is None or value == "":
        return "-"
    return escape_rich_markup(str(value))


def print_next_page(command: str) -> None:
    console.print("\n[blue dim]To display the next page, run:[/blue dim]")
    console.print(f"  [dim]-[/dim] [white]{escape_rich_markup(command)}[/white]")


def page_cursor(meta: object) -> str | None:
    if meta is None:
        return None
    has_more = getattr(meta, "has_more", None)
    cursor = getattr(meta, "next_cursor", None)
    if has_more is False:
        return None
    if isinstance(cursor, str) and cursor:
        return cursor
    return None


def shell_arg(value: str) -> str:
    return shlex.quote(value)


def print_detail(title: str, rows: list[tuple[str, str]]) -> None:
    console.rule(f"[primary]{title}[/primary]", align="left")
    label_width = max(len(label) for label, _value in rows)
    for label, value in rows:
        padded = f"{label:<{label_width}}"
        console.print(f"[dim]{padded}[/dim]  {value}")


def _optimizer_name(resource: ModelResources) -> str:
    if resource.optimizer_config.adam is not None:
        return "adam"
    if resource.optimizer_config.muon is not None:
        return "muon"
    return "-"


def _compute_summary(resource: ModelResources) -> str:
    replicas = resource.compute_config.num_generator_replicas
    gpu = resource.compute_config.gpu_type or "default GPU"
    if replicas == 0:
        return "trainer only"
    return f"{replicas}× {gpu}"


def print_resources_table(resources: list[ModelResources]) -> None:
    table = ListTable("Model resources", empty_message="No model resources found.")
    table.add_primary_column("ID", ratio=2, overflow="fold")
    table.add_column("Base model", ratio=3, overflow="fold")
    table.add_column("Status", width=9, no_wrap=True, overflow="fold")
    table.add_column("Compute", ratio=2, overflow="fold")
    table.add_column("LoRA", width=4, no_wrap=True)
    for resource in resources:
        table.add_row(
            cell(resource.id),
            cell(resource.base_model),
            status_markup(resource.status, "MODEL_RESOURCES_STATUS_"),
            cell(_compute_summary(resource)),
            "yes" if resource.lora_enabled else "no",
        )
    console.print(table)


def print_model_resource(resource: ModelResources) -> None:
    rows: list[tuple[str, str]] = [
        ("ID", cell(resource.id)),
        ("Status", status_markup(resource.status, "MODEL_RESOURCES_STATUS_")),
        ("Base model", cell(resource.base_model)),
        ("LoRA", "yes" if resource.lora_enabled else "no"),
        ("Compute", cell(_compute_summary(resource))),
        ("Optimizer", cell(_optimizer_name(resource))),
        ("Created by", cell(resource.created_by)),
        ("Created", format_datetime(resource.created_at)),
        ("Updated", format_datetime(resource.updated_at)),
    ]
    if resource.base_weights_ref:
        rows.insert(3, ("Base weights", cell(resource.base_weights_ref)))
    if resource.error is not None:
        rows.append(("Error", f"[red]{escape_rich_markup(resource.error.message)}[/red]"))
    print_detail("Model resource", rows)


def print_sessions_table(sessions: list[Session]) -> None:
    table = ListTable("Training sessions", empty_message="No training sessions found.")
    table.add_primary_column("ID", ratio=2, overflow="fold")
    table.add_column("Name", ratio=2, overflow="fold")
    table.add_column("Status", width=9, no_wrap=True, overflow="fold")
    table.add_column("Base model", ratio=3, overflow="fold")
    table.add_column("Step", width=6, no_wrap=True)
    table.add_column("Resources", ratio=2, overflow="fold")
    for session in sessions:
        table.add_row(
            cell(session.id),
            cell(session.display_name),
            status_markup(session.status, "TRAINING_SESSION_STATUS_"),
            cell(session.base_model),
            cell(session.step),
            cell(session.resources_id),
        )
    console.print(table)


def print_session(session: Session) -> None:
    rows: list[tuple[str, str]] = [
        ("ID", cell(session.id)),
        ("Name", cell(session.display_name)),
        ("Status", status_markup(session.status, "TRAINING_SESSION_STATUS_")),
        ("Base model", cell(session.base_model)),
        ("Step", cell(session.step)),
        ("Resources", cell(session.resources_id)),
        ("Inference checkpoints", cell(len(session.inference_checkpoints))),
        ("Training checkpoints", cell(len(session.training_checkpoints))),
        ("Created by", cell(session.created_by)),
        ("Created", format_datetime(session.created_at)),
        ("Updated", format_datetime(session.updated_at)),
    ]
    if session.resume_from_checkpoint_id:
        rows.append(("Resumed from", cell(session.resume_from_checkpoint_id)))
    if session.error is not None:
        rows.append(("Error", f"[red]{escape_rich_markup(session.error.message)}[/red]"))
    print_detail("Training session", rows)


def _registered_model(checkpoint: InferenceCheckpoint) -> str:
    if checkpoint.registration is None:
        return "-"
    return checkpoint.registration.registered_model_name


def print_checkpoints_table(rows: list[tuple[str, InferenceCheckpoint]]) -> None:
    table = ListTable(
        "Inference checkpoints",
        empty_message="No inference checkpoints found.",
    )
    table.add_primary_column("ID", ratio=2, overflow="fold")
    table.add_column("Session", ratio=2, overflow="fold")
    table.add_column("Step", width=6, no_wrap=True)
    table.add_column("Model", ratio=3, overflow="fold")
    for session_id, checkpoint in rows:
        table.add_row(
            cell(checkpoint.id),
            cell(session_id),
            cell(checkpoint.step),
            cell(_registered_model(checkpoint)),
        )
    console.print(table)


def print_checkpoint(checkpoint: Checkpoint) -> None:
    kind = readable_enum(checkpoint.type, "CHECKPOINT_TYPE_")
    title = "Inference checkpoint" if checkpoint.type == "CHECKPOINT_TYPE_INFERENCE" else "Training checkpoint"
    rows = [
        ("ID", cell(checkpoint.id)),
        ("Type", cell(kind)),
        ("Base model", cell(checkpoint.base_model)),
        ("Session", cell(checkpoint.session_id)),
        ("Step", cell(checkpoint.step)),
        ("Created", format_datetime(checkpoint.created_at)),
    ]
    if checkpoint.lora_rank is not None:
        rows.append(("LoRA rank", cell(checkpoint.lora_rank)))
    print_detail(title, rows)


def checkpoint_kind(checkpoint: Checkpoint) -> str:
    if checkpoint.type == "CHECKPOINT_TYPE_INFERENCE":
        return "inference_checkpoint"
    return "training_checkpoint"
