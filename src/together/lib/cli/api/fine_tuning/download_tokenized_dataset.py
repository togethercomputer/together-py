from __future__ import annotations

from typing import Optional, Annotated
from pathlib import Path

from cyclopts import Parameter

from together import APIError, NotFoundError, APIStatusError
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.resources.tokenized_dataset import default_cache_dir

OutputDirParam = Annotated[
    Optional[Path],
    Parameter(name=["--output-dir", "-o"], help="Directory to unpack the tokenized dataset sample into"),
]


async def download_tokenized_dataset(
    fine_tune_id: str,
    output_dir: OutputDirParam = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Download a fine-tuning job's tokenized dataset sample archive (≤100 rows) and unpack it."""
    try:
        await show_loading_status(
            "Downloading tokenized dataset sample...",
            config.client.fine_tuning.download_tokenized_dataset(
                ft_id=fine_tune_id,
                output_dir=output_dir,
                return_dataset_object=False,
            ),
        )
    except NotFoundError as e:
        raise APIError(
            "Tokenized dataset sample not found for this fine-tuning job. "
            "It may not have been uploaded yet, or the job may not support samples.",
            request=e.request,
            body=None,
        ) from e
    except ImportError as e:
        console.print(str(e))
        raise SystemExit(1) from e
    except APIStatusError as e:
        raise APIError(
            "Failed to download tokenized dataset sample.",
            request=e.request,
            body=e.body,
        ) from e

    dest = Path(output_dir) if output_dir is not None else default_cache_dir(fine_tune_id)
    if config.json:
        console.print_json(
            openapi_dumps(
                {
                    "object": "local",
                    "id": fine_tune_id,
                    "path": str(dest.resolve()),
                }
            ).decode("utf-8")
        )
    else:
        console.print(f"Tokenized dataset sample saved to {dest.resolve()}")
