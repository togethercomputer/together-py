# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["RemoteUploadCreateParams"]


class RemoteUploadCreateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    model_id: Required[Annotated[str, PropertyInfo(alias="modelId")]]
    """ID of the registered model that will receive the imported files."""

    remote_url: Required[Annotated[str, PropertyInfo(alias="remoteUrl")]]
    """Hugging Face repository URL or presigned archive URL to import."""

    token: str
    """Optional source credential used to access a private remote location.

    The value is write-only and is not returned.
    """
