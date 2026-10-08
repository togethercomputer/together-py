# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["S3Origin"]


class S3Origin(BaseModel):
    """S3 source configuration for volume sync."""

    role_arn: str
    """IAM role ARN Together assumes to read the S3 bucket or prefix."""

    uri: str
    """S3 bucket or prefix to copy into the volume."""
