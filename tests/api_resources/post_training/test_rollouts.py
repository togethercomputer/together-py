# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.post_training import EstimateRolloutResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRollouts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_estimate(self, client: Together) -> None:
        rollout = client.post_training.rollouts.estimate(
            added_tokens_per_turn=0,
            base_model="zai-org/GLM-5.3",
            concurrency=1,
            episodes=1,
            generated_tokens_per_turn=1,
            prompt_tokens=1,
            turns=1,
        )
        assert_matches_type(EstimateRolloutResponse, rollout, path=["response"])

    @parametrize
    def test_method_estimate_with_all_params(self, client: Together) -> None:
        rollout = client.post_training.rollouts.estimate(
            added_tokens_per_turn=0,
            base_model="zai-org/GLM-5.3",
            concurrency=1,
            episodes=1,
            generated_tokens_per_turn=1,
            prompt_tokens=1,
            turns=1,
            compute_config={
                "gpu_type": "B200-SXM",
                "num_generator_replicas": 2,
                "num_trainer_replicas": 0,
            },
            distinct_prompts_per_replica=1,
            episodes_per_prompt=1,
            lora_enabled=True,
            shared_prefix_tokens=0,
        )
        assert_matches_type(EstimateRolloutResponse, rollout, path=["response"])

    @parametrize
    def test_raw_response_estimate(self, client: Together) -> None:
        response = client.post_training.rollouts.with_raw_response.estimate(
            added_tokens_per_turn=0,
            base_model="zai-org/GLM-5.3",
            concurrency=1,
            episodes=1,
            generated_tokens_per_turn=1,
            prompt_tokens=1,
            turns=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(EstimateRolloutResponse, rollout, path=["response"])

    @parametrize
    def test_streaming_response_estimate(self, client: Together) -> None:
        with client.post_training.rollouts.with_streaming_response.estimate(
            added_tokens_per_turn=0,
            base_model="zai-org/GLM-5.3",
            concurrency=1,
            episodes=1,
            generated_tokens_per_turn=1,
            prompt_tokens=1,
            turns=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(EstimateRolloutResponse, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRollouts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_estimate(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.post_training.rollouts.estimate(
            added_tokens_per_turn=0,
            base_model="zai-org/GLM-5.3",
            concurrency=1,
            episodes=1,
            generated_tokens_per_turn=1,
            prompt_tokens=1,
            turns=1,
        )
        assert_matches_type(EstimateRolloutResponse, rollout, path=["response"])

    @parametrize
    async def test_method_estimate_with_all_params(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.post_training.rollouts.estimate(
            added_tokens_per_turn=0,
            base_model="zai-org/GLM-5.3",
            concurrency=1,
            episodes=1,
            generated_tokens_per_turn=1,
            prompt_tokens=1,
            turns=1,
            compute_config={
                "gpu_type": "B200-SXM",
                "num_generator_replicas": 2,
                "num_trainer_replicas": 0,
            },
            distinct_prompts_per_replica=1,
            episodes_per_prompt=1,
            lora_enabled=True,
            shared_prefix_tokens=0,
        )
        assert_matches_type(EstimateRolloutResponse, rollout, path=["response"])

    @parametrize
    async def test_raw_response_estimate(self, async_client: AsyncTogether) -> None:
        response = await async_client.post_training.rollouts.with_raw_response.estimate(
            added_tokens_per_turn=0,
            base_model="zai-org/GLM-5.3",
            concurrency=1,
            episodes=1,
            generated_tokens_per_turn=1,
            prompt_tokens=1,
            turns=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(EstimateRolloutResponse, rollout, path=["response"])

    @parametrize
    async def test_streaming_response_estimate(self, async_client: AsyncTogether) -> None:
        async with async_client.post_training.rollouts.with_streaming_response.estimate(
            added_tokens_per_turn=0,
            base_model="zai-org/GLM-5.3",
            concurrency=1,
            episodes=1,
            generated_tokens_per_turn=1,
            prompt_tokens=1,
            turns=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(EstimateRolloutResponse, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True
