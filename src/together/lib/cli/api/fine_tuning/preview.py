from __future__ import annotations

from typing import Literal, Optional, Annotated

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.types.fine_tune_preview_row import FineTunePreviewRow

_TOKEN_PREVIEW_LIMIT = 32


def _format_token(token: str) -> str:
    return escape_rich_markup(token.encode("unicode_escape").decode("ascii"))


def _format_tokens(row: FineTunePreviewRow) -> str:
    tokens = row.tokens[:_TOKEN_PREVIEW_LIMIT]
    labels = row.labels[:_TOKEN_PREVIEW_LIMIT]
    formatted: list[str] = []
    for token, label in zip(tokens, labels):
        token_text = _format_token(token)
        formatted.append(f"[dim]{token_text}[/dim]" if label == -100 else token_text)

    if len(row.tokens) > _TOKEN_PREVIEW_LIMIT:
        formatted.append("[dim]...[/dim]")

    return " ".join(formatted)


def _format_spans(row: FineTunePreviewRow) -> str:
    if not row.trained_spans:
        return "-"
    return ", ".join(f"{start}-{end}" for start, end in row.trained_spans)


async def preview(
    training_file: Annotated[
        str,
        Parameter(
            alias="-t",
            help="Training file ID from the Files API to sample for preview",
        ),
    ],
    model: Annotated[
        str,
        Parameter(
            alias="-M",
            help="Name of the base model whose tokenizer and chat template will be used",
        ),
    ],
    top_k: Annotated[
        Optional[int],
        Parameter(help="Maximum number of rows from the start of the training file to tokenize"),
    ] = None,
    train_on_inputs: Annotated[
        Optional[bool],
        Parameter(help="Whether prompt or user-message tokens should contribute to training loss"),
    ] = None,
    training_method: Annotated[
        Literal["sft"],
        Parameter(help="Fine-tuning method to preview; only supervised fine-tuning is currently supported"),
    ] = "sft",
    *,
    config: CLIConfigParameter,
) -> None:
    """Preview how a fine-tuning training file will be tokenized."""
    response = await show_loading_status(
        "Loading fine-tuning preview...",
        config.client.fine_tuning.preview(
            model=model,
            training_file=training_file,
            top_k=top_k if top_k is not None else omit,
            train_on_inputs=train_on_inputs if train_on_inputs is not None else omit,
            training_method=training_method,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print(f"[dim][primary]Model:[/primary][/dim]\t\t[bold]{escape_rich_markup(response.model)}[/bold]")
    console.print(f"[dim][primary]Dataset format:[/primary][/dim]\t{response.dataset_format}")
    console.print(f"[dim][primary]Max sequence:[/primary][/dim]\t{response.max_seq_length}")
    console.print(f"[dim][primary]Train inputs:[/primary][/dim]\t{response.train_on_inputs}")

    table = ListTable("Preview Rows", empty_message="No preview rows returned")
    table.add_primary_column("Row")
    table.add_column("Tokens", justify="right")
    table.add_column("Trained", justify="right")
    table.add_column("Truncated")
    table.add_column("Trained Spans")
    table.add_column("Token Preview", ratio=4)

    for index, row in enumerate(response.rows, start=1):
        table.add_row(
            str(index),
            str(row.num_tokens),
            str(row.num_trained_tokens),
            "yes" if row.truncated else "no",
            _format_spans(row),
            _format_tokens(row),
        )

    console.print(table)
