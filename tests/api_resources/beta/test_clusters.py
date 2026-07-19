# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together._utils import parse_datetime
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
            cuda_version="cuda_version",
            gpu_type="H100_SXM",
            num_gpus=0,
            nvidia_driver_version="nvidia_driver_version",
            region="region",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        cluster = client.beta.clusters.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            cuda_version="cuda_version",
            gpu_type="H100_SXM",
            num_gpus=0,
            nvidia_driver_version="nvidia_driver_version",
            region="region",
            acceptance_tests_params={
                "dcgm_diag_level": "DCGM_DIAG_LEVEL_SHORT",
                "dcgm_diag_skipped": True,
                "enabled": True,
                "gpu_burn_duration": 0,
                "gpu_burn_skipped": True,
                "nccl_multi_node_skipped": True,
                "nccl_single_node_skipped": True,
                "storage_skipped": True,
            },
            add_ons=[
                {
                    "add_on_type": "add_on_type",
                    "name": "name",
                    "config": {
                        "dashboard": {"enabled": True},
                        "ingress": {"enabled": True},
                        "torchpass": {"enabled": True},
                    },
                }
            ],
            auto_scale=True,
            auto_scale_max_gpus=0,
            auto_scaled=True,
            capacity_pool_id="capacity_pool_id",
            cluster_config={
                "load_balancer": "NONE",
                "gpu_operator_version": "gpu_operator_version",
                "ingress": {"enabled": True},
                "jumphost_enabled": True,
                "kubernetes_dashboard_enabled": True,
                "network_operator_version": "network_operator_version",
                "observability": {"enabled": True},
                "slurm_startup_scripts": {
                    "controller_epilog": "controller_epilog",
                    "controller_prolog": "controller_prolog",
                    "extra_slurm_conf": "extra_slurm_conf",
                    "login_init_script": "login_init_script",
                    "nodeset_init_script": "nodeset_init_script",
                    "worker_epilog": "worker_epilog",
                    "worker_prolog": "worker_prolog",
                },
                "ssh_ca_enabled": True,
            },
            cluster_type="KUBERNETES",
            duration_days=0,
            install_traefik=True,
            num_capacity_pool_gpus=0,
            num_preemptible_gpus=0,
            num_reserved_gpus=0,
            oidc_config={
                "client_id": "client_id",
                "group_claim": "group_claim",
                "group_prefix": "group_prefix",
                "issuer_url": "issuer_url",
                "username_claim": "username_claim",
                "username_prefix": "username_prefix",
                "ca_cert": "ca_cert",
            },
            project_id="project_id",
            reservation_end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            reservation_start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            shared_volume={
                "region": "region",
                "size_tib": 0,
                "volume_name": "volume_name",
                "is_lifecycle_independent": True,
                "project_id": "project_id",
            },
            slurm_image="slurm_image",
            slurm_shm_size_gib=0,
            volume_id="volume_id",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.clusters.with_raw_response.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            cuda_version="cuda_version",
            gpu_type="H100_SXM",
            num_gpus=0,
            nvidia_driver_version="nvidia_driver_version",
            region="region",
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
            cuda_version="cuda_version",
            gpu_type="H100_SXM",
            num_gpus=0,
            nvidia_driver_version="nvidia_driver_version",
            region="region",
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
            add_ons=[
                {
                    "name": "name",
                    "config": {
                        "dashboard": {"enabled": True},
                        "ingress": {"enabled": True},
                        "torchpass": {"enabled": True},
                    },
                }
            ],
            cluster_config={
                "load_balancer": "NONE",
                "gpu_operator_version": "gpu_operator_version",
                "ingress": {"enabled": True},
                "jumphost_enabled": True,
                "kubernetes_dashboard_enabled": True,
                "network_operator_version": "network_operator_version",
                "observability": {"enabled": True},
                "slurm_startup_scripts": {
                    "controller_epilog": "controller_epilog",
                    "controller_prolog": "controller_prolog",
                    "extra_slurm_conf": "extra_slurm_conf",
                    "login_init_script": "login_init_script",
                    "nodeset_init_script": "nodeset_init_script",
                    "worker_epilog": "worker_epilog",
                    "worker_prolog": "worker_prolog",
                },
                "ssh_ca_enabled": True,
            },
            cluster_type="KUBERNETES",
            num_capacity_pool_gpus=0,
            num_gpus=0,
            num_preemptible_gpus=0,
            num_reserved_gpus=0,
            reservation_end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
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
    def test_method_list_with_all_params(self, client: Together) -> None:
        cluster = client.beta.clusters.list(
            project_id="projectId",
        )
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
            cuda_version="cuda_version",
            gpu_type="H100_SXM",
            num_gpus=0,
            nvidia_driver_version="nvidia_driver_version",
            region="region",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        cluster = await async_client.beta.clusters.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            cuda_version="cuda_version",
            gpu_type="H100_SXM",
            num_gpus=0,
            nvidia_driver_version="nvidia_driver_version",
            region="region",
            acceptance_tests_params={
                "dcgm_diag_level": "DCGM_DIAG_LEVEL_SHORT",
                "dcgm_diag_skipped": True,
                "enabled": True,
                "gpu_burn_duration": 0,
                "gpu_burn_skipped": True,
                "nccl_multi_node_skipped": True,
                "nccl_single_node_skipped": True,
                "storage_skipped": True,
            },
            add_ons=[
                {
                    "add_on_type": "add_on_type",
                    "name": "name",
                    "config": {
                        "dashboard": {"enabled": True},
                        "ingress": {"enabled": True},
                        "torchpass": {"enabled": True},
                    },
                }
            ],
            auto_scale=True,
            auto_scale_max_gpus=0,
            auto_scaled=True,
            capacity_pool_id="capacity_pool_id",
            cluster_config={
                "load_balancer": "NONE",
                "gpu_operator_version": "gpu_operator_version",
                "ingress": {"enabled": True},
                "jumphost_enabled": True,
                "kubernetes_dashboard_enabled": True,
                "network_operator_version": "network_operator_version",
                "observability": {"enabled": True},
                "slurm_startup_scripts": {
                    "controller_epilog": "controller_epilog",
                    "controller_prolog": "controller_prolog",
                    "extra_slurm_conf": "extra_slurm_conf",
                    "login_init_script": "login_init_script",
                    "nodeset_init_script": "nodeset_init_script",
                    "worker_epilog": "worker_epilog",
                    "worker_prolog": "worker_prolog",
                },
                "ssh_ca_enabled": True,
            },
            cluster_type="KUBERNETES",
            duration_days=0,
            install_traefik=True,
            num_capacity_pool_gpus=0,
            num_preemptible_gpus=0,
            num_reserved_gpus=0,
            oidc_config={
                "client_id": "client_id",
                "group_claim": "group_claim",
                "group_prefix": "group_prefix",
                "issuer_url": "issuer_url",
                "username_claim": "username_claim",
                "username_prefix": "username_prefix",
                "ca_cert": "ca_cert",
            },
            project_id="project_id",
            reservation_end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            reservation_start_time=parse_datetime("2019-12-27T18:11:19.117Z"),
            shared_volume={
                "region": "region",
                "size_tib": 0,
                "volume_name": "volume_name",
                "is_lifecycle_independent": True,
                "project_id": "project_id",
            },
            slurm_image="slurm_image",
            slurm_shm_size_gib=0,
            volume_id="volume_id",
        )
        assert_matches_type(Cluster, cluster, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.clusters.with_raw_response.create(
            billing_type="RESERVED",
            cluster_name="cluster_name",
            cuda_version="cuda_version",
            gpu_type="H100_SXM",
            num_gpus=0,
            nvidia_driver_version="nvidia_driver_version",
            region="region",
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
            cuda_version="cuda_version",
            gpu_type="H100_SXM",
            num_gpus=0,
            nvidia_driver_version="nvidia_driver_version",
            region="region",
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
            add_ons=[
                {
                    "name": "name",
                    "config": {
                        "dashboard": {"enabled": True},
                        "ingress": {"enabled": True},
                        "torchpass": {"enabled": True},
                    },
                }
            ],
            cluster_config={
                "load_balancer": "NONE",
                "gpu_operator_version": "gpu_operator_version",
                "ingress": {"enabled": True},
                "jumphost_enabled": True,
                "kubernetes_dashboard_enabled": True,
                "network_operator_version": "network_operator_version",
                "observability": {"enabled": True},
                "slurm_startup_scripts": {
                    "controller_epilog": "controller_epilog",
                    "controller_prolog": "controller_prolog",
                    "extra_slurm_conf": "extra_slurm_conf",
                    "login_init_script": "login_init_script",
                    "nodeset_init_script": "nodeset_init_script",
                    "worker_epilog": "worker_epilog",
                    "worker_prolog": "worker_prolog",
                },
                "ssh_ca_enabled": True,
            },
            cluster_type="KUBERNETES",
            num_capacity_pool_gpus=0,
            num_gpus=0,
            num_preemptible_gpus=0,
            num_reserved_gpus=0,
            reservation_end_time=parse_datetime("2019-12-27T18:11:19.117Z"),
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
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        cluster = await async_client.beta.clusters.list(
            project_id="projectId",
        )
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
