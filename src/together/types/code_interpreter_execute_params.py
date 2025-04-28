# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["CodeInterpreterExecuteParams", "File"]


class CodeInterpreterExecuteParams(TypedDict, total=False):
    code: Required[str]
    """Code snippet to execute."""

    language: Required[Literal["python"]]
    """Programming language for the code to execute.

    Currently only supports Python, but more will be added.
    """

    files: Iterable[File]
    """Files to upload to the session.

    If present, files will be uploaded before executing the given code.
    """

    session_id: str
    """Identifier of the current session.

    Used to make follow-up calls. Requests will return an error if the session does
    not belong to the caller or has expired.
    """


class File(TypedDict, total=False):
    content: Required[str]

    encoding: Required[Literal["string", "base64"]]
    """Encoding of the file content.

    Use `string` for text files such as code, and `base64` for binary files, such as
    images.
    """

    name: Required[str]
