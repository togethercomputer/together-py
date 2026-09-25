# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta.rl import (
    SampleOperation,
    OptimStepOperation,
    WeightsSyncOperation,
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
            session_id="session_id",
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_create_inference_checkpoint(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.create_inference_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_create_inference_checkpoint(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.create_inference_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
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
                session_id="",
                idempotency_key="Idempotency-Key",
            )

    @parametrize
    def test_method_create_training_checkpoint(self, client: Together) -> None:
        operation = client.beta.rl.operations.create_training_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_create_training_checkpoint(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.create_training_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_create_training_checkpoint(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.create_training_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
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
                session_id="",
                idempotency_key="Idempotency-Key",
            )

    @parametrize
    def test_method_custom_forward_backward(self, client: Together) -> None:
        operation = client.beta.rl.operations.custom_forward_backward(
            session_id="session_id",
            gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
            samples=[
                {
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_custom_forward_backward(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.custom_forward_backward(
            session_id="session_id",
            gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
            samples=[
                {
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
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
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
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
                        "loss_fn_inputs": {
                            "foo": {
                                "data": [1, 2, 3],
                                "dtype": "int64",
                            }
                        },
                        "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                    }
                ],
                idempotency_key="Idempotency-Key",
            )

    @parametrize
    def test_method_forward_backward(self, client: Together) -> None:
        operation = client.beta.rl.operations.forward_backward(
            session_id="session_id",
            loss={"type": "LOSS_TYPE_GRPO"},
            samples=[
                {
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_method_forward_backward_with_all_params(self, client: Together) -> None:
        operation = client.beta.rl.operations.forward_backward(
            session_id="session_id",
            loss={
                "type": "LOSS_TYPE_GRPO",
                "cispo_params": {
                    "clip_high_threshold": 4,
                    "clip_low_threshold": 0,
                },
                "cross_entropy_params": {},
                "dppo_params": {
                    "delta_high": 0.15,
                    "delta_low": 0.15,
                },
                "dro_params": {"beta": 0.05},
                "grpo_params": {
                    "agg_type": "GRPO_LOSS_AGGREGATION_TYPE_FIXED_HORIZON",
                    "beta": 0.1,
                    "clip_high_threshold": 1.2,
                    "clip_low_threshold": 0.8,
                    "ratio_type": "GRPO_LOSS_RATIO_TYPE_TOKEN",
                },
                "ppo_params": {
                    "clip_high_threshold": 1.2,
                    "clip_low_threshold": 0.8,
                },
            },
            samples=[
                {
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                            "shape": [3],
                            "sparse_col_indices": [0, 2],
                            "sparse_crow_indices": [0, 2],
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                    "routed_experts_key": "routing/._.K--w2k.1v/fe91bd231a9ad9bd2aada37aa7ccc3d3.8840",
                }
            ],
            idempotency_key="Idempotency-Key",
            forward_only=True,
            return_loss_fn_outputs=True,
        )
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_forward_backward(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.forward_backward(
            session_id="session_id",
            loss={"type": "LOSS_TYPE_GRPO"},
            samples=[
                {
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
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
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
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
                        "loss_fn_inputs": {
                            "foo": {
                                "data": [1, 2, 3],
                                "dtype": "int64",
                            }
                        },
                        "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                    }
                ],
                idempotency_key="Idempotency-Key",
            )

    @parametrize
    def test_method_optim_step(self, client: Together) -> None:
        operation = client.beta.rl.operations.optim_step(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    def test_method_optim_step_with_all_params(self, client: Together) -> None:
        operation = client.beta.rl.operations.optim_step(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
            adam_params={
                "beta1": 0.9,
                "beta2": 0.95,
                "eps": 1e-8,
                "grad_clip_norm": 10,
                "learning_rate": 0.0001,
                "weight_decay": 0.1,
            },
            muon_params={
                "adam": {
                    "beta1": 0.9,
                    "beta2": 0.95,
                    "eps": 1e-8,
                    "grad_clip_norm": 10,
                    "learning_rate": 0.0001,
                    "weight_decay": 0.1,
                },
                "grad_clip_norm": 10,
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
            idempotency_key="Idempotency-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_optim_step(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.optim_step(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
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
                idempotency_key="Idempotency-Key",
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
    def test_method_retrieve_weights_sync(self, client: Together) -> None:
        operation = client.beta.rl.operations.retrieve_weights_sync(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(WeightsSyncOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_retrieve_weights_sync(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.retrieve_weights_sync(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(WeightsSyncOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_weights_sync(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.retrieve_weights_sync(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(WeightsSyncOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_weights_sync(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_weights_sync(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            client.beta.rl.operations.with_raw_response.retrieve_weights_sync(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    def test_method_sample(self, client: Together) -> None:
        operation = client.beta.rl.operations.sample(
            session_id="session_id",
            model_inputs=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    def test_method_sample_with_all_params(self, client: Together) -> None:
        operation = client.beta.rl.operations.sample(
            session_id="session_id",
            model_inputs=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
            idempotency_key="Idempotency-Key",
            num_samples=1,
            prompt_logprobs=False,
            return_routed_experts=False,
            sampling_params={
                "max_tokens": 512,
                "seed": "42",
                "stop": ["\n", "END"],
                "temperature": 1,
                "top_k": -1,
                "top_p": 1,
            },
            topk_prompt_logprobs=0,
        )
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_sample(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.sample(
            session_id="session_id",
            model_inputs=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
            idempotency_key="Idempotency-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_sample(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.sample(
            session_id="session_id",
            model_inputs=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
            idempotency_key="Idempotency-Key",
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
                model_inputs=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
                idempotency_key="Idempotency-Key",
            )

    @parametrize
    def test_method_weights_sync(self, client: Together) -> None:
        operation = client.beta.rl.operations.weights_sync(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(WeightsSyncOperation, operation, path=["response"])

    @parametrize
    def test_raw_response_weights_sync(self, client: Together) -> None:
        response = client.beta.rl.operations.with_raw_response.weights_sync(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
            idempotency_key="Idempotency-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = response.parse()
        assert_matches_type(WeightsSyncOperation, operation, path=["response"])

    @parametrize
    def test_streaming_response_weights_sync(self, client: Together) -> None:
        with client.beta.rl.operations.with_streaming_response.weights_sync(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
            idempotency_key="Idempotency-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = response.parse()
            assert_matches_type(WeightsSyncOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_weights_sync(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.rl.operations.with_raw_response.weights_sync(
                session_id="",
                weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
                idempotency_key="Idempotency-Key",
            )


class TestAsyncOperations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.create_inference_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_create_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.create_inference_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(InferenceCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_create_inference_checkpoint(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.create_inference_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
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
                session_id="",
                idempotency_key="Idempotency-Key",
            )

    @parametrize
    async def test_method_create_training_checkpoint(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.create_training_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_create_training_checkpoint(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.create_training_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(TrainingCheckpointOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_create_training_checkpoint(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.create_training_checkpoint(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
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
                session_id="",
                idempotency_key="Idempotency-Key",
            )

    @parametrize
    async def test_method_custom_forward_backward(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.custom_forward_backward(
            session_id="session_id",
            gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
            samples=[
                {
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(CustomForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_custom_forward_backward(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.custom_forward_backward(
            session_id="session_id",
            gradients=[{"data": [-0.1, 0.05, -0.08, 0.12, -0.03]}],
            samples=[
                {
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
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
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
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
                        "loss_fn_inputs": {
                            "foo": {
                                "data": [1, 2, 3],
                                "dtype": "int64",
                            }
                        },
                        "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                    }
                ],
                idempotency_key="Idempotency-Key",
            )

    @parametrize
    async def test_method_forward_backward(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.forward_backward(
            session_id="session_id",
            loss={"type": "LOSS_TYPE_GRPO"},
            samples=[
                {
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_method_forward_backward_with_all_params(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.forward_backward(
            session_id="session_id",
            loss={
                "type": "LOSS_TYPE_GRPO",
                "cispo_params": {
                    "clip_high_threshold": 4,
                    "clip_low_threshold": 0,
                },
                "cross_entropy_params": {},
                "dppo_params": {
                    "delta_high": 0.15,
                    "delta_low": 0.15,
                },
                "dro_params": {"beta": 0.05},
                "grpo_params": {
                    "agg_type": "GRPO_LOSS_AGGREGATION_TYPE_FIXED_HORIZON",
                    "beta": 0.1,
                    "clip_high_threshold": 1.2,
                    "clip_low_threshold": 0.8,
                    "ratio_type": "GRPO_LOSS_RATIO_TYPE_TOKEN",
                },
                "ppo_params": {
                    "clip_high_threshold": 1.2,
                    "clip_low_threshold": 0.8,
                },
            },
            samples=[
                {
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                            "shape": [3],
                            "sparse_col_indices": [0, 2],
                            "sparse_crow_indices": [0, 2],
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                    "routed_experts_key": "routing/._.K--w2k.1v/fe91bd231a9ad9bd2aada37aa7ccc3d3.8840",
                }
            ],
            idempotency_key="Idempotency-Key",
            forward_only=True,
            return_loss_fn_outputs=True,
        )
        assert_matches_type(ForwardBackwardOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_forward_backward(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.forward_backward(
            session_id="session_id",
            loss={"type": "LOSS_TYPE_GRPO"},
            samples=[
                {
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
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
                    "loss_fn_inputs": {
                        "foo": {
                            "data": [1, 2, 3],
                            "dtype": "int64",
                        }
                    },
                    "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                }
            ],
            idempotency_key="Idempotency-Key",
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
                        "loss_fn_inputs": {
                            "foo": {
                                "data": [1, 2, 3],
                                "dtype": "int64",
                            }
                        },
                        "model_input": {"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]},
                    }
                ],
                idempotency_key="Idempotency-Key",
            )

    @parametrize
    async def test_method_optim_step(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.optim_step(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    async def test_method_optim_step_with_all_params(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.optim_step(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
            adam_params={
                "beta1": 0.9,
                "beta2": 0.95,
                "eps": 1e-8,
                "grad_clip_norm": 10,
                "learning_rate": 0.0001,
                "weight_decay": 0.1,
            },
            muon_params={
                "adam": {
                    "beta1": 0.9,
                    "beta2": 0.95,
                    "eps": 1e-8,
                    "grad_clip_norm": 10,
                    "learning_rate": 0.0001,
                    "weight_decay": 0.1,
                },
                "grad_clip_norm": 10,
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
            idempotency_key="Idempotency-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(OptimStepOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_optim_step(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.optim_step(
            session_id="session_id",
            idempotency_key="Idempotency-Key",
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
                idempotency_key="Idempotency-Key",
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
    async def test_method_retrieve_weights_sync(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.retrieve_weights_sync(
            operation_id="operation_id",
            session_id="session_id",
        )
        assert_matches_type(WeightsSyncOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_weights_sync(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.retrieve_weights_sync(
            operation_id="operation_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(WeightsSyncOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_weights_sync(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.retrieve_weights_sync(
            operation_id="operation_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(WeightsSyncOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_weights_sync(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_weights_sync(
                operation_id="operation_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `operation_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.retrieve_weights_sync(
                operation_id="",
                session_id="session_id",
            )

    @parametrize
    async def test_method_sample(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.sample(
            session_id="session_id",
            model_inputs=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    async def test_method_sample_with_all_params(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.sample(
            session_id="session_id",
            model_inputs=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
            idempotency_key="Idempotency-Key",
            num_samples=1,
            prompt_logprobs=False,
            return_routed_experts=False,
            sampling_params={
                "max_tokens": 512,
                "seed": "42",
                "stop": ["\n", "END"],
                "temperature": 1,
                "top_k": -1,
                "top_p": 1,
            },
            topk_prompt_logprobs=0,
        )
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_sample(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.sample(
            session_id="session_id",
            model_inputs=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
            idempotency_key="Idempotency-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(SampleOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_sample(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.sample(
            session_id="session_id",
            model_inputs=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
            idempotency_key="Idempotency-Key",
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
                model_inputs=[{"chunks": [{"encoded_text": {"tokens": [123, 456, 789]}}]}],
                idempotency_key="Idempotency-Key",
            )

    @parametrize
    async def test_method_weights_sync(self, async_client: AsyncTogether) -> None:
        operation = await async_client.beta.rl.operations.weights_sync(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(WeightsSyncOperation, operation, path=["response"])

    @parametrize
    async def test_raw_response_weights_sync(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.operations.with_raw_response.weights_sync(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
            idempotency_key="Idempotency-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operation = await response.parse()
        assert_matches_type(WeightsSyncOperation, operation, path=["response"])

    @parametrize
    async def test_streaming_response_weights_sync(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.operations.with_streaming_response.weights_sync(
            session_id="session_id",
            weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
            idempotency_key="Idempotency-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operation = await response.parse()
            assert_matches_type(WeightsSyncOperation, operation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_weights_sync(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.rl.operations.with_raw_response.weights_sync(
                session_id="",
                weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
                idempotency_key="Idempotency-Key",
            )
