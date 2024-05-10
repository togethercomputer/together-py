# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.



from ..._models import BaseModel

__all__ = ["Usage"]


class Usage(BaseModel):
    completion_tokens: int

    prompt_tokens: int

    total_tokens: int
