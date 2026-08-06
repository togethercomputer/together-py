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
weights = [0.0, 1.0, 1.0]
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
                dtype="D_TYPE_FLOAT32",
            ),
            target_tokens=LossTargetTokens(
                data=target_tokens,
                dtype="D_TYPE_INT64",
            ),
        ),
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
    weights = [0.0] * len(prompt_tokens) + [1.0] * len(response_tokens)
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
                dtype="D_TYPE_FLOAT32",
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
sync = session.training.weights_sync(
    weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
)
print("step", optim.step, "weights_version", int(sync.weights_version))
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

1. Run training (`forward_backward`, `optim_step`, `weights_sync`, etc.) through `session.training`.
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
print(f"Checkpoint registered as: {ckpt.registered_model_name}")

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
model_name = ckpt.registration.registered_model_name

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

## Tinker-compatible entry point

For the RL training-loop subset described below, a script written against the `tinker` SDK runs on
Together by changing only its import line:

```python
import together.lib.beta.rl.tinker as tinker  # instead of: import tinker
```

Install the optional extra (requires Python >= 3.11); that pulls in `tinker>=0.22.3,<1`:

```bash
pip install 'together[tinker]'
```

Types are the genuine `tinker.types` (`Datum`, `ModelInput`, `SamplingParams`, …), re-exported unchanged,
so objects built by `tinker_cookbook` — renderer prompts, `Datum`s — pass through as-is.

```python
service_client = tinker.ServiceClient()
training_client = service_client.create_lora_training_client(base_model="Qwen/Qwen3-8B", rank=32)

sampling_client = training_client.save_weights_and_get_sampling_client()
result = sampling_client.sample(prompt, num_samples=8, sampling_params=params).result()

training_client.forward_backward(datums, loss_fn="importance_sampling").result()
training_client.optim_step(adam_params).result()
```

### Client surface

`ServiceClient(user_metadata=None, project_id=None, *, base_url=None, api_key=None, model_resources_id=None, **kwargs)`:

- `base_url` / `api_key` select Together's transport.
- `model_resources_id` is a Together extension: attach existing model resources instead of provisioning
  new ones. Attached resources are left running on close; provisioned ones are stopped (see
  [Resource lifecycle](#resource-lifecycle) below).
- `user_metadata`, `project_id`, and other kwargs are accepted and ignored.

`create_lora_training_client` takes the same seven keyword arguments as tinker:

| Argument | Status |
| -------- | ------ |
| `base_model`, `rank` | Honored |
| `seed` | Honored (forwarded into the session LoRA config) |
| `train_mlp`, `train_attn`, `train_unembed` | Accepted; non-`True` values warn and are ignored (Together cannot select trainable modules independently) |
| `user_metadata` | Accepted and ignored |

Training and sampling methods:

- `TrainingClient.forward_backward(data, loss_fn, loss_fn_config=None)` — returns a future of
  tinker's `ForwardBackwardOutput`. See [Loss functions](#loss-functions) for accepted values.
- `TrainingClient.optim_step(adam_params)` — Adam fields are forwarded as-is (including `grad_clip_norm`).
- `TrainingClient.save_weights_and_get_sampling_client(name=None, retry_config=None)` — publishes weights
  synchronously and returns a `SamplingClient`. `name` and `retry_config` are accepted and ignored.
- `SamplingClient.sample(prompt, num_samples, sampling_params, include_prompt_logprobs=False, topk_prompt_logprobs=0)` —
  both prompt-logprob flags are honored; `topk_prompt_logprobs` must be in `0..20` or a `ValueError` is raised.
- `future.result(timeout=None)` — polls to completion. Pass a float to bound polling; omit or pass `None`
  to wait indefinitely.

### Loss functions

The converter expects each `Datum.loss_fn_inputs` to carry `target_tokens`, `logprobs`, and `advantages`
(as `TensorData`) and maps them into Together's `{loss}_inputs` wire shape. Only losses that fit that
shape are accepted:

| `loss_fn` | Status | Notes |
| --------- | ------ | ----- |
| `importance_sampling` | Supported | No `loss_fn_config` keys |
| `ppo` | Supported | Optional `loss_fn_config`: `clip_low_threshold`, `clip_high_threshold` |
| `cross_entropy` | Rejected | Datum carries `weights`, not `logprobs` / `advantages` |
| `cispo`, `dro` | Rejected | Converter only emits the `{logprobs, advantages}` pair and would silently drop any extra Datum keys |

Unknown `loss_fn_config` keys raise `ValueError`.

### Limitations

- **Empty `loss_fn_outputs`.** `forward_backward(...).result()` is a genuine
  `tinker.ForwardBackwardOutput`. Together's total loss is published as `metrics["loss:sum"]`
  (plus any Together-native metric keys), so scripts that only read `.metrics` keep working.
  `loss_fn_outputs` is always `[]` — Together does not return per-datum logprobs, and inventing
  them would silently corrupt training. Accesses like `result.loss_fn_outputs[i]["logprobs"]`
  (used in `tinker_cookbook/rl/train.py`, `supervised/train.py`, and several tutorials) therefore
  fail; those scripts need to skip per-datum logprobs here.
- **Sampling clients are not weight snapshots.** Together's sampler serves the most recently published
  weights. After a later `save_weights_and_get_sampling_client()`, sampling on an earlier client raises
  `RuntimeError` rather than silently using the wrong policy. This breaks DPO-style frozen reference
  clients held across training steps, and pipelined/off-policy loops that keep sampling from an older
  client while training advances. Re-create the sampling client after each publish.
- **Token-id stop sequences are dropped.** Together's wire `stop` field is strings only. Integer stops
  are ignored with a warning; generation then relies on the model's own end token, so trajectories can
  differ from tinker when a dropped token is not that end token. Cookbook renderers often emit non-EOS
  stops (e.g. `GptOssRenderer`'s `<|return|>` / `<|call|>`, `Llama3Renderer`'s `<|eot_id|>`) — pass
  those as strings if you need them enforced.
- **No async.** Futures expose `result(timeout=...)` only — not tinker's `result_async` / `__await__`.
  `*_async` methods and `await future` do not work.
- **No checkpointing.** `save_state`, `load_state`, `create_training_client_from_state`, and
  `save_weights_for_sampler` are absent, as is `RestClient`.

### Resource lifecycle

Together-specific; tinker has no equivalent. Prefer an explicit close:

```python
with service_client.create_lora_training_client(base_model="Qwen/Qwen3-8B", rank=32) as training_client:
    ...
# or: training_client.close()
```

`TrainingClient.close()` (and the context manager) always stops the session this client created. If
`ServiceClient` provisioned the model resources, they are stopped too; if you passed
`model_resources_id=...`, they are only detached and left running.

An interpreter-exit fallback also stops owned resources (registered so it runs before the HTTP client's
executor shuts down). SIGTERM on the main thread is translated to `SystemExit` so that fallback can run.
If automatic teardown fails, the GPUs stay allocated — release them with:

```python
from together.lib.beta.rl import ModelResourcesClient

ModelResourcesClient.attach(model_resources_id="...").stop()
```

## Session lifecycle

1. Provision resources with `ModelResourcesClient.create(...)`, then create a session with `resources.create_session(...)` (or `SessionClient.create(model_resources_id=...)`).
2. Use `session.sampling` for `sample` and `session.training` for `forward_backward`, `optim_step`, and `weights_sync`.
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
| `metadata`                  | `SessionMetadata \| None` | `None` | Auxiliary session metadata, including optional W&B details (see [Session metadata](#session-metadata)). |
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

Fetches the current session state from the API, as a `Session` (see [Session state](#session-state)). Use
`retrieve_async()` in async workflows.

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

Applies accumulated gradients and updates model parameters. Does not make the
updated parameters available for sampling — call `weights_sync` afterwards when
you want subsequent samples to use the updated policy.

**Migration:** `weight_sync_type` is no longer accepted on `optim_step` (passing it
raises `TypeError`). The old default was `WEIGHT_SYNC_TYPE_UNSPECIFIED` (also
removed from the enum); bare `optim_step()` calls previously still sent that
value on the wire. `optim_step` now only applies gradients — it does not publish
weights for sampling. Every loop that samples after an optim step must add
`session.training.weights_sync(weight_sync_type=...)` with an explicit mode
(`SYNCHRONOUS`, `BACKGROUND_PUBLISH`, or `PIPELINE`), even if it never named
`weight_sync_type` before. Without that call, subsequent samples keep using a
stale policy with no client-side error.

Also drop `policy_segments` from training `Sample`s (it is no longer a request
field; `SampleResult.policy_segments` on the response is unchanged). And switch
`Weights` to float data with `dtype="D_TYPE_FLOAT32"` — the old
`dtype="D_TYPE_INT64"` int arrays are no longer the documented contract.

```python
def optim_step(
    *,
    adam_params: AdamParams | None = None,
    muon_params: MuonParams | None = None,
) -> OptimStepResult
```

| Parameter     | Type                 | Default | Description                        |
| ------------- | -------------------- | ------- | ---------------------------------- |
| `adam_params` | `AdamParams \| None` | `None`  | Per-step Adam optimizer overrides. |
| `muon_params` | `MuonParams \| None` | `None`  | Per-step Muon optimizer overrides. |

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

#### `session.training.weights_sync(...)`

Makes the session's current trained parameters available for sampling. Call after
`optim_step` when you want subsequent samples to use the updated policy.

```python
def weights_sync(
    *,
    weight_sync_type: WeightSyncType,
) -> WeightsSyncResult
```

| Parameter          | Type             | Default      | Description                                                                 |
| ------------------ | ---------------- | ------------ | --------------------------------------------------------------------------- |
| `weight_sync_type` | `WeightSyncType` | _(required)_ | How updated parameters are made available for sampling. See values below. |

Accepted `WeightSyncType` values: `"WEIGHT_SYNC_TYPE_SYNCHRONOUS"`,
`"WEIGHT_SYNC_TYPE_BACKGROUND_PUBLISH"`, `"WEIGHT_SYNC_TYPE_PIPELINE"`.

**Returns:** `WeightsSyncResult`. The policy version now available (or queued) for
sampling is at `.weights_version` (`str | int` — coerce with `int(...)` before
comparing to `PolicyVersionSegment.version`, which is always `int`).

#### `session.create_inference_checkpoint()`

Snapshots the current model state into a downloadable inference checkpoint.

```python
def create_inference_checkpoint() -> InferenceCheckpointResult
```

**Returns:** `InferenceCheckpointResult`. The resolved value has `.registered_model_name` — the registered model name for the checkpoint.

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
| `metadata`                  | `SessionMetadata \| None` | `None`   | Auxiliary session metadata, including optional W&B details (see [Session metadata](#session-metadata)). |
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
            data=[0.0, 1.0, 1.0],
            dtype="D_TYPE_FLOAT32",
        ),
        target_tokens=LossTargetTokens(
            data=[2, 3, 0],
            dtype="D_TYPE_INT64",
        ),
    ),
)
```

`Sample` fields:

| Field             | Type                                  | When to use                                                                 |
| ----------------- | ------------------------------------- | --------------------------------------------------------------------------- |
| `model_input` | `ModelInput` | Always required. The full token sequence (prompt + response) to train on. |
| `loss_inputs` | `LossInputs` | Always required. Per-token loss inputs (see below).                       |

`LossInputs` fields:

| Field                        | Type                                | When to use                                                                 |
| ---------------------------- | ----------------------------------- | --------------------------------------------------------------------------- |
| `target_tokens`              | `LossTargetTokens`             | Always required. Next-token targets (shifted by 1).                         |
| `weights`                    | `Weights`                      | Required for cross-entropy `forward_backward`; optional for `forward` and advantage-based losses, where omission includes all tokens. Per-token non-negative floats (`dtype="D_TYPE_FLOAT32"`); cross-entropy honors fractional weights, other losses treat them as a 0/1 mask. |
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

| Field     | Type          | Default | Description                                                                 |
| --------- | ------------- | ------- | --------------------------------------------------------------------------- |
| `rank`    | `int`         | `32`    | Rank of the low-rank adapter matrices (1–64).                               |
| `alpha`   | `int`         | `64`    | LoRA scaling factor (1–128).                                                |
| `dropout` | `float`       | `0.0`   | Dropout probability applied to LoRA layers (0 ≤ x < 1).                     |
| `seed`    | `str \| int` | —       | Random seed for initializing LoRA adapter weights. Ignored when LoRA is disabled or the session resumes from a checkpoint. |

Defaults mirror the server's; only fields you set explicitly are sent, so the server remains authoritative for the rest.

---

### Session state

`session.retrieve()` returns a `Session`, a Pydantic model whose fields are read as attributes:

```python
from together.lib.beta.rl import Session, SessionStatus, SessionError, SessionErrorCode

state = session.retrieve()
if state.status == "TRAINING_SESSION_STATUS_ERROR":
    print(state.error.code, state.error.message)
```

| Field                       | Type                          | Description                                                    |
| --------------------------- | ----------------------------- | -------------------------------------------------------------- |
| `id`                        | `str`                         | ID of the training session.                                    |
| `status`                    | `SessionStatus`               | Current status of the session.                                 |
| `step`                      | `str \| int`                  | Current training step.                                         |
| `model_resources_id`        | `str`                         | Model resources the session runs on.                           |
| `metadata`                  | `SessionMetadata`             | Auxiliary metadata (see [Session metadata](#session-metadata)). |
| `training_checkpoints`      | `list[TrainingCheckpoint]`    | Saved training checkpoints.                                    |
| `inference_checkpoints`     | `list[InferenceCheckpoint]`   | Saved inference checkpoints.                                   |
| `display_name`              | `str \| None`                 | Human-readable name for the session.                           |
| `error`                     | `SessionError \| None`        | Set when the session is in an error state.                     |
| `lora_config`               | Pydantic model \| `None`      | Present only for LoRA-enabled sessions. Read as attributes (`.rank`) — the public `LoraConfig` name is bound to the request type. |
| `resume_from_checkpoint_id` | `str \| None`                 | Training checkpoint this session was resumed from.             |
| `created_at` / `updated_at` | `datetime`                    | Creation and last-update timestamps.                           |
| `created_by`                | `str`                         | ID of the user who created the session.                        |

`SessionStatus` is a string literal type:

| Value | Meaning |
| ----- | ------- |
| `TRAINING_SESSION_STATUS_CREATING` | Provisioning; not yet ready for operations. |
| `TRAINING_SESSION_STATUS_RUNNING`  | Ready. `SessionClient.create(...)` returns here. |
| `TRAINING_SESSION_STATUS_STOPPING` | Shutting down. |
| `TRAINING_SESSION_STATUS_STOPPED`  | Terminal; stopped normally. |
| `TRAINING_SESSION_STATUS_ERROR`    | Terminal; see `error`. |
| `TRAINING_SESSION_STATUS_EXPIRED`  | Terminal; the session outlived its lifetime. |
| `TRAINING_SESSION_STATUS_UNSPECIFIED` | Status not reported. |

`SessionError` carries `code` (`SessionErrorCode`), `message` (user-safe detail), and `occurred_at`
(`datetime`). `SessionErrorCode` is one of `TRAINING_SESSION_ERROR_CODE_RESOURCE_UNAVAILABLE`,
`TRAINING_SESSION_ERROR_CODE_RESOURCE_AT_CAPACITY`, `TRAINING_SESSION_ERROR_CODE_TIMED_OUT`, or
`TRAINING_SESSION_ERROR_CODE_SESSION_FAILED` — branch on `code`, not on `message`.

`TrainingCheckpoint` and `InferenceCheckpoint` both carry `id`, `step`, and `created_at` — pass `id` to
[`download_checkpoint(...)`](#sessiondownload_checkpoint) or `resume_from_checkpoint_id`.
`InferenceCheckpoint` additionally carries `registration` (`None` until the checkpoint is registered), whose
`registered_model_name` and `registered_at` are what [dedicated endpoint
deployment](#deploying-a-checkpoint-as-a-dedicated-endpoint) consumes.

---

### Session metadata

`SessionMetadata` and `WandbMetadata` are `TypedDict`s — plain dicts work, and every field is optional:

```python
from together.lib.beta.rl import ModelResourcesClient, SessionMetadata, WandbMetadata

resources = ModelResourcesClient.create(base_model="Qwen/Qwen3-0.6B", api_key="...", base_url="...")
session = resources.create_session(
    display_name="grpo-run-7",
    metadata=SessionMetadata(wandb=WandbMetadata(entity="my-team", project="rl", run_id="abc123")),
)
```

`SessionMetadata` has a single field, `wandb`, holding a `WandbMetadata`:

| Field      | Type  | Description                                              |
| ---------- | ----- | -------------------------------------------------------- |
| `entity`   | `str` | W&B username or team that owns the project.              |
| `project`  | `str` | W&B project containing the run.                          |
| `group`    | `str` | W&B group used to organize related runs.                 |
| `run_id`   | `str` | Unique identifier assigned to the run by W&B.            |
| `run_name` | `str` | Human-readable name of the run.                          |
| `url`      | `str` | HTTPS URL for the run.                                   |

The fields associate a session with an existing W&B run for your own bookkeeping. The SDK forwards them to
the API unchanged and never creates or writes to the run itself.
