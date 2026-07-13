from __future__ import annotations

import json
import logging
from typing import Any, Union, TypeVar, cast
from collections.abc import Mapping
from typing_extensions import TypeAlias

import httpx

from ...._types import Omit
from ...._utils import maybe_transform
from ...._client import AsyncTogether
from ...._compat import model_parse
from ...._models import BaseModel

logger = logging.getLogger("together")

_LARGE_PAYLOAD_THRESHOLD = 0.5 * 1024 * 1024  # 0.5 MiB
_MAX_PAYLOAD_SIZE = 5 * 1024**3 - 5 * 1024**2  # 4.995 GiB, R2's single-PUT upload limit
_VALIDATION_MAX_SEQ_LEN = 8
_MAX_RETRIES = 5

JsonValue: TypeAlias = Union[str, int, float, bool, None, Mapping[str, Any], list[Any]]
ResultModel = TypeVar("ResultModel", bound=BaseModel)


def _truncate_sequences(data: JsonValue, max_len: int = _VALIDATION_MAX_SEQ_LEN) -> JsonValue:
    if isinstance(data, dict):
        return {k: _truncate_sequences(v, max_len) for k, v in data.items()}
    if isinstance(data, list):
        if data and isinstance(data[0], (int, float)):
            return data[:max_len]
        return [_truncate_sequences(item, max_len) for item in data]
    return data


def _build_validation_body(body: Mapping[str, Any]) -> dict[str, Any]:
    validation_body = dict(body)
    for field, value in validation_body.items():
        if isinstance(value, list):
            validation_body[field] = _truncate_sequences(cast(JsonValue, value))
    return validation_body


async def prepare_operation_body(
    client: AsyncTogether,
    *,
    session_id: str,
    body: dict[str, Any],
    expected_type: object,
) -> tuple[dict[str, Any], str | None]:
    """Prepare an operation request body, uploading large payloads to R2.

    Args:
        client: Async Together client used to request upload URLs.
        session_id: Training session ID that owns the operation.
        body: Operation request body to serialize and potentially upload.
        expected_type: Stainless request type used to transform the body before
            measuring payload size.

    Returns:
        A tuple containing the inline validation body and an optional payload ID.
        When the payload is small, the original body is returned with no payload
        ID. When it is large, the full serialized body is uploaded and the
        returned body contains truncated sequence fields for inline validation.
    """
    serialized = maybe_transform(body, expected_type=expected_type)
    payload = json.dumps(serialized, separators=(",", ":")).encode()
    if len(payload) <= _LARGE_PAYLOAD_THRESHOLD:
        return body, None

    if len(payload) > _MAX_PAYLOAD_SIZE:
        raise ValueError(
            f"Operation payload is {len(payload) / 1024**3:.2f} GiB, which exceeds the "
            f"{_MAX_PAYLOAD_SIZE / 1024**3:.2f} GiB upload limit. "
            "Reduce the batch size or sequence length."
        )

    payload_id = await _upload_payload(client, session_id=session_id, payload=payload)
    return _build_validation_body(body), payload_id


async def _upload_payload(
    client: AsyncTogether,
    *,
    session_id: str,
    payload: bytes,
) -> str:
    """Request a pre-signed upload URL, PUT the payload to R2, return payload_id."""
    upload_info = cast(
        Mapping[str, Any],
        await client.post(
            f"/rl/training-sessions/{session_id}/payloads/upload-url",
            cast_to=object,
            options={"max_retries": _MAX_RETRIES},
        ),
    )
    payload_id = cast(str, upload_info["payload_id"])
    upload_url = cast(str, upload_info["upload_url"])

    await client.put(
        upload_url,
        content=payload,
        cast_to=httpx.Response,
        options={
            "max_retries": _MAX_RETRIES,
            "headers": {"Authorization": Omit()},
        },
    )

    logger.debug(f"Uploaded payload {payload_id} with {len(payload)} bytes")
    return payload_id


async def _download_payload(
    client: AsyncTogether,
    *,
    session_id: str,
    payload_id: str,
) -> bytes:
    """Request a pre-signed download URL, GET the payload from R2."""
    download_info = cast(
        Mapping[str, Any],
        await client.post(
            f"/rl/training-sessions/{session_id}/payloads/{payload_id}/download-url",
            cast_to=object,
            options={"max_retries": _MAX_RETRIES},
        ),
    )
    download_url = cast(str, download_info["download_url"])

    response = await client.get(
        download_url,
        cast_to=httpx.Response,
        options={
            "max_retries": _MAX_RETRIES,
            "headers": {"Authorization": Omit()},
        },
    )

    logger.debug(f"Downloaded payload {payload_id} ({len(response.content)} bytes)")
    return response.content


async def resolve_result_payload(
    client: AsyncTogether,
    *,
    session_id: str,
    result: ResultModel,
) -> ResultModel:
    """Resolve an operation result that may reference an external payload.

    Args:
        client: Async Together client used to request download URLs.
        session_id: Training session ID that owns the result payload.
        result: Parsed operation result, possibly containing a runtime
            ``payload_id`` extra field.

    Returns:
        The original result when no payload ID is present, otherwise a new result
        parsed from the downloaded payload using the same model type.
    """
    payload_id = getattr(result, "payload_id", None)
    if not payload_id:
        return result

    raw = await _download_payload(client, session_id=session_id, payload_id=payload_id)
    data = json.loads(raw)
    return model_parse(type(result), data)
