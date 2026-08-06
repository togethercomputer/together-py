"""Tinker-compatible entry point for RL training.

For the RL training-loop subset described in ``RL_README.md``, a script written
against the ``tinker`` SDK runs on Together by changing only its import line::

    import together.lib.beta.rl.tinker as tinker

Types are the genuine ``tinker`` ones (re-exported below), so objects built by
``tinker_cookbook`` — renderer prompts, ``Datum``s — pass through unchanged; only
the service client swaps. ``forward_backward`` returns a genuine
``ForwardBackwardOutput`` whose ``.metrics`` includes Together's total loss under
``loss:sum``, but per-datum ``loss_fn_outputs`` are always empty.
"""

from __future__ import annotations

from ._compat import types as types
from ._futures import _Pending as APIFuture
from ._service import ServiceClient as ServiceClient
from ._sampling import SamplingClient as SamplingClient
from ._training import TrainingClient as TrainingClient

AdamParams = types.AdamParams
Checkpoint = types.Checkpoint
CheckpointType = types.CheckpointType
Datum = types.Datum
DmelChunk = types.DmelChunk
EncodedTextChunk = types.EncodedTextChunk
ForwardBackwardOutput = types.ForwardBackwardOutput
LoraConfig = types.LoraConfig
ModelID = types.ModelID
ModelInput = types.ModelInput
ModelInputChunk = types.ModelInputChunk
OptimStepRequest = types.OptimStepRequest
OptimStepResponse = types.OptimStepResponse
ParsedCheckpointTinkerPath = types.ParsedCheckpointTinkerPath
SampleRequest = types.SampleRequest
SampleResponse = types.SampleResponse
SampledSequence = types.SampledSequence
SamplingParams = types.SamplingParams
StopReason = types.StopReason
TensorData = types.TensorData
TensorDtype = types.TensorDtype
TrainingRun = types.TrainingRun

__all__ = [
    "APIFuture",
    "AdamParams",
    "Checkpoint",
    "CheckpointType",
    "Datum",
    "DmelChunk",
    "EncodedTextChunk",
    "ForwardBackwardOutput",
    "LoraConfig",
    "ModelID",
    "ModelInput",
    "ModelInputChunk",
    "OptimStepRequest",
    "OptimStepResponse",
    "ParsedCheckpointTinkerPath",
    "SampleRequest",
    "SampleResponse",
    "SampledSequence",
    "SamplingClient",
    "SamplingParams",
    "ServiceClient",
    "StopReason",
    "TensorData",
    "TensorDtype",
    "TrainingClient",
    "TrainingRun",
    "types",
]
