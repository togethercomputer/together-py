# Reinforcement Learning (RL) Training

The RL APIs are exposed under `together.lib.beta.rl`. They are designed around a session-based training loop with
typed inputs for samples, loss configuration, and optimizer steps. This section focuses on the client-side workflow;
the full API reference remains in [api.md](api.md).

## Concepts at a glance

- `ModelResources.create(...)` provisions GPU resources for a base model and waits until `READY`.
- `resources.attach_trainer(...)` starts a training session on those resources and waits until `RUNNING`,
  returning a `Trainer`. Attach more than once for multi-LoRA. Delete the resources when done.
- `Trainer.create(model_resources_id=...)` is the lower-level equivalent of `attach_trainer` when you already
  have a resources ID.
- `Trainer` is the handle you use for sampling, forward/backward, optimization steps, and checkpointing.
- `trainer.compute_logprobs(...)` (and `compute_logprobs_batch(...)`) teacher-force scores arbitrary token sequences on the generator, returning per-token logprobs (for sampler↔trainer KL and cross-service logprob comparisons on a fixed token set).
- Training operations return operation outputs directly.
- After one or more training steps, call `trainer.create_inference_checkpoint()` to snapshot the model,
  then `trainer.download_checkpoint(...)` to pull the weights locally.
- To save/resume from the full training state, call `trainer.create_training_checkpoint()` to get a `checkpoint_id`, stop the trainer, then attach a new trainer with `resume_from_checkpoint_id=checkpoint_id` (and `lora_config` if used) to continue on a new session over the same resources.
- Use `trainer.session` to fetch the full session state from the API (status, checkpoints, step).
- All request data uses typed constructors (`Prompt`, `Sample`, `Loss`, etc.) exported from `together.lib.beta.rl`. Plain dicts also work at runtime since these are `TypedDict`s.

## Quickstart: SFT-style loop (sync)

```python
import os
from together.lib.beta.rl import (
    ModelResources,
    AdamwOptimizerParams,
    Loss,
    Sample,
    SampleLossInputs,
    SampleLossInputsLossMask,
    SampleLossInputsTargetTokens,
    SampleModelInput,
    SampleModelInputChunk,
    SampleModelInputChunkEncodedText,
)

resources = ModelResources.create(
    base_model="Qwen/Qwen3-0.6B",
    api_key=os.environ.get("TOGETHER_API_KEY"),
    base_url=os.environ.get("TOGETHER_RL_BASE_URL"),
    num_generator_replicas=0,  # SFT does not need a generator; provisions a trainer-only resource.
)
trainer = resources.attach_trainer()

tokens = [101, 102, 103]  # your tokenizer output
loss_mask = [0, 1, 1]
target_tokens = [102, 103, 0]

chunk = SampleModelInputChunk(
    encoded_text=SampleModelInputChunkEncodedText(
        tokens=tokens,
    ),
)

samples = [
    Sample(
        model_input=SampleModelInput(chunks=[chunk]),
        loss_inputs=SampleLossInputs(
            loss_mask=SampleLossInputsLossMask(
                data=loss_mask,
                dtype="D_TYPE_INT64",
            ),
            target_tokens=SampleLossInputsTargetTokens(
                data=target_tokens,
                dtype="D_TYPE_INT64",
            ),
        ),
    )
]

loss = Loss(type="LOSS_TYPE_CROSS_ENTROPY")
trainer.forward_backward(samples=samples, loss=loss)

trainer.optim_step(
    adamw_params=AdamwOptimizerParams(
        beta1=0.9, beta2=0.95, weight_decay=0.1, learning_rate=1e-6,
    ),
)
```

## Quickstart: GRPO-style loop (sync)

```python
import os
from together.lib.beta.rl import (
    ModelResources,
    AdamwOptimizerParams,
    Loss,
    LossGrpoParams,
    Prompt,
    PromptChunk,
    PromptChunkEncodedText,
    Sample,
    SamplingParams,
    SampleLossInputs,
    SampleLossInputsGrpoInputs,
    SampleLossInputsGrpoInputsAdvantages,
    SampleLossInputsGrpoInputsGeneratorLogprobs,
    SampleLossInputsLossMask,
    SampleLossInputsTargetTokens,
    SampleModelInput,
    SampleModelInputChunk,
    SampleModelInputChunkEncodedText,
)

resources = ModelResources.create(
    base_model="Qwen/Qwen3-0.6B",
    api_key=os.environ.get("TOGETHER_API_KEY"),
    base_url=os.environ.get("TOGETHER_RL_BASE_URL"),
)
trainer = resources.attach_trainer()

prompt_tokens = [101, 102, 103]  # your tokenizer output
prompt_chunk = PromptChunk(
    encoded_text=PromptChunkEncodedText(
        tokens=prompt_tokens,
    ),
)
prompt = Prompt(chunks=[prompt_chunk])

sampling = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=256)
sample_result = trainer.sample(
    prompt,
    num_samples=4,
    sampling_params=sampling,
)

sequences = sample_result.rollouts[0].sequences
samples = []
for seq in sequences:
    response_tokens = [int(t) for t in (seq.tokens or [])]
    response_logprobs = [float(v) for v in (seq.logprobs or [])]
    model_tokens = prompt_tokens + response_tokens
    loss_mask = [0] * len(prompt_tokens) + [1] * len(response_tokens)
    target_tokens = model_tokens[1:] + [0]
    advantages = [0.0] * len(prompt_tokens) + [1.0] * len(response_tokens)
    logprobs = [0.0] * len(prompt_tokens) + response_logprobs

    chunk = SampleModelInputChunk(
        encoded_text=SampleModelInputChunkEncodedText(
            tokens=model_tokens,
        ),
    )
    samples.append(Sample(
        model_input=SampleModelInput(chunks=[chunk]),
        loss_inputs=SampleLossInputs(
            loss_mask=SampleLossInputsLossMask(
                data=loss_mask,
                dtype="D_TYPE_INT64",
            ),
            target_tokens=SampleLossInputsTargetTokens(
                data=target_tokens,
                dtype="D_TYPE_INT64",
            ),
            grpo_inputs=SampleLossInputsGrpoInputs(
                advantages=SampleLossInputsGrpoInputsAdvantages(
                    data=advantages,
                    dtype="D_TYPE_FLOAT32",
                ),
                generator_logprobs=SampleLossInputsGrpoInputsGeneratorLogprobs(
                    data=logprobs,
                    dtype="D_TYPE_FLOAT32",
                ),
            ),
        ),
    ))

loss = Loss(
    type="LOSS_TYPE_GRPO",
    grpo_params=LossGrpoParams(
        agg_type="GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN",
        beta=0.0,
    ),
)
trainer.forward_backward(samples=samples, loss=loss)

optim = trainer.optim_step(
    adamw_params=AdamwOptimizerParams(
        beta1=0.9, beta2=0.95, weight_decay=0.1, learning_rate=1e-6,
    ),
)
print("step", optim.step)
```

## Multi-LoRA: shared model resources (sync)

Provision GPU resources once with `ModelResources.create(...)`, then attach multiple LoRA training sessions
to them. Each attached trainer is a regular `Trainer` — train, checkpoint, and stop each one independently.

```python
import os
from together.lib.beta.rl import ModelResources, LoraConfigParam

resources = ModelResources.create(
    base_model="Qwen/Qwen3-0.6B",
    api_key=os.environ.get("TOGETHER_API_KEY"),
    base_url=os.environ.get("TOGETHER_RL_BASE_URL"),
)

trainer_a = resources.attach_trainer(lora_config=LoraConfigParam(rank=8, alpha=16))
trainer_b = resources.attach_trainer(lora_config=LoraConfigParam(rank=16, alpha=32))

# ... run forward_backward / optim_step / sample on each trainer independently ...

trainer_a.stop()
trainer_b.stop()
resources.stop()
```

`ModelResources` also works as a context manager; on exit it stops the resources:

```python
with ModelResources.create(base_model="Qwen/Qwen3-0.6B", api_key="...", base_url="...") as resources:
    with resources.attach_trainer() as trainer:
        ...
```

## Training checkpoint: save and resume

Training checkpoints persist full training state (adapter, optimizer, step) so you can stop the session and later start a new session that continues from that state.

**Flow:**

1. Run training (`forward_backward`, `optim_step`, etc.) on the trainer.
2. Call `trainer.create_training_checkpoint()` and wait until the operation completes; read `checkpoint_id`.
3. Stop the trainer.
4. Attach a new trainer with `resume_from_checkpoint_id=checkpoint_id` over the same resources (and optional `lora_config` if you used one).
5. Continue training on the new trainer.

Saved checkpoints also appear on `trainer.session.training_checkpoints`.

```python
from together.lib.beta.rl import ModelResources, Trainer

resources = ModelResources.create(base_model="Qwen/Qwen3-0.6B", api_key="...", base_url="...")
trainer = resources.attach_trainer()
# ... train ...

save_result = trainer.create_training_checkpoint()
checkpoint_id = save_result.checkpoint_id
trainer.stop()

trainer = Trainer.create(
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
ckpt = trainer.create_inference_checkpoint()
print(f"Checkpoint registered as: {ckpt.api_model_name}")

# The checkpoint ID is available via trainer.session
checkpoint_id = trainer.session.inference_checkpoints[-1].id

# Download merged weights to a local directory
from pathlib import Path

paths = trainer.download_checkpoint(
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

client = Together(api_key="...", base_url="...")

# Get the registered model name from the checkpoint
ckpt = trainer.session.inference_checkpoints[-1]
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
    min_replicas=1,
    max_replicas=1,
    inactive_timeout=10,
)

# Wait for the endpoint to be ready
while endpoint.state != "STARTED":
    time.sleep(5)
    print(f"Endpoint state: {endpoint.state}")
    endpoint = client.endpoints.get(endpoint.id)

# Run inference
response = client.chat.completions.create(
    model=endpoint.name,
    messages=[{"role": "user", "content": "How are you today?"}],
    max_tokens=1000,
)
print(response.choices[0].message.content)
```

## Async usage

Trainer methods are synchronous by default. For async workflows, use the `*_async` methods:

```python
import os
import asyncio
from together.lib.beta.rl import (
    ModelResources,
    Prompt,
    PromptChunk,
    PromptChunkEncodedText,
)


async def main() -> None:
    resources = await ModelResources.create_async(
        base_model="Qwen/Qwen3-0.6B",
        api_key=os.environ.get("TOGETHER_API_KEY"),
        base_url=os.environ.get("TOGETHER_RL_BASE_URL"),
    )
    trainer = await resources.attach_trainer_async()
    prompt_chunk = PromptChunk(
        encoded_text=PromptChunkEncodedText(
            tokens=[101, 102, 103],
        ),
    )
    prompt = Prompt(chunks=[prompt_chunk])
    await trainer.sample_async(prompt)


asyncio.run(main())
```

`ModelResources` follows the same split: `create_async`, `attach_trainer_async`, `retrieve_async`, and
`stop_async`, plus `async with` support.

## Trainer lifecycle

1. Provision resources with `ModelResources.create(...)`, then attach a trainer with `resources.attach_trainer(...)` (or `Trainer.create(model_resources_id=...)`).
2. Use the `Trainer` methods to run `sample`, `forward_backward`, and `optim_step` operations.
3. Optionally call `create_inference_checkpoint()` to snapshot the model and `download_checkpoint(...)` to pull weights locally.
4. To pause and resume later: `trainer.create_training_checkpoint()` → save `checkpoint_id`, `trainer.stop()`, then attach a new trainer with `resume_from_checkpoint_id=...` over the same resources.
5. Close the trainer when finished (context manager or `stop()`).

Attach more than one trainer to the same resources for multi-LoRA, and stop the resources after stopping the
trainers.

## Configuration notes

- Use `TOGETHER_RL_BASE_URL` or `base_url=...` to point to the RL service.
- `TOGETHER_RL_MAX_CONNECTIONS` (default `256`) caps the underlying httpx connection pool (both `max_connections` and `max_keepalive_connections`). Raise it when many operations run concurrently and you see requests queueing on the client.
- `TOGETHER_RL_THREAD_POOL_SIZE` widens the event loop's default thread pool used by multi-turn rollouts, which bridge synchronous, network-blocking env steps onto the loop via `asyncio.to_thread`. Set it to roughly your peak concurrent env steps when the default pool becomes the bottleneck; if unset, the asyncio default is used.

---

## API Reference

### `Trainer.create`

```python
from together.lib.beta.rl import Trainer
```

Creates a training session and polls until it reaches `RUNNING` status.

```python
Trainer.create(
    *,
    model_resources_id: str,
    api_key: str | None = None,
    base_url: str | httpx.URL | None = None,
    resume_from_checkpoint_id: str | None = None,
    lora_config: LoraConfigParam | None = None,
    optimizer_config: OptimizerConfigParam | None = None,
    timeout: float | None = 3600.0,
    interval: float = 10.0,
) -> Trainer
```

Attaches a session to existing model resources. To start from a base model, provision resources first with
[`ModelResources.create`](#modelresourcescreate) (or use `resources.attach_trainer(...)`).

| Parameter                   | Type            | Default      | Description                                                     |
| --------------------------- | --------------- | ------------ | --------------------------------------------------------------- |
| `model_resources_id`        | `str`           | _(required)_ | ID of the model resources to attach to (see [ModelResources](#modelresourcescreate)). The base model and session type are inherited from the resources. |
| `api_key`                   | `str \| None`   | `None`       | API key; defaults to `TOGETHER_API_KEY` if omitted.             |
| `base_url`                  | `str \| httpx.URL \| None` | `None` | Base URL; defaults to Together default or `TOGETHER_BASE_URL`. |
| `resume_from_checkpoint_id` | `str \| None`   | `None`       | Training checkpoint ID to resume from. |
| `lora_config`   | `LoraConfigParam \| None`  | `None`       | Optional LoRA adapter config (see [LoRA config](#lora-config)). |
| `optimizer_config` | `OptimizerConfigParam \| None` | `None` | Optional optimizer selection and hyperparameters for the session. |
| `timeout`       | `float \| None` | `3600.0`     | Max seconds to wait. `None` waits indefinitely.                 |
| `interval`      | `float`         | `10.0`       | Polling interval in seconds.                                    |

**Returns:** a `Trainer` once the underlying session is `RUNNING`.

**Raises:**

- `RuntimeError` -- if the session enters a terminal status (`STOPPED`, `STOPPING`, `ERROR`, `EXPIRED`).
- `TimeoutError` -- if `timeout` is exceeded before the session is ready.

---

### `Trainer`

```python
from together.lib.beta.rl import Trainer
```

A dataclass that wraps a running training session. Returned by `Trainer.create(...)` and `Trainer.create_async(...)`.

#### Properties

| Property  | Type              | Description                                                            |
| --------- | ----------------- | ---------------------------------------------------------------------- |
| `session` | `TrainingSession` | Fetches full session state from the API (status, checkpoints, step).   |

Client and event loop internals are private implementation details.

#### `trainer.sample(...)`

Generates text completions with logprobs from the current model.

```python
def sample(
    prompt: Prompt,
    num_samples: int | None = None,
    sampling_params: SamplingParams | None = None,
) -> SampleResult

def sample_batch(
    prompts: Iterable[Prompt],
    num_samples: int | None = None,
    sampling_params: SamplingParams | None = None,
) -> SampleResult
```

| Parameter         | Type                          | Default      | Description                                                |
| ----------------- | ----------------------------- | ------------ | ---------------------------------------------------------- |
| `prompt`          | `Prompt`                      | _(required)_ | A tokenized prompt represented as a model input dict.      |
| `num_samples`     | `int \| None`                 | `None`       | Number of completions to generate per prompt (server default: 1). |
| `sampling_params` | `SamplingParams \| None`      | `None`       | Sampling configuration dict.                               |

Use `sample_batch` with `Iterable[Prompt]` to sample multiple prompts in one operation.

A prompt has the shape:

```python
prompt_chunk = PromptChunk(
    encoded_text=PromptChunkEncodedText(
        tokens=[101, 102, 103],
    ),
)
Prompt(chunks=[prompt_chunk])
```

**Returns:** `SampleResult`. The resolved value has `.rollouts`, where each rollout has `.sequences` (`SampleSequence`):

| Field         | Type                   | Description                                  |
| ------------- | ---------------------- | -------------------------------------------- |
| `tokens`      | `list[str]`            | Generated token IDs (as strings).            |
| `logprobs`    | `list[float] \| None`  | Log probability for each generated token.    |
| `stop_reason` | `str`                  | Reason generation stopped (e.g. `"length"`). |

#### `trainer.compute_logprobs(...)`

Teacher-force scores an existing token sequence on the generator, returning the log-probability
of each prompt token under the current policy. Unlike `trainer.sample`, which reports logprobs
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

**Returns:** `list[float]` — per-token logprobs for the prompt, following the generator's
prompt-logprob convention (`log P(tokenᵢ | token_<i)`, offset by one from the input tokens).
Like `sample`, it requires a session with a generator replica.

Use `trainer.compute_logprobs_batch(prompts: Iterable[ModelInput]) -> list[list[float]]` to score
several sequences in one call (mirroring `sample` / `sample_batch`); it returns one list of
per-token logprobs per input prompt.

#### `trainer.forward_backward(...)`

Runs a forward and backward pass to compute gradients.

```python
def forward_backward(
    *,
    samples: Iterable[Sample],
    loss: Loss,
) -> ForwardBackwardResult
```

| Parameter | Type                | Default      | Description                                                    |
| --------- | ------------------- | ------------ | -------------------------------------------------------------- |
| `samples` | `Iterable[Sample]`  | _(required)_ | Batch of training samples (see [Training sample](#training-sample)). |
| `loss`    | `Loss`              | _(required)_ | Loss configuration (see [Loss configs](#loss-configurations)). |

**Returns:** `ForwardBackwardResult`. The resolved value has:

| Field     | Type               | Description                                                                          |
| --------- | ------------------ | ------------------------------------------------------------------------------------ |
| `loss`    | `float`            | Scalar loss value for the batch.                                                     |
| `metrics` | `dict[str, float]` | Loss-specific metrics (e.g. `loss/clip/high_fraction`, `loss/kl_ref/mean` for GRPO). |

#### `trainer.optim_step(...)`

Applies accumulated gradients and updates model parameters.

```python
def optim_step(
    *,
    weight_sync_type: WeightSyncType = "WEIGHT_SYNC_TYPE_UNSPECIFIED",
    adamw_params: AdamwOptimizerParams | None = None,
    muon_params: MuonOptimizerParams | None = None,
    max_grad_norm: float | None = None,
) -> OptimStepResult
```

| Parameter          | Type                          | Default                            | Description                                                                    |
| ------------------ | ----------------------------- | ---------------------------------- | ------------------------------------------------------------------------------ |
| `weight_sync_type` | `WeightSyncType`              | `"WEIGHT_SYNC_TYPE_UNSPECIFIED"`   | How the trainer's updated weights are propagated to the generator after the step. |
| `adamw_params`     | `AdamwOptimizerParams \| None`| `None`                             | Per-step AdamW optimizer overrides.                                            |
| `muon_params`      | `MuonOptimizerParams \| None` | `None`                             | Per-step Muon optimizer overrides.                                             |
| `max_grad_norm`    | `float \| None`               | `None`                             | Gradients across all model parameters are clipped to this value.               |

`adamw_params` fields:

| Field           | Type    | Server default | Description                        |
| --------------- | ------- | -------------- | ---------------------------------- |
| `beta1`         | `float` | `0.9`          | First moment decay rate.           |
| `beta2`         | `float` | `0.95`         | Second moment decay rate.          |
| `eps`           | `float` | `1e-8`         | Epsilon for numerical stability.   |
| `learning_rate` | `float` | —              | Learning rate for the AdamW-tuned parameters. |
| `weight_decay`  | `float` | `0.1`          | Weight decay coefficient.          |

`muon_params` fields:

| Field                | Type                    | Description                                                       |
| -------------------- | ----------------------- | ---------------------------------------------------------------- |
| `learning_rate`      | `float`                 | Learning rate for this Muon optimizer step.                      |
| `momentum`           | `float`                 | Momentum coefficient.                                            |
| `newton_schulz_steps`| `int`                   | Number of Newton-Schulz iterations.                              |
| `weight_decay`       | `float`                 | Weight decay coefficient.                                        |
| `adamw`              | `AdamwOptimizerParams`  | AdamW overrides for the AdamW-tuned parameters in a Muon session. |

**Returns:** `OptimStepResult`. The step counter is at `.step`.

#### `trainer.create_inference_checkpoint()`

Snapshots the current model state into a downloadable inference checkpoint.

```python
def create_inference_checkpoint() -> InferenceCheckpointResult
```

**Returns:** `InferenceCheckpointResult`. The resolved value has `.api_model_name` — the registered model name for the checkpoint.

After the operation completes, the checkpoint appears in the session's `inference_checkpoints` list
(visible via `trainer.session`).

#### `trainer.create_training_checkpoint()`

Saves full training state (adapter + optimizer + step) to storage so you can later resume from it.

```python
def create_training_checkpoint() -> TrainingCheckpointResult
```

**Returns:** `TrainingCheckpointResult`. The resolved value has `.checkpoint_id` — the ID to pass as `resume_from_checkpoint_id` when creating a new trainer.

After the operation completes, the checkpoint appears in the session's `training_checkpoints` list
(visible via `trainer.session`).

#### `trainer.download_checkpoint(...)`

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

#### `trainer.stop()`

Stops the training session. Called automatically when using `Trainer` as a context manager.

#### Context manager

`Trainer` supports the `with` statement. On exit it calls `stop()` automatically:

```python
from together.lib.beta.rl import (
    ModelResources,
    Prompt,
    PromptChunk,
    PromptChunkEncodedText,
)

with ModelResources.create(
    base_model="Qwen/Qwen3-0.6B",
    api_key="...",
    base_url="...",
) as resources:
    with resources.attach_trainer() as trainer:
        prompt_chunk = PromptChunk(
            encoded_text=PromptChunkEncodedText(
                tokens=[101, 102, 103],
            ),
        )
        prompt = Prompt(chunks=[prompt_chunk])
        trainer.sample(prompt)
```

---

### `ModelResources.create`

```python
from together.lib.beta.rl import ModelResources
```

Provisions shared GPU model resources and polls until they reach `READY` status. Multiple LoRA training
sessions can then be attached via `attach_trainer`.

```python
ModelResources.create(
    *,
    base_model: str,
    api_key: str | None = None,
    base_url: str | httpx.URL | None = None,
    lora_enabled: bool = True,
    num_generator_replicas: int = 1,
    timeout: float | None = 3600.0,
    interval: float = 10.0,
) -> ModelResources
```

| Parameter       | Type            | Default      | Description                                                     |
| --------------- | --------------- | ------------ | --------------------------------------------------------------- |
| `base_model`    | `str`           | _(required)_ | Base model name (e.g. `"Qwen/Qwen3-0.6B"`).                     |
| `api_key`       | `str \| None`   | `None`       | API key; defaults to `TOGETHER_API_KEY` if omitted.             |
| `base_url`      | `str \| httpx.URL \| None` | `None` | Base URL; defaults to Together default or `TOGETHER_BASE_URL`. |
| `lora_enabled`  | `bool`          | `True`       | Enable LoRA adapters on the provisioned resources.              |
| `num_generator_replicas` | `int`  | `1`          | Number of generator replicas to provision. `0` runs the trainer only, with no generator. |
| `timeout`       | `float \| None` | `3600.0`     | Max seconds to wait. `None` waits indefinitely.                 |
| `interval`      | `float`         | `10.0`       | Polling interval in seconds.                                    |

**Returns:** a `ModelResources` once the underlying resources are `READY`.

**Raises:**

- `RuntimeError` -- if the resources enter a terminal status (`ERROR`, `STOPPING`, `STOPPED`).
- `TimeoutError` -- if `timeout` is exceeded before the resources are ready.

On failure the partially created resources are stopped automatically.

---

### `ModelResources`

A dataclass that wraps provisioned model resources. Returned by `ModelResources.create(...)` and
`ModelResources.create_async(...)`.

#### Properties

| Property             | Type  | Description                          |
| -------------------- | ----- | ------------------------------------ |
| `model_resources_id` | `str` | ID of the provisioned resources.     |

#### `resources.attach_trainer(...)`

Creates a training session on these resources and polls until it reaches `RUNNING` status.

```python
def attach_trainer(
    *,
    lora_config: LoraConfigParam | None = None,
    timeout: float | None = 3600.0,
    interval: float = 10.0,
) -> Trainer
```

| Parameter     | Type                      | Default  | Description                                                     |
| ------------- | ------------------------- | -------- | --------------------------------------------------------------- |
| `lora_config` | `LoraConfigParam \| None` | `None`   | Optional LoRA adapter config (see [LoRA config](#lora-config)). |
| `timeout`     | `float \| None`           | `3600.0` | Max seconds to wait. `None` waits indefinitely.                 |
| `interval`    | `float`                   | `10.0`   | Polling interval in seconds.                                    |

The trainer inherits the resources' API key, base URL, base model, and session type.

**Returns:** a `Trainer` attached to these resources — same handle as `Trainer.create(...)` returns.

**Raises:** same as `Trainer.create` -- `RuntimeError` on terminal session status, `TimeoutError` on timeout.

#### `resources.retrieve()`

Fetches the current resources state from the API (status, base model).

#### `resources.stop()`

Stops the resources and releases the GPUs. Stop attached trainers first. Called automatically when using
`ModelResources` as a context manager.

---

### Training sample

A training sample has the shape:

```python
chunk = SampleModelInputChunk(
    encoded_text=SampleModelInputChunkEncodedText(
        tokens=[1, 2, 3],
    ),
)
Sample(
    model_input=SampleModelInput(chunks=[chunk]),
    loss_inputs=SampleLossInputs(
        loss_mask=SampleLossInputsLossMask(
            data=[0, 1, 1],
            dtype="D_TYPE_INT64",
        ),
        target_tokens=SampleLossInputsTargetTokens(
            data=[2, 3, 0],
            dtype="D_TYPE_INT64",
        ),
    ),
)
```

`SampleLossInputs` fields:

| Field             | Type                               | When to use                                                                 |
| ----------------- | ---------------------------------- | --------------------------------------------------------------------------- |
| `loss_mask`       | `SampleLossInputsLossMask`        | Required for cross-entropy; optional for GRPO. `1` for tokens that contribute to the loss, `0` otherwise. |
| `target_tokens`   | `SampleLossInputsTargetTokens`    | Always required. Next-token targets (shifted by 1).                         |
| `grpo_inputs`     | `SampleLossInputsGrpoInputs`      | GRPO loss only. See [GRPO loss inputs](#grpo-loss-inputs).                  |

#### GRPO loss inputs

`SampleLossInputsGrpoInputs` contains per-token data for the GRPO loss:

| Field                  | Type                                            | Required      | Description                                                            |
| ---------------------- | ----------------------------------------------- | ------------- | ---------------------------------------------------------------------- |
| `advantages`           | `SampleLossInputsGrpoInputsAdvantages`         | Yes           | Per-token advantage values.                                            |
| `generator_logprobs`   | `SampleLossInputsGrpoInputsGeneratorLogprobs`  | Yes           | Log probabilities from the generator model.                            |
| `reference_logprobs`   | `SampleLossInputsGrpoInputsReferenceLogprobs`  | If `beta > 0` | Log probabilities from the reference model for KL penalty computation. |

Each tensor TypedDict has `data` (list of floats) and `dtype` (`"D_TYPE_FLOAT32"`).

### Sampling params

Sampling parameters are passed as `SamplingParams` to `trainer.sample(...)`:

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
| `seed`        | `str`   | --              | Random seed for reproducibility.                       |

---

### Loss configurations

The `Loss` TypedDict passed to `forward_backward` controls the loss function.

| Value                     | Description                           |
| ------------------------- | ------------------------------------- |
| `LOSS_TYPE_CROSS_ENTROPY` | Standard next-token prediction (SFT). |
| `LOSS_TYPE_GRPO`          | Group Relative Policy Optimization.   |

#### Cross-entropy (SFT)

```python
loss = Loss(type="LOSS_TYPE_CROSS_ENTROPY")
```

Standard next-token prediction loss. Requires `loss_mask` and `target_tokens` in `loss_inputs`.

#### GRPO

```python
loss = Loss(
    type="LOSS_TYPE_GRPO",
    grpo_params=LossGrpoParams(
        agg_type="GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN",
        beta=0.0,
    ),
)
```

`grpo_params` fields:

| Field       | Type    | Default                                    | Description                                                                               |
| ----------- | ------- | ------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `agg_type`  | `str`   | `GRPO_LOSS_AGGREGATION_TYPE_FIXED_HORIZON` | How to aggregate per-token loss (see below).                                              |
| `beta`      | `float` | `0.0`                                      | KL penalty coefficient. When > 0, `reference_logprobs` must be provided in `grpo_inputs`. |
| `clip_low`  | `float` | `0.2`                                      | Lower clip bound for the importance-sampling ratio.                                       |
| `clip_high` | `float` | `0.28`                                     | Upper clip bound for the importance-sampling ratio.                                       |

Aggregation types:

| Value                                      | Description                          |
| ------------------------------------------ | ------------------------------------ |
| `GRPO_LOSS_AGGREGATION_TYPE_FIXED_HORIZON` | Fixed-horizon aggregation (default). |
| `GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN`    | Mean over valid tokens.              |

Requires `target_tokens` and `grpo_inputs` (with `advantages`, `generator_logprobs`, and optionally `reference_logprobs`) in `loss_inputs`; `loss_mask` is optional.

---

### LoRA config

When creating a trainer with a LoRA adapter, pass `LoraConfigParam` to `lora_config`:

```python
from together.lib.beta.rl import ModelResources, LoraConfigParam

resources = ModelResources.create(base_model="Qwen/Qwen3-0.6B", api_key="...", base_url="...")
trainer = resources.attach_trainer(
    lora_config=LoraConfigParam(alpha=16, dropout=0.05, rank=8),
)
```

| Field     | Type    | Default | Description                                 |
| --------- | ------- | ------- | ------------------------------------------- |
| `rank`    | `int`   | `8`     | Rank of the low-rank adapter matrices.      |
| `alpha`   | `int`   | `16`    | LoRA scaling factor.                        |
| `dropout` | `float` | `0.05`  | Dropout probability applied to LoRA layers. |
