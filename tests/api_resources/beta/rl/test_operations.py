# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta.rl import (
    SampleOperation,
    ForwardOperation,
    OptimStepOperation,
    ForwardBackwardOperation,
    TrainingCheckpointOperation,
    InferenceCheckpointOperation,
    CustomForwardBackwardOperation,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOperations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_inference_checkpoint(self, client: Together) -> None:
        operation = client.beta.rl.operations.create_inference_checkpoint(
            "session_id",
        )
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_create_inference_checkpoint(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.create_inference_checkpoint(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_create_inference_checkpoint(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.create_inference_checkpoint(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create_inference_checkpoint(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.create_inference_checkpoint(
                "",
            )

    @parametrize
    def test_method_create_training_checkpoint(self, client: Together) -> None:
        operation = client.beta.rl.operations.create_training_checkpoint(
            "session_id",
        )
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_create_training_checkpoint(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.create_training_checkpoint(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_create_training_checkpoint(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.create_training_checkpoint(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create_training_checkpoint(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.create_training_checkpoint(
                "",
            )

    @parametrize
    def test_method_custom_forward_backward(self, client: Together) -> None:
        operation = client.beta.rl.operations.custom_forward_backward(
            session_id="session_id",
            gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )
        assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_custom_forward_backward(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.custom_forward_backward(
            session_id="session_id",
            gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_custom_forward_backward(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.custom_forward_backward(
            session_id="session_id",
            gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_custom_forward_backward(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.custom_forward_backward(
                session_id="",
                gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
                samples=[
                    {
                        "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                        "model_input": {"chunks": [{}]},
                    }
                ],
            )

    @parametrize
    def test_method_forward(self, client: Together) -> None:
        operation = client.beta.rl.operations.forward(
            session_id="session_id",
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )
        assert_matches_type(ForwardOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_forward(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.forward(
            session_id="session_id",
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(ForwardOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_forward(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.forward(
            session_id="session_id",
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(ForwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_forward(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.forward(
                session_id="",
                samples=[
                    {
                        "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                        "model_input": {"chunks": [{}]},
                    }
                ],
            )

    @parametrize
    def test_method_forward_backward(self, client: Together) -> None:
        operation = client.beta.rl.operations.forward_backward(
            session_id="session_id",
            loss={"type": "LOSS_TYPE_GRPO"},
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_method_forward_backward_with_all_params(self, client: Together) -> None:
        operation = client.beta.rl.operations.forward_backward(
            session_id="session_id",
            loss={
                "type": "LOSS_TYPE_GRPO",
                "cross_entropy_params": {},
                "grpo_params": {
                    "agg_type": "GRPO_LOSS_AGGREGATION_TYPE_FIXED_HORIZON",
                    "beta": 0.1,
                    "clip_high": 0.28,
                    "clip_low": 0.2,
                    "ratio_type": "GRPO_LOSS_RATIO_TYPE_TOKEN",
                },
            },
            samples=[
                {
                    "loss_inputs": {
                        "target_tokens": {
                            "data": [123, 456, 789],
                            "dtype": "D_TYPE_INT64",
                        },
                        "grpo_inputs": {
                            "advantages": {
                                "data": [0.5, 0.5],
                                "dtype": "D_TYPE_FLOAT32",
                            },
                            "generator_logprobs": {
                                "data": [-1.2, -0.8],
                                "dtype": "D_TYPE_FLOAT32",
                            },
                            "reference_logprobs": {
                                "data": [-1.2, -0.8],
                                "dtype": "D_TYPE_FLOAT32",
                            },
                        },
                        "loss_mask": {
                            "data": [0, 0, 1],
                            "dtype": "D_TYPE_INT64",
                        },
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                    "policy_segments": [
                        {
                            "start_token": 0,
                            "version": 5,
                        }
                    ],
                }
            ],
        )
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_forward_backward(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.forward_backward(
            session_id="session_id",
            loss={"type": "LOSS_TYPE_GRPO"},
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_forward_backward(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.forward_backward(
            session_id="session_id",
            loss={"type": "LOSS_TYPE_GRPO"},
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_forward_backward(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.forward_backward(
                session_id="",
                loss={"type": "LOSS_TYPE_GRPO"},
                samples=[
                    {
                        "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                        "model_input": {"chunks": [{}]},
                    }
                ],
            )

    @parametrize
    def test_method_optim_step(self, client: Together) -> None:
        operation = client.beta.rl.operations.optim_step(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_UNSPECIFIED",
        )
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    def test_method_optim_step_with_all_params(self, client: Together) -> None:
        operation = client.beta.rl.operations.optim_step(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_UNSPECIFIED",
            adamw_params={
                "beta1": 0.9,
                "beta2": 0.95,
                "eps": 1e-8,
                "learning_rate": 0.0001,
                "weight_decay": 0.1,
            },
            max_grad_norm=10,
            muon_params={
                "adamw": {
                    "beta1": 0.9,
                    "beta2": 0.95,
                    "eps": 1e-8,
                    "learning_rate": 0.0001,
                    "weight_decay": 0.1,
                },
                "learning_rate": 0.02,
                "momentum": 0.95,
                "newton_schulz_steps": 5,
                "weight_decay": 0,
            },
        )
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_optim_step(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.optim_step(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_optim_step(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.optim_step(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(OptimStepOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_optim_step(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.optim_step(
                session_id="",
                weight_sync_type="WEIGHT_SYNC_TYPE_UNSPECIFIED",
            )

    @parametrize
    def test_method_retrieve_custom_forward_backward(self, client: Together) -> None:
        operation = client.beta.rl.operations.retrieve_custom_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_retrieve_custom_forward_backward(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.retrieve_custom_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_custom_forward_backward(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.retrieve_custom_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_custom_forward_backward(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_custom_forward_backward(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_custom_forward_backward(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    def test_method_retrieve_forward(self, client: Together) -> None:
        operation = client.beta.rl.operations.retrieve_forward(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(ForwardOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_retrieve_forward(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.retrieve_forward(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(ForwardOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_forward(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.retrieve_forward(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(ForwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_forward(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_forward(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_forward(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    def test_method_retrieve_forward_backward(self, client: Together) -> None:
        operation = client.beta.rl.operations.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_retrieve_forward_backward(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_forward_backward(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_forward_backward(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_forward_backward(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_forward_backward(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    def test_method_retrieve_inference_checkpoint(self, client: Together) -> None:
        operation = client.beta.rl.operations.retrieve_inference_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_retrieve_inference_checkpoint(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.retrieve_inference_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_inference_checkpoint(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.retrieve_inference_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_inference_checkpoint(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_inference_checkpoint(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_inference_checkpoint(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    def test_method_retrieve_optim_step(self, client: Together) -> None:
        operation = client.beta.rl.operations.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_retrieve_optim_step(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_optim_step(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(OptimStepOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_optim_step(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_optim_step(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_optim_step(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    def test_method_retrieve_sample(self, client: Together) -> None:
        operation = client.beta.rl.operations.retrieve_sample(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_retrieve_sample(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.retrieve_sample(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_sample(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.retrieve_sample(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(SampleOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_sample(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_sample(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_sample(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    def test_method_retrieve_training_checkpoint(self, client: Together) -> None:
        operation = client.beta.rl.operations.retrieve_training_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_retrieve_training_checkpoint(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.retrieve_training_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_training_checkpoint(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.retrieve_training_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_training_checkpoint(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_training_checkpoint(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_training_checkpoint(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    def test_method_sample(self, client: Together) -> None:
        operation = client.beta.rl.operations.sample(
            session_id="session_id",
            prompts=[{"chunks": [{}]}],
        )
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    def test_method_sample_with_all_params(self, client: Together) -> None:
        operation = client.beta.rl.operations.sample(
            session_id="session_id",
            prompts=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
            num_samples=1,
            sampling_params={
                "max_tokens": 100,
                "seed": "42",
                "stop": ["\n", "END"],
                "temperature": 1,
                "top_k": -1,
                "top_p": 1,
            },
        )
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_sample(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.sample(
            session_id="session_id",
            prompts=[{"chunks": [{}]}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_sample(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.sample(
            session_id="session_id",
            prompts=[{"chunks": [{}]}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(SampleOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_sample(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.sample(
                session_id="",
                prompts=[{"chunks": [{}]}],
            )


class TestAsyncOperations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.create_inference_checkpoint(
            "session_id",
        )
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_create_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.create_inference_checkpoint(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_create_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.create_inference_checkpoint(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.create_inference_checkpoint(
                "",
            )

    @parametrize
    async def test_method_create_training_checkpoint(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.create_training_checkpoint(
            "session_id",
        )
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_create_training_checkpoint(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.create_training_checkpoint(
            "session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_create_training_checkpoint(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.create_training_checkpoint(
            "session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create_training_checkpoint(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.create_training_checkpoint(
                "",
            )

    @parametrize
    async def test_method_custom_forward_backward(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.custom_forward_backward(
            session_id="session_id",
            gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )
        assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_custom_forward_backward(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.custom_forward_backward(
            session_id="session_id",
            gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_custom_forward_backward(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.custom_forward_backward(
            session_id="session_id",
            gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_custom_forward_backward(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.custom_forward_backward(
                session_id="",
                gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
                samples=[
                    {
                        "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                        "model_input": {"chunks": [{}]},
                    }
                ],
            )

    @parametrize
    async def test_method_forward(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.forward(
            session_id="session_id",
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )
        assert_matches_type(ForwardOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_forward(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.forward(
            session_id="session_id",
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(ForwardOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_forward(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.forward(
            session_id="session_id",
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(ForwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_forward(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.forward(
                session_id="",
                samples=[
                    {
                        "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                        "model_input": {"chunks": [{}]},
                    }
                ],
            )

    @parametrize
    async def test_method_forward_backward(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.forward_backward(
            session_id="session_id",
            loss={"type": "LOSS_TYPE_GRPO"},
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_method_forward_backward_with_all_params(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.forward_backward(
            session_id="session_id",
            loss={
                "type": "LOSS_TYPE_GRPO",
                "cross_entropy_params": {},
                "grpo_params": {
                    "agg_type": "GRPO_LOSS_AGGREGATION_TYPE_FIXED_HORIZON",
                    "beta": 0.1,
                    "clip_high": 0.28,
                    "clip_low": 0.2,
                    "ratio_type": "GRPO_LOSS_RATIO_TYPE_TOKEN",
                },
            },
            samples=[
                {
                    "loss_inputs": {
                        "target_tokens": {
                            "data": [123, 456, 789],
                            "dtype": "D_TYPE_INT64",
                        },
                        "grpo_inputs": {
                            "advantages": {
                                "data": [0.5, 0.5],
                                "dtype": "D_TYPE_FLOAT32",
                            },
                            "generator_logprobs": {
                                "data": [-1.2, -0.8],
                                "dtype": "D_TYPE_FLOAT32",
                            },
                            "reference_logprobs": {
                                "data": [-1.2, -0.8],
                                "dtype": "D_TYPE_FLOAT32",
                            },
                        },
                        "loss_mask": {
                            "data": [0, 0, 1],
                            "dtype": "D_TYPE_INT64",
                        },
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                    "policy_segments": [
                        {
                            "start_token": 0,
                            "version": 5,
                        }
                    ],
                }
            ],
        )
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_forward_backward(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.forward_backward(
            session_id="session_id",
            loss={"type": "LOSS_TYPE_GRPO"},
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_forward_backward(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.forward_backward(
            session_id="session_id",
            loss={"type": "LOSS_TYPE_GRPO"},
            samples=[
                {
                    "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                    "model_input": {"chunks": [{}]},
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_forward_backward(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.forward_backward(
                session_id="",
                loss={"type": "LOSS_TYPE_GRPO"},
                samples=[
                    {
                        "loss_inputs": {"target_tokens": {"data": [123, 456, 789]}},
                        "model_input": {"chunks": [{}]},
                    }
                ],
            )

    @parametrize
    async def test_method_optim_step(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.optim_step(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_UNSPECIFIED",
        )
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    async def test_method_optim_step_with_all_params(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.optim_step(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_UNSPECIFIED",
            adamw_params={
                "beta1": 0.9,
                "beta2": 0.95,
                "eps": 1e-8,
                "learning_rate": 0.0001,
                "weight_decay": 0.1,
            },
            max_grad_norm=10,
            muon_params={
                "adamw": {
                    "beta1": 0.9,
                    "beta2": 0.95,
                    "eps": 1e-8,
                    "learning_rate": 0.0001,
                    "weight_decay": 0.1,
                },
                "learning_rate": 0.02,
                "momentum": 0.95,
                "newton_schulz_steps": 5,
                "weight_decay": 0,
            },
        )
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_optim_step(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.optim_step(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_UNSPECIFIED",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_optim_step(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.optim_step(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_UNSPECIFIED",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(OptimStepOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_optim_step(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.optim_step(
                session_id="",
                weight_sync_type="WEIGHT_SYNC_TYPE_UNSPECIFIED",
            )

    @parametrize
    async def test_method_retrieve_custom_forward_backward(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.retrieve_custom_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_custom_forward_backward(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.retrieve_custom_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_custom_forward_backward(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.retrieve_custom_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_custom_forward_backward(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_custom_forward_backward(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_custom_forward_backward(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    async def test_method_retrieve_forward(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.retrieve_forward(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(ForwardOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_forward(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.retrieve_forward(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(ForwardOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_forward(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.retrieve_forward(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(ForwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_forward(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_forward(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_forward(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    async def test_method_retrieve_forward_backward(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_forward_backward(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_forward_backward(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.retrieve_forward_backward(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_forward_backward(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_forward_backward(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_forward_backward(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    async def test_method_retrieve_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.retrieve_inference_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.retrieve_inference_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.retrieve_inference_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_inference_checkpoint(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_inference_checkpoint(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    async def test_method_retrieve_optim_step(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_optim_step(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_optim_step(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.retrieve_optim_step(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(OptimStepOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_optim_step(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_optim_step(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_optim_step(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    async def test_method_retrieve_sample(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.retrieve_sample(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_sample(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.retrieve_sample(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_sample(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.retrieve_sample(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(SampleOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_sample(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_sample(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_sample(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    async def test_method_retrieve_training_checkpoint(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.retrieve_training_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_training_checkpoint(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.retrieve_training_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_training_checkpoint(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.retrieve_training_checkpoint(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_training_checkpoint(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_training_checkpoint(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_training_checkpoint(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    async def test_method_sample(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.sample(
            session_id="session_id",
            prompts=[{"chunks": [{}]}],
        )
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    async def test_method_sample_with_all_params(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.sample(
            session_id="session_id",
            prompts=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
            num_samples=1,
            sampling_params={
                "max_tokens": 100,
                "seed": "42",
                "stop": ["\n", "END"],
                "temperature": 1,
                "top_k": -1,
                "top_p": 1,
            },
        )
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_sample(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.sample(
            session_id="session_id",
            prompts=[{"chunks": [{}]}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_sample(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.sample(
            session_id="session_id",
            prompts=[{"chunks": [{}]}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(SampleOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_sample(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.sample(
                session_id="",
                prompts=[{"chunks": [{}]}],
            )
