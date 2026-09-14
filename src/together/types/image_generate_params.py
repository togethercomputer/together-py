# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["ImageGenerateParams", "ImageLora"]


class ImageGenerateParams(TypedDict, total=False):
    model: Required[
        Union[
            Literal[
                "black-forest-labs/FLUX.1-schnell-Free",
                "black-forest-labs/FLUX.1-schnell",
                "black-forest-labs/FLUX.1.1-pro",
            ],
            str,
        ]
    ]
    """The model to use for image generation.

    [See all of Together AI's image models](https://docs.together.ai/docs/serverless-models#image-models)
    """

    prompt: Required[str]
    """A description of the desired images. Maximum length varies by model."""

    disable_safety_checker: bool
    """If true, disables the safety checker for image generation."""

    guidance_scale: float
    """Adjusts the alignment of the generated image with the input prompt.

    Higher values (e.g., 8-10) make the output more faithful to the prompt, while
    lower values (e.g., 1-5) encourage more creative freedom.
    """

    height: int
    """Height of the image to generate in number of pixels."""

    image_loras: Iterable[ImageLora]
    """
    An array of objects that define LoRAs (Low-Rank Adaptations) to influence the
    generated image.
    """

    image_url: str
    """URL of an image to use for image models that support it."""

    n: int
    """Number of image results to generate."""

    negative_prompt: str
    """The prompt or prompts not to guide the image generation."""

    output_format: Literal["jpeg", "png"]
    """The format of the image response.

    Can be either be `jpeg` or `png`. Defaults to `jpeg`.
    """

    reference_images: SequenceNotStr[str]
    """
    An array of image URLs that guide the overall appearance and style of the
    generated image. These reference images influence the visual characteristics
    consistently across the generation.
    """

    response_format: Literal["base64", "url"]
    """Format of the image response. Can be either a base64 string or a URL."""

    seed: int
    """Seed used for generation. Can be used to reproduce image generations."""

    steps: int
    """Number of generation steps."""

    width: int
    """Width of the image to generate in number of pixels."""


class ImageLora(TypedDict, total=False):
    path: Required[str]
    """The URL of the LoRA to apply (e.g.

    https://huggingface.co/strangerzonehf/Flux-Midjourney-Mix2-LoRA).
    """

    scale: Required[float]
    """The strength of the LoRA's influence. Most LoRA's recommend a value of 1."""
