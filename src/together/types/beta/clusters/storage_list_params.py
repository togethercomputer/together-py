# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["StorageListParams"]


class StorageListParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Optional UMS project ID to filter volumes by.

    When set, only volumes belonging to this project are returned. The caller must
    be a member of the project; otherwise the result set will be empty.
    """
