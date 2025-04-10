# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["CodeInterpreterExecuteParams"]


class CodeInterpreterExecuteParams(TypedDict, total=False):
    code: Required[str]
    """Code snippet to execute."""

    language: Required[Literal["python"]]
    """Programming language for the code to execute.

    Currently only supports Python, but more will be added.
    """

    session_id: str
    """Identifier of the current session.

    Used to make follow-up calls. Requests will return an error if the session does
    not belong to the caller or has expired.
    """
