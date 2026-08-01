from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel
from rich.markup import escape as escape_rich_markup

from together import APIError
from together._utils._json import openapi_dumps
from together.lib.cli.utils._console import console


class _ErrorContents(BaseModel):
    message: str
    type: str
    param: Optional[str] = None
    code: Optional[str] = None


class _ErrorEnvelope(BaseModel):
    error: _ErrorContents


class _RPCError(BaseModel):
    message: str
    code: int
    details: Optional[list[Any]] = None


def _parse_error_envelope(body: object) -> _ErrorEnvelope:
    # Pydantic v1: parse_obj; v2: model_validate
    if hasattr(_ErrorEnvelope, "model_validate"):
        return _ErrorEnvelope.model_validate(body)
    return _ErrorEnvelope.parse_obj(body)  # type: ignore


def _parse_rpc_error_envelope(body: object) -> _RPCError:
    # Pydantic v1: parse_obj; v2: model_validate
    if hasattr(_RPCError, "model_validate"):
        return _RPCError.model_validate(body)
    return _RPCError.parse_obj(body)  # type: ignore


def parse_api_error(e: APIError) -> tuple[str, dict[str, Any]]:
    # If the error is from the API and uses the standard error envelope, print the message
    message = ""
    dump = {}
    try:
        standard_envelope = _parse_error_envelope(e.body)
        dump = standard_envelope.model_dump()
        message = standard_envelope.error.message
    # Some APIs are returning the RPC error format, so we need to parse that instead.
    except Exception:
        rpc_envelope = _parse_rpc_error_envelope(e.body)
        dump = rpc_envelope.model_dump()
        if isinstance(rpc_envelope.details, list):
            for detail_dict in rpc_envelope.details:
                message = detail_dict["detail"]
        else:
            message = rpc_envelope.message

    return message, dump


def try_handle_server_error_message(e: APIError, json: bool) -> None:
    message, dump = parse_api_error(e)

    if json:
        console.print_json(openapi_dumps(dump).decode("utf-8"))
        return
    console.print(f"[red]×[/red] [bold]Error[/bold]")
    console.print(f"  [white]{escape_rich_markup(message)}[/white]")
