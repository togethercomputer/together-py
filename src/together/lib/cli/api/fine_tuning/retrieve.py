from __future__ import annotations

from typing import Any, cast
from datetime import datetime

from rich.markup import escape as escape_rich_markup

from together.lib.utils import convert_bytes, finetune_price_to_dollars
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.api._utils import generate_progress_bar
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.types.fine_tuning import COMPLETED_STATUSES
from together.lib.cli.utils._console import console
from together.types.finetune_response import FinetuneResponse
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.fine_tuning.list import status_colors

_NEST_INDENT = 4


def _plain(v: Any) -> str | None:
    """Plain escaped text for a scalar, or None if missing."""
    if v is None:
        return None
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        s = f"{v:g}" if not v.is_integer() else str(int(v))
        return escape_rich_markup(s)
    if isinstance(v, int):
        return escape_rich_markup(f"{v:,}")
    return escape_rich_markup(str(v))


def _plain_dt(v: datetime | None) -> str | None:
    if v is None:
        return None
    try:
        return escape_rich_markup(format_datetime(v))
    except Exception:
        return escape_rich_markup(str(v))


def _plain_price(nano: int | None) -> str | None:
    if nano is None:
        return None
    dollars = finetune_price_to_dollars(float(nano))
    return escape_rich_markup(f"${dollars:,.2f}")


def _plain_bytes(n: int | None) -> str | None:
    if n is None:
        return None
    s = convert_bytes(float(n))
    return escape_rich_markup(s or str(n))


def _print_kv(label: str, text: str | None) -> None:
    lab = escape_rich_markup(label)
    if text is not None:
        console.print(f"[dim]{lab}:[/dim] [white]{text}[/white]")


def _as_jsonlike(obj: Any) -> Any:
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    return obj


def _walk_jsonlike(data: Any, indent: int) -> None:
    """Print JSON-like dict/list trees as indented key/value lines (same style as top-level)."""
    pad = " " * indent
    if data is None:
        console.print(f"{pad}[dim]—[/dim]")
        return
    if isinstance(data, dict):
        d = cast(dict[str, Any], data)
        if not d:
            console.print(f"{pad}[dim](empty)[/dim]")
            return
        for key in sorted(d, key=str):
            v = d[key]
            kdisp = escape_rich_markup(str(key))
            if isinstance(v, dict):
                console.print(f"{pad}[dim]{kdisp}:[/dim]")
                _walk_jsonlike(v, indent + _NEST_INDENT)
            elif isinstance(v, list):
                console.print(f"{pad}[dim]{kdisp}:[/dim]")
                _walk_jsonlike(v, indent + _NEST_INDENT)
            else:
                sv = _plain(v)
                if sv is not None:
                    console.print(f"{pad}[dim]{kdisp}:[/dim] [white]{sv}[/white]")
        return
    if isinstance(data, list):
        lst = cast(list[Any], data)
        if not lst:
            console.print(f"{pad}[dim]—[/dim]")
            return
        for i, item in enumerate(lst):
            if isinstance(item, dict):
                console.print(f"{pad}[dim][{i}][/dim]")
                _walk_jsonlike(item, indent + _NEST_INDENT)
            elif isinstance(item, list):
                console.print(f"{pad}[dim][{i}][/dim]")
                _walk_jsonlike(item, indent + _NEST_INDENT)
            else:
                sv = _plain(item)
                if sv is None:
                    console.print(f"{pad}[dim][{i}]:[/dim] [dim]—[/dim]")
                else:
                    console.print(f"{pad}[dim][{i}]:[/dim] [white]{sv}[/white]")
        return
    sv = _plain(data)
    console.print(f"{pad}[white]{sv}[/white]" if sv else f"{pad}[dim]—[/dim]")


def _print_nested_section(title: str, obj: Any, indent: int = _NEST_INDENT) -> None:
    console.print(f"[dim]{escape_rich_markup(title)}:[/dim]")
    if obj is None:
        console.print(" " * indent + "[dim]—[/dim]")
        return
    _walk_jsonlike(_as_jsonlike(obj), indent)


def _print_job_details(r: FinetuneResponse, fine_tune_id: str) -> None:
    sc = status_colors.get(r.status, "white")
    _print_kv("Job ID", _plain(r.id))
    console.print(f"[dim]{escape_rich_markup('Status')}:[/dim] [bold {sc}]{escape_rich_markup(r.status)}[/bold {sc}]")
    _print_kv("Model Name", _plain(r.x_model_output_name))
    _print_kv("Total price", _plain_price(r.total_price))
    _print_kv("Created", _plain_dt(r.created_at))
    _print_kv("Started", _plain_dt(r.started_at))
    _print_kv("Updated", _plain_dt(r.updated_at))

    console.print(f"\n[dim]Training Data:[/dim]")
    _print_kv("  Base model", _plain(r.model))
    _print_kv("  Training file", _plain(r.training_file))
    _print_kv("  Validation file", _plain(r.validation_file))
    _print_kv("  Training lines", _plain(r.trainingfile_numlines))
    _print_kv("  Training file size", _plain_bytes(r.trainingfile_size))
    _print_kv("  From checkpoint", _plain(r.from_checkpoint))
    _print_kv("  From HF model", _plain(r.from_hf_model))
    _print_kv("  HF model revision", _plain(r.hf_model_revision))
    _print_kv("  Batch size", _plain(r.batch_size))
    _print_kv("  Learning rate", _plain(r.learning_rate))
    _print_kv("  Warmup ratio", _plain(r.warmup_ratio))
    _print_kv("  Weight decay", _plain(r.weight_decay))
    _print_kv("  Max grad norm", _plain(r.max_grad_norm))
    _print_kv("  Train on inputs", _plain(r.train_on_inputs))
    _print_kv("  Epochs (configured)", _plain(r.n_epochs))
    _print_kv("  Epochs completed", _plain(r.epochs_completed))
    _print_kv("  Checkpoints to save", _plain(r.n_checkpoints))
    _print_kv("  Eval loops", _plain(r.n_evals))
    _print_kv("  Eval steps", _plain(r.eval_steps))
    _print_kv("  Token count", _plain(r.token_count))
    _print_kv("  Parameter count", _plain(r.param_count))
    _print_kv("  Queue depth", _plain(r.queue_depth))
    _print_nested_section("  LR scheduler", r.lr_scheduler)
    _print_nested_section("  Training type", r.training_type)
    _print_nested_section("  Training method", r.training_method)
    _print_nested_section("  Multimodal params", r.multimodal_params)

    if r.events:
        console.print("\n[dim]FT Events:[/dim]")
        console.print(f"  [dim]Total events:[/dim] {len(r.events)}")
        console.print(f"  [dim]To see event log data run[/dim] tg fine-tuning list-events {fine_tune_id}")


async def retrieve(
    fine_tune_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve fine-tuning job details."""
    response = await show_loading_status(
        "Retrieving fine-tuning job...", config.client.fine_tuning.retrieve(fine_tune_id)
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    if response.status in COMPLETED_STATUSES:
        _print_job_details(response, fine_tune_id)
        return

    progress_text = generate_progress_bar(response, datetime.now().astimezone(), use_rich=True)

    console.print(f"[bold primary]Fine-tuning job[/bold primary] [dim]{escape_rich_markup(response.id)}[/dim]")
    console.print(progress_text)
