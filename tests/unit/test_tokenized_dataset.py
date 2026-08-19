from __future__ import annotations

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
import io
import tarfile
import importlib
from typing import Any, cast
from pathlib import Path

import pytest
import zstandard
from respx import MockRouter
from datasets import Dataset, DatasetDict

from together import Together, AsyncTogether
from together.lib import tokenized_dataset


def _write_archive(tmp_path: Path, splits: dict[str, Dataset]) -> Path:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    for name, dataset in splits.items():
        dataset.save_to_disk(source_dir / name)

    tar_path = tmp_path / "datasets.tar"
    with tarfile.open(tar_path, "w") as archive:
        for name in splits:
            archive.add(source_dir / name, arcname=name)

    archive_path = tmp_path / "datasets.tar.zst"
    with tar_path.open("rb") as source, archive_path.open("wb") as target:
        zstandard.ZstdCompressor().copy_stream(source, target)
    return archive_path


def _write_member_archive(tmp_path: Path, member_name: str) -> Path:
    tar_path = tmp_path / "member.tar"
    content = b"unexpected"
    with tarfile.open(tar_path, "w") as archive:
        member = tarfile.TarInfo(member_name)
        member.size = len(content)
        archive.addfile(member, io.BytesIO(content))

    archive_path = tmp_path / "member.tar.zst"
    with tar_path.open("rb") as source, archive_path.open("wb") as target:
        zstandard.ZstdCompressor().copy_stream(source, target)
    return archive_path


def _mock_metadata(respx_mock: MockRouter, url: str, size: int = 100) -> None:
    respx_mock.get("https://api.example/fine-tunes/ft-test/download-tokenized-dataset").respond(
        json={
            "content_type": "application/zstd",
            "expires_at": "2026-08-19T10:00:00Z",
            "filename": "tokenized-datasets.tar.zst",
            "size": size,
            "url": url,
        }
    )


@pytest.mark.parametrize("include_validation", [False, True])
def test_load_archive(tmp_path: Path, include_validation: bool) -> None:
    splits = {"train_dataset": Dataset.from_dict({"input_ids": [[1, 2], [3, 4]]})}
    if include_validation:
        splits["eval_dataset"] = Dataset.from_dict({"input_ids": [[5, 6]]})

    result = tokenized_dataset._load_archive(_write_archive(tmp_path, splits))

    assert isinstance(result, DatasetDict)
    assert result["train"]["input_ids"] == [[1, 2], [3, 4]]
    if include_validation:
        assert result["validation"]["input_ids"] == [[5, 6]]
    else:
        assert "validation" not in result


@pytest.mark.parametrize(
    "member_name",
    ["../outside", r"train_dataset\..\outside", "other_dataset/state.json"],
)
def test_load_archive_rejects_unexpected_members(tmp_path: Path, member_name: str) -> None:
    with pytest.raises(ValueError, match="Unexpected tokenized dataset archive member"):
        tokenized_dataset._load_archive(_write_member_archive(tmp_path, member_name))


def test_load_archive_requires_train_split(tmp_path: Path) -> None:
    archive_path = _write_archive(
        tmp_path,
        {"eval_dataset": Dataset.from_dict({"input_ids": [[5, 6]]})},
    )

    with pytest.raises(ValueError, match="does not contain a train dataset"):
        tokenized_dataset._load_archive(archive_path)


def test_load_archive_limits_extracted_size(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    archive_path = _write_archive(
        tmp_path,
        {"train_dataset": Dataset.from_dict({"input_ids": [[1, 2]]})},
    )
    monkeypatch.setattr(tokenized_dataset, "_MAX_EXTRACTED_BYTES", 1)

    with pytest.raises(ValueError, match="too large after extraction"):
        tokenized_dataset._load_archive(archive_path)


def test_missing_datasets_extra_raises_runtime_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import_module = importlib.import_module

    def missing_datasets(name: str):
        if name == "datasets":
            raise ImportError("datasets is not installed")
        return import_module(name)

    monkeypatch.setattr(tokenized_dataset.importlib, "import_module", missing_datasets)

    with pytest.raises(RuntimeError, match=r"pip install together\[datasets\]"):
        tokenized_dataset._require_datasets()


def test_retrieve_requires_https() -> None:
    with pytest.raises(ValueError, match="must use HTTPS"):
        tokenized_dataset.retrieve_dataset("http://download.example/archive.tar.zst", expected_size=0)


def test_retrieve_rejects_insecure_redirect(respx_mock: MockRouter) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    redirect = respx_mock.get(url).respond(
        status_code=302,
        headers={"location": "http://insecure.example/tokenized-datasets.tar.zst"},
    )
    insecure_download = respx_mock.get("http://insecure.example/tokenized-datasets.tar.zst").respond(content=b"")

    with pytest.raises(ValueError, match="must use HTTPS"):
        tokenized_dataset.retrieve_dataset(url, expected_size=0)

    assert redirect.called
    assert not insecure_download.called


def test_retrieve_tokenized_dataset_returns_dataset(
    respx_mock: MockRouter,
    tmp_path: Path,
) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    archive_path = _write_archive(
        tmp_path,
        {"train_dataset": Dataset.from_dict({"input_ids": [[1, 2]]})},
    )
    archive_content = archive_path.read_bytes()
    _mock_metadata(respx_mock, url, len(archive_content))
    download = respx_mock.get(url).respond(content=archive_content)

    with Together(api_key="test", base_url="https://api.example") as client:
        result = client.fine_tuning.retrieve_tokenized_dataset("ft-test", return_dataset=True)

    assert result["train"]["input_ids"] == [[1, 2]]
    assert download.called
    assert "authorization" not in download.calls.last.request.headers


async def test_async_retrieve_tokenized_dataset_returns_dataset(
    respx_mock: MockRouter,
    tmp_path: Path,
) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    archive_path = _write_archive(
        tmp_path,
        {"train_dataset": Dataset.from_dict({"input_ids": [[1, 2]]})},
    )
    archive_content = archive_path.read_bytes()
    _mock_metadata(respx_mock, url, len(archive_content))
    download = respx_mock.get(url).respond(content=archive_content)

    async with AsyncTogether(api_key="test", base_url="https://api.example") as client:
        result = await client.fine_tuning.retrieve_tokenized_dataset("ft-test", return_dataset=True)

    assert result["train"]["input_ids"] == [[1, 2]]
    assert download.called
    assert "authorization" not in download.calls.last.request.headers


def test_retrieve_tokenized_dataset_returns_metadata_by_default(respx_mock: MockRouter) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    _mock_metadata(respx_mock, url)
    download = respx_mock.get(url).respond(content=b"not requested")

    with Together(api_key="test", base_url="https://api.example") as client:
        result = client.fine_tuning.retrieve_tokenized_dataset("ft-test")

    assert result.url == url
    assert not download.called


def test_retrieve_validates_download_size(respx_mock: MockRouter) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    _mock_metadata(respx_mock, url, size=10)
    respx_mock.get(url).respond(content=b"short")

    with Together(api_key="test", base_url="https://api.example") as client:
        with pytest.raises(ValueError, match="does not match remote file size"):
            client.fine_tuning.retrieve_tokenized_dataset("ft-test", return_dataset=True)


def test_retrieve_stops_oversized_download(respx_mock: MockRouter) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    _mock_metadata(respx_mock, url, size=2)
    respx_mock.get(url).respond(content=b"too large")

    with Together(api_key="test", base_url="https://api.example") as client:
        with pytest.raises(ValueError, match="exceeds the remote file size"):
            client.fine_tuning.retrieve_tokenized_dataset("ft-test", return_dataset=True)


def test_raw_retrieve_preserves_response_wrapper(respx_mock: MockRouter) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    _mock_metadata(respx_mock, url)
    download = respx_mock.get(url).respond(content=b"not requested")

    with Together(api_key="test", base_url="https://api.example") as client:
        response = client.fine_tuning.with_raw_response.retrieve_tokenized_dataset(
            "ft-test",
        )

    assert cast(Any, response.parse()).url == url
    assert not download.called


def test_streaming_retrieve_preserves_response_wrapper(respx_mock: MockRouter) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    _mock_metadata(respx_mock, url)
    download = respx_mock.get(url).respond(content=b"not requested")

    with Together(api_key="test", base_url="https://api.example") as client:
        with client.fine_tuning.with_streaming_response.retrieve_tokenized_dataset(
            "ft-test",
        ) as response:
            assert cast(Any, response.parse()).url == url

    assert not download.called


async def test_async_raw_retrieve_preserves_response_wrapper(respx_mock: MockRouter) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    _mock_metadata(respx_mock, url)
    download = respx_mock.get(url).respond(content=b"not requested")

    async with AsyncTogether(api_key="test", base_url="https://api.example") as client:
        response = await client.fine_tuning.with_raw_response.retrieve_tokenized_dataset(
            "ft-test",
        )

    assert cast(Any, await response.parse()).url == url
    assert not download.called


async def test_async_streaming_retrieve_preserves_response_wrapper(respx_mock: MockRouter) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    _mock_metadata(respx_mock, url)
    download = respx_mock.get(url).respond(content=b"not requested")

    async with AsyncTogether(api_key="test", base_url="https://api.example") as client:
        async with client.fine_tuning.with_streaming_response.retrieve_tokenized_dataset(
            "ft-test",
        ) as response:
            assert cast(Any, await response.parse()).url == url

    assert not download.called


def test_response_wrapper_rejects_return_dataset() -> None:
    with Together(api_key="test", base_url="https://api.example") as client:
        retrieve = cast(Any, client.fine_tuning.with_raw_response.retrieve_tokenized_dataset)
        with pytest.raises(TypeError, match="return_dataset"):
            retrieve(
                "ft-test",
                return_dataset=True,
            )
