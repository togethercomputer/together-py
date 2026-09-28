from __future__ import annotations

import logging
from pathlib import Path

import httpx

from ...._types import omit
from ...._client import Together, AsyncTogether
from ....types.beta.rl.checkpoint_variant import CheckpointVariant

logger = logging.getLogger("together")

_MAX_RETRIES = 7


def _checkpoint_file_path(destination: Path, filename: str) -> Path:
    basename = Path(filename).name
    if not basename or basename != filename:
        raise ValueError(f"Unsafe checkpoint filename: {filename!r}")
    return destination / basename


def download_checkpoint(
    client: Together,
    checkpoint_id: str,
    *,
    variant: CheckpointVariant = "CHECKPOINT_VARIANT_MERGED",
    output_dir: str | Path = ".",
) -> list[Path]:
    """Download checkpoint files using an existing Together client.

    Args:
        client: Configured client used to request and download the checkpoint.
        checkpoint_id: ID of the inference checkpoint to download.
        variant: Download merged full-model or adapter-only weights.
        output_dir: Local directory to save files into. Created if it does not exist.

    Returns:
        Paths to the downloaded files.

    Raises:
        APIError: If checkpoint metadata or a file download request fails.
        OSError: If the output directory or a checkpoint file cannot be written.
        ValueError: If the server returns an unsafe checkpoint filename.
    """
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    response = client.beta.rl.checkpoints.download(
        id=checkpoint_id,
        variant=variant,
    )
    downloaded: list[Path] = []
    for file_info in response.data:
        file_path = _checkpoint_file_path(destination, file_info.filename)
        logger.info("Downloading %s", file_info.filename)
        stream = client.get(
            file_info.url,
            cast_to=httpx.Response,
            stream=True,
            options={
                "max_retries": _MAX_RETRIES,
                "headers": {"Authorization": omit},
            },
        )
        try:
            with file_path.open("wb") as file:
                for chunk in stream.iter_bytes():
                    file.write(chunk)
        finally:
            stream.close()
        downloaded.append(file_path)
        logger.info("Saved %s", file_path)

    return downloaded


async def download_checkpoint_async(
    client: AsyncTogether,
    checkpoint_id: str,
    *,
    variant: CheckpointVariant = "CHECKPOINT_VARIANT_MERGED",
    output_dir: str | Path = ".",
) -> list[Path]:
    """Download checkpoint files using an existing AsyncTogether client.

    Args:
        client: Configured async client used to request and download the checkpoint.
        checkpoint_id: ID of the inference checkpoint to download.
        variant: Download merged full-model or adapter-only weights.
        output_dir: Local directory to save files into. Created if it does not exist.

    Returns:
        Paths to the downloaded files.

    Raises:
        APIError: If checkpoint metadata or a file download request fails.
        OSError: If the output directory or a checkpoint file cannot be written.
        ValueError: If the server returns an unsafe checkpoint filename.
    """
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    response = await client.beta.rl.checkpoints.download(
        id=checkpoint_id,
        variant=variant,
    )
    downloaded: list[Path] = []
    for file_info in response.data:
        file_path = _checkpoint_file_path(destination, file_info.filename)
        logger.info("Downloading %s", file_info.filename)
        stream = await client.get(
            file_info.url,
            cast_to=httpx.Response,
            stream=True,
            options={
                "max_retries": _MAX_RETRIES,
                "headers": {"Authorization": omit},
            },
        )
        try:
            with file_path.open("wb") as file:
                async for chunk in stream.aiter_bytes():
                    file.write(chunk)
        finally:
            await stream.aclose()
        downloaded.append(file_path)
        logger.info("Saved %s", file_path)

    return downloaded
