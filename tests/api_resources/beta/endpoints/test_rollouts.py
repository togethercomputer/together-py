# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.pagination import SyncCursorPagination, AsyncCursorPagination
from together.types.beta.endpoints import (
    Rollout,
    RolloutDeleteResponse,
    RolloutDefaultsPreview,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

# Prism still generates retired `serving_latency` in preview-defaults examples.
_SKIP_PRISM_SERVING_LATENCY = pytest.mark.skip(
    reason="Prism mock still emits retired serving_latency in preview-defaults examples"
)


class TestRollouts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.create(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.create(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
            blue_green={},
            canary={
                "step_interval": "300s",
                "steps": [
                    {
                        "traffic": 25,
                        "replicas": 0,
                    },
                    {
                        "traffic": 50,
                        "replicas": 0,
                    },
                    {
                        "traffic": 100,
                        "replicas": 0,
                    },
                ],
            },
            final_source_replicas=0,
            final_target_replicas=0,
            metrics=[
                {
                    "name": "router_latency",
                    "percentile": 95,
                    "regression_check": {
                        "direction": "REGRESSION_DIRECTION_HIGHER_IS_WORSE",
                        "max_regression_percent": 0,
                    },
                    "stat": "METRIC_STAT_TYPE_PERCENTILE",
                    "threshold_check": {
                        "operator": "THRESHOLD_OPERATOR_LT",
                        "value": 30000,
                    },
                    "window": "300s",
                }
            ],
            rolling={},
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.endpoints.rollouts.with_raw_response.create(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.endpoints.rollouts.with_streaming_response.create(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.create(
                endpoint_id="endpointId",
                project_id="",
                source_deployment_id="dep_source123",
                target_deployment_id="dep_target456",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.create(
                endpoint_id="",
                project_id="projectId",
                source_deployment_id="dep_source123",
                target_deployment_id="dep_target456",
            )

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.endpoints.rollouts.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.endpoints.rollouts.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.retrieve(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.retrieve(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.list(
            endpoint_id="endpointId",
            project_id="projectId",
        )
        assert_matches_type(SyncCursorPagination[Rollout], rollout, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.list(
            endpoint_id="endpointId",
            project_id="projectId",
            after="after",
            filter="ROLLOUT_FILTER_ACTIVE",
            limit=0,
        )
        assert_matches_type(SyncCursorPagination[Rollout], rollout, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.endpoints.rollouts.with_raw_response.list(
            endpoint_id="endpointId",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(SyncCursorPagination[Rollout], rollout, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.endpoints.rollouts.with_streaming_response.list(
            endpoint_id="endpointId",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(SyncCursorPagination[Rollout], rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.list(
                endpoint_id="endpointId",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.list(
                endpoint_id="",
                project_id="projectId",
            )

    @parametrize
    def test_method_delete(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(RolloutDeleteResponse, rollout, path=["response"])

    @parametrize
    def test_method_delete_with_all_params(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            etag="etag",
        )
        assert_matches_type(RolloutDeleteResponse, rollout, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Together) -> None:
        response = client.beta.endpoints.rollouts.with_raw_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(RolloutDeleteResponse, rollout, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Together) -> None:
        with client.beta.endpoints.rollouts.with_streaming_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(RolloutDeleteResponse, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.delete(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.delete(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    def test_method_cancel(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.cancel(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            reason="reason",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_method_cancel_with_all_params(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.cancel(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            reason="reason",
            disposition="CANCEL_DISPOSITION_FREEZE",
            etag="etag",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: Together) -> None:
        response = client.beta.endpoints.rollouts.with_raw_response.cancel(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: Together) -> None:
        with client.beta.endpoints.rollouts.with_streaming_response.cancel(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.cancel(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                reason="reason",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.cancel(
                id="id",
                project_id="projectId",
                endpoint_id="",
                reason="reason",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.cancel(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                reason="reason",
            )

    @parametrize
    def test_method_pause(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.pause(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_method_pause_with_all_params(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.pause(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            etag="etag",
            reason="reason",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_raw_response_pause(self, client: Together) -> None:
        response = client.beta.endpoints.rollouts.with_raw_response.pause(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_streaming_response_pause(self, client: Together) -> None:
        with client.beta.endpoints.rollouts.with_streaming_response.pause(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_pause(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.pause(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.pause(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.pause(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    @_SKIP_PRISM_SERVING_LATENCY
    def test_method_preview_defaults(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.preview_defaults(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        )
        assert_matches_type(RolloutDefaultsPreview, rollout, path=["response"])

    @parametrize
    @_SKIP_PRISM_SERVING_LATENCY
    def test_method_preview_defaults_with_all_params(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.preview_defaults(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
            blue_green={},
            canary={
                "step_interval": "300s",
                "steps": [
                    {
                        "traffic": 25,
                        "replicas": 0,
                    },
                    {
                        "traffic": 50,
                        "replicas": 0,
                    },
                    {
                        "traffic": 100,
                        "replicas": 0,
                    },
                ],
            },
            final_source_replicas=0,
            final_target_replicas=0,
            metrics=[
                {
                    "name": "router_latency",
                    "percentile": 95,
                    "regression_check": {
                        "direction": "REGRESSION_DIRECTION_HIGHER_IS_WORSE",
                        "max_regression_percent": 0,
                    },
                    "stat": "METRIC_STAT_TYPE_PERCENTILE",
                    "threshold_check": {
                        "operator": "THRESHOLD_OPERATOR_LT",
                        "value": 30000,
                    },
                    "window": "300s",
                }
            ],
            rolling={},
        )
        assert_matches_type(RolloutDefaultsPreview, rollout, path=["response"])

    @parametrize
    @_SKIP_PRISM_SERVING_LATENCY
    def test_raw_response_preview_defaults(self, client: Together) -> None:
        response = client.beta.endpoints.rollouts.with_raw_response.preview_defaults(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(RolloutDefaultsPreview, rollout, path=["response"])

    @parametrize
    @_SKIP_PRISM_SERVING_LATENCY
    def test_streaming_response_preview_defaults(self, client: Together) -> None:
        with client.beta.endpoints.rollouts.with_streaming_response.preview_defaults(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(RolloutDefaultsPreview, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_preview_defaults(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.preview_defaults(
                endpoint_id="endpointId",
                project_id="",
                source_deployment_id="dep_source123",
                target_deployment_id="dep_target456",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.preview_defaults(
                endpoint_id="",
                project_id="projectId",
                source_deployment_id="dep_source123",
                target_deployment_id="dep_target456",
            )

    @parametrize
    def test_method_promote(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.promote(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_method_promote_with_all_params(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.promote(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            etag="etag",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_raw_response_promote(self, client: Together) -> None:
        response = client.beta.endpoints.rollouts.with_raw_response.promote(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_streaming_response_promote(self, client: Together) -> None:
        with client.beta.endpoints.rollouts.with_streaming_response.promote(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_promote(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.promote(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.promote(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.promote(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    def test_method_resume(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.resume(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_method_resume_with_all_params(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.resume(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            etag="etag",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_raw_response_resume(self, client: Together) -> None:
        response = client.beta.endpoints.rollouts.with_raw_response.resume(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_streaming_response_resume(self, client: Together) -> None:
        with client.beta.endpoints.rollouts.with_streaming_response.resume(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_resume(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.resume(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.resume(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.resume(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    def test_method_start(self, client: Together) -> None:
        rollout = client.beta.endpoints.rollouts.start(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_raw_response_start(self, client: Together) -> None:
        response = client.beta.endpoints.rollouts.with_raw_response.start(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    def test_streaming_response_start(self, client: Together) -> None:
        with client.beta.endpoints.rollouts.with_streaming_response.start(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_start(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.start(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.start(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.rollouts.with_raw_response.start(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )


class TestAsyncRollouts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.create(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.create(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
            blue_green={},
            canary={
                "step_interval": "300s",
                "steps": [
                    {
                        "traffic": 25,
                        "replicas": 0,
                    },
                    {
                        "traffic": 50,
                        "replicas": 0,
                    },
                    {
                        "traffic": 100,
                        "replicas": 0,
                    },
                ],
            },
            final_source_replicas=0,
            final_target_replicas=0,
            metrics=[
                {
                    "name": "router_latency",
                    "percentile": 95,
                    "regression_check": {
                        "direction": "REGRESSION_DIRECTION_HIGHER_IS_WORSE",
                        "max_regression_percent": 0,
                    },
                    "stat": "METRIC_STAT_TYPE_PERCENTILE",
                    "threshold_check": {
                        "operator": "THRESHOLD_OPERATOR_LT",
                        "value": 30000,
                    },
                    "window": "300s",
                }
            ],
            rolling={},
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.rollouts.with_raw_response.create(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.rollouts.with_streaming_response.create(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.create(
                endpoint_id="endpointId",
                project_id="",
                source_deployment_id="dep_source123",
                target_deployment_id="dep_target456",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.create(
                endpoint_id="",
                project_id="projectId",
                source_deployment_id="dep_source123",
                target_deployment_id="dep_target456",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.rollouts.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.rollouts.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.retrieve(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.retrieve(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.list(
            endpoint_id="endpointId",
            project_id="projectId",
        )
        assert_matches_type(AsyncCursorPagination[Rollout], rollout, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.list(
            endpoint_id="endpointId",
            project_id="projectId",
            after="after",
            filter="ROLLOUT_FILTER_ACTIVE",
            limit=0,
        )
        assert_matches_type(AsyncCursorPagination[Rollout], rollout, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.rollouts.with_raw_response.list(
            endpoint_id="endpointId",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(AsyncCursorPagination[Rollout], rollout, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.rollouts.with_streaming_response.list(
            endpoint_id="endpointId",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(AsyncCursorPagination[Rollout], rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.list(
                endpoint_id="endpointId",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.list(
                endpoint_id="",
                project_id="projectId",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(RolloutDeleteResponse, rollout, path=["response"])

    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            etag="etag",
        )
        assert_matches_type(RolloutDeleteResponse, rollout, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.rollouts.with_raw_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(RolloutDeleteResponse, rollout, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.rollouts.with_streaming_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(RolloutDeleteResponse, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.delete(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.delete(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    async def test_method_cancel(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.cancel(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            reason="reason",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_method_cancel_with_all_params(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.cancel(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            reason="reason",
            disposition="CANCEL_DISPOSITION_FREEZE",
            etag="etag",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.rollouts.with_raw_response.cancel(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.rollouts.with_streaming_response.cancel(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.cancel(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                reason="reason",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.cancel(
                id="id",
                project_id="projectId",
                endpoint_id="",
                reason="reason",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.cancel(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                reason="reason",
            )

    @parametrize
    async def test_method_pause(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.pause(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_method_pause_with_all_params(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.pause(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            etag="etag",
            reason="reason",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_raw_response_pause(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.rollouts.with_raw_response.pause(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_streaming_response_pause(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.rollouts.with_streaming_response.pause(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_pause(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.pause(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.pause(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.pause(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    @_SKIP_PRISM_SERVING_LATENCY
    async def test_method_preview_defaults(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.preview_defaults(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        )
        assert_matches_type(RolloutDefaultsPreview, rollout, path=["response"])

    @parametrize
    @_SKIP_PRISM_SERVING_LATENCY
    async def test_method_preview_defaults_with_all_params(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.preview_defaults(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
            blue_green={},
            canary={
                "step_interval": "300s",
                "steps": [
                    {
                        "traffic": 25,
                        "replicas": 0,
                    },
                    {
                        "traffic": 50,
                        "replicas": 0,
                    },
                    {
                        "traffic": 100,
                        "replicas": 0,
                    },
                ],
            },
            final_source_replicas=0,
            final_target_replicas=0,
            metrics=[
                {
                    "name": "router_latency",
                    "percentile": 95,
                    "regression_check": {
                        "direction": "REGRESSION_DIRECTION_HIGHER_IS_WORSE",
                        "max_regression_percent": 0,
                    },
                    "stat": "METRIC_STAT_TYPE_PERCENTILE",
                    "threshold_check": {
                        "operator": "THRESHOLD_OPERATOR_LT",
                        "value": 30000,
                    },
                    "window": "300s",
                }
            ],
            rolling={},
        )
        assert_matches_type(RolloutDefaultsPreview, rollout, path=["response"])

    @parametrize
    @_SKIP_PRISM_SERVING_LATENCY
    async def test_raw_response_preview_defaults(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.rollouts.with_raw_response.preview_defaults(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(RolloutDefaultsPreview, rollout, path=["response"])

    @parametrize
    @_SKIP_PRISM_SERVING_LATENCY
    async def test_streaming_response_preview_defaults(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.rollouts.with_streaming_response.preview_defaults(
            endpoint_id="endpointId",
            project_id="projectId",
            source_deployment_id="dep_source123",
            target_deployment_id="dep_target456",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(RolloutDefaultsPreview, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_preview_defaults(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.preview_defaults(
                endpoint_id="endpointId",
                project_id="",
                source_deployment_id="dep_source123",
                target_deployment_id="dep_target456",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.preview_defaults(
                endpoint_id="",
                project_id="projectId",
                source_deployment_id="dep_source123",
                target_deployment_id="dep_target456",
            )

    @parametrize
    async def test_method_promote(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.promote(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_method_promote_with_all_params(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.promote(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            etag="etag",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_raw_response_promote(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.rollouts.with_raw_response.promote(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_streaming_response_promote(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.rollouts.with_streaming_response.promote(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_promote(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.promote(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.promote(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.promote(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    async def test_method_resume(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.resume(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_method_resume_with_all_params(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.resume(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            etag="etag",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_raw_response_resume(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.rollouts.with_raw_response.resume(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_streaming_response_resume(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.rollouts.with_streaming_response.resume(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_resume(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.resume(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.resume(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.resume(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    async def test_method_start(self, async_client: AsyncTogether) -> None:
        rollout = await async_client.beta.endpoints.rollouts.start(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_raw_response_start(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.rollouts.with_raw_response.start(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rollout = await response.parse()
        assert_matches_type(Rollout, rollout, path=["response"])

    @parametrize
    async def test_streaming_response_start(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.rollouts.with_streaming_response.start(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rollout = await response.parse()
            assert_matches_type(Rollout, rollout, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_start(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.start(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.start(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.rollouts.with_raw_response.start(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )
