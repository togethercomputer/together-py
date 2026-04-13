from __future__ import annotations

import os
import json
import base64
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call
from click.testing import CliRunner

from together.lib.cli import main

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"
_ENV = {"TOGETHER_BASE_URL": base_url, "TOGETHER_API_KEY": API_KEY}


def _cluster_body(cluster_id: str = "cluster-1", name: str = "my-cluster", **overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "cluster_id": cluster_id,
        "cluster_name": name,
        "cluster_type": "KUBERNETES",
        "control_plane_nodes": [],
        "driver_version": "CUDA_12_6_565",
        "duration_hours": 24,
        "gpu_type": "H100_SXM",
        "gpu_worker_nodes": [],
        "kube_config": base64.b64encode(b"").decode("ascii"),
        "num_gpus": 8,
        "region": "us-central-8",
        "status": "Ready",
        "volumes": [],
    }
    body.update(overrides)
    return body


_REGIONS_BODY = {
    "regions": [
        {
            "name": "us-central-8",
            "driver_versions": [{"cuda_version": "12.6", "nvidia_driver_version": "565"}],
            "supported_instance_types": ["H100_SXM"],
        }
    ]
}

_VOLUME_BODY = {
    "volume_id": "vol-1",
    "volume_name": "data",
    "size_tib": 2,
    "status": "available",
}


class TestBetaClustersList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_table(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(
                200,
                json={"clusters": [_cluster_body("a", "alpha"), _cluster_body("b", "beta")]},
            )
        )
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["beta", "clusters", "list"])
        assert result.exit_code == 0
        assert "a" in result.output
        assert "alpha" in result.output
        assert "b" in result.output

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter) -> None:
        payload = {"clusters": [_cluster_body()]}
        respx_mock.get("/compute/clusters").mock(return_value=httpx.Response(200, json=payload))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["beta", "clusters", "list", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == payload


class TestBetaClustersListRegions:
    @pytest.mark.respx(base_url=base_url)
    def test_list_regions_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/compute/regions").mock(return_value=httpx.Response(200, json=_REGIONS_BODY))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["beta", "clusters", "list-regions", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == _REGIONS_BODY


class TestBetaClustersRetrieve:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_json(self, respx_mock: MockRouter) -> None:
        c = _cluster_body()
        respx_mock.get("/compute/clusters/cluster-1").mock(return_value=httpx.Response(200, json=c))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["beta", "clusters", "retrieve", "cluster-1", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == c


class TestBetaClustersCreate:
    @pytest.mark.respx(base_url=base_url)
    def test_create_non_interactive_posts_expected_body(self, respx_mock: MockRouter) -> None:
        created = _cluster_body("new-id", "together-py-testing-suite")
        route = respx_mock.post("/compute/clusters").mock(return_value=httpx.Response(200, json=created))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(
            main,
            [
                "beta",
                "clusters",
                "create",
                "--non-interactive",
                "--cluster-type",
                "KUBERNETES",
                "--gpu-type",
                "H100_SXM",
                "--nvidia-driver-version",
                "565",
                "--cuda-version",
                "12.6",
                "--region",
                "us-central-8",
                "--num-gpus",
                "8",
                "--billing-type",
                "ON_DEMAND",
                "--name",
                "together-py-testing-suite",
                "--volume",
                "vol-attach",
            ],
        )
        assert result.exit_code == 0
        assert "new-id" in result.output
        raw = cast(Call, route.calls[0]).request.content.decode()
        body = json.loads(raw)
        assert body["cluster_name"] == "together-py-testing-suite"
        assert body["volume_id"] == "vol-attach"
        assert body["num_gpus"] == 8
        assert body["billing_type"] == "ON_DEMAND"


class TestBetaClustersUpdate:
    @pytest.mark.respx(base_url=base_url)
    def test_update_json_triggers_put_and_second_get(self, respx_mock: MockRouter) -> None:
        updated = _cluster_body("c1", num_gpus=16, cluster_type="SLURM")
        put = respx_mock.put("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=updated))
        get = respx_mock.get("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=updated))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(
            main,
            ["beta", "clusters", "update", "c1", "--num-gpus", "16", "--cluster-type", "SLURM", "--json"],
        )
        assert result.exit_code == 0
        assert put.calls
        assert get.calls
        assert json.loads(result.output)["num_gpus"] == 16
        put_body = json.loads(cast(Call, put.calls[0]).request.content.decode())
        assert put_body["num_gpus"] == 16
        assert put_body["cluster_type"] == "SLURM"


class TestBetaClustersDelete:
    @pytest.mark.respx(base_url=base_url)
    def test_delete_json(self, respx_mock: MockRouter) -> None:
        respx_mock.delete("/compute/clusters/c-del").mock(
            return_value=httpx.Response(200, json={"cluster_id": "c-del"})
        )
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["beta", "clusters", "delete", "c-del", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == {"cluster_id": "c-del"}

    @pytest.mark.respx(base_url=base_url)
    def test_delete_confirm_yes(self, respx_mock: MockRouter) -> None:
        c = _cluster_body("c1", "to-delete")
        respx_mock.get("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=c))
        respx_mock.delete("/compute/clusters/c1").mock(return_value=httpx.Response(200, json={"cluster_id": "c1"}))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["beta", "clusters", "delete", "c1"], input="y\n")
        assert result.exit_code == 0
        assert "Deleted" in result.output


class TestBetaClustersGetCredentials:
    @pytest.mark.respx(base_url=base_url)
    def test_get_credentials_stdout(self, respx_mock: MockRouter) -> None:
        cfg = "apiVersion: v1\nkind: Config\n"
        c = _cluster_body(kube_config=base64.b64encode(cfg.encode()).decode("ascii"))
        respx_mock.get("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=c))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["beta", "clusters", "get-credentials", "c1", "--file", "-"])
        assert result.exit_code == 0
        assert result.output.strip() == cfg.strip()


class TestBetaClustersStorage:
    @pytest.mark.respx(base_url=base_url)
    def test_storage_list_json(self, respx_mock: MockRouter) -> None:
        payload = {"volumes": [_VOLUME_BODY]}
        respx_mock.get("/compute/clusters/storage/volumes").mock(return_value=httpx.Response(200, json=payload))
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["beta", "clusters", "storage", "list", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == payload

    @pytest.mark.respx(base_url=base_url)
    def test_storage_create_json(self, respx_mock: MockRouter) -> None:
        route = respx_mock.post("/compute/clusters/storage/volumes").mock(
            return_value=httpx.Response(200, json=_VOLUME_BODY)
        )
        runner = CliRunner(env=_ENV)
        result = runner.invoke(
            main,
            [
                "beta",
                "clusters",
                "storage",
                "create",
                "--region",
                "us-east-1",
                "--size-tib",
                "1",
                "--volume-name",
                "test-volume",
                "--json",
            ],
        )
        assert result.exit_code == 0
        out = json.loads(result.output)
        assert out["volume_id"] == "vol-1"
        raw = cast(Call, route.calls[0]).request.content.decode()
        assert json.loads(raw) == {"region": "us-east-1", "size_tib": 1, "volume_name": "test-volume"}

    @pytest.mark.respx(base_url=base_url)
    def test_storage_retrieve_json(self, respx_mock: MockRouter) -> None:
        respx_mock.get("/compute/clusters/storage/volumes/vol-1").mock(
            return_value=httpx.Response(200, json=_VOLUME_BODY)
        )
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["beta", "clusters", "storage", "retrieve", "vol-1", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == _VOLUME_BODY

    @pytest.mark.respx(base_url=base_url)
    def test_storage_delete_json(self, respx_mock: MockRouter) -> None:
        respx_mock.delete("/compute/clusters/storage/volumes/vol-1").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        runner = CliRunner(env=_ENV)
        result = runner.invoke(main, ["beta", "clusters", "storage", "delete", "vol-1", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output) == {"success": True}
