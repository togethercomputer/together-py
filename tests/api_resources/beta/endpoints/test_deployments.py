# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.pagination import SyncCursorPagination, AsyncCursorPagination
from together.types.beta import EndpointDeployment
from together.types.beta.endpoints import (
    DeploymentDeleteResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDeployments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        deployment = client.beta.endpoints.deployments.create(
            endpoint_id="endpointId",
            project_id="projectId",
            autoscaling={},
            name="name",
        )
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        deployment = client.beta.endpoints.deployments.create(
            endpoint_id="endpointId",
            project_id="projectId",
            autoscaling={
                "max_replicas": 0,
                "min_replicas": 0,
                "scale_down_window": "-160513s",
                "scale_to_zero_window": "-160513s",
                "scale_up_window": "-160513s",
                "scaling_metrics": [
                    {
                        "name": "name",
                        "target": 0,
                        "type": "METRIC_TARGET_TYPE_VALUE",
                        "percentile": "percentile",
                    }
                ],
            },
            name="name",
            validate_only=True,
            config="config",
            config_id="configId",
            enable_lora=True,
            model="model",
            model_id="modelId",
            model_revision_id="modelRevisionId",
            placement={
                "inline": {
                    "constraint": "ENFORCEMENT_REQUIRED",
                    "regions": ["string"],
                }
            },
        )
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.endpoints.deployments.with_raw_response.create(
            endpoint_id="endpointId",
            project_id="projectId",
            autoscaling={},
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.endpoints.deployments.with_streaming_response.create(
            endpoint_id="endpointId",
            project_id="projectId",
            autoscaling={},
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(EndpointDeployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.create(
                endpoint_id="endpointId",
                project_id="",
                autoscaling={},
                name="name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.create(
                endpoint_id="",
                project_id="projectId",
                autoscaling={},
                name="name",
            )

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        deployment = client.beta.endpoints.deployments.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.endpoints.deployments.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.endpoints.deployments.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(EndpointDeployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.retrieve(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.retrieve(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    def test_method_update(self, client: Together) -> None:
        deployment = client.beta.endpoints.deployments.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Together) -> None:
        deployment = client.beta.endpoints.deployments.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            update_mask="updateMask",
            autoscaling={
                "max_replicas": 0,
                "min_replicas": 0,
                "scale_down_window": "-160513s",
                "scale_to_zero_window": "-160513s",
                "scale_up_window": "-160513s",
                "scaling_metrics": [
                    {
                        "name": "name",
                        "target": 0,
                        "type": "METRIC_TARGET_TYPE_VALUE",
                        "percentile": "percentile",
                    }
                ],
            },
            etag="etag",
            name="name",
        )
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Together) -> None:
        response = client.beta.endpoints.deployments.with_raw_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Together) -> None:
        with client.beta.endpoints.deployments.with_streaming_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(EndpointDeployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.update(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.update(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.update(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        deployment = client.beta.endpoints.deployments.list(
            endpoint_id="endpointId",
            project_id="projectId",
        )
        assert_matches_type(SyncCursorPagination[EndpointDeployment], deployment, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        deployment = client.beta.endpoints.deployments.list(
            endpoint_id="endpointId",
            project_id="projectId",
            after="after",
            filter="filter",
            limit=0,
            order_by="orderBy",
        )
        assert_matches_type(SyncCursorPagination[EndpointDeployment], deployment, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.endpoints.deployments.with_raw_response.list(
            endpoint_id="endpointId",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(SyncCursorPagination[EndpointDeployment], deployment, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.endpoints.deployments.with_streaming_response.list(
            endpoint_id="endpointId",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(SyncCursorPagination[EndpointDeployment], deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.list(
                endpoint_id="endpointId",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.list(
                endpoint_id="",
                project_id="projectId",
            )

    @parametrize
    def test_method_delete(self, client: Together) -> None:
        deployment = client.beta.endpoints.deployments.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(DeploymentDeleteResponse, deployment, path=["response"])

    @parametrize
    def test_method_delete_with_all_params(self, client: Together) -> None:
        deployment = client.beta.endpoints.deployments.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            etag="etag",
        )
        assert_matches_type(DeploymentDeleteResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Together) -> None:
        response = client.beta.endpoints.deployments.with_raw_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeploymentDeleteResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Together) -> None:
        with client.beta.endpoints.deployments.with_streaming_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeploymentDeleteResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.delete(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.deployments.with_raw_response.delete(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )


class TestAsyncDeployments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.endpoints.deployments.create(
            endpoint_id="endpointId",
            project_id="projectId",
            autoscaling={},
            name="name",
        )
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.endpoints.deployments.create(
            endpoint_id="endpointId",
            project_id="projectId",
            autoscaling={
                "max_replicas": 0,
                "min_replicas": 0,
                "scale_down_window": "-160513s",
                "scale_to_zero_window": "-160513s",
                "scale_up_window": "-160513s",
                "scaling_metrics": [
                    {
                        "name": "name",
                        "target": 0,
                        "type": "METRIC_TARGET_TYPE_VALUE",
                        "percentile": "percentile",
                    }
                ],
            },
            name="name",
            validate_only=True,
            config="config",
            config_id="configId",
            enable_lora=True,
            model="model",
            model_id="modelId",
            model_revision_id="modelRevisionId",
            placement={
                "inline": {
                    "constraint": "ENFORCEMENT_REQUIRED",
                    "regions": ["string"],
                }
            },
        )
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.deployments.with_raw_response.create(
            endpoint_id="endpointId",
            project_id="projectId",
            autoscaling={},
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.deployments.with_streaming_response.create(
            endpoint_id="endpointId",
            project_id="projectId",
            autoscaling={},
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(EndpointDeployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.create(
                endpoint_id="endpointId",
                project_id="",
                autoscaling={},
                name="name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.create(
                endpoint_id="",
                project_id="projectId",
                autoscaling={},
                name="name",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.endpoints.deployments.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.deployments.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.deployments.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(EndpointDeployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.retrieve(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.retrieve(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.endpoints.deployments.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.endpoints.deployments.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            update_mask="updateMask",
            autoscaling={
                "max_replicas": 0,
                "min_replicas": 0,
                "scale_down_window": "-160513s",
                "scale_to_zero_window": "-160513s",
                "scale_up_window": "-160513s",
                "scaling_metrics": [
                    {
                        "name": "name",
                        "target": 0,
                        "type": "METRIC_TARGET_TYPE_VALUE",
                        "percentile": "percentile",
                    }
                ],
            },
            etag="etag",
            name="name",
        )
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.deployments.with_raw_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(EndpointDeployment, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.deployments.with_streaming_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(EndpointDeployment, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.update(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.update(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.update(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.endpoints.deployments.list(
            endpoint_id="endpointId",
            project_id="projectId",
        )
        assert_matches_type(AsyncCursorPagination[EndpointDeployment], deployment, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.endpoints.deployments.list(
            endpoint_id="endpointId",
            project_id="projectId",
            after="after",
            filter="filter",
            limit=0,
            order_by="orderBy",
        )
        assert_matches_type(AsyncCursorPagination[EndpointDeployment], deployment, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.deployments.with_raw_response.list(
            endpoint_id="endpointId",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(AsyncCursorPagination[EndpointDeployment], deployment, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.deployments.with_streaming_response.list(
            endpoint_id="endpointId",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(AsyncCursorPagination[EndpointDeployment], deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.list(
                endpoint_id="endpointId",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.list(
                endpoint_id="",
                project_id="projectId",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.endpoints.deployments.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )
        assert_matches_type(DeploymentDeleteResponse, deployment, path=["response"])

    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.endpoints.deployments.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            etag="etag",
        )
        assert_matches_type(DeploymentDeleteResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.deployments.with_raw_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeploymentDeleteResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.deployments.with_streaming_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeploymentDeleteResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.delete(
                id="id",
                project_id="",
                endpoint_id="endpointId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.deployments.with_raw_response.delete(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
            )
