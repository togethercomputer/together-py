from typing import Optional

from pydantic import BaseModel

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


def _parse_error_envelope(body: object) -> _ErrorEnvelope:
    # Pydantic v1: parse_obj; v2: model_validate
    if hasattr(_ErrorEnvelope, "model_validate"):
        return _ErrorEnvelope.model_validate(body)
    return _ErrorEnvelope.parse_obj(body) # type: ignore


def try_handle_server_error_message(e: APIError, json: bool) -> None:
    # If the error is from the API and uses the standard error envelope, print the message
    envelope = _parse_error_envelope(e.body)
    if json:
        console.print_json(openapi_dumps(envelope.model_dump()).decode("utf-8"))
        return
    console.print(f"[red]×[/red] [bold]Error[/bold]")
    console.print(f"  [white]{envelope.error.message}[/white]")
