"""Compatibility alias for :mod:`together.post_training`.

The public names below are the old ``together.lib.beta.rl`` import path.
Submodule imports (``together.lib.beta.rl.tinker`` and the rest) resolve to the
same module objects as ``together.lib.post_training.*``.
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

from together.post_training import (
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

_OLD_PREFIX = "together.lib.beta.rl"
_NEW_PREFIX = "together.lib.post_training"


class _AliasLoader(importlib.abc.Loader):
    def __init__(self, target: str) -> None:
        self._target = target
        self._real_spec: ModuleSpec | None = None

    @override
    def create_module(self, spec: ModuleSpec) -> ModuleType:
        del spec
        module = importlib.import_module(self._target)
        # importlib overwrites ``__spec__`` after create_module returns. Relative
        # imports compare ``__package__`` to ``__spec__.parent``, so keep the
        # implementation spec.
        self._real_spec = module.__spec__
        return module

    @override
    def exec_module(self, module: ModuleType) -> None:
        if self._real_spec is not None:
            module.__spec__ = self._real_spec


class _AliasFinder(importlib.abc.MetaPathFinder):
    @override
    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        del path, target
        if not fullname.startswith(_OLD_PREFIX + "."):
            return None
        target_name = _NEW_PREFIX + fullname[len(_OLD_PREFIX) :]
        return importlib.util.spec_from_loader(fullname, _AliasLoader(target_name))


def _install_submodule_alias() -> None:
    if any(isinstance(finder, _AliasFinder) for finder in sys.meta_path):
        return
    sys.meta_path.insert(0, _AliasFinder())


_install_submodule_alias()
