from typing import Any, List, Optional

from ..._models import BaseModel


class FinetuneFullTrainingLimits(BaseModel):
    max_batch_size: int
    max_batch_size_dpo: int = -1
    min_batch_size: int

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if self.max_batch_size_dpo == -1:
            half_max = self.max_batch_size // 2
            rounded_half_max = (half_max // 8) * 8
            self.max_batch_size_dpo = max(self.min_batch_size, rounded_half_max)


class FinetuneLoraTrainingLimits(FinetuneFullTrainingLimits):
    max_rank: int
    target_modules: List[str]


class FinetuneTrainingLimits(BaseModel):
    max_num_epochs: int
    max_learning_rate: float
    min_learning_rate: float
    full_training: Optional[FinetuneFullTrainingLimits] = None
    lora_training: Optional[FinetuneLoraTrainingLimits] = None
