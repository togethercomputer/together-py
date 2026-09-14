# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from .._utils import PropertyInfo
from .._models import BaseModel

__all__ = [
    "ExecuteResponse",
    "SuccessfulExecution",
    "SuccessfulExecutionData",
    "SuccessfulExecutionDataOutput",
    "SuccessfulExecutionDataOutputStreamOutput",
    "SuccessfulExecutionDataOutputError",
    "SuccessfulExecutionDataOutputDisplayorExecuteOutput",
    "SuccessfulExecutionDataOutputDisplayorExecuteOutputData",
    "FailedExecution",
]


class SuccessfulExecutionDataOutputStreamOutput(BaseModel):
    """Outputs that were printed to stdout or stderr"""

    data: str

    type: Literal["stdout", "stderr"]


class SuccessfulExecutionDataOutputError(BaseModel):
    """Errors and exceptions that occurred.

    If this output type is present, your code did not execute successfully.
    """

    data: str

    type: Literal["error"]


class SuccessfulExecutionDataOutputDisplayorExecuteOutputData(BaseModel):
    application_geo_json: Optional[Dict[str, object]] = FieldInfo(alias="application/geo+json", default=None)

    application_javascript: Optional[str] = FieldInfo(alias="application/javascript", default=None)

    application_json: Optional[Dict[str, object]] = FieldInfo(alias="application/json", default=None)

    application_pdf: Optional[str] = FieldInfo(alias="application/pdf", default=None)

    application_vnd_vega_v5_json: Optional[Dict[str, object]] = FieldInfo(
        alias="application/vnd.vega.v5+json", default=None
    )

    application_vnd_vegalite_v4_json: Optional[Dict[str, object]] = FieldInfo(
        alias="application/vnd.vegalite.v4+json", default=None
    )

    image_gif: Optional[str] = FieldInfo(alias="image/gif", default=None)

    image_jpeg: Optional[str] = FieldInfo(alias="image/jpeg", default=None)

    image_png: Optional[str] = FieldInfo(alias="image/png", default=None)

    image_svg_xml: Optional[str] = FieldInfo(alias="image/svg+xml", default=None)

    text_html: Optional[str] = FieldInfo(alias="text/html", default=None)

    text_latex: Optional[str] = FieldInfo(alias="text/latex", default=None)

    text_markdown: Optional[str] = FieldInfo(alias="text/markdown", default=None)

    text_plain: Optional[str] = FieldInfo(alias="text/plain", default=None)


class SuccessfulExecutionDataOutputDisplayorExecuteOutput(BaseModel):
    data: SuccessfulExecutionDataOutputDisplayorExecuteOutputData

    type: Literal["display_data", "execute_result"]


SuccessfulExecutionDataOutput: TypeAlias = Annotated[
    Union[
        SuccessfulExecutionDataOutputStreamOutput,
        SuccessfulExecutionDataOutputError,
        SuccessfulExecutionDataOutputDisplayorExecuteOutput,
    ],
    PropertyInfo(discriminator="type"),
]


class SuccessfulExecutionData(BaseModel):
    outputs: List[SuccessfulExecutionDataOutput]

    session_id: str
    """Identifier of the current session. Used to make follow-up calls."""

    status: Optional[Literal["success"]] = None
    """Status of the execution. Currently only supports success."""


class SuccessfulExecution(BaseModel):
    data: SuccessfulExecutionData

    errors: None = None


class FailedExecution(BaseModel):
    data: None = None

    errors: List[Union[str, Dict[str, object]]]


ExecuteResponse: TypeAlias = Union[SuccessfulExecution, FailedExecution]
