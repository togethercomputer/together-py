from __future__ import annotations

import os
import json
import base64
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from tests.cli.utils import CliRunner

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


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


def _remediation_body(remediation_id: str = "rem-1", **overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": remediation_id,
        "cluster_id": "c1",
        "instance_id": "i1",
        "mode": "REMEDIATION_MODE_VM_ONLY",
        "state": "PENDING_APPROVAL",
        "trigger": "REMEDIATION_TRIGGER_AUTOMATED",
        "reason": "health check failed",
    }
    body.update(overrides)
    return body


def _remediation_list_body(*remediations: dict[str, Any]) -> dict[str, Any]:
    return {
        "has_next": False,
        "next_page_token": "",
        "remediations": list(remediations),
    }


class TestBetaClustersList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_table(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(
                200,
                json={"clusters": [_cluster_body("a", "alpha"), _cluster_body("b", "beta")]},
            )
        )
        result = cli_runner.invoke(["beta", "clusters", "list"])
        assert "a" in result.output
        assert "alpha" in result.output
        assert "b" in result.output
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        payload = {"clusters": [_cluster_body()]}
        respx_mock.get("/compute/clusters").mock(return_value=httpx.Response(200, json=payload))
        result = cli_runner.invoke(["beta", "clusters", "list", "--json"])
        assert json.loads(result.output) == payload
        assert result.exit_code == 0


class TestBetaClustersListRegions:
    @pytest.mark.respx(base_url=base_url)
    def test_list_regions_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/compute/regions").mock(return_value=httpx.Response(200, json=_REGIONS_BODY))
        result = cli_runner.invoke(["beta", "clusters", "list-regions", "--json"])
        assert json.loads(result.output) == _REGIONS_BODY
        assert result.exit_code == 0


class TestBetaClustersRetrieve:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        c = _cluster_body()
        respx_mock.get("/compute/clusters/cluster-1").mock(return_value=httpx.Response(200, json=c))
        result = cli_runner.invoke(["beta", "clusters", "retrieve", "cluster-1", "--json"])
        assert json.loads(result.output) == c
        assert result.exit_code == 0


class TestBetaClustersCreate:
    @pytest.mark.respx(base_url=base_url)
    def test_create_non_interactive_posts_expected_body(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        created = _cluster_body("new-id", "together-py-testing-suite")
        route = respx_mock.post("/compute/clusters").mock(return_value=httpx.Response(200, json=created))
        result = cli_runner.invoke(
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
        assert "new-id" in result.output
        raw = cast(Call, route.calls[0]).request.content.decode()
        body = json.loads(raw)
        assert body["cluster_name"] == "together-py-testing-suite"
        assert body["volume_id"] == "vol-attach"
        assert body["num_gpus"] == 8
        assert body["billing_type"] == "ON_DEMAND"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_create_accepts_new_cluster_params(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        created = _cluster_body("new-id", "scheduled")
        route = respx_mock.post("/compute/clusters").mock(return_value=httpx.Response(200, json=created))
        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "create",
                "--non-interactive",
                "--cluster-type",
                "SLURM",
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
                "SCHEDULED_CAPACITY",
                "--name",
                "scheduled",
                "--auto-scale",
                "--auto-scale-max-gpus",
                "16",
                "--capacity-pool-id",
                "pool-1",
                "--install-traefik",
                "--num-capacity-pool-gpus",
                "8",
                "--num-preemptible-gpus",
                "8",
                "--num-reserved-gpus",
                "8",
                "--project-id",
                "proj-1",
                "--reservation-start-time",
                "2026-06-01T00:00:00Z",
                "--reservation-end-time",
                "2026-06-02T00:00:00Z",
                "--slurm-image",
                "slurm:latest",
                "--slurm-shm-size-gib",
                "32",
            ],
        )

        body = json.loads(cast(Call, route.calls[0]).request.content.decode())
        assert body["billing_type"] == "SCHEDULED_CAPACITY"
        assert body["auto_scale"] is True
        assert body["auto_scale_max_gpus"] == 16
        assert body["capacity_pool_id"] == "pool-1"
        assert "gpu_node_failover_enabled" not in body
        assert body["install_traefik"] is True
        assert body["num_capacity_pool_gpus"] == 8
        assert body["num_preemptible_gpus"] == 8
        assert body["num_reserved_gpus"] == 8
        assert body["project_id"] == "proj-1"
        assert body["reservation_start_time"] == "2026-06-01T00:00:00Z"
        assert body["reservation_end_time"] == "2026-06-02T00:00:00Z"
        assert body["slurm_image"] == "slurm:latest"
        assert body["slurm_shm_size_gib"] == 32
        assert result.exit_code == 0


class TestBetaClustersUpdate:
    @pytest.mark.respx(base_url=base_url)
    def test_update_json_triggers_put_and_second_get(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        updated = _cluster_body("c1", num_gpus=16, cluster_type="SLURM")
        put = respx_mock.put("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=updated))
        get = respx_mock.get("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=updated))
        result = cli_runner.invoke(
            ["beta", "clusters", "update", "c1", "--num-gpus", "16", "--cluster-type", "SLURM", "--json"],
        )
        assert put.calls
        assert get.calls
        assert json.loads(result.output)["num_gpus"] == 16
        put_body = json.loads(cast(Call, put.calls[0]).request.content.decode())
        assert put_body["num_gpus"] == 16
        assert put_body["cluster_type"] == "SLURM"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_update_accepts_new_cluster_params(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        updated = _cluster_body("c1", num_gpus=16)
        put = respx_mock.put("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=updated))
        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "update",
                "c1",
                "--num-preemptible-gpus",
                "8",
                "--num-reserved-gpus",
                "16",
                "--reservation-end-time",
                "2026-06-02T00:00:00Z",
            ],
        )

        put_body = json.loads(cast(Call, put.calls[0]).request.content.decode())
        assert put_body["num_preemptible_gpus"] == 8
        assert put_body["num_reserved_gpus"] == 16
        assert put_body["reservation_end_time"] == "2026-06-02T00:00:00Z"
        assert result.exit_code == 0


class TestBetaClustersDelete:
    @pytest.mark.respx(base_url=base_url)
    def test_delete_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.delete("/compute/clusters/c-del").mock(
            return_value=httpx.Response(200, json={"cluster_id": "c-del"})
        )
        result = cli_runner.invoke(["beta", "clusters", "delete", "c-del", "--json"])
        assert json.loads(result.output) == {"cluster_id": "c-del"}
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_delete_confirm_yes(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        c = _cluster_body("c1", "to-delete")
        respx_mock.get("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=c))
        respx_mock.delete("/compute/clusters/c1").mock(return_value=httpx.Response(200, json={"cluster_id": "c1"}))
        result = cli_runner.invoke(["beta", "clusters", "delete", "c1"], input="y\n")
        assert "Deleted" in result.output
        assert result.exit_code == 0


class TestBetaClustersGetCredentials:
    @pytest.mark.respx(base_url=base_url)
    def test_get_credentials_stdout(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        cfg = "apiVersion: v1\nkind: Config\n"
        c = _cluster_body(kube_config=base64.b64encode(cfg.encode()).decode("ascii"))
        respx_mock.get("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=c))
        result = cli_runner.invoke(["beta", "clusters", "get-credentials", "c1", "--file", "-"])
        assert result.output.strip() == cfg.strip()
        assert result.exit_code == 0


class TestBetaClustersStorage:
    @pytest.mark.respx(base_url=base_url)
    def test_storage_list_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        payload = {"volumes": [_VOLUME_BODY]}
        respx_mock.get("/compute/clusters/storage/volumes").mock(return_value=httpx.Response(200, json=payload))
        result = cli_runner.invoke(["beta", "clusters", "storage", "list", "--json"])
        assert json.loads(result.output) == payload
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_storage_create_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.post("/compute/clusters/storage/volumes").mock(
            return_value=httpx.Response(200, json=_VOLUME_BODY)
        )
        result = cli_runner.invoke(
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
                "--is-lifecycle-independent",
                "--json",
            ],
        )
        out = json.loads(result.output)
        assert out["volume_id"] == "vol-1"
        raw = cast(Call, route.calls[0]).request.content.decode()
        assert json.loads(raw) == {
            "region": "us-east-1",
            "size_tib": 1,
            "volume_name": "test-volume",
            "is_lifecycle_independent": True,
        }
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_storage_update_allows_omitting_size(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.put("/compute/clusters/storage/volumes").mock(
            return_value=httpx.Response(200, json=_VOLUME_BODY)
        )
        result = cli_runner.invoke(["beta", "clusters", "storage", "update", "vol-1", "--json"])

        assert json.loads(cast(Call, route.calls[0]).request.content.decode()) == {"volume_id": "vol-1"}
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_storage_retrieve_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/compute/clusters/storage/volumes/vol-1").mock(
            return_value=httpx.Response(200, json=_VOLUME_BODY)
        )
        result = cli_runner.invoke(["beta", "clusters", "storage", "retrieve", "vol-1", "--json"])
        assert json.loads(result.output) == _VOLUME_BODY
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_storage_delete_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.delete("/compute/clusters/storage/volumes/vol-1").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        result = cli_runner.invoke(["beta", "clusters", "storage", "delete", "vol-1", "--json"])
        assert json.loads(result.output) == {"success": True}
        assert result.exit_code == 0


class TestBetaClustersRemediations:
    @pytest.mark.respx(base_url=base_url)
    def test_remediations_create_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.post("/compute/clusters/c1/instances/i1/remediations").mock(
            return_value=httpx.Response(200, json=_remediation_body("rem-created", state="PENDING"))
        )
        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "remediations",
                "create",
                "c1",
                "i1",
                "--mode",
                "VM_ONLY",
                "--reason",
                "node unhealthy",
                "--remediation-id",
                "rem-created",
                "--json",
            ],
        )

        assert json.loads(result.output)["id"] == "rem-created"
        request = cast(Call, route.calls[0]).request
        assert request.url.params["remediation_id"] == "rem-created"
        assert json.loads(request.content.decode()) == {
            "mode": "REMEDIATION_MODE_VM_ONLY",
            "reason": "node unhealthy",
        }
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_list_uses_wildcard_when_instance_id_omitted(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        payload = _remediation_list_body(_remediation_body())
        route = respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = cli_runner.invoke(["beta", "clusters", "remediations", "list", "c1", "--json"])

        assert json.loads(result.output) == payload
        assert cast(Call, route.calls[0]).request.url.path == "/compute/clusters/c1/instances/-/remediations"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_list_accepts_instance_id(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        payload = _remediation_list_body(_remediation_body())
        route = respx_mock.get("/compute/clusters/c1/instances/i1/remediations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = cli_runner.invoke(["beta", "clusters", "remediations", "list", "c1", "i1", "--json"])

        assert json.loads(result.output) == payload
        assert cast(Call, route.calls[0]).request.url.path == "/compute/clusters/c1/instances/i1/remediations"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_list_table_uses_instance_name(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        payload = _remediation_list_body(_remediation_body(instance_name="gpu-node-a"))
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=payload)
        )

        result = cli_runner.invoke(["beta", "clusters", "remediations", "list", "c1"])

        assert "gpu-node-a (i1)" in result.output
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_list_table_falls_back_to_instance_id(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        payload = _remediation_list_body(_remediation_body())
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=payload)
        )

        result = cli_runner.invoke(["beta", "clusters", "remediations", "list", "c1"])

        assert "i1" in result.output
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_list_accepts_filters(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        payload = _remediation_list_body(_remediation_body())
        route = respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "remediations",
                "list",
                "c1",
                "--mode",
                "VM_ONLY",
                "--mode",
                "REBOOT_VM",
                "--state",
                "PENDING_APPROVAL",
                "--trigger",
                "AUTOMATED",
                "--after",
                "next-token",
                "--json",
            ]
        )

        params = cast(Call, route.calls[0]).request.url.params
        assert params["mode"] == "REMEDIATION_MODE_VM_ONLY,REMEDIATION_MODE_REBOOT_VM"
        assert params["state"] == "PENDING_APPROVAL"
        assert params["trigger"] == "REMEDIATION_TRIGGER_AUTOMATED"
        assert params["page_token"] == "next-token"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_retrieve_resolves_cluster_and_instance(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        body = _remediation_body("rem-get", state="RUNNING")
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(200, json={"clusters": [_cluster_body("c1")]})
        )
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=_remediation_list_body(_remediation_body("rem-get")))
        )
        route = respx_mock.get("/compute/clusters/c1/instances/i1/remediations/rem-get").mock(
            return_value=httpx.Response(200, json=body)
        )

        result = cli_runner.invoke(["beta", "clusters", "remediations", "get", "rem-get", "--json"])

        assert json.loads(result.output) == body
        assert cast(Call, route.calls[0]).request.url.path == "/compute/clusters/c1/instances/i1/remediations/rem-get"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_approve_resolves_cluster_and_instance(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(200, json={"clusters": [_cluster_body("c1")]})
        )
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=_remediation_list_body(_remediation_body("rem-approve")))
        )
        route = respx_mock.post("/compute/clusters/c1/instances/i1/remediations/rem-approve/approve").mock(
            return_value=httpx.Response(200, json=_remediation_body("rem-approve", state="PENDING"))
        )

        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "remediations",
                "approve",
                "rem-approve",
                "--comment",
                "go",
                "--mode",
                "REBOOT_VM",
                "--json",
            ]
        )

        assert json.loads(result.output)["state"] == "PENDING"
        assert json.loads(cast(Call, route.calls[0]).request.content.decode()) == {
            "comment": "go",
            "mode": "REMEDIATION_MODE_REBOOT_VM",
        }
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_cancel_resolves_cluster_and_instance(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(200, json={"clusters": [_cluster_body("c1")]})
        )
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=_remediation_list_body(_remediation_body("rem-cancel")))
        )
        route = respx_mock.post("/compute/clusters/c1/instances/i1/remediations/rem-cancel/cancel").mock(
            return_value=httpx.Response(200, json=_remediation_body("rem-cancel", state="CANCELLED"))
        )

        result = cli_runner.invoke(["beta", "clusters", "remediations", "cancel", "rem-cancel", "--json"])

        assert json.loads(result.output)["state"] == "CANCELLED"
        assert route.calls
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_reject_resolves_cluster_and_instance(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(200, json={"clusters": [_cluster_body("c1")]})
        )
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=_remediation_list_body(_remediation_body("rem-reject")))
        )
        route = respx_mock.post("/compute/clusters/c1/instances/i1/remediations/rem-reject/reject").mock(
            return_value=httpx.Response(200, json=_remediation_body("rem-reject", state="CANCELLED"))
        )

        result = cli_runner.invoke(
            ["beta", "clusters", "remediations", "reject", "rem-reject", "--comment", "skip", "--json"]
        )

        assert json.loads(result.output)["state"] == "CANCELLED"
        assert json.loads(cast(Call, route.calls[0]).request.content.decode()) == {"comment": "skip"}
        assert result.exit_code == 0
