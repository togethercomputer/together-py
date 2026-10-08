# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["S3OriginParam"]


class S3OriginParam(TypedDict, total=False):
    """S3 source configuration for volume sync."""

    role_arn: Required[str]
    """IAM role ARN Together assumes to read the S3 bucket or prefix."""

    uri: Required[str]
    """S3 bucket or prefix to copy into the volume."""
