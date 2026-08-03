# Reinforcement Learning (RL) Training

The RL APIs are exposed under `together.lib.beta.rl`. They are designed around a session-based training loop with
typed inputs for samples, loss configuration, and optimizer steps. This section focuses on the client-side workflow;
the full API reference remains in [api.md](api.md).

## Concepts at a glance

- `ModelResourcesClient.create(...)` provisions GPU resources for a base model and waits until `READY`.
- `resources.create_session(...)` starts a session on those resources and waits until `RUNNING`,
  returning a `SessionClient`. Create more than one session for multi-LoRA. Delete the resources when done.
- `SessionClient.create(model_resources_id=...)` is the lower-level equivalent of `create_session` when you already
  have a resources ID.
- `SessionClient` owns lifecycle and checkpoints. Use `session.training` for training operations and
  `session.sampling` for sampling operations. Accessing `session.sampling` on a trainer-only resource raises
  a clear capability error; use `session.has_sampling` when capability discovery is needed.
- `session.sampling.compute_logprobs(...)` (and `compute_logprobs_batch(...)`) teacher-force scores arbitrary token sequences on the generator, returning per-token logprobs (for sampler↔trainer KL and cross-service logprob comparisons on a fixed token set).
- Training operations return operation outputs directly.
- After one or more training steps, call `session.create_inference_checkpoint()` to snapshot the model,
  then `session.download_checkpoint(...)` to pull the weights locally.
- To save/resume from the full training state, call `session.create_training_checkpoint()` to get a `checkpoint_id`, stop the session, then create a new session with `resume_from_checkpoint_id=checkpoint_id` (and `lora_config` if used) over the same resources.
- Use `session.retrieve()` to fetch the full session state from the API (status, checkpoints, step).
- All request data uses typed constructors exported from `together.lib.beta.rl`. Every one of them (`Sample`, `ModelInput`, `LossConfig`, `LossInputs`, `LoraConfig`, `OptimizerConfig`, etc.) is a `TypedDict`, so plain dicts also work at runtime.

## Quickstart: SFT-style loop (sync)

```python
import os
from together.lib.beta.rl import (
    ModelResourcesClient,
    AdamParams,
    EncodedTextChunk,
    LossConfig,
    LossInputs,
    LossTargetTokens,
    ModelInput,
    ModelInputChunk,
    Sample,
    Weights,
)

resources = ModelResourcesClient.create(
    base_model="Qwen/Qwen3-0.6B",
    api_key=os.environ.get("TOGETHER_API_KEY"),
    base_url=os.environ.get("TOGETHER_RL_BASE_URL"),
    num_generator_replicas=0,  # SFT does not need a generator; provisions a trainer-only resource.
)
session = resources.create_session()

tokens = [101, 102, 103]  # your tokenizer output
weights = [0, 1, 1]
target_tokens = [102, 103, 0]

chunk = ModelInputChunk(
    encoded_text=EncodedTextChunk(
        tokens=tokens,
    ),
)

samples = [
    Sample(
        model_input=ModelInput(chunks=[chunk]),
        loss_inputs=LossInputs(
            weights=Weights(
                data=weights,
                dtype="D_TYPE_INT64",
            ),
            target_tokens=LossTargetTokens(
                data=target_tokens,
                dtype="D_TYPE_INT64",
            ),
        ),
        policy_segments=[],
    )
]

loss = LossConfig(type="LOSS_TYPE_CROSS_ENTROPY")
session.training.forward_backward(samples=samples, loss=loss)

session.training.optim_step(
    adam_params=AdamParams(
        beta1=0.9, beta2=0.95, weight_decay=0.1, learning_rate=1e-6,
    ),
)
```

## Quickstart: GRPO-style loop (sync)

```python
import os
from together.lib.beta.rl import (
    ModelResourcesClient,
    AdamParams,
    EncodedTextChunk,
    GrpoLossInputs,
    GrpoLossParams,
    LossAdvantages,
    LossConfig,
    LossInputs,
    LossLogprobs,
    LossTargetTokens,
    ModelInput,
    ModelInputChunk,
    Sample,
    SamplingParams,
    Weights,
)

resources = ModelResourcesClient.create(
    base_model="Qwen/Qwen3-0.6B",
    api_key=os.environ.get("TOGETHER_API_KEY"),
    base_url=os.environ.get("TOGETHER_RL_BASE_URL"),
)
session = resources.create_session()

prompt_tokens = [101, 102, 103]  # your tokenizer output
prompt_chunk = ModelInputChunk(
    encoded_text=EncodedTextChunk(
        tokens=prompt_tokens,
    ),
)
prompt = ModelInput(chunks=[prompt_chunk])

sampling = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=256)
sample_result = session.sampling.sample(
    prompt,
    num_samples=4,
    sampling_params=sampling,
)

samples = []
for seq in sample_result.sequences:
    response_tokens = [int(t) for t in seq.tokens]
    response_logprobs = [float(v) for v in (seq.logprobs or [])]
    model_tokens = prompt_tokens + response_tokens
    weights = [0] * len(prompt_tokens) + [1] * len(response_tokens)
    target_tokens = model_tokens[1:] + [0]
    advantages = [0.0] * len(prompt_tokens) + [1.0] * len(response_tokens)
    logprobs = [0.0] * len(prompt_tokens) + response_logprobs

    chunk = ModelInputChunk(
        encoded_text=EncodedTextChunk(
            tokens=model_tokens,
        ),
    )
    samples.append(Sample(
        model_input=ModelInput(chunks=[chunk]),
        loss_inputs=LossInputs(
            weights=Weights(
                data=weights,
                dtype="D_TYPE_INT64",
            ),
            target_tokens=LossTargetTokens(
                data=target_tokens,
                dtype="D_TYPE_INT64",
            ),
            grpo_inputs=GrpoLossInputs(
                advantages=LossAdvantages(
                    data=advantages,
                    dtype="D_TYPE_FLOAT32",
                ),
                logprobs=LossLogprobs(
                    data=logprobs,
                    dtype="D_TYPE_FLOAT32",
                ),
            ),
        ),
        # Carry the sample result's policy segments over to the training sample.
        policy_segments=[
            {"version": s.version, "start_token": s.start_token}
            for s in sample_result.policy_segments
        ],
    ))

loss = LossConfig(
    type="LOSS_TYPE_GRPO",
    grpo_params=GrpoLossParams(
        agg_type="GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN",
        beta=0.0,
    ),
)
session.training.forward_backward(samples=samples, loss=loss)

optim = session.training.optim_step(
    adam_params=AdamParams(
        beta1=0.9, beta2=0.95, weight_decay=0.1, learning_rate=1e-6,
    ),
)
print("step", optim.step)
```

## Multi-LoRA: shared model resources (sync)

Provision GPU resources once with `ModelResourcesClient.create(...)`, then create multiple LoRA sessions
on them. Each `SessionClient` has independent training state, checkpoints, and lifecycle.

```python
import os
from together.lib.beta.rl import ModelResourcesClient, LoraConfig

resources = ModelResourcesClient.create(
    base_model="Qwen/Qwen3-0.6B",
    api_key=os.environ.get("TOGETHER_API_KEY"),
    base_url=os.environ.get("TOGETHER_RL_BASE_URL"),
)

session_a = resources.create_session(lora_config=LoraConfig(rank=8, alpha=16))
session_b = resources.create_session(lora_config=LoraConfig(rank=16, alpha=32))

# ... use session.training and session.sampling on each session independently ...

session_a.stop()
session_b.stop()
resources.stop()
```

`ModelResourcesClient` also works as a context manager; on exit it stops the resources:

```python
with ModelResourcesClient.create(base_model="Qwen/Qwen3-0.6B", api_key="...", base_url="...") as resources:
    with resources.create_session() as session:
        ...
```

## Training checkpoint: save and resume

Training checkpoints persist full training state (adapter, optimizer, step) so you can stop the session and later start a new session that continues from that state.

**Flow:**

1. Run training (`forward_backward`, `optim_step`, etc.) through `session.training`.
2. Call `session.create_training_checkpoint()` and wait until the operation completes; read `checkpoint_id`.
3. Stop the session.
4. Create a new session with `resume_from_checkpoint_id=checkpoint_id` over the same resources (and optional `lora_config` if you used one).
5. Continue training through the new session's `training` client.

Saved checkpoints also appear on `session.retrieve().training_checkpoints`.

```python
from together.lib.beta.rl import ModelResourcesClient, SessionClient

resources = ModelResourcesClient.create(base_model="Qwen/Qwen3-0.6B", api_key="...", base_url="...")
session = resources.create_session()
# ... train ...

save_result = session.create_training_checkpoint()
checkpoint_id = save_result.checkpoint_id
session.stop()

session = SessionClient.create(
    model_resources_id=resources.model_resources_id,
    api_key="...",
    base_url="...",
    resume_from_checkpoint_id=checkpoint_id,
)
# ... continue training ...
```

## Checkpointing & downloading weights

After training, create an inference checkpoint and download the model weights:

```python
ckpt = session.create_inference_checkpoint()
print(f"Checkpoint registered as: {ckpt.api_model_name}")

# The checkpoint ID is available via session.retrieve()
checkpoint_id = session.retrieve().inference_checkpoints[-1].id

# Download merged weights to a local directory
from pathlib import Path

paths = session.download_checkpoint(
    checkpoint_id,
    variant="CHECKPOINT_VARIANT_MERGED",
    output_dir=Path("./my_checkpoint"),
)
print(f"Downloaded {len(paths)} file(s)")
for p in paths:
    print(f"  {p.name}  ({p.stat().st_size:,} bytes)")
```

To download only the LoRA adapter weights instead, use `variant="CHECKPOINT_VARIANT_ADAPTER"`.

## Deploying a checkpoint as a dedicated endpoint

Once a checkpoint is registered, you can deploy it as a dedicated inference endpoint and query it
through the standard chat completions API:

```python
import time
from together import Together
from together.types import AutoscalingParam

client = Together(api_key="...", base_url="...")

# Get the registered model name from the checkpoint
ckpt = session.retrieve().inference_checkpoints[-1]
model_name = ckpt.registration.api_model_name

# Find available hardware for the model
hardware_list = client.endpoints.list_hardware(
    model=model_name,
)
available = [
    h for h in hardware_list.data
    if h.availability is not None
    and h.availability.status == "available"
]
assert available, "No hardware available for this model"

# Create a dedicated endpoint
endpoint = client.endpoints.create(
    model=model_name,
    hardware=available[0].id,
    autoscaling=AutoscalingParam(min_replicas=1, max_replicas=1),
    inactive_timeout=10,
)

# Wait for the endpoint to be ready
while endpoint.state != "STARTED":
    time.sleep(5)
    print(f"Endpoint state: {endpoint.state}")
    endpoint = client.endpoints.retrieve(endpoint.id)

# Run inference
response = client.chat.completions.create(
    model=endpoint.name,
    messages=[{"role": "user", "content": "How are you today?"}],
    max_tokens=1000,
)
print(response.choices[0].message.content)
```

## Async usage

RL client methods are synchronous by default. For async workflows, use the `*_async` methods:

```python
import os
import asyncio
from together.lib.beta.rl import (
    ModelResourcesClient,
    EncodedTextChunk,
    ModelInput,
    ModelInputChunk,
)


async def main() -> None:
    resources = await ModelResourcesClient.create_async(
        base_model="Qwen/Qwen3-0.6B",
        api_key=os.environ.get("TOGETHER_API_KEY"),
        base_url=os.environ.get("TOGETHER_RL_BASE_URL"),
    )
    session = await resources.create_session_async()
    prompt_chunk = ModelInputChunk(
        encoded_text=EncodedTextChunk(
            tokens=[101, 102, 103],
        ),
    )
    prompt = ModelInput(chunks=[prompt_chunk])
    await session.sampling.sample_async(prompt)


asyncio.run(main())
```

`ModelResourcesClient` follows the same split: `create_async`, `create_session_async`, `retrieve_async`, and
`stop_async`, plus `async with` support.

## Session lifecycle

1. Provision resources with `ModelResourcesClient.create(...)`, then create a session with `resources.create_session(...)` (or `SessionClient.create(model_resources_id=...)`).
2. Use `session.sampling` for `sample` and `session.training` for `forward_backward` and `optim_step`.
3. Optionally call `create_inference_checkpoint()` to snapshot the model and `download_checkpoint(...)` to pull weights locally.
4. To pause and resume later: `session.create_training_checkpoint()` → save `checkpoint_id`, `session.stop()`, then create a new session with `resume_from_checkpoint_id=...` over the same resources.
5. Close the session when finished (context manager or `stop()`).

Create more than one session on the same resources for multi-LoRA, and stop the resources after stopping the
sessions.

## Configuration notes

- Use `TOGETHER_RL_BASE_URL` or `base_url=...` to point to the RL service.
- `TOGETHER_RL_MAX_CONNECTIONS` (default `256`) caps the underlying httpx connection pool (both `max_connections` and `max_keepalive_connections`). Raise it when many operations run concurrently and you see requests queueing on the client.
- `TOGETHER_RL_THREAD_POOL_SIZE` widens the event loop's default thread pool used by multi-turn rollouts, which bridge synchronous, network-blocking env steps onto the loop via `asyncio.to_thread`. Set it to roughly your peak concurrent env steps when the default pool becomes the bottleneck; if unset, the asyncio default is used.

---

## API Reference

### `SessionClient.create`

```python
from together.lib.beta.rl import SessionClient
```

Creates a training session and polls until it reaches `RUNNING` status.

```python
SessionClient.create(
    *,
    model_resources_id: str,
    api_key: str | None = None,
    base_url: str | httpx.URL | None = None,
    display_name: str | None = None,
    metadata: SessionMetadata | None = None,
    resume_from_checkpoint_id: str | None = None,
    lora_config: LoraConfig | None = None,
    timeout: float | None = 3600.0,
    interval: float = 10.0,
) -> SessionClient
```

Attaches a session to existing model resources. To start from a base model, provision resources first with
[`ModelResourcesClient.create`](#modelresourcesclientcreate) (or use `resources.create_session(...)`).

| Parameter                   | Type            | Default      | Description                                                     |
| --------------------------- | --------------- | ------------ | --------------------------------------------------------------- |
| `model_resources_id`        | `str`           | _(required)_ | ID of the model resources to attach to (see [ModelResourcesClient](#modelresourcesclientcreate)). The base model and session type are inherited from the resources. |
| `api_key`                   | `str \| None`   | `None`       | API key; defaults to `TOGETHER_API_KEY` if omitted.             |
| `base_url`                  | `str \| httpx.URL \| None` | `None` | Base URL; defaults to Together default or `TOGETHER_BASE_URL`. |
| `display_name`              | `str \| None`   | `None`       | Human-readable name for the session. |
| `metadata`                  | `SessionMetadata \| None` | `None` | Auxiliary session metadata, including optional W&B details. |
| `resume_from_checkpoint_id` | `str \| None`   | `None`       | Training checkpoint ID to resume from. |
| `lora_config`   | `LoraConfig \| None`  | `None`       | Optional LoRA adapter config (see [LoRA config](#lora-config)). |
| `timeout`       | `float \| None` | `3600.0`     | Max seconds to wait. `None` waits indefinitely.                 |
| `interval`      | `float`         | `10.0`       | Polling interval in seconds.                                    |

**Returns:** a `SessionClient` once the underlying session is `RUNNING`.

**Raises:**

- `RuntimeError` -- if the session enters a terminal status (`STOPPED`, `STOPPING`, `ERROR`, `EXPIRED`).
- `TimeoutError` -- if `timeout` is exceeded before the session is ready.

---

### `SessionClient`

```python
from together.lib.beta.rl import SessionClient
```

A dataclass that owns a running session's lifecycle and checkpoints. Returned by `SessionClient.create(...)`
and `SessionClient.create_async(...)`.

#### Properties

| Property  | Type              | Description                                                            |
| --------- | ----------------- | ---------------------------------------------------------------------- |
| `training` | `TrainingClient` | Session-scoped forward, backward, and optimizer operations.            |
| `has_sampling` | `bool` | Whether the session's MR has a generator. |
| `sampling` | `SamplingClient` | Session-scoped sampling operations. Raises `RuntimeError` when the MR has no generator. |

Client and event loop internals are private implementation details.

#### `session.retrieve()`

Fetches the current session state from the API. Use `retrieve_async()` in async workflows.

#### `session.sampling.sample(...)`

Generates text completions with logprobs from the current model.

```python
def sample(
    prompt: ModelInput,
    num_samples: int | None = None,
    sampling_params: SamplingParams | None = None,
    *,
    prompt_logprobs: bool | None = None,
) -> SampleResult

def sample_batch(
    prompts: Iterable[ModelInput],
    num_samples: int | None = None,
    sampling_params: SamplingParams | None = None,
    *,
    prompt_logprobs: bool | None = None,
) -> list[SampleResult]
```

| Parameter         | Type                          | Default      | Description                                                |
| ----------------- | ----------------------------- | ------------ | ---------------------------------------------------------- |
| `prompt`          | `ModelInput`                  | _(required)_ | A tokenized prompt represented as a model input dict.      |
| `num_samples`     | `int \| None`                 | `None`       | Number of completions to generate per prompt (server default: 1). |
| `sampling_params` | `SamplingParams \| None`      | `None`       | Sampling configuration dict.                               |
| `prompt_logprobs` | `bool \| None`                | `None`       | Also teacher-force score the prompt tokens and return them in `SampleResult.prompt_logprobs`. |

Use `sample_batch` with `Iterable[ModelInput]` to sample multiple prompts in one operation; it returns one
`SampleResult` per prompt, in input order.

A prompt has the shape:

```python
prompt_chunk = ModelInputChunk(
    encoded_text=EncodedTextChunk(
        tokens=[101, 102, 103],
    ),
)
ModelInput(chunks=[prompt_chunk])
```

**Returns:** `SampleResult` — the completions for one prompt:

| Field             | Type                      | Description                                                                                  |
| ----------------- | ------------------------- | -------------------------------------------------------------------------------------------- |
| `sequences`       | `list[SampledSequence]`   | One entry per requested completion (see below).                                              |
| `policy_segments` | `list[PolicyVersionSegment]` | Policy versions that produced these completions. Usually one segment `(version, start_token=0)`; longer generations may span several when the policy was updated mid-generation. |
| `prompt_logprobs` | `list[float] \| None`     | Teacher-forced logprobs for the prompt tokens, one per prompt token (entry 0 is always `0`); present only when `prompt_logprobs=True` was requested (see `session.sampling.compute_logprobs`). |

Each `SampledSequence` has:

| Field         | Type                    | Description                                                          |
| ------------- | ----------------------- | -------------------------------------------------------------------- |
| `tokens`      | `list[str \| int]`      | Generated token IDs.                                                 |
| `logprobs`    | `list[float] \| None`   | Log probability for each generated token.                            |
| `stop_reason` | `StopReason`            | `"STOP_REASON_LENGTH"` or `"STOP_REASON_STOP"`.                      |

#### `session.sampling.compute_logprobs(...)`

Teacher-force scores an existing token sequence on the generator, returning the log-probability
of each prompt token under the current policy. Unlike `session.sampling.sample`, which reports logprobs
only for the tokens the generator *itself drew*, this scores arbitrary/frozen tokens on the
generator — the same measurement path the sampler uses at rollout time. Useful for
sampler↔trainer KL and cross-service logprob comparisons on a fixed token set.

```python
def compute_logprobs(
    prompt: ModelInput,
) -> list[float]
```

| Parameter | Type         | Default      | Description                                 |
| --------- | ------------ | ------------ | ------------------------------------------- |
| `prompt`  | `ModelInput` | _(required)_ | Tokenized sequence to score (see `sample`). |

**Returns:** `list[float]` — per-token logprobs for the prompt (`log P(tokenᵢ | token_<i)`), one entry
per input token. Entry 0 is always `0`, since the first token has no conditioning context.
Like `sample`, it requires a session with a generator replica.

Use `session.sampling.compute_logprobs_batch(prompts: Iterable[ModelInput]) -> list[list[float]]` to score
several sequences in one call (mirroring `sample` / `sample_batch`); it returns one list of
per-token logprobs per input prompt.

#### `session.training.forward_backward(...)`

Runs a forward and backward pass to compute gradients.

```python
def forward_backward(
    *,
    samples: Iterable[Sample],
    loss: LossConfig,
) -> ForwardBackwardResult
```

| Parameter | Type                | Default      | Description                                                    |
| --------- | ------------------- | ------------ | -------------------------------------------------------------- |
| `samples` | `Iterable[Sample]`  | _(required)_ | Batch of training samples (see [Training sample](#training-sample)). |
| `loss`    | `LossConfig`   | _(required)_ | Loss configuration (see [Loss configs](#loss-configurations)). |

**Returns:** `ForwardBackwardResult`. The resolved value has:

| Field     | Type               | Description                                                                          |
| --------- | ------------------ | ------------------------------------------------------------------------------------ |
| `loss`    | `float`            | Scalar loss value for the batch.                                                     |
| `metrics` | `dict[str, float]` | Loss-specific metrics (e.g. `loss/clip/high_fraction`, `loss/kl_ref/mean` for GRPO). |

#### `session.training.optim_step(...)`

Applies accumulated gradients and updates model parameters.

```python
def optim_step(
    *,
    weight_sync_type: WeightSyncType = "WEIGHT_SYNC_TYPE_UNSPECIFIED",
    adam_params: AdamParams | None = None,
    muon_params: MuonParams | None = None,
) -> OptimStepResult
```

| Parameter          | Type                          | Default                            | Description                                                                    |
| ------------------ | ----------------------------- | ---------------------------------- | ------------------------------------------------------------------------------ |
| `weight_sync_type` | `WeightSyncType`              | `"WEIGHT_SYNC_TYPE_UNSPECIFIED"`   | How the trainer's updated weights are propagated to the generator after the step. |
| `adam_params`      | `AdamParams \| None`          | `None`                             | Per-step Adam optimizer overrides.                                             |
| `muon_params`      | `MuonParams \| None`          | `None`                             | Per-step Muon optimizer overrides.                                             |

`adam_params` fields:

| Field            | Type    | Server default | Description                        |
| ---------------- | ------- | -------------- | ---------------------------------- |
| `beta1`          | `float` | `0.9`          | First moment decay rate.           |
| `beta2`          | `float` | `0.95`         | Second moment decay rate.          |
| `eps`            | `float` | `1e-8`         | Epsilon for numerical stability.   |
| `grad_clip_norm` | `float` | `1.0`          | Gradients across all model parameters are clipped to this value; `0` disables clipping. |
| `learning_rate`  | `float` | —              | Learning rate for the Adam-tuned parameters. |
| `weight_decay`   | `float` | `0.1`          | Weight decay coefficient.          |

`muon_params` fields:

| Field                | Type                    | Description                                                       |
| -------------------- | ----------------------- | ---------------------------------------------------------------- |
| `learning_rate`      | `float`                 | Learning rate for this Muon optimizer step.                      |
| `momentum`           | `float`                 | Momentum coefficient.                                            |
| `newton_schulz_steps`| `int`                   | Number of Newton-Schulz iterations.                              |
| `weight_decay`       | `float`                 | Weight decay coefficient.                                        |
| `grad_clip_norm`     | `float`                 | Gradients across all model parameters are clipped to this value; `0` disables clipping. |
| `adam`               | `AdamParams`            | Adam overrides for the Adam-tuned parameters in a Muon session.  |

**Returns:** `OptimStepResult`. The step counter is at `.step`.

#### `session.create_inference_checkpoint()`

Snapshots the current model state into a downloadable inference checkpoint.

```python
def create_inference_checkpoint() -> InferenceCheckpointResult
```

**Returns:** `InferenceCheckpointResult`. The resolved value has `.api_model_name` — the registered model name for the checkpoint.

After the operation completes, the checkpoint appears in the session's `inference_checkpoints` list
(visible via `session.retrieve()`).

#### `session.create_training_checkpoint()`

Saves full training state (adapter + optimizer + step) to storage so you can later resume from it.

```python
def create_training_checkpoint() -> TrainingCheckpointResult
```

**Returns:** `TrainingCheckpointResult`. The resolved value has `.checkpoint_id` — the ID to pass as `resume_from_checkpoint_id` when creating a new session.

After the operation completes, the checkpoint appears in the session's `training_checkpoints` list
(visible via `session.retrieve()`).

#### `session.download_checkpoint(...)`

Downloads all files for a checkpoint to a local directory.

```python
def download_checkpoint(
    checkpoint_id: str,
    *,
    variant: CheckpointVariant = "CHECKPOINT_VARIANT_MERGED",
    output_dir: str | Path = ".",
) -> list[Path]
```

| Parameter       | Type                | Default                       | Description                                                    |
| --------------- | ------------------- | ----------------------------- | -------------------------------------------------------------- |
| `checkpoint_id` | `str`               | _(required)_                  | ID of the inference checkpoint to download.                    |
| `variant`       | `CheckpointVariant` | `"CHECKPOINT_VARIANT_MERGED"` | Download merged full model or adapter-only weights.            |
| `output_dir`    | `str \| Path`       | `"."`                         | Local directory to save files into. Created if it doesn't exist. |

**Returns:** list of `Path` objects pointing to the downloaded files.

#### `session.stop()`

Stops the session. Called automatically when using `SessionClient` as a context manager.

#### Context manager

`SessionClient` supports the `with` statement. On exit it calls `stop()` automatically:

```python
from together.lib.beta.rl import (
    ModelResourcesClient,
    EncodedTextChunk,
    ModelInput,
    ModelInputChunk,
)

with ModelResourcesClient.create(
    base_model="Qwen/Qwen3-0.6B",
    api_key="...",
    base_url="...",
) as resources:
    with resources.create_session() as session:
        prompt_chunk = ModelInputChunk(
            encoded_text=EncodedTextChunk(
                tokens=[101, 102, 103],
            ),
        )
        prompt = ModelInput(chunks=[prompt_chunk])
        session.sampling.sample(prompt)
```

---

### `ModelResourcesClient.create`

```python
from together.lib.beta.rl import ModelResourcesClient
```

Provisions shared GPU model resources and polls until they reach `READY` status. Multiple LoRA training
sessions can then be created via `create_session`.

```python
ModelResourcesClient.create(
    *,
    base_model: str,
    api_key: str | None = None,
    base_url: str | httpx.URL | None = None,
    lora_enabled: bool = True,
    num_generator_replicas: int = 1,
    optimizer_config: OptimizerConfig | None = None,
    timeout: float | None = 3600.0,
    interval: float = 10.0,
) -> ModelResourcesClient
```

| Parameter       | Type            | Default      | Description                                                     |
| --------------- | --------------- | ------------ | --------------------------------------------------------------- |
| `base_model`    | `str`           | _(required)_ | Base model name (e.g. `"Qwen/Qwen3-0.6B"`).                     |
| `api_key`       | `str \| None`   | `None`       | API key; defaults to `TOGETHER_API_KEY` if omitted.             |
| `base_url`      | `str \| httpx.URL \| None` | `None` | Base URL; defaults to Together default or `TOGETHER_BASE_URL`. |
| `lora_enabled`  | `bool`          | `True`       | Enable LoRA adapters on the provisioned resources.              |
| `num_generator_replicas` | `int`  | `1`          | Number of generator replicas to provision. `0` runs the trainer only, with no generator. |
| `optimizer_config` | `OptimizerConfig \| None` | `None` | Optimizer selection and hyperparameters for sessions on these resources, e.g. `OptimizerConfig(muon=...)`. Defaults to AdamW, which can also be selected explicitly with `OptimizerConfig(adamw={})`. |
| `timeout`       | `float \| None` | `3600.0`     | Max seconds to wait. `None` waits indefinitely.                 |
| `interval`      | `float`         | `10.0`       | Polling interval in seconds.                                    |

**Returns:** a `ModelResourcesClient` once the underlying resources are `READY`.

**Raises:**

- `RuntimeError` -- if the resources enter a terminal status (`ERROR`, `STOPPING`, `STOPPED`).
- `TimeoutError` -- if `timeout` is exceeded before the resources are ready.

On failure the partially created resources are stopped automatically.

---

### `ModelResourcesClient`

A dataclass that wraps provisioned model resources. Returned by `ModelResourcesClient.create(...)` and
`ModelResourcesClient.create_async(...)`.

#### Properties

| Property             | Type  | Description                          |
| -------------------- | ----- | ------------------------------------ |
| `model_resources_id` | `str` | ID of the provisioned resources.     |

#### `resources.create_session(...)`

Creates a training session on these resources and polls until it reaches `RUNNING` status.

```python
def create_session(
    *,
    display_name: str | None = None,
    metadata: SessionMetadata | None = None,
    resume_from_checkpoint_id: str | None = None,
    lora_config: LoraConfig | None = None,
    timeout: float | None = 3600.0,
    interval: float = 10.0,
) -> SessionClient
```

| Parameter                   | Type                      | Default  | Description                                                     |
| --------------------------- | ------------------------- | -------- | --------------------------------------------------------------- |
| `display_name`              | `str \| None`             | `None`   | Human-readable name for the session.                            |
| `metadata`                  | `SessionMetadata \| None` | `None`   | Auxiliary session metadata, including optional W&B details.     |
| `resume_from_checkpoint_id` | `str \| None`             | `None`   | Training checkpoint ID to resume from.                          |
| `lora_config`               | `LoraConfig \| None` | `None`   | Optional LoRA adapter config (see [LoRA config](#lora-config)). |
| `timeout`                   | `float \| None`           | `3600.0` | Max seconds to wait. `None` waits indefinitely.                 |
| `interval`                  | `float`                   | `10.0`   | Polling interval in seconds.                                    |

The session inherits the resources' API key, base URL, base model, and session type.

**Returns:** a `SessionClient` on these resources — same handle as `SessionClient.create(...)` returns.

**Raises:** same as `SessionClient.create` -- `RuntimeError` on terminal session status, `TimeoutError` on timeout.

#### `resources.retrieve()`

Fetches the current resources state from the API (status, base model).

#### `resources.stop()`

Stops the resources and releases the GPUs. Stop attached trainers first. Called automatically when using
`ModelResourcesClient` as a context manager.

---

### Training sample

A training sample has the shape:

```python
chunk = ModelInputChunk(
    encoded_text=EncodedTextChunk(
        tokens=[1, 2, 3],
    ),
)
Sample(
    model_input=ModelInput(chunks=[chunk]),
    loss_inputs=LossInputs(
        weights=Weights(
            data=[0, 1, 1],
            dtype="D_TYPE_INT64",
        ),
        target_tokens=LossTargetTokens(
            data=[2, 3, 0],
            dtype="D_TYPE_INT64",
        ),
    ),
    policy_segments=[],
)
```

`Sample` fields:

| Field             | Type                                  | When to use                                                                 |
| ----------------- | ------------------------------------- | --------------------------------------------------------------------------- |
| `model_input`     | `ModelInput`                          | Always required. The full token sequence (prompt + response) to train on.   |
| `loss_inputs`     | `LossInputs`                     | Always required. Per-token loss inputs (see below).                         |
| `policy_segments` | `Iterable[dict]` | Always required. Policy versions that generated these tokens, as `{"version": int, "start_token": int}` dicts; rebuild them from `SampleResult.policy_segments`. Pass `[]` for tokens that did not come from sampling (e.g. SFT data). |

`LossInputs` fields:

| Field                        | Type                                | When to use                                                                 |
| ---------------------------- | ----------------------------------- | --------------------------------------------------------------------------- |
| `target_tokens`              | `LossTargetTokens`             | Always required. Next-token targets (shifted by 1).                         |
| `weights`                    | `Weights`                      | Required for cross-entropy `forward_backward`; optional for `forward` and advantage-based losses, where omission includes all tokens. `1` for tokens that contribute to the loss, `0` otherwise. |
| `grpo_inputs`                | `GrpoLossInputs`               | GRPO loss only. See [GRPO loss inputs](#grpo-loss-inputs).                  |
| `ppo_inputs`                 | `PpoLossInputs`                | PPO loss only.                                                              |
| `cispo_inputs`               | `CispoLossInputs`              | CISPO loss only.                                                            |
| `dro_inputs`                 | `DroLossInputs`                | DRO loss only.                                                              |
| `importance_sampling_inputs` | `ImportanceSamplingLossInputs` | Importance-sampling loss only.                                              |

#### GRPO loss inputs

`GrpoLossInputs` contains per-token data for the GRPO loss:

| Field                  | Type                    | Required      | Description                                                            |
| ---------------------- | ----------------------- | ------------- | ---------------------------------------------------------------------- |
| `advantages`           | `LossAdvantages`   | Yes           | Per-token advantage values.                                            |
| `logprobs`             | `LossLogprobs`     | Yes           | Log probabilities from the generator model.                            |
| `reference_logprobs`   | `LossLogprobs`     | If `beta > 0` | Log probabilities from the reference model for KL penalty computation. |

Each tensor TypedDict has `data` (list of floats) and `dtype` (`"D_TYPE_FLOAT32"`).

### Sampling params

Sampling parameters are passed as `SamplingParams` to `session.sampling.sample(...)`:

```python
SamplingParams(temperature=0.7, top_p=0.9, max_tokens=256)
```

| Field         | Type    | Server default  | Description                                            |
| ------------- | ------- | --------------- | ------------------------------------------------------ |
| `max_tokens`  | `int`   | `100`           | Maximum tokens to generate per completion.             |
| `temperature` | `float` | `1.0`           | Sampling temperature.                                  |
| `top_p`       | `float` | `1.0`           | Nucleus sampling probability threshold.                |
| `top_k`       | `int`   | `-1` (disabled) | Top-k sampling limit.                                  |
| `stop`        | `list[str]` | --          | Stop sequences; generation stops when any is produced. |
| `seed`        | `str \| int` | --             | Random seed for reproducibility.                       |

---

### Loss configurations

The `LossConfig` TypedDict passed to `forward_backward` controls the loss function.

| `type`                          | Params field           | Description                           |
| ------------------------------- | ---------------------- | ------------------------------------- |
| `LOSS_TYPE_CROSS_ENTROPY`       | `cross_entropy_params` | Standard next-token prediction (SFT). |
| `LOSS_TYPE_GRPO`                | `grpo_params`          | Group Relative Policy Optimization.   |
| `LOSS_TYPE_PPO`                 | `ppo_params`           | Proximal Policy Optimization.         |
| `LOSS_TYPE_CISPO`               | `cispo_params`         | Clipped importance-sampling policy optimization. |
| `LOSS_TYPE_DRO`                 | `dro_params`           | Direct Reward Optimization.           |
| `LOSS_TYPE_IMPORTANCE_SAMPLING` | --                     | Plain importance-sampling loss.       |

Short names are accepted too — `type="grpo"` is converted to `"LOSS_TYPE_GRPO"` before the request is sent,
so loop code written against other RL SDKs works unchanged.

#### Cross-entropy (SFT)

```python
loss = LossConfig(type="LOSS_TYPE_CROSS_ENTROPY")
```

Standard next-token prediction loss. Requires `weights` and `target_tokens` in `loss_inputs`.

#### GRPO

```python
loss = LossConfig(
    type="LOSS_TYPE_GRPO",
    grpo_params=GrpoLossParams(
        agg_type="GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN",
        beta=0.0,
    ),
)
```

`grpo_params` fields:

| Field                 | Type    | Default                                    | Description                                                                               |
| --------------------- | ------- | ------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `agg_type`            | `str`   | `GRPO_LOSS_AGGREGATION_TYPE_FIXED_HORIZON` | How to aggregate per-token loss (see below).                                              |
| `beta`                | `float` | `0.0`                                      | KL penalty coefficient. When > 0, `reference_logprobs` must be provided in `grpo_inputs`. |
| `clip_low_threshold`  | `float` | _(server default)_                         | Lower bound the importance-sampling ratio is clamped to (e.g. `0.8`). Must be <= 1.       |
| `clip_high_threshold` | `float` | _(server default)_                         | Upper bound the importance-sampling ratio is clamped to (e.g. `1.2`). Must be >= 1.       |
| `ratio_type`          | `str`   | `GRPO_LOSS_RATIO_TYPE_TOKEN`               | Token-level ratios (standard GRPO) or `GRPO_LOSS_RATIO_TYPE_SEQUENCE` for GSPO-style loss. |

Aggregation types:

| Value                                      | Description                          |
| ------------------------------------------ | ------------------------------------ |
| `GRPO_LOSS_AGGREGATION_TYPE_FIXED_HORIZON` | Fixed-horizon aggregation (default). |
| `GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN`    | Mean over valid tokens.              |
| `GRPO_LOSS_AGGREGATION_TYPE_SEQUENCE_MEAN` | Mean over sequences.                 |

Requires `target_tokens` and `grpo_inputs` (with `advantages`, `logprobs`, and optionally `reference_logprobs`) in `loss_inputs`; `weights` is optional.

---

### LoRA config

When creating a session with a LoRA adapter, pass `LoraConfig` to `lora_config`:

```python
from together.lib.beta.rl import ModelResourcesClient, LoraConfig

resources = ModelResourcesClient.create(base_model="Qwen/Qwen3-0.6B", api_key="...", base_url="...")
session = resources.create_session(
    lora_config=LoraConfig(alpha=16, dropout=0.05, rank=8),
)
```

| Field     | Type    | Default | Description                                 |
| --------- | ------- | ------- | ------------------------------------------- |
| `rank`    | `int`   | `32`    | Rank of the low-rank adapter matrices (1–64). |
| `alpha`   | `int`   | `64`    | LoRA scaling factor (1–128).                |
| `dropout` | `float` | `0.0`   | Dropout probability applied to LoRA layers (0 ≤ x < 1). |

Defaults mirror the server's; only fields you set explicitly are sent, so the server remains authoritative for the rest.
