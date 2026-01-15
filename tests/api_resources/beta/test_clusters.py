# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta import (
    Cluster,
    ClusterListResponse,
    ClusterDeleteResponse,
    ClusterListRegionsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClusters:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        cluster = client.beta.clusters.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            driver_version="CUDA_12_5_555",
            gpu_type="H100_SXM",
            num_gpus=0,
            region="us-central-8",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        cluster = client.beta.clusters.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            driver_version="CUDA_12_5_555",
            gpu_type="H100_SXM",
            num_gpus=0,
            region="us-central-8",
            cluster_type="KUBERNETES",
            duration_days=0,
            shared_volume={
                "region": "region",
                "size_tib": 0,
                "volume_name": "volume_name",
            },
            volume_id="volume_id",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.clusters.with_raw_response.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            driver_version="CUDA_12_5_555",
            gpu_type="H100_SXM",
            num_gpus=0,
            region="us-central-8",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.clusters.with_streaming_response.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            driver_version="CUDA_12_5_555",
            gpu_type="H100_SXM",
            num_gpus=0,
            region="us-central-8",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(Cluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        cluster = client.beta.clusters.retrieve(
            "cluster_id",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.clusters.with_raw_response.retrieve(
            "cluster_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.clusters.with_streaming_response.retrieve(
            "cluster_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(Cluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.beta.clusters.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: Together) -> None:
        cluster = client.beta.clusters.update(
            cluster_id="cluster_id",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Together) -> None:
        cluster = client.beta.clusters.update(
            cluster_id="cluster_id",
            cluster_type="KUBERNETES",
            num_gpus=0,
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Together) -> None:
        response = client.beta.clusters.with_raw_response.update(
            cluster_id="cluster_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Together) -> None:
        with client.beta.clusters.with_streaming_response.update(
            cluster_id="cluster_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(Cluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.beta.clusters.with_raw_response.update(
                cluster_id="",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        cluster = client.beta.clusters.list()
        assert_matches_type(ClusterListResponse, cluster, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.clusters.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(ClusterListResponse, cluster, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.clusters.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(ClusterListResponse, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Together) -> None:
        cluster = client.beta.clusters.delete(
            "cluster_id",
        )
        assert_matches_type(ClusterDeleteResponse, cluster, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Together) -> None:
        response = client.beta.clusters.with_raw_response.delete(
            "cluster_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(ClusterDeleteResponse, cluster, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Together) -> None:
        with client.beta.clusters.with_streaming_response.delete(
            "cluster_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(ClusterDeleteResponse, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            client.beta.clusters.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_list_regions(self, client: Together) -> None:
        cluster = client.beta.clusters.list_regions()
        assert_matches_type(ClusterListRegionsResponse, cluster, path=["response"])

    @parametrize
    def test_raw_response_list_regions(self, client: Together) -> None:
        response = client.beta.clusters.with_raw_response.list_regions()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = response.parse()
        assert_matches_type(ClusterListRegionsResponse, cluster, path=["response"])

    @parametrize
    def test_streaming_response_list_regions(self, client: Together) -> None:
        with client.beta.clusters.with_streaming_response.list_regions() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = response.parse()
            assert_matches_type(ClusterListRegionsResponse, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClusters:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        cluster = await async_client.beta.clusters.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            driver_version="CUDA_12_5_555",
            gpu_type="H100_SXM",
            num_gpus=0,
            region="us-central-8",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        cluster = await async_client.beta.clusters.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            driver_version="CUDA_12_5_555",
            gpu_type="H100_SXM",
            num_gpus=0,
            region="us-central-8",
            cluster_type="KUBERNETES",
            duration_days=0,
            shared_volume={
                "region": "region",
                "size_tib": 0,
                "volume_name": "volume_name",
            },
            volume_id="volume_id",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.with_raw_response.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            driver_version="CUDA_12_5_555",
            gpu_type="H100_SXM",
            num_gpus=0,
            region="us-central-8",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.with_streaming_response.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            driver_version="CUDA_12_5_555",
            gpu_type="H100_SXM",
            num_gpus=0,
            region="us-central-8",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(Cluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        cluster = await async_client.beta.clusters.retrieve(
            "cluster_id",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.with_raw_response.retrieve(
            "cluster_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.with_streaming_response.retrieve(
            "cluster_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(Cluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.beta.clusters.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncTogether) -> None:
        cluster = await async_client.beta.clusters.update(
            cluster_id="cluster_id",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncTogether) -> None:
        cluster = await async_client.beta.clusters.update(
            cluster_id="cluster_id",
            cluster_type="KUBERNETES",
            num_gpus=0,
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.with_raw_response.update(
            cluster_id="cluster_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.with_streaming_response.update(
            cluster_id="cluster_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(Cluster, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.beta.clusters.with_raw_response.update(
                cluster_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        cluster = await async_client.beta.clusters.list()
        assert_matches_type(ClusterListResponse, cluster, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(ClusterListResponse, cluster, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(ClusterListResponse, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncTogether) -> None:
        cluster = await async_client.beta.clusters.delete(
            "cluster_id",
        )
        assert_matches_type(ClusterDeleteResponse, cluster, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.with_raw_response.delete(
            "cluster_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(ClusterDeleteResponse, cluster, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.with_streaming_response.delete(
            "cluster_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(ClusterDeleteResponse, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `cluster_id` but received ''"):
            await async_client.beta.clusters.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_list_regions(self, async_client: AsyncTogether) -> None:
        cluster = await async_client.beta.clusters.list_regions()
        assert_matches_type(ClusterListRegionsResponse, cluster, path=["response"])

    @parametrize
    async def test_raw_response_list_regions(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.with_raw_response.list_regions()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cluster = await response.parse()
        assert_matches_type(ClusterListRegionsResponse, cluster, path=["response"])

    @parametrize
    async def test_streaming_response_list_regions(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.clusters.with_streaming_response.list_regions() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cluster = await response.parse()
            assert_matches_type(ClusterListRegionsResponse, cluster, path=["response"])

        assert cast(Any, response.is_closed) is True
