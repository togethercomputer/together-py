# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["VideoCreateParams", "FrameImage"]


class VideoCreateParams(TypedDict, total=False):
    model: Required[str]
    """The model to be used for the video creation request."""

    fps: int
    """Frames per second. Defaults to 24."""

    frame_images: Iterable[FrameImage]
    """Array of images to guide video generation, similar to keyframes."""

    guidance_scale: int
    """Controls how closely the video generation follows your prompt.

    Higher values make the model adhere more strictly to your text description,
    while lower values allow more creative freedom. guidence_scale affects both
    visual content and temporal consistency.Recommended range is 6.0-10.0 for most
    video models. Values above 12 may cause over-guidance artifacts or unnatural
    motion patterns.
    """

    height: int

    negative_prompt: str
    """Similar to prompt, but specifies what to avoid instead of what to include"""

    output_format: Literal["MP4", "WEBM"]
    """Specifies the format of the output video. Defaults to MP4."""

    output_quality: int
    """Compression quality. Defaults to 20."""

    prompt: str
    """Text prompt that describes the video to generate."""

    reference_images: SequenceNotStr[str]
    """
    Unlike frame_images which constrain specific timeline positions, reference
    images guide the general appearance that should appear consistently across the
    video.
    """

    seconds: str
    """Clip duration in seconds."""

    seed: int
    """Seed to use in initializing the video generation.

    Using the same seed allows deterministic video generation. If not provided a
    random seed is generated for each request.
    """

    steps: int
    """The number of denoising steps the model performs during video generation.

    More steps typically result in higher quality output but require longer
    processing time.
    """

    width: int


class FrameImage(TypedDict, total=False):
    input_image: Required[str]
    """URL path to hosted image that is used for a frame"""

    frame: Union[float, Literal["first", "last"]]
    """Optional param to specify where to insert the frame.

    If this is omitted, the following heuristics are applied:

    - frame_images size is one, frame is first.
    - If size is two, frames are first and last.
    - If size is larger, frames are first, last and evenly spaced between.
    """
