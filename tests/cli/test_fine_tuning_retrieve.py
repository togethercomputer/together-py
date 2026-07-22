from __future__ import annotations

from together.types import FinetuneResponse
from together.lib.cli.api.fine_tuning.retrieve import _output_model_line


def _resp(*, model_object_name: str | None, model_object_id: str | None) -> FinetuneResponse:
    # model_construct keys off aliases: model_object_id -> api_model_object_id.
    return FinetuneResponse.model_construct(model_object_name=model_object_name, model_object_id=model_object_id)


def test_output_model_line_links_by_object_id() -> None:
    line = _output_model_line(_resp(model_object_name="acme-corp/m", model_object_id="ml_1"))
    assert line == "[link=https://api.together.ai/models/ml_1]acme-corp/m[/link]"


def test_output_model_line_bare_name_without_object_id() -> None:
    line = _output_model_line(_resp(model_object_name="acme-corp/m", model_object_id=None))
    assert line == "acme-corp/m"


def test_output_model_line_none_when_unresolved() -> None:
    assert _output_model_line(_resp(model_object_name=None, model_object_id="ml_1")) is None
