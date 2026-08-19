from __future__ import annotations

import shutil
import tarfile
import tempfile
import importlib
from typing import TYPE_CHECKING, Any
from pathlib import Path, PurePosixPath

import httpx

if TYPE_CHECKING:
    from datasets import DatasetDict  # type: ignore[import-untyped]  # pyright: ignore[reportMissingTypeStubs]

_DATASETS_INSTALL_HINT = (
    "Returning a Hugging Face dataset requires the `datasets` extra. Install it with `pip install together[datasets]`."
)
_TRAIN_DATASET_DIR = "train_dataset"
_EVAL_DATASET_DIR = "eval_dataset"
_EXPECTED_DATASET_DIRS = {_TRAIN_DATASET_DIR, _EVAL_DATASET_DIR}


def _require_datasets() -> tuple[Any, Any, Any]:
    try:
        datasets = importlib.import_module("datasets")
        zstandard = importlib.import_module("zstandard")
    except ImportError as exc:
        raise RuntimeError(_DATASETS_INSTALL_HINT) from exc
    return datasets.DatasetDict, datasets.load_from_disk, zstandard.ZstdDecompressor


def _extract_archive(archive_path: Path, output_dir: Path, decompressor_type: Any) -> None:
    with archive_path.open("rb") as compressed:
        with decompressor_type().stream_reader(compressed) as decompressed:
            with tarfile.open(fileobj=decompressed, mode="r|") as archive:
                for member in archive:
                    member_path = PurePosixPath(member.name)
                    if (
                        member_path.is_absolute()
                        or "\\" in member.name
                        or ".." in member_path.parts
                        or not member_path.parts
                        or member_path.parts[0] not in _EXPECTED_DATASET_DIRS
                    ):
                        raise ValueError(f"Unexpected tokenized dataset archive member: {member.name!r}")

                    destination = output_dir.joinpath(*member_path.parts)
                    if member.isdir():
                        destination.mkdir(parents=True, exist_ok=True)
                        continue
                    if not member.isfile():
                        raise ValueError(f"Unsupported tokenized dataset archive member: {member.name!r}")

                    source = archive.extractfile(member)
                    if source is None:
                        raise ValueError(f"Could not read tokenized dataset archive member: {member.name!r}")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with source, destination.open("wb") as target:
                        shutil.copyfileobj(source, target)


def _load_archive(archive_path: Path) -> DatasetDict:
    dataset_dict_type, load_from_disk, decompressor_type = _require_datasets()
    with tempfile.TemporaryDirectory() as temporary_directory:
        output_dir = Path(temporary_directory)
        _extract_archive(archive_path, output_dir, decompressor_type)

        train_path = output_dir / _TRAIN_DATASET_DIR
        if not train_path.is_dir():
            raise ValueError("Tokenized dataset archive does not contain a train dataset.")

        splits = {"train": load_from_disk(train_path, keep_in_memory=True)}
        eval_path = output_dir / _EVAL_DATASET_DIR
        if eval_path.is_dir():
            splits["validation"] = load_from_disk(eval_path, keep_in_memory=True)
        return dataset_dict_type(splits)


def retrieve_dataset(url: str) -> DatasetDict:
    with tempfile.TemporaryDirectory() as temporary_directory:
        archive_path = Path(temporary_directory) / "tokenized-datasets.tar.zst"
        with httpx.stream("GET", url, follow_redirects=True) as response:
            response.raise_for_status()
            with archive_path.open("wb") as archive:
                for chunk in response.iter_bytes():
                    archive.write(chunk)
        return _load_archive(archive_path)


async def async_retrieve_dataset(url: str) -> DatasetDict:
    with tempfile.TemporaryDirectory() as temporary_directory:
        archive_path = Path(temporary_directory) / "tokenized-datasets.tar.zst"
        async with httpx.AsyncClient(follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                with archive_path.open("wb") as archive:
                    async for chunk in response.aiter_bytes():
                        archive.write(chunk)
        return _load_archive(archive_path)
