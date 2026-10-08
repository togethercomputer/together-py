"""Public import surface for the post-training SDK (`client.post_training`).

    from together.post_training import SessionClient, Trainer

The implementation lives in `together.lib.post_training`.
"""

from __future__ import annotations

import sys
import importlib
import importlib.abc
import importlib.util
from types import ModuleType
from typing import Sequence
from typing_extensions import override
from importlib.machinery import ModuleSpec

from .lib.post_training import (
    Sample as Sample,
    Session as Session,
    Trainer as Trainer,
    Gradient as Gradient,
    Generator as Generator,
    AdamConfig as AdamConfig,
    AdamParams as AdamParams,
    Checkpoint as Checkpoint,
    LoraConfig as LoraConfig,
    LossConfig as LossConfig,
    ModelInput as ModelInput,
    MuonConfig as MuonConfig,
    MuonParams as MuonParams,
    StopReason as StopReason,
    TensorData as TensorData,
    LossFnOutput as LossFnOutput,
    SampleResult as SampleResult,
    SessionError as SessionError,
    ComputeConfig as ComputeConfig,
    DroLossParams as DroLossParams,
    PpoLossParams as PpoLossParams,
    SessionClient as SessionClient,
    SessionStatus as SessionStatus,
    WandbMetadata as WandbMetadata,
    CheckpointType as CheckpointType,
    DppoLossParams as DppoLossParams,
    GrpoLossParams as GrpoLossParams,
    ModelResources as ModelResources,
    SamplingParams as SamplingParams,
    WeightSyncType as WeightSyncType,
    CispoLossParams as CispoLossParams,
    ModelInputChunk as ModelInputChunk,
    OperationFuture as OperationFuture,
    OptimizerConfig as OptimizerConfig,
    OptimStepResult as OptimStepResult,
    SampledSequence as SampledSequence,
    SessionMetadata as SessionMetadata,
    EncodedTextChunk as EncodedTextChunk,
    SessionErrorCode as SessionErrorCode,
    CheckpointVariant as CheckpointVariant,
    WeightsSyncResult as WeightsSyncResult,
    TrainingCheckpoint as TrainingCheckpoint,
    InferenceCheckpoint as InferenceCheckpoint,
    MuonScalingStrategy as MuonScalingStrategy,
    ModelResourcesClient as ModelResourcesClient,
    ModelResourcesStatus as ModelResourcesStatus,
    PolicyVersionSegment as PolicyVersionSegment,
    ForwardBackwardResult as ForwardBackwardResult,
    CrossEntropyLossParams as CrossEntropyLossParams,
    TrainingCheckpointResult as TrainingCheckpointResult,
    InferenceCheckpointResult as InferenceCheckpointResult,
    CustomForwardBackwardResult as CustomForwardBackwardResult,
    __all__ as __all__,
    download_checkpoint as download_checkpoint,
    download_checkpoint_async as download_checkpoint_async,
)

# `post_training.py` is a module. Give it a package path so
# `together.post_training.tinker` (and the other implementation submodules)
# can resolve, then hand those imports to `together.lib.post_training`.
__path__: list[str] = []

_PUBLIC_PREFIX = "together.post_training"
_IMPL_PREFIX = "together.lib.post_training"


class _ImplLoader(importlib.abc.Loader):
    def __init__(self, target: str) -> None:
        self._target = target

    @override
    def create_module(self, spec: ModuleSpec) -> ModuleType:
        del spec
        return importlib.import_module(self._target)

    @override
    def exec_module(self, module: ModuleType) -> None:
        del module


class _ImplFinder(importlib.abc.MetaPathFinder):
    @override
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        del path, target
        if not fullname.startswith(_PUBLIC_PREFIX + "."):
            return None
        target_name = _IMPL_PREFIX + fullname[len(_PUBLIC_PREFIX) :]
        return importlib.util.spec_from_loader(fullname, _ImplLoader(target_name))


def _install_impl_alias() -> None:
    if any(isinstance(finder, _ImplFinder) for finder in sys.meta_path):
        return
    sys.meta_path.insert(0, _ImplFinder())


_install_impl_alias()
