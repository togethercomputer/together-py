# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["VideoJob", "Error", "Outputs"]


class Error(BaseModel):
    """Error payload that explains why generation failed, if applicable."""

    message: str

    code: Optional[str] = None


class Outputs(BaseModel):
    """
    Available upon completion, the outputs provides the cost charged and the hosted url to access the video
    """

    cost: int
    """The cost of generated video charged to the owners account."""

    video_url: str
    """URL hosting the generated video"""


class VideoJob(BaseModel):
    """Structured information describing a generated video job."""

    id: str
    """Unique identifier for the video job."""

    created_at: float
    """Unix timestamp (seconds) for when the job was created."""

    model: str
    """The video generation model that produced the job."""

    seconds: str
    """Duration of the generated clip in seconds."""

    size: str
    """The resolution of the generated video."""

    status: Literal["in_progress", "completed", "failed"]
    """Current lifecycle status of the video job."""

    completed_at: Optional[float] = None
    """Unix timestamp (seconds) for when the job completed, if finished."""

    error: Optional[Error] = None
    """Error payload that explains why generation failed, if applicable."""

    object: Optional[Literal["video"]] = None
    """The object type, which is always video."""

    outputs: Optional[Outputs] = None
    """
    Available upon completion, the outputs provides the cost charged and the hosted
    url to access the video
    """
