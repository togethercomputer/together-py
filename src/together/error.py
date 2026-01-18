# Manually added to minimize breaking changes from V1
from ._exceptions import (
    APIError as APIError,
    RateLimitError as RateLimitError,
    APITimeoutError,
    BadRequestError,
    APIConnectionError as APIConnectionError,
    AuthenticationError as AuthenticationError,
    APIResponseValidationError,
)

Timeout = APITimeoutError
InvalidRequestError = BadRequestError
TogetherException = APIError
ResponseError = APIResponseValidationError
