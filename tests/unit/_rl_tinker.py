"""Shared doubles and testdata for the Tinker-wrapper unit tests."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("tinker")

from tinker import types

from together.lib.beta.rl import tinker as tinker_compat
from together.lib.beta.rl.tinker import _service
from together.lib.beta.rl.clients.session import SessionClient

_OPERATION = SimpleNamespace(id="op-1", status="TRAINING_OPERATION_STATUS_PENDING", output=None, error=None)
_WEIGHTS_SYNC_OUTPUT = {"weights_version": 1}


def _noop() -> None:
    pass


def _ignore(_value: Any) -> None:
    pass


def _session_mock() -> Any:
    """A stand-in for SessionClient that refuses attributes the real class lacks.

    ``spec`` is the point: a bare MagicMock answers to anything, so production code
    reading an attribute no client defines still passes here.
    """
    session = MagicMock(spec=SessionClient)
    session.session_id = "sess"
    return session


def _model_resources_mock(model_resources_id: str) -> Any:
    resources = MagicMock(spec=_service.ModelResourcesClient)
    resources.model_resources_id = model_resources_id
    return resources


def _session_with_operations(**operations: Any) -> SessionClient:
    client = SimpleNamespace(
        beta=SimpleNamespace(rl=SimpleNamespace(operations=SimpleNamespace(**operations))),
        close=AsyncMock(),
    )
    return SessionClient("sess", _client=cast(Any, client))


def _training_client(session: SessionClient) -> tinker_compat.TrainingClient:
    return tinker_compat.TrainingClient(session)


def _close(session: SessionClient) -> None:
    session.detach()


def _rl_loop_datum() -> types.Datum:
    """A Datum built exactly the way tinker's rl_loop.py builds one.

    Prompt [1, 2, 3, 4], sampled response [10, 11, 12]: model_input drops the final
    sampled token and the arrays are already shifted to align with next-token targets.
    Float values are exactly representable in float32 so equality stays exact.
    """
    prompt = types.ModelInput.from_ints([1, 2, 3, 4])
    sampled = [10, 11, 12]
    model_input = prompt.append(types.EncodedTextChunk(tokens=sampled[:-1]))
    ob_len = prompt.length - 1
    return types.Datum(
        model_input=model_input,
        loss_fn_inputs={
            "target_tokens": types.TensorData([0] * ob_len + sampled, dtype="int64"),
            "logprobs": types.TensorData([0.0] * ob_len + [-0.5, -0.25, -0.125], dtype="float32"),
            "advantages": types.TensorData([0.0] * ob_len + [0.5] * len(sampled), dtype="float32"),
        },
    )


def _tensors(*keys: str) -> dict[str, types.TensorData]:
    """One placeholder tensor per key, typed as the wire shape declares it."""
    return {
        key: types.TensorData([1, 2], dtype="int64")
        if key == "target_tokens"
        else types.TensorData([1.0, 0.5], dtype="float32")
        for key in keys
    }


def _advantage_datum() -> types.Datum:
    return types.Datum(
        model_input=types.ModelInput.from_ints([1, 2, 3]),
        loss_fn_inputs={
            "target_tokens": types.TensorData([0, 4, 5], dtype="int64"),
            "logprobs": types.TensorData([0.0, -0.5, -0.25], dtype="float32"),
            "advantages": types.TensorData([0.0, 0.5, 0.5], dtype="float32"),
        },
    )
