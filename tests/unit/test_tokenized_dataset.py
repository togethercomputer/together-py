from __future__ import annotations

import io
import tarfile
import importlib
from pathlib import Path

import pytest
import zstandard
from datasets import Dataset, DatasetDict
from respx import MockRouter
from pytest_mock import MockerFixture

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


@pytest.mark.parametrize("member_name", ["../outside", "other_dataset/state.json"])
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


def test_missing_datasets_extra_raises_runtime_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import_module = importlib.import_module

    def missing_datasets(name: str):
        if name == "datasets":
            raise ImportError("datasets is not installed")
        return import_module(name)

    monkeypatch.setattr(tokenized_dataset.importlib, "import_module", missing_datasets)

    with pytest.raises(RuntimeError, match=r"pip install together\[datasets\]"):
        tokenized_dataset._require_datasets()


def test_retrieve_tokenized_dataset_returns_dataset(
    respx_mock: MockRouter,
    mocker: MockerFixture,
) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    respx_mock.get("https://api.example/fine-tunes/ft-test/download-tokenized-dataset").respond(
        json={
            "content_type": "application/zstd",
            "expires_at": "2026-08-19T10:00:00Z",
            "filename": "tokenized-datasets.tar.zst",
            "size": 100,
            "url": url,
        }
    )
    expected = DatasetDict({"train": Dataset.from_dict({"input_ids": [[1, 2]]})})
    retrieve = mocker.patch(
        "together.resources.fine_tuning._retrieve_tokenized_dataset",
        return_value=expected,
    )

    with Together(api_key="test", base_url="https://api.example") as client:
        result = client.fine_tuning.retrieve_tokenized_dataset("ft-test", return_dataset=True)

    assert result is expected
    retrieve.assert_called_once_with(url)


async def test_async_retrieve_tokenized_dataset_returns_dataset(
    respx_mock: MockRouter,
    mocker: MockerFixture,
) -> None:
    url = "https://download.example/tokenized-datasets.tar.zst"
    respx_mock.get("https://api.example/fine-tunes/ft-test/download-tokenized-dataset").respond(
        json={
            "content_type": "application/zstd",
            "expires_at": "2026-08-19T10:00:00Z",
            "filename": "tokenized-datasets.tar.zst",
            "size": 100,
            "url": url,
        }
    )
    expected = DatasetDict({"train": Dataset.from_dict({"input_ids": [[1, 2]]})})
    retrieve = mocker.patch(
        "together.resources.fine_tuning._async_retrieve_tokenized_dataset",
        return_value=expected,
    )

    async with AsyncTogether(api_key="test", base_url="https://api.example") as client:
        result = await client.fine_tuning.retrieve_tokenized_dataset("ft-test", return_dataset=True)

    assert result is expected
    retrieve.assert_awaited_once_with(url)
