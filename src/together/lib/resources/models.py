from typing import List
from typing_extensions import TypeAlias

from together import Together
from together._models import BaseModel
from together.types.model_list_response import ModelListResponse


class DedicatedModel(BaseModel):
    name: str
    id: str


ModelList: TypeAlias = List[DedicatedModel]


def filter_by_dedicated_models(client: Together, models: ModelListResponse) -> ModelListResponse:
    """
    Filter models based on dedicated model response.

    Args:
    models (List[BaseModel]): List of all models
    dedicated_response (APIResponse): Response from autoscale models endpoint

    Returns:
    List[BaseModel]: Filtered list of models
    """
    dedicated_models = client.get("/autoscale/models", cast_to=ModelList)

    # Create a set of dedicated model names for efficient lookup
    dedicated_model_names = {model.name for model in dedicated_models}

    # Filter models to only include those in dedicated_model_names
    # Note: The model.id from ModelObject matches the name field in the autoscale response
    return [model for model in models if model.id in dedicated_model_names]
