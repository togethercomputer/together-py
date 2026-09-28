from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Union, TypeVar, cast
from collections.abc import Mapping, Sequence
from typing_extensions import TypeAlias

import httpx

from ...._types import Omit
from ...._utils import transform
from ...._client import AsyncTogether
from ...._compat import model_parse
from ...._models import BaseModel
from ._operations import OperationResponse, require_output

if TYPE_CHECKING:
    from .clients.session import SessionClient

logger = logging.getLogger("together")

_LARGE_PAYLOAD_THRESHOLD = 0.5 * 1024 * 1024  # 0.5 MiB
_MAX_PAYLOAD_SIZE = 5 * 1024**3 - 5 * 1024**2  # 4.995 GiB, R2's single-PUT upload limit
_VALIDATION_MAX_SEQ_LEN = 8
# Shape/CSR metadata describes the full tensor, not the truncated validation body.
# Opaque routing keys stay unchanged in both the validation body and uploaded payload.
_VALIDATION_OMITTED_KEYS = frozenset({"shape", "sparse_crow_indices", "sparse_col_indices"})
_MAX_RETRIES = 5

JsonValue: TypeAlias = Union[str, int, float, bool, None, Mapping[str, Any], list[Any]]
ResultModel = TypeVar("ResultModel", bound=BaseModel)


def _shrink_member(key: str, value: JsonValue, max_len: int) -> JsonValue:
    """Shrink one mapping member, giving model-input chunks their shared token budget."""
    if key == "chunks" and isinstance(value, list):
        return _shrink_model_input_chunks(value, max_len)
    return _shrink_for_validation(value, max_len)


def _shrink_for_validation(data: JsonValue, max_len: int = _VALIDATION_MAX_SEQ_LEN) -> JsonValue:
    """Shrink a serialized body into an inline stand-in for an uploaded payload.

    Numeric sequences are truncated to ``max_len`` and ``_VALIDATION_OMITTED_KEYS`` are
    dropped at every depth, so no surviving metadata describes the untruncated data.
    Model-input chunks consume one shared token budget to stay aligned with loss tensor
    data, which is truncated to the same ``max_len``.
    """
    if isinstance(data, dict):
        return {
            key: _shrink_member(key, value, max_len)
            for key, value in data.items()
            if key not in _VALIDATION_OMITTED_KEYS
        }
    if isinstance(data, list):
        if data and isinstance(data[0], (int, float)):
            return data[:max_len]
        return [_shrink_for_validation(item, max_len) for item in data]
    return data


def _shrink_model_input_chunks(chunks: Sequence[Any], max_len: int) -> list[Any]:
    """Shrink encoded-text chunks in order against one token budget."""
    shrunk_chunks: list[Any] = []
    remaining = max_len

    for chunk in chunks:
        if remaining <= 0:
            break

        shrunk_chunks.append(_shrink_for_validation(chunk, remaining))
        if not isinstance(chunk, dict):
            continue

        chunk_mapping = cast("Mapping[str, Any]", chunk)
        encoded_text = chunk_mapping.get("encoded_text")
        if not isinstance(encoded_text, dict):
            continue

        encoded_text_mapping = cast("Mapping[str, Any]", encoded_text)
        tokens = encoded_text_mapping.get("tokens")
        if isinstance(tokens, list):
            remaining -= min(len(cast("list[Any]", tokens)), remaining)

    return shrunk_chunks


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
        A tuple containing the transformed request body and an optional payload ID.
        When the payload is small, the serialized body is returned with no payload
        ID. When it is large, the full serialized body is uploaded and the returned
        body is shrunk for inline validation: sequences are truncated and the keys in
        ``_VALIDATION_OMITTED_KEYS`` are dropped.
    """
    serialized = transform(body, expected_type=expected_type)
    # JSON has no NaN or infinity, and `json.dumps` emits bare `NaN` and `-Infinity` tokens
    # by default, which the server cannot parse.
    try:
        payload = json.dumps(serialized, separators=(",", ":"), allow_nan=False).encode()
    except ValueError as error:
        if "Out of range float" not in str(error):
            raise  # Some other encoding failure; its own message is the useful one.
        raise ValueError(
            "Operation payload holds a NaN or infinite value, which JSON cannot represent."
            " Check the request tensors and float parameters for non-finite entries; to mask"
            " a position, give it a zero 'weights' entry rather than a -inf logprob."
        ) from error
    if len(payload) <= _LARGE_PAYLOAD_THRESHOLD:
        return serialized, None

    if len(payload) > _MAX_PAYLOAD_SIZE:
        raise ValueError(
            f"Operation payload is {len(payload) / 1024**3:.2f} GiB, which exceeds the "
            f"{_MAX_PAYLOAD_SIZE / 1024**3:.2f} GiB upload limit. "
            "Reduce the batch size or sequence length."
        )

    payload_id = await _upload_payload(client, session_id=session_id, payload=payload)
    return cast("dict[str, Any]", _shrink_for_validation(serialized)), payload_id


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
        of the same model type built from the inline fields merged with the
        downloaded payload.

    Raises:
        ValueError: If the downloaded payload is not a JSON object.
    """
    payload_id = getattr(result, "payload_id", None)
    if not payload_id:
        return result

    raw = await _download_payload(client, session_id=session_id, payload_id=payload_id)
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"Result payload {payload_id} must be a JSON object, got {type(data).__name__}")
    # The service keeps the small members (`loss`, `metrics`) inline and offloads only
    # the large ones, so the payload alone does not validate as the result model.
    inline = result.to_dict(use_api_names=True, exclude_unset=True)
    inline.pop("payload_id")
    return model_parse(type(result), {**inline, **data})


async def resolve_operation_payload(completed: OperationResponse, *, session: SessionClient) -> Any:
    """Resolve a completed operation's required output, downloading its external payload if any."""
    return await resolve_result_payload(
        session._client,
        session_id=session.session_id,
        result=require_output(completed.output, operation=completed),
    )
