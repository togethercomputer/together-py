"""Download and load fine-tune tokenized dataset sample archives.

The archive is a small (≤100 row) HuggingFace ``save_to_disk`` snapshot uploaded
after dataset preparation. Loading requires the optional ``datasets`` extra:

    pip install together[datasets]
"""

from __future__ import annotations

import io
import shutil
import tarfile
from typing import TYPE_CHECKING, Any
from pathlib import Path

import httpx
from filelock import FileLock

from together._utils import path_template
from together.lib.types.tokenized_dataset import TokenizedDatasetDownloadResponse

if TYPE_CHECKING:
    from datasets import DatasetDict

    from together import Together, AsyncTogether

_TRAIN_MEMBER = "train_dataset"
_EVAL_MEMBER = "eval_dataset"
_READY_MARKER = ".ready"


def _require_zstandard() -> Any:
    try:
        import zstandard
    except ImportError as e:
        raise ImportError(
            "zstandard is not installed and is required to unpack tokenized dataset archives. "
            "Please install it via `pip install together[datasets]`"
        ) from e
    return zstandard


def _require_datasets() -> tuple[Any, Any]:
    try:
        from datasets import DatasetDict, load_from_disk
    except ImportError as e:
        raise ImportError(
            "datasets is not installed and is required to load tokenized dataset snapshots. "
            "Please install it via `pip install together[datasets]`"
        ) from e
    return DatasetDict, load_from_disk


def default_cache_dir(fine_tune_id: str) -> Path:
    return Path.home() / ".cache" / "together" / "tokenized-datasets" / fine_tune_id


def _unpack_tar_zst(archive_bytes: bytes, output_dir: Path) -> None:
    """Unpack a ``.tar.zst`` archive.

    Uses streaming decompression so frames produced by ``tar -I zstd`` (no content
    size in the frame header) work, not only one-shot ``ZstdCompressor.compress``.
    """
    zstandard = _require_zstandard()
    dctx = zstandard.ZstdDecompressor()
    with dctx.stream_reader(io.BytesIO(archive_bytes)) as reader:
        # Streaming tar mode pairs with the zstd stream reader (unknown length).
        with tarfile.open(fileobj=reader, mode="r|") as tar:  # type: ignore[arg-type]
            tar.extractall(path=output_dir)


def _download_url_bytes(url: str) -> bytes:
    # Use plain httpx so Together auth headers are not sent to the presigned URL.
    with httpx.Client(follow_redirects=True, timeout=60.0) as http:
        response = http.get(url)
        response.raise_for_status()
        return response.content


async def _async_download_url_bytes(url: str) -> bytes:
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as http:
        response = await http.get(url)
        response.raise_for_status()
        return response.content


def _validate_unpacked(output_dir: Path) -> None:
    train_path = output_dir / _TRAIN_MEMBER
    if not train_path.is_dir():
        raise FileNotFoundError(
            f"Tokenized dataset archive is missing required member `{_TRAIN_MEMBER}` under {output_dir}"
        )


def _clear_unpacked(dest: Path) -> None:
    for child in dest.iterdir():
        if child.name == _READY_MARKER or child.is_file():
            child.unlink(missing_ok=True)
        elif child.is_dir() and child.name in {_TRAIN_MEMBER, _EVAL_MEMBER}:
            shutil.rmtree(child)


def _fetch_presign(client: Together, fine_tune_id: str) -> TokenizedDatasetDownloadResponse:
    return client.get(
        path_template("/fine-tunes/{id}/download-tokenized-dataset", id=fine_tune_id),
        cast_to=TokenizedDatasetDownloadResponse,
    )


async def _async_fetch_presign(client: AsyncTogether, fine_tune_id: str) -> TokenizedDatasetDownloadResponse:
    return await client.get(
        path_template("/fine-tunes/{id}/download-tokenized-dataset", id=fine_tune_id),
        cast_to=TokenizedDatasetDownloadResponse,
    )


def _ensure_unpacked(
    client: Together,
    fine_tune_id: str,
    *,
    output_dir: Path | None,
    force_download: bool,
) -> Path:
    dest = Path(output_dir) if output_dir is not None else default_cache_dir(fine_tune_id)
    dest.mkdir(parents=True, exist_ok=True)
    ready = dest / _READY_MARKER
    lock_path = dest.with_suffix(dest.suffix + ".lock")

    with FileLock(str(lock_path)):
        if ready.exists() and (dest / _TRAIN_MEMBER).is_dir() and not force_download:
            return dest.resolve()

        if force_download and dest.exists():
            _clear_unpacked(dest)

        meta = _fetch_presign(client, fine_tune_id)
        archive_bytes = _download_url_bytes(meta.url)
        _unpack_tar_zst(archive_bytes, dest)
        _validate_unpacked(dest)
        ready.write_text("ok\n", encoding="utf-8")

    return dest.resolve()


async def _async_ensure_unpacked(
    client: AsyncTogether,
    fine_tune_id: str,
    *,
    output_dir: Path | None,
    force_download: bool,
) -> Path:
    dest = Path(output_dir) if output_dir is not None else default_cache_dir(fine_tune_id)
    dest.mkdir(parents=True, exist_ok=True)
    ready = dest / _READY_MARKER
    lock_path = dest.with_suffix(dest.suffix + ".lock")

    with FileLock(str(lock_path)):
        if ready.exists() and (dest / _TRAIN_MEMBER).is_dir() and not force_download:
            return dest.resolve()

        if force_download and dest.exists():
            _clear_unpacked(dest)

        meta = await _async_fetch_presign(client, fine_tune_id)
        archive_bytes = await _async_download_url_bytes(meta.url)
        _unpack_tar_zst(archive_bytes, dest)
        _validate_unpacked(dest)
        ready.write_text("ok\n", encoding="utf-8")

    return dest.resolve()


def _dataset_dict_from_unpacked(unpacked: Path) -> DatasetDict:
    DatasetDict, load_from_disk = _require_datasets()
    splits: dict[str, Any] = {"train": load_from_disk(str(unpacked / _TRAIN_MEMBER))}
    eval_path = unpacked / _EVAL_MEMBER
    if eval_path.is_dir():
        splits["validation"] = load_from_disk(str(eval_path))
    return DatasetDict(splits)


def download_tokenized_dataset(
    client: Together,
    fine_tune_id: str,
    *,
    output_dir: Path | None = None,
    force_download: bool = False,
    return_dataset_object: bool = False,
) -> DatasetDict | None:
    """Download and unpack a tokenized dataset sample archive for a fine-tune job.

    Args:
        return_dataset_object: If True, load and return a HuggingFace ``DatasetDict``
            (keys ``\"train\"`` and optional ``\"validation\"``). Requires
            ``pip install together[datasets]``. If False, returns ``None`` after
            unpacking (still requires ``zstandard`` via the same extra).
    """
    unpacked = _ensure_unpacked(
        client,
        fine_tune_id,
        output_dir=output_dir,
        force_download=force_download,
    )
    if not return_dataset_object:
        return None
    return _dataset_dict_from_unpacked(unpacked)


async def async_download_tokenized_dataset(
    client: AsyncTogether,
    fine_tune_id: str,
    *,
    output_dir: Path | None = None,
    force_download: bool = False,
    return_dataset_object: bool = False,
) -> DatasetDict | None:
    """Async variant of :func:`download_tokenized_dataset`."""
    unpacked = await _async_ensure_unpacked(
        client,
        fine_tune_id,
        output_dir=output_dir,
        force_download=force_download,
    )
    if not return_dataset_object:
        return None
    return _dataset_dict_from_unpacked(unpacked)


def load_tokenized_dataset(
    client: Together,
    fine_tune_id: str,
    *,
    cache_dir: Path | None = None,
    force_download: bool = False,
) -> DatasetDict:
    """Download (if needed) and load a tokenized dataset sample as a ``DatasetDict``.

    Keys are ``\"train\"`` and, when present in the archive, ``\"validation\"``.

    Raises:
        ImportError: If HuggingFace ``datasets`` is not installed.
    """
    dataset = download_tokenized_dataset(
        client,
        fine_tune_id,
        output_dir=cache_dir,
        force_download=force_download,
        return_dataset_object=True,
    )
    assert dataset is not None
    return dataset


async def async_load_tokenized_dataset(
    client: AsyncTogether,
    fine_tune_id: str,
    *,
    cache_dir: Path | None = None,
    force_download: bool = False,
) -> DatasetDict:
    """Async variant of :func:`load_tokenized_dataset`."""
    dataset = await async_download_tokenized_dataset(
        client,
        fine_tune_id,
        output_dir=cache_dir,
        force_download=force_download,
        return_dataset_object=True,
    )
    assert dataset is not None
    return dataset


def pack_tokenized_dataset_archive(source_dir: Path, *, write_content_size: bool = False) -> bytes:
    """Pack ``train_dataset`` / optional ``eval_dataset`` under ``source_dir`` into tar.zst bytes.

    Intended for tests and local tooling. By default emits a streaming zstd frame
    (no content size), matching production ``tar -I zstd`` archives.
    """
    zstandard = _require_zstandard()
    members = [_TRAIN_MEMBER]
    if (source_dir / _EVAL_MEMBER).is_dir():
        members.append(_EVAL_MEMBER)

    tar_buf = io.BytesIO()
    with tarfile.open(fileobj=tar_buf, mode="w") as tar:
        for member in members:
            tar.add(source_dir / member, arcname=member)
    tar_bytes = tar_buf.getvalue()

    if write_content_size:
        return zstandard.ZstdCompressor(level=3).compress(tar_bytes)

    # Streaming frame without content size — same shape as ``tar -I zstd``.
    # compressobj avoids ZstdCompressor.compress(), which embeds content size.
    compressobj = zstandard.ZstdCompressor(level=3).compressobj()
    return compressobj.compress(tar_bytes) + compressobj.flush()


__all__ = [
    "download_tokenized_dataset",
    "async_download_tokenized_dataset",
    "load_tokenized_dataset",
    "async_load_tokenized_dataset",
    "default_cache_dir",
    "pack_tokenized_dataset_archive",
]
