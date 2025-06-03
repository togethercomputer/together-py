# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes
from .file_type import FileType
from .file_purpose import FilePurpose

__all__ = ["FileUploadParams"]


class FileUploadParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The content of the file being uploaded"""

    file_name: Required[str]
    """The name of the file being uploaded"""

    purpose: Required[FilePurpose]
    """The purpose of the file"""

    file_type: FileType
    """The type of the file"""
