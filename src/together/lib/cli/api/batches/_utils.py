from __future__ import annotations

from typing import Literal
from typing_extensions import TypeAlias

BatchApiType: TypeAlias = Literal["chat.completions", "audio.transcriptions", "audio.translations"]
BatchEndpoint: TypeAlias = Literal["/v1/chat/completions", "/v1/audio/transcriptions", "/v1/audio/translations"]

API_TO_ENDPOINT: dict[BatchApiType, BatchEndpoint] = {
    "chat.completions": "/v1/chat/completions",
    "audio.transcriptions": "/v1/audio/transcriptions",
    "audio.translations": "/v1/audio/translations",
}

ENDPOINT_TO_API: dict[str, BatchApiType] = {endpoint: api for api, endpoint in API_TO_ENDPOINT.items()}


def format_endpoint(endpoint: str | None) -> str:
    if not endpoint:
        return ""
    return ENDPOINT_TO_API.get(endpoint, endpoint)
