# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ImageCreateParams"]


class ImageCreateParams(TypedDict, total=False):
    model: Required[str]
    """The model to use for image generation."""

    prompt: Required[str]
    """A description of the desired images. Maximum length varies by model."""

    height: int
    """Height of the image to generate in number of pixels."""

    n: int
    """Number of image results to generate."""

    negative_prompt: str
    """The prompt or prompts not to guide the image generation."""

    seed: int
    """Seed used for generation. Can be used to reproduce image generations."""

    steps: int
    """Number of generation steps."""

    width: int
    """Width of the image to generate in number of pixels."""
