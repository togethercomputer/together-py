# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta import (
    DeploymentListResponse,
    DeploymentCreateResponse,
    DeploymentUpdateResponse,
    DeploymentGetLogsResponse,
    DeploymentRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDeployments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        deployment = client.beta.deployments.create(
            gpu_type="h100-80gb",
            image="image",
            name="x",
        )
        assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        deployment = client.beta.deployments.create(
            gpu_type="h100-80gb",
            image="image",
            name="x",
            args=["string"],
            autoscaling={"foo": "string"},
            command=["string"],
            cpu=0.1,
            description="description",
            environment_variables=[
                {
                    "name": "name",
                    "value": "value",
                    "value_from_secret": "value_from_secret",
                }
            ],
            gpu_count=0,
            health_check_path="health_check_path",
            max_replicas=0,
            memory=0.1,
            min_replicas=0,
            port=0,
            storage=0,
            termination_grace_period_seconds=0,
            volumes=[
                {
                    "mount_path": "mount_path",
                    "name": "name",
                }
            ],
        )
        assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.deployments.with_raw_response.create(
            gpu_type="h100-80gb",
            image="image",
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.deployments.with_streaming_response.create(
            gpu_type="h100-80gb",
            image="image",
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        deployment = client.beta.deployments.retrieve(
            "id",
        )
        assert_matches_type(DeploymentRetrieveResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.deployments.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeploymentRetrieveResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.deployments.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeploymentRetrieveResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.deployments.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: Together) -> None:
        deployment = client.beta.deployments.update(
            id="id",
        )
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Together) -> None:
        deployment = client.beta.deployments.update(
            id="id",
            args=["string"],
            autoscaling={"foo": "string"},
            command=["string"],
            cpu=0.1,
            description="description",
            environment_variables=[
                {
                    "name": "name",
                    "value": "value",
                    "value_from_secret": "value_from_secret",
                }
            ],
            gpu_count=0,
            gpu_type="h100-80gb",
            health_check_path="health_check_path",
            image="image",
            max_replicas=0,
            memory=0.1,
            min_replicas=0,
            name="x",
            port=0,
            storage=0,
            termination_grace_period_seconds=0,
            volumes=[
                {
                    "mount_path": "mount_path",
                    "name": "name",
                }
            ],
        )
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Together) -> None:
        response = client.beta.deployments.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Together) -> None:
        with client.beta.deployments.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.deployments.with_raw_response.update(
                id="",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        deployment = client.beta.deployments.list()
        assert_matches_type(DeploymentListResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.deployments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeploymentListResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.deployments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeploymentListResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Together) -> None:
        deployment = client.beta.deployments.delete(
            "id",
        )
        assert_matches_type(object, deployment, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Together) -> None:
        response = client.beta.deployments.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(object, deployment, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Together) -> None:
        with client.beta.deployments.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(object, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.deployments.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_get_logs(self, client: Together) -> None:
        deployment = client.beta.deployments.get_logs(
            id="id",
        )
        assert_matches_type(DeploymentGetLogsResponse, deployment, path=["response"])

    @parametrize
    def test_method_get_logs_with_all_params(self, client: Together) -> None:
        deployment = client.beta.deployments.get_logs(
            id="id",
            follow=True,
            replica_id="replica_id",
        )
        assert_matches_type(DeploymentGetLogsResponse, deployment, path=["response"])

    @parametrize
    def test_raw_response_get_logs(self, client: Together) -> None:
        response = client.beta.deployments.with_raw_response.get_logs(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = response.parse()
        assert_matches_type(DeploymentGetLogsResponse, deployment, path=["response"])

    @parametrize
    def test_streaming_response_get_logs(self, client: Together) -> None:
        with client.beta.deployments.with_streaming_response.get_logs(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = response.parse()
            assert_matches_type(DeploymentGetLogsResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get_logs(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.deployments.with_raw_response.get_logs(
                id="",
            )


class TestAsyncDeployments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.deployments.create(
            gpu_type="h100-80gb",
            image="image",
            name="x",
        )
        assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.deployments.create(
            gpu_type="h100-80gb",
            image="image",
            name="x",
            args=["string"],
            autoscaling={"foo": "string"},
            command=["string"],
            cpu=0.1,
            description="description",
            environment_variables=[
                {
                    "name": "name",
                    "value": "value",
                    "value_from_secret": "value_from_secret",
                }
            ],
            gpu_count=0,
            health_check_path="health_check_path",
            max_replicas=0,
            memory=0.1,
            min_replicas=0,
            port=0,
            storage=0,
            termination_grace_period_seconds=0,
            volumes=[
                {
                    "mount_path": "mount_path",
                    "name": "name",
                }
            ],
        )
        assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.deployments.with_raw_response.create(
            gpu_type="h100-80gb",
            image="image",
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.deployments.with_streaming_response.create(
            gpu_type="h100-80gb",
            image="image",
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeploymentCreateResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.deployments.retrieve(
            "id",
        )
        assert_matches_type(DeploymentRetrieveResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.deployments.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeploymentRetrieveResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.deployments.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeploymentRetrieveResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.deployments.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.deployments.update(
            id="id",
        )
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.deployments.update(
            id="id",
            args=["string"],
            autoscaling={"foo": "string"},
            command=["string"],
            cpu=0.1,
            description="description",
            environment_variables=[
                {
                    "name": "name",
                    "value": "value",
                    "value_from_secret": "value_from_secret",
                }
            ],
            gpu_count=0,
            gpu_type="h100-80gb",
            health_check_path="health_check_path",
            image="image",
            max_replicas=0,
            memory=0.1,
            min_replicas=0,
            name="x",
            port=0,
            storage=0,
            termination_grace_period_seconds=0,
            volumes=[
                {
                    "mount_path": "mount_path",
                    "name": "name",
                }
            ],
        )
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.deployments.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.deployments.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeploymentUpdateResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.deployments.with_raw_response.update(
                id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.deployments.list()
        assert_matches_type(DeploymentListResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.deployments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeploymentListResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.deployments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeploymentListResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.deployments.delete(
            "id",
        )
        assert_matches_type(object, deployment, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.deployments.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(object, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.deployments.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(object, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.deployments.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_get_logs(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.deployments.get_logs(
            id="id",
        )
        assert_matches_type(DeploymentGetLogsResponse, deployment, path=["response"])

    @parametrize
    async def test_method_get_logs_with_all_params(self, async_client: AsyncTogether) -> None:
        deployment = await async_client.beta.deployments.get_logs(
            id="id",
            follow=True,
            replica_id="replica_id",
        )
        assert_matches_type(DeploymentGetLogsResponse, deployment, path=["response"])

    @parametrize
    async def test_raw_response_get_logs(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.deployments.with_raw_response.get_logs(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        deployment = await response.parse()
        assert_matches_type(DeploymentGetLogsResponse, deployment, path=["response"])

    @parametrize
    async def test_streaming_response_get_logs(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.deployments.with_streaming_response.get_logs(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            deployment = await response.parse()
            assert_matches_type(DeploymentGetLogsResponse, deployment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get_logs(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.deployments.with_raw_response.get_logs(
                id="",
            )
