"""Regen-guard: `client.beta.realtime` is a handwritten addition to the generated
resources/beta/beta.py. If a Stainless regeneration drops the cached_property, these tests
fail loudly instead of the feature silently disappearing.
"""

from __future__ import annotations

from together import Together, AsyncTogether
from together.resources.realtime import RealtimeResource, AsyncRealtimeResource


def test_sync_client_exposes_realtime() -> None:
    client = Together(api_key="test-key", base_url="http://127.0.0.1:4010")
    assert isinstance(client.beta.realtime, RealtimeResource)
    manager = client.beta.realtime.connect(model="openai/whisper-large-v3")
    assert manager is not None


def test_async_client_exposes_realtime() -> None:
    client = AsyncTogether(api_key="test-key", base_url="http://127.0.0.1:4010")
    assert isinstance(client.beta.realtime, AsyncRealtimeResource)


def test_public_lib_surface_importable() -> None:
    import together.lib.realtime as rt

    for name in rt.__all__:
        assert getattr(rt, name) is not None


def test_root_realtime_module_reexports_public_surface() -> None:
    """`together.realtime` is the stable public import path; it must expose
    everything the lib package exports (a regen or refactor that drops the
    root shim or lets it drift fails here)."""
    import together.realtime as public
    import together.lib.realtime as lib

    for name in lib.__all__:
        assert getattr(public, name) is getattr(lib, name), name


def test_url_and_header_derivation() -> None:
    import httpx

    from together.lib.realtime._connection import build_realtime_url, build_realtime_headers

    url = build_realtime_url(
        httpx.URL("https://api.together.ai/v1/"),
        model="openai/whisper-large-v3",
        turn_detection={"type": "server_vad", "min_silence_duration_ms": 400},
    )
    assert url.startswith("wss://api.together.ai/v1/realtime?")
    assert "model=openai%2Fwhisper-large-v3" in url or "model=openai/whisper-large-v3" in url
    assert "input_audio_format=pcm_s16le_16000" in url
    assert "turn_detection=server_vad" in url
    assert "min_silence_duration_ms=400" in url

    headers = build_realtime_headers({"Authorization": "Bearer k"})
    assert headers["Authorization"] == "Bearer k"
    assert headers["OpenAI-Beta"] == "realtime=v1"


def test_url_language_query_param() -> None:
    """language is a connection-time query param: the server ignores it in
    transcription_session.updated and only honors it on the URL (#505)."""
    from urllib.parse import parse_qs, urlsplit

    import httpx

    from together.lib.realtime._connection import build_realtime_url

    base = httpx.URL("https://api.together.ai/v1/")

    url = build_realtime_url(base, model="openai/whisper-large-v3", language="es")
    assert parse_qs(urlsplit(url).query)["language"] == ["es"]

    # "auto" passes through verbatim, not translated or dropped
    url = build_realtime_url(base, model="openai/whisper-large-v3", language="auto")
    assert parse_qs(urlsplit(url).query)["language"] == ["auto"]

    # omitted -> no language param at all
    url = build_realtime_url(base, model="openai/whisper-large-v3")
    assert "language" not in parse_qs(urlsplit(url).query)

    # an explicit extra_query overrides the language argument — one value, no
    # duplicate query param
    url = build_realtime_url(
        base,
        model="openai/whisper-large-v3",
        language="en",
        extra_query={"language": "fr"},
    )
    assert parse_qs(urlsplit(url).query)["language"] == ["fr"]


def test_sync_async_resource_signatures_stay_in_sync() -> None:
    """The sync/async resource surfaces are intentionally duplicated for IDE
    ergonomics; this guard catches parameter drift between them."""
    import inspect

    for name in ("connect", "transcription"):
        sync_params = inspect.signature(getattr(RealtimeResource, name)).parameters
        async_params = inspect.signature(getattr(AsyncRealtimeResource, name)).parameters
        assert sync_params == async_params, f"{name}() signatures diverged"
