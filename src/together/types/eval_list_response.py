# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .evaluation_job import EvaluationJob

__all__ = ["EvalListResponse"]

EvalListResponse: TypeAlias = List[EvaluationJob]
