from __future__ import annotations

import shutil
import tarfile
import tempfile
import importlib
from typing import TYPE_CHECKING, Any
from pathlib import Path, PurePosixPath

import anyio
import httpx
from anyio.to_thread import run_sync

from together._types import NotGiven, not_given

if TYPE_CHECKING:
    from datasets import DatasetDict  # type: ignore[import-untyped]  # pyright: ignore[reportMissingTypeStubs]
else:
    DatasetDict = Any

_DATASETS_INSTALL_HINT = (
    "Returning a Hugging Face dataset requires the `datasets` extra. Install it with `pip install together[datasets]`."
)
_TRAIN_DATASET_DIR = "train_dataset"
_EVAL_DATASET_DIR = "eval_dataset"
_EXPECTED_DATASET_DIRS = {_TRAIN_DATASET_DIR, _EVAL_DATASET_DIR}
_REDIRECT_STATUS_CODES = {301, 302, 303, 307, 308}
_MAX_REDIRECTS = 20
_MAX_ARCHIVE_MEMBERS = 10_000
_MAX_MEMBER_BYTES = 512 * 1024 * 1024
_MAX_EXTRACTED_BYTES = 1024 * 1024 * 1024

_DatasetDependencies = tuple[Any, Any, Any]


def _require_datasets() -> _DatasetDependencies:
    try:
        datasets = importlib.import_module("datasets")
        zstandard = importlib.import_module("zstandard")
    except ImportError as exc:
        raise RuntimeError(_DATASETS_INSTALL_HINT) from exc
    return datasets.DatasetDict, datasets.load_from_disk, zstandard.ZstdDecompressor


def _extract_archive(archive_path: Path, output_dir: Path, decompressor_type: Any) -> None:
    member_count = 0
    extracted_bytes = 0
    with archive_path.open("rb") as compressed:
        with decompressor_type().stream_reader(compressed) as decompressed:
            with tarfile.open(fileobj=decompressed, mode="r|") as archive:
                for member in archive:
                    member_count += 1
                    if member_count > _MAX_ARCHIVE_MEMBERS:
                        raise ValueError("Tokenized dataset archive contains too many members.")
                    if member.size < 0 or member.size > _MAX_MEMBER_BYTES:
                        raise ValueError(f"Tokenized dataset archive member is too large: {member.name!r}")
                    extracted_bytes += member.size
                    if extracted_bytes > _MAX_EXTRACTED_BYTES:
                        raise ValueError("Tokenized dataset archive is too large after extraction.")

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


def _load_archive(
    archive_path: Path,
    dependencies: _DatasetDependencies | None = None,
) -> DatasetDict:
    if dependencies is None:
        dependencies = _require_datasets()
    dataset_dict_type, load_from_disk, decompressor_type = dependencies
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


def _validate_download_url(url: str) -> None:
    parsed_url = httpx.URL(url)
    if parsed_url.scheme != "https" or not parsed_url.host:
        raise ValueError("Tokenized dataset download URL must use HTTPS.")


def _get_redirect_url(response: httpx.Response) -> str | None:
    if response.status_code not in _REDIRECT_STATUS_CODES:
        return None
    location = response.headers.get("location")
    if location is None:
        raise ValueError("Tokenized dataset download redirect is missing a location.")
    return str(response.url.join(location))


def _client_options(
    timeout: float | httpx.Timeout | None | NotGiven,
) -> dict[str, Any]:
    if isinstance(timeout, NotGiven):
        return {}
    return {"timeout": timeout}


def retrieve_dataset(
    url: str,
    *,
    expected_size: int,
    timeout: float | httpx.Timeout | None | NotGiven = not_given,
) -> DatasetDict:
    dependencies = _require_datasets()
    _validate_download_url(url)
    with tempfile.TemporaryDirectory() as temporary_directory:
        archive_path = Path(temporary_directory) / "tokenized-datasets.tar.zst"
        with httpx.Client(**_client_options(timeout)) as client:
            for _ in range(_MAX_REDIRECTS + 1):
                with client.stream("GET", url) as response:
                    redirect_url = _get_redirect_url(response)
                    if redirect_url is not None:
                        _validate_download_url(redirect_url)
                        url = redirect_url
                        continue

                    response.raise_for_status()
                    bytes_written = 0
                    with archive_path.open("wb") as archive:
                        for chunk in response.iter_bytes():
                            if bytes_written + len(chunk) > expected_size:
                                raise ValueError("Downloaded file exceeds the remote file size.")
                            archive.write(chunk)
                            bytes_written += len(chunk)
                    if bytes_written != expected_size:
                        raise ValueError(
                            f"Downloaded file size `{bytes_written}` bytes does not match "
                            f"remote file size `{expected_size}` bytes."
                        )
                    break
            else:
                raise ValueError("Tokenized dataset download exceeded the maximum number of redirects.")
        return _load_archive(archive_path, dependencies)


async def async_retrieve_dataset(
    url: str,
    *,
    expected_size: int,
    timeout: float | httpx.Timeout | None | NotGiven = not_given,
) -> DatasetDict:
    _validate_download_url(url)
    dependencies = await run_sync(_require_datasets)
    with tempfile.TemporaryDirectory() as temporary_directory:
        archive_path = Path(temporary_directory) / "tokenized-datasets.tar.zst"
        async with httpx.AsyncClient(**_client_options(timeout)) as client:
            for _ in range(_MAX_REDIRECTS + 1):
                async with client.stream("GET", url) as response:
                    redirect_url = _get_redirect_url(response)
                    if redirect_url is not None:
                        _validate_download_url(redirect_url)
                        url = redirect_url
                        continue

                    response.raise_for_status()
                    bytes_written = 0
                    async with await anyio.open_file(archive_path, "wb") as archive:
                        async for chunk in response.aiter_bytes():
                            if bytes_written + len(chunk) > expected_size:
                                raise ValueError("Downloaded file exceeds the remote file size.")
                            await archive.write(chunk)
                            bytes_written += len(chunk)
                    if bytes_written != expected_size:
                        raise ValueError(
                            f"Downloaded file size `{bytes_written}` bytes does not match "
                            f"remote file size `{expected_size}` bytes."
                        )
                    break
            else:
                raise ValueError("Tokenized dataset download exceeded the maximum number of redirects.")
        return await run_sync(_load_archive, archive_path, dependencies)
