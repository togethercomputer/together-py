# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["ModelResourcesStatus"]

ModelResourcesStatus: TypeAlias = Literal[
    "MODEL_RESOURCES_STATUS_PENDING",
    "MODEL_RESOURCES_STATUS_CREATING",
    "MODEL_RESOURCES_STATUS_READY",
    "MODEL_RESOURCES_STATUS_ERROR",
    "MODEL_RESOURCES_STATUS_STOPPED",
    "MODEL_RESOURCES_STATUS_STOPPING",
]
