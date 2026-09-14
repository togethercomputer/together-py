# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["EndpointListHardwareParams"]


class EndpointListHardwareParams(TypedDict, total=False):
    model: str
    """Filter hardware configurations by model compatibility.

    When provided, the response includes availability status for each compatible
    configuration.
    [See all of Together AI's dedicated models](https://docs.together.ai/docs/dedicated-models)
    """
