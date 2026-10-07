from __future__ import annotations

import asyncio
from typing import Any
from dataclasses import dataclass
from typing_extensions import Annotated

from cyclopts import Parameter

from together import APIError, BaseModel, NotFoundError
from together._utils._json import openapi_dumps
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.utils.config import CLIConfigParameter
from together.types.beta.rl.session import Session
from together.lib.cli.utils._console import console
from together.types.beta.rl.checkpoint import Checkpoint
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.training._display import (
    cell,
    print_session,
    checkpoint_kind,
    print_checkpoint,
    print_model_resource,
)
from together.types.beta.rl.model_resources import ModelResources


@dataclass
class _Lookup:
    value: BaseModel | None = None
    error: APIError | None = None


async def retrieve(
    id: Annotated[
        str,
        Parameter(help="Model resource ID, training session ID, or checkpoint ID"),
    ],
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve a model resource, training session, or checkpoint by ID."""
    resource, session, checkpoint = await show_loading_status(
        "Loading training object...",
        asyncio.gather(
            _lookup(config.client.beta.rl.model_resources.retrieve(id)),
            _lookup(config.client.beta.rl.sessions.retrieve(id)),
            _lookup(config.client.beta.rl.checkpoints.retrieve(id)),
        ),
    )
    found = _first_hit(resource, session, checkpoint)
    if found is None:
        _missing(id, config=config, lookups=(resource, session, checkpoint))
        return

    kind, value = found
    if config.json:
        console.print_json(openapi_dumps({"kind": kind, "data": value}).decode("utf-8"))
        return

    if isinstance(value, ModelResources):
        print_model_resource(value)
    elif isinstance(value, Session):
        print_session(value)
    elif isinstance(value, Checkpoint):
        print_checkpoint(value)


async def _lookup(request: Any) -> _Lookup:
    try:
        return _Lookup(value=await request)
    except NotFoundError:
        return _Lookup()
    except APIError as exc:
        return _Lookup(error=exc)


def _first_hit(*lookups: _Lookup) -> tuple[str, BaseModel] | None:
    for lookup in lookups:
        value = lookup.value
        if isinstance(value, ModelResources):
            return "model_resource", value
        if isinstance(value, Session):
            return "training_session", value
        if isinstance(value, Checkpoint):
            return checkpoint_kind(value), value
    return None


def _missing(id: str, *, config: CLIConfigParameter, lookups: tuple[_Lookup, ...]) -> None:
    for lookup in lookups:
        if lookup.error is not None:
            raise lookup.error

    message = f"No model resource, training session, or checkpoint found for {id}."
    if config.json:
        console.print_json(openapi_dumps({"error": message}).decode("utf-8"))
    else:
        console.print(f"[red]×[/red] {cell(message)}")
    raise CliDiagnosticExit(message)
