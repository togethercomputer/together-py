# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.pagination import SyncCursorPagination, AsyncCursorPagination
from together.types.beta.endpoints.shadow_experiments import (
    TargetDeleteResponse,
    ShadowExperimentTarget,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTargets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        target = client.beta.endpoints.shadow_experiments.targets.create(
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            name="name",
            target_deployment_id="targetDeploymentId",
        )
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        target = client.beta.endpoints.shadow_experiments.targets.create(
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            name="name",
            target_deployment_id="targetDeploymentId",
            description="description",
        )
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.endpoints.shadow_experiments.targets.with_raw_response.create(
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            name="name",
            target_deployment_id="targetDeploymentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.endpoints.shadow_experiments.targets.with_streaming_response.create(
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            name="name",
            target_deployment_id="targetDeploymentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = response.parse()
            assert_matches_type(ShadowExperimentTarget, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.create(
                project_id="",
                endpoint_id="endpointId",
                experiment_id="experimentId",
                name="name",
                target_deployment_id="targetDeploymentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.create(
                project_id="projectId",
                endpoint_id="",
                experiment_id="experimentId",
                name="name",
                target_deployment_id="targetDeploymentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `experiment_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.create(
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="",
                name="name",
                target_deployment_id="targetDeploymentId",
            )

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        target = client.beta.endpoints.shadow_experiments.targets.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        )
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.endpoints.shadow_experiments.targets.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.endpoints.shadow_experiments.targets.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = response.parse()
            assert_matches_type(ShadowExperimentTarget, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.retrieve(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                experiment_id="experimentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="",
                experiment_id="experimentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `experiment_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.retrieve(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="experimentId",
            )

    @parametrize
    def test_method_update(self, client: Together) -> None:
        target = client.beta.endpoints.shadow_experiments.targets.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            update_mask="updateMask",
        )
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Together) -> None:
        target = client.beta.endpoints.shadow_experiments.targets.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            update_mask="updateMask",
            description="description",
            etag="etag",
            name="name",
            target_deployment_id="targetDeploymentId",
        )
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Together) -> None:
        response = client.beta.endpoints.shadow_experiments.targets.with_raw_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            update_mask="updateMask",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Together) -> None:
        with client.beta.endpoints.shadow_experiments.targets.with_streaming_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            update_mask="updateMask",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = response.parse()
            assert_matches_type(ShadowExperimentTarget, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.update(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                experiment_id="experimentId",
                update_mask="updateMask",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.update(
                id="id",
                project_id="projectId",
                endpoint_id="",
                experiment_id="experimentId",
                update_mask="updateMask",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `experiment_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.update(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="",
                update_mask="updateMask",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.update(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="experimentId",
                update_mask="updateMask",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        target = client.beta.endpoints.shadow_experiments.targets.list(
            endpoint_id="endpointId",
            experiment_id="experimentId",
            project_id="projectId",
        )
        assert_matches_type(SyncCursorPagination[ShadowExperimentTarget], target, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        target = client.beta.endpoints.shadow_experiments.targets.list(
            endpoint_id="endpointId",
            experiment_id="experimentId",
            project_id="projectId",
            after="after",
            limit=0,
        )
        assert_matches_type(SyncCursorPagination[ShadowExperimentTarget], target, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.endpoints.shadow_experiments.targets.with_raw_response.list(
            endpoint_id="endpointId",
            experiment_id="experimentId",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(SyncCursorPagination[ShadowExperimentTarget], target, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.endpoints.shadow_experiments.targets.with_streaming_response.list(
            endpoint_id="endpointId",
            experiment_id="experimentId",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = response.parse()
            assert_matches_type(SyncCursorPagination[ShadowExperimentTarget], target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.list(
                endpoint_id="endpointId",
                experiment_id="experimentId",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.list(
                endpoint_id="",
                experiment_id="experimentId",
                project_id="projectId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `experiment_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.list(
                endpoint_id="endpointId",
                experiment_id="",
                project_id="projectId",
            )

    @parametrize
    def test_method_delete(self, client: Together) -> None:
        target = client.beta.endpoints.shadow_experiments.targets.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        )
        assert_matches_type(TargetDeleteResponse, target, path=["response"])

    @parametrize
    def test_method_delete_with_all_params(self, client: Together) -> None:
        target = client.beta.endpoints.shadow_experiments.targets.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            etag="etag",
        )
        assert_matches_type(TargetDeleteResponse, target, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Together) -> None:
        response = client.beta.endpoints.shadow_experiments.targets.with_raw_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = response.parse()
        assert_matches_type(TargetDeleteResponse, target, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Together) -> None:
        with client.beta.endpoints.shadow_experiments.targets.with_streaming_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = response.parse()
            assert_matches_type(TargetDeleteResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.delete(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                experiment_id="experimentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="",
                experiment_id="experimentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `experiment_id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.shadow_experiments.targets.with_raw_response.delete(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="experimentId",
            )


class TestAsyncTargets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        target = await async_client.beta.endpoints.shadow_experiments.targets.create(
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            name="name",
            target_deployment_id="targetDeploymentId",
        )
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        target = await async_client.beta.endpoints.shadow_experiments.targets.create(
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            name="name",
            target_deployment_id="targetDeploymentId",
            description="description",
        )
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.create(
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            name="name",
            target_deployment_id="targetDeploymentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.shadow_experiments.targets.with_streaming_response.create(
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            name="name",
            target_deployment_id="targetDeploymentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = await response.parse()
            assert_matches_type(ShadowExperimentTarget, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.create(
                project_id="",
                endpoint_id="endpointId",
                experiment_id="experimentId",
                name="name",
                target_deployment_id="targetDeploymentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.create(
                project_id="projectId",
                endpoint_id="",
                experiment_id="experimentId",
                name="name",
                target_deployment_id="targetDeploymentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `experiment_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.create(
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="",
                name="name",
                target_deployment_id="targetDeploymentId",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        target = await async_client.beta.endpoints.shadow_experiments.targets.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        )
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.shadow_experiments.targets.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = await response.parse()
            assert_matches_type(ShadowExperimentTarget, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.retrieve(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                experiment_id="experimentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="",
                experiment_id="experimentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `experiment_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.retrieve(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.retrieve(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="experimentId",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncTogether) -> None:
        target = await async_client.beta.endpoints.shadow_experiments.targets.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            update_mask="updateMask",
        )
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncTogether) -> None:
        target = await async_client.beta.endpoints.shadow_experiments.targets.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            update_mask="updateMask",
            description="description",
            etag="etag",
            name="name",
            target_deployment_id="targetDeploymentId",
        )
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            update_mask="updateMask",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(ShadowExperimentTarget, target, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.shadow_experiments.targets.with_streaming_response.update(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            update_mask="updateMask",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = await response.parse()
            assert_matches_type(ShadowExperimentTarget, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.update(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                experiment_id="experimentId",
                update_mask="updateMask",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.update(
                id="id",
                project_id="projectId",
                endpoint_id="",
                experiment_id="experimentId",
                update_mask="updateMask",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `experiment_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.update(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="",
                update_mask="updateMask",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.update(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="experimentId",
                update_mask="updateMask",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        target = await async_client.beta.endpoints.shadow_experiments.targets.list(
            endpoint_id="endpointId",
            experiment_id="experimentId",
            project_id="projectId",
        )
        assert_matches_type(AsyncCursorPagination[ShadowExperimentTarget], target, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        target = await async_client.beta.endpoints.shadow_experiments.targets.list(
            endpoint_id="endpointId",
            experiment_id="experimentId",
            project_id="projectId",
            after="after",
            limit=0,
        )
        assert_matches_type(AsyncCursorPagination[ShadowExperimentTarget], target, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.list(
            endpoint_id="endpointId",
            experiment_id="experimentId",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(AsyncCursorPagination[ShadowExperimentTarget], target, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.shadow_experiments.targets.with_streaming_response.list(
            endpoint_id="endpointId",
            experiment_id="experimentId",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = await response.parse()
            assert_matches_type(AsyncCursorPagination[ShadowExperimentTarget], target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.list(
                endpoint_id="endpointId",
                experiment_id="experimentId",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.list(
                endpoint_id="",
                experiment_id="experimentId",
                project_id="projectId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `experiment_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.list(
                endpoint_id="endpointId",
                experiment_id="",
                project_id="projectId",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncTogether) -> None:
        target = await async_client.beta.endpoints.shadow_experiments.targets.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        )
        assert_matches_type(TargetDeleteResponse, target, path=["response"])

    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncTogether) -> None:
        target = await async_client.beta.endpoints.shadow_experiments.targets.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
            etag="etag",
        )
        assert_matches_type(TargetDeleteResponse, target, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        target = await response.parse()
        assert_matches_type(TargetDeleteResponse, target, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.shadow_experiments.targets.with_streaming_response.delete(
            id="id",
            project_id="projectId",
            endpoint_id="endpointId",
            experiment_id="experimentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            target = await response.parse()
            assert_matches_type(TargetDeleteResponse, target, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.delete(
                id="id",
                project_id="",
                endpoint_id="endpointId",
                experiment_id="experimentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="",
                experiment_id="experimentId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `experiment_id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.delete(
                id="id",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.shadow_experiments.targets.with_raw_response.delete(
                id="",
                project_id="projectId",
                endpoint_id="endpointId",
                experiment_id="experimentId",
            )
