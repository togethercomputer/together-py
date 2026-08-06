from __future__ import annotations

from typing import Optional, Annotated
from pathlib import Path

import httpx
from cyclopts import Parameter, validators

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.files.retrieve_content import resolve_download_path, safe_download_filename

OutputDirParam = Annotated[
    Optional[Path],
    Parameter(
        name=["--output-dir", "-o"],
        help="Directory to save the tokenized dataset archive",
        validator=validators.Path(file_okay=False, dir_okay=True),
    ),
]


async def _download_url(url: str, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bytes_written = 0
    async with httpx.AsyncClient(follow_redirects=True) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            with output_path.open("wb") as file:
                async for chunk in response.aiter_bytes():
                    file.write(chunk)
                    bytes_written += len(chunk)
    return bytes_written


async def download_tokenized_dataset(
    fine_tune_id: str,
    output_dir: OutputDirParam = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Download the tokenized dataset archive generated for a fine-tuning job."""
    metadata = await show_loading_status(
        "Retrieving tokenized dataset download URL...",
        config.client.fine_tuning.retrieve_tokenized_dataset(fine_tune_id),
    )

    filename = safe_download_filename(metadata.filename, fallback=f"{fine_tune_id}-tokenized-dataset")
    if output_dir is None:
        output_path = Path(filename).resolve()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = resolve_download_path(output_dir, filename)

    bytes_written = await show_loading_status(
        "Downloading tokenized dataset...", _download_url(metadata.url, output_path)
    )

    if metadata.size and bytes_written != metadata.size:
        raise ValueError(
            f"Downloaded file size `{bytes_written}` bytes does not match remote file size `{metadata.size}` bytes."
        )

    if config.json:
        console.print_json(
            openapi_dumps(
                {"object": "local", "id": fine_tune_id, "filename": str(output_path), "size": bytes_written}
            ).decode("utf-8")
        )
    else:
        console.print(f"File saved to {output_path}")
