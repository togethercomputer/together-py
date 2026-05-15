# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ...._models import BaseModel
from .remediation import Remediation

__all__ = ["RemediationListResponse"]


class RemediationListResponse(BaseModel):
    """ListRemediationsResponse is the response for ListRemediations."""

    has_next: bool
    """Indicates if there are more results available."""

    next_page_token: str
    """Token for the next page."""

    remediations: List[Remediation]
    """The list of remediations."""
