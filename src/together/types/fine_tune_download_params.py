# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["FineTuneDownloadParams"]


class FineTuneDownloadParams(TypedDict, total=False):
    ft_id: Required[str]
    """Fine-tune ID to download. A string that starts with `ft-`."""

    checkpoint: Literal["merged", "adapter"]
    """Specifies checkpoint type to download - `merged` vs `adapter`.

    This field is required if the checkpoint_step is not set.
    """

    checkpoint_step: int
    """Specifies step number for checkpoint to download.

    Ignores `checkpoint` value if set.
    """

    output: str
    """Specifies output file name for downloaded model.

    Defaults to `$PWD/{model_name}.{extension}`.
    """
