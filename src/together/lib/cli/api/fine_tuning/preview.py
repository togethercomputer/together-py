from __future__ import annotations

from typing import Optional, Annotated
from typing_extensions import Literal

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status

_TOKEN_PREVIEW_LIMIT = 24


def _format_spans(spans: list[list[int]]) -> str:
    if len(spans) == 0:
        return "-"

    formatted = []
    for span in spans:
        if len(span) == 2:
            formatted.append(f"{span[0]}:{span[1]}")
    return ", ".join(formatted) if formatted else "-"


def _format_tokens(tokens: list[str], labels: list[int]) -> str:
    if len(tokens) == 0:
        return "-"

    rendered_tokens: list[str] = []
    for index, token in enumerate(tokens[:_TOKEN_PREVIEW_LIMIT]):
        text = escape_rich_markup(repr(token))
        if index < len(labels) and labels[index] != -100:
            rendered_tokens.append(f"[primary]{text}[/primary]")
        else:
            rendered_tokens.append(f"[dim]{text}[/dim]")

    remaining = len(tokens) - _TOKEN_PREVIEW_LIMIT
    if remaining > 0:
        rendered_tokens.append(f"[dim]... +{remaining} tokens[/dim]")

    return " ".join(rendered_tokens)


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
    *,
    config: CLIConfigParameter,
    top_k: Annotated[
        Optional[int],
        Parameter(help="Maximum number of rows from the start of the training file to tokenize"),
    ] = None,
    train_on_inputs: Annotated[
        Optional[bool],
        Parameter(
            negative=(),
            help="Whether prompt or user-message tokens should contribute to training loss",
        ),
    ] = None,
    training_method: Annotated[
        Literal["sft"],
        Parameter(
            alias="-m",
            help="Fine-tuning method to preview. Only supervised fine-tuning is currently supported.",
        ),
    ] = "sft",
) -> None:
    """Preview how a fine-tuning training file will be tokenized."""
    response = await show_loading_status(
        "Generating fine-tuning preview...",
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

    console.print(f"[muted]Model:[/muted] {response.model}")
    console.print(f"[muted]Dataset format:[/muted] {response.dataset_format}")
    console.print(f"[muted]Max sequence length:[/muted] {response.max_seq_length}")
    console.print(f"[muted]Train on inputs:[/muted] {response.train_on_inputs}")

    table = ListTable(title="Preview rows", empty_message="No preview rows returned")
    table.add_primary_column("Row", width=5)
    table.add_column("Tokens", ratio=4)
    table.add_column("Trained Spans")
    table.add_column("Trained / Total", justify="right")
    table.add_column("Truncated", justify="center")

    for index, row in enumerate(response.rows, start=1):
        table.add_row(
            str(index),
            _format_tokens(row.tokens, row.labels),
            _format_spans(row.trained_spans),
            f"{row.num_trained_tokens} / {row.num_tokens}",
            "yes" if row.truncated else "no",
        )

    console.print(table)
