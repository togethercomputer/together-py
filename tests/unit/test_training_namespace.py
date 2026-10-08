"""Regen-guard: `client.training` is a handwritten alias for resources Stainless still emits at `client.beta.rl`."""

from __future__ import annotations

from together import Together, AsyncTogether
from together.resources.beta.rl.rl import (
    RlResource,
    AsyncRlResource,
    RlResourceWithRawResponse,
    AsyncRlResourceWithRawResponse,
    RlResourceWithStreamingResponse,
    AsyncRlResourceWithStreamingResponse,
)


def test_sync_training_is_beta_rl() -> None:
    client = Together(api_key="test-key", base_url="http://127.0.0.1:4010")
    assert isinstance(client.training, RlResource)
    assert client.training is client.beta.rl
    assert isinstance(client.with_raw_response.training, RlResourceWithRawResponse)
    assert client.with_raw_response.training is client.with_raw_response.beta.rl
    assert isinstance(client.with_streaming_response.training, RlResourceWithStreamingResponse)
    assert client.with_streaming_response.training is client.with_streaming_response.beta.rl


def test_async_training_is_beta_rl() -> None:
    client = AsyncTogether(api_key="test-key", base_url="http://127.0.0.1:4010")
    assert isinstance(client.training, AsyncRlResource)
    assert client.training is client.beta.rl
    assert isinstance(client.with_raw_response.training, AsyncRlResourceWithRawResponse)
    assert client.with_raw_response.training is client.with_raw_response.beta.rl
    assert isinstance(client.with_streaming_response.training, AsyncRlResourceWithStreamingResponse)
    assert client.with_streaming_response.training is client.with_streaming_response.beta.rl
