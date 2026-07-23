from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import httpx
import respx
import pytest

from together import Together
from together.lib.resources import tokenized_dataset as td

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
API_KEY = "0000000000000000000000000000000000000000"


@pytest.fixture
def client() -> Together:
    return Together(base_url=base_url, api_key=API_KEY)


def _write_fake_member(path: Path, payload: str = "ok") -> None:
    path.mkdir(parents=True)
    (path / "marker.txt").write_text(payload, encoding="utf-8")


def _make_archive_bytes(tmp_path: Path, *, with_eval: bool = True) -> bytes:
    source = tmp_path / "source"
    _write_fake_member(source / "train_dataset", "train")
    if with_eval:
        _write_fake_member(source / "eval_dataset", "eval")
    return td.pack_tokenized_dataset_archive(source)


@respx.mock
def test_download_tokenized_dataset_unpacks_train_and_eval(client: Together, tmp_path: Path) -> None:
    pytest.importorskip("zstandard")
    archive = _make_archive_bytes(tmp_path, with_eval=True)
    presign_url = "https://r2.example/tokenized_datasets.tar.zst?sig=1"

    respx.get(f"{base_url}/fine-tunes/ft-abc/download-tokenized-dataset").mock(
        return_value=httpx.Response(
            200,
            json={
                "url": presign_url,
                "filename": "tokenized_datasets.tar.zst",
                "size": len(archive),
                "content_type": "application/zstd",
            },
        )
    )
    respx.get(presign_url).mock(return_value=httpx.Response(200, content=archive))

    out = tmp_path / "out"
    result = td.download_tokenized_dataset(client, "ft-abc", output_dir=out)

    assert result is None
    assert (out / "train_dataset" / "marker.txt").read_text(encoding="utf-8") == "train"
    assert (out / "eval_dataset" / "marker.txt").read_text(encoding="utf-8") == "eval"
    assert (out / ".ready").exists()


@respx.mock
def test_download_tokenized_dataset_reuses_cache(client: Together, tmp_path: Path) -> None:
    pytest.importorskip("zstandard")
    archive = _make_archive_bytes(tmp_path, with_eval=False)
    presign_url = "https://r2.example/tokenized_datasets.tar.zst?sig=1"

    route = respx.get(f"{base_url}/fine-tunes/ft-abc/download-tokenized-dataset").mock(
        return_value=httpx.Response(
            200,
            json={
                "url": presign_url,
                "filename": "tokenized_datasets.tar.zst",
                "size": len(archive),
                "content_type": "application/zstd",
            },
        )
    )
    respx.get(presign_url).mock(return_value=httpx.Response(200, content=archive))

    out = tmp_path / "out"
    td.download_tokenized_dataset(client, "ft-abc", output_dir=out)
    td.download_tokenized_dataset(client, "ft-abc", output_dir=out)

    assert route.call_count == 1


@respx.mock
def test_download_tokenized_dataset_404(client: Together, tmp_path: Path) -> None:
    respx.get(f"{base_url}/fine-tunes/ft-missing/download-tokenized-dataset").mock(
        return_value=httpx.Response(404, json={"error": {"message": "not found"}})
    )

    with pytest.raises(Exception):
        td.download_tokenized_dataset(client, "ft-missing", output_dir=tmp_path / "out")


def test_download_return_dataset_object_requires_datasets(client: Together, tmp_path: Path) -> None:
    real_import = __import__

    def fake_import(name: str, *args: object, **kwargs: object):
        if name == "datasets" or name.startswith("datasets."):
            raise ImportError("No module named 'datasets'")
        return real_import(name, *args, **kwargs)

    with (
        patch("builtins.__import__", side_effect=fake_import),
        patch.object(td, "_ensure_unpacked", return_value=tmp_path / "cache"),
    ):
        with pytest.raises(ImportError, match="together\\[datasets\\]"):
            td.download_tokenized_dataset(
                client,
                "ft-abc",
                output_dir=tmp_path / "cache",
                return_dataset_object=True,
            )


@respx.mock
def test_load_tokenized_dataset_returns_dataset_dict(client: Together, tmp_path: Path) -> None:
    datasets = pytest.importorskip("datasets")
    pytest.importorskip("zstandard")

    source = tmp_path / "source"
    train = datasets.Dataset.from_dict({"input_ids": [[1, 2], [3, 4]], "labels": [[1, 2], [3, 4]]})
    eval_ds = datasets.Dataset.from_dict({"input_ids": [[5, 6]], "labels": [[5, 6]]})
    train.save_to_disk(source / "train_dataset")
    eval_ds.save_to_disk(source / "eval_dataset")
    archive = td.pack_tokenized_dataset_archive(source)

    presign_url = "https://r2.example/tokenized_datasets.tar.zst?sig=1"
    respx.get(f"{base_url}/fine-tunes/ft-abc/download-tokenized-dataset").mock(
        return_value=httpx.Response(
            200,
            json={
                "url": presign_url,
                "filename": "tokenized_datasets.tar.zst",
                "size": len(archive),
                "content_type": "application/zstd",
            },
        )
    )
    respx.get(presign_url).mock(return_value=httpx.Response(200, content=archive))

    loaded = td.download_tokenized_dataset(
        client,
        "ft-abc",
        output_dir=tmp_path / "cache",
        return_dataset_object=True,
    )
    assert loaded is not None
    assert list(loaded.keys()) == ["train", "validation"]
    assert len(loaded["train"]) == 2
    assert len(loaded["validation"]) == 1


def test_unpack_streaming_zstd_without_content_size(tmp_path: Path) -> None:
    """Production archives use ``tar -I zstd`` frames without content size."""
    pytest.importorskip("zstandard")
    source = tmp_path / "source"
    _write_fake_member(source / "train_dataset", "train")
    archive = td.pack_tokenized_dataset_archive(source, write_content_size=False)

    out = tmp_path / "out"
    out.mkdir()
    td._unpack_tar_zst(archive, out)
    assert (out / "train_dataset" / "marker.txt").read_text(encoding="utf-8") == "train"


def test_require_datasets_install_hint() -> None:
    real_import = __import__

    def fake_import(name: str, *args: object, **kwargs: object):
        if name == "datasets" or name.startswith("datasets."):
            raise ImportError("No module named 'datasets'")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        with pytest.raises(ImportError, match="pip install together\\[datasets\\]"):
            td._require_datasets()


@respx.mock
def test_client_get_tokenized_dataset_delegates(client: Together, tmp_path: Path) -> None:
    datasets = pytest.importorskip("datasets")
    pytest.importorskip("zstandard")

    source = tmp_path / "source"
    train = datasets.Dataset.from_dict({"input_ids": [[1, 2]], "labels": [[1, 2]]})
    train.save_to_disk(source / "train_dataset")
    archive = td.pack_tokenized_dataset_archive(source)

    presign_url = "https://r2.example/tokenized_datasets.tar.zst?sig=1"
    respx.get(f"{base_url}/fine-tunes/ft-abcd1234/download-tokenized-dataset").mock(
        return_value=httpx.Response(
            200,
            json={
                "url": presign_url,
                "filename": "tokenized_datasets.tar.zst",
                "size": len(archive),
                "content_type": "application/zstd",
            },
        )
    )
    respx.get(presign_url).mock(return_value=httpx.Response(200, content=archive))

    loaded = client.fine_tuning.get_tokenized_dataset(
        ft_id="ft-abcd1234",
        cache_dir=tmp_path / "cache",
    )
    assert list(loaded.keys()) == ["train"]
    assert len(loaded["train"]) == 1


def test_client_get_tokenized_dataset_requires_ft_id(client: Together) -> None:
    with pytest.raises(ValueError, match="ft_id"):
        client.fine_tuning.get_tokenized_dataset(ft_id="")
