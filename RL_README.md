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
- `SessionClient` owns session lifecycle and checkpoint creation. Use `session.trainer` for training operations and
  `session.generator` for sampling operations. Accessing `session.generator` on a trainer-only resource raises
  a clear capability error; use `session.has_generator` when capability discovery is needed.
- `session.generator.compute_logprobs(...)` (and `compute_logprobs_batch(...)`) teacher-force scores arbitrary token sequences on the generator, returning per-token logprobs (for sampler↔trainer KL and cross-service logprob comparisons on a fixed token set).
- Training operations return operation outputs directly.
- After one or more training steps, call `session.create_inference_checkpoint()` to snapshot the model,
  then `download_checkpoint(client, ...)` with a configured `Together` client to pull the weights locally.
- To save/resume from the full training state, call `session.create_training_checkpoint()` to get a `checkpoint_id`, stop the session, then create a new session with `resume_from_checkpoint_id=checkpoint_id` (and `lora_config` if used) over the same resources.
- Use `session.retrieve()` to fetch the full session state from the API (status, checkpoints, step).
- All request data uses typed constructors exported from `together.lib.beta.rl`. Every one of them (`Sample`, `ModelInput`, `LossConfig`, `TensorData`, `LoraConfig`, `OptimizerConfig`, etc.) is a `TypedDict`, so plain dicts also work at runtime.

## Quickstart: SFT-style loop (sync)

```python
import os
from together.lib.beta.rl import (
    ModelResourcesClient,
    AdamParams,
    EncodedTextChunk,
    TensorData,
    LossConfig,
    ModelInput,
    ModelInputChunk,
    Sample,
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
        loss_fn_inputs={
            "weights": TensorData(
                data=weights,
                dtype="float32",
            ),
            "target_tokens": TensorData(
                data=target_tokens,
                dtype="int64",
            ),
        },
    )
]

loss = LossConfig(type="LOSS_TYPE_CROSS_ENTROPY")
session.trainer.forward_backward(samples=samples, loss=loss)

session.trainer.optim_step(
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
    TensorData,
    GrpoLossParams,
    LossConfig,
    ModelInput,
    ModelInputChunk,
    Sample,
    SamplingParams,
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
sample_result = session.generator.sample(
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
        loss_fn_inputs={
            "weights": TensorData(
                data=weights,
                dtype="float32",
            ),
            "target_tokens": TensorData(
                data=target_tokens,
                dtype="int64",
            ),
            "advantages": TensorData(
                data=advantages,
                dtype="float32",
            ),
            "logprobs": TensorData(
                data=logprobs,
                dtype="float32",
            ),
        },
    ))

loss = LossConfig(
    type="LOSS_TYPE_GRPO",
    grpo_params=GrpoLossParams(
        agg_type="GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN",
        beta=0.0,
    ),
)
session.trainer.forward_backward(samples=samples, loss=loss)

optim = session.trainer.optim_step(
    adam_params=AdamParams(
        beta1=0.9, beta2=0.95, weight_decay=0.1, learning_rate=1e-6,
    ),
)
sync = session.trainer.weights_sync(
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

# ... use session.trainer and session.generator on each session independently ...

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

1. Run training (`forward_backward`, `optim_step`, `weights_sync`, etc.) through `session.trainer`.
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
from together import Together
from together.lib.beta.rl import download_checkpoint

with Together(api_key="...", base_url="...") as client:
    paths = download_checkpoint(
        client,
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
    await session.generator.sample_async(prompt)


asyncio.run(main())
```

`ModelResourcesClient` follows the same split: `create_async`, `create_session_async`, `retrieve_async`, and
`stop_async`, plus `async with` support.

## Concurrency and event loops

Every RL handle submits work to one process-wide background event loop on a daemon thread named
`together-rl`. The loop starts on first use and is not torn down when a handle stops — `stop()` /
`detach()` only cancel that handle's in-flight work and close its HTTP client. Sync- and async-created
handles share the same loop, so you do not pick a construction color to get a usable concurrency story.

That makes one handle safe to share:

- **Many threads, one session.** Blocking calls from several threads run concurrently on the shared loop
  instead of queueing behind whichever caller holds it.
- **`*_async` from anywhere.** Public `*_async` methods (and `create_async` / `attach_async`) run on the
  process loop, so `asyncio.run(session.generator.sample_async(...))` works after either `create()` or
  `await create_async(...)`. When the caller is already on that loop the hop is a no-op, so
  `asyncio.gather` still overlaps.
- **Your own async work, on the same loop.** `session.run(coro)` drives a caller-owned coroutine — a
  multi-turn rollout, say — on the process loop, tracked so `stop()` cancels it. Work awaited in place
  because the caller was already on that loop is the caller's own coroutine and is not cancelled by
  `stop()`.
- **Blocking calls need a thread of their own.** `sample()`, `forward_backward()`, `stop()` and friends block
  the calling thread and raise if called from inside a running event loop (outside notebooks), where the
  `*_async` variant is the one you want.
- **Notebooks are the exception.** A Jupyter, Colab or qtconsole cell runs under a kernel event loop, and
  blocking calls work there: the cell blocks while the work runs on the process loop. Prefer the `*_async`
  variants for long waits, so the kernel stays responsive.
- **Do not share a handle across `fork`.** Sockets do not survive it; give each worker its own
  `SessionClient` / `ModelResourcesClient`. A `fork` child does not inherit the thread driving the
  background loop, so the loop is rebuilt on first use in the child — new handles work there, inherited
  ones do not.

`TOGETHER_RL_MAX_CONNECTIONS` and `TOGETHER_RL_THREAD_POOL_SIZE` (see
[Configuration notes](#configuration-notes)) are the knobs for how wide that concurrency goes.

Polling is bounded by the connection pool, not by a poll scheduler: every waiting operation polls on its own
fixed `interval` (default 0.5s, no backoff), and once a session's client has `TOGETHER_RL_MAX_CONNECTIONS`
requests in flight the rest queue there instead of reaching the service. On that client a `429` is retried up
to 7 times, honouring `Retry-After` and backing off exponentially otherwise. With many operations waiting at
once, raise `interval` rather than the connection cap. `ModelResourcesClient` polls for provisioning and
stop, and keeps the SDK connection defaults.

## Tinker-compatible entry point

For the RL training-loop subset described below, a script written against the `tinker` SDK runs on
Together by changing only its import line:

```python
import together.lib.beta.rl.tinker as tinker  # instead of: import tinker
```

Install the optional extra (requires Python >= 3.11):

```bash
pip install 'together[tinker]'
```

Types are the genuine `tinker.types` (`Datum`, `ModelInput`, `SamplingParams`, …), resolved via `__getattr__`,
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
- `user_metadata` and `project_id` are accepted and ignored (no warning — tagging/org
  fields that Together does not surface).
- Known Tinker HTTP kwargs (`default_headers`, `default_query`, `http_client`, `max_retries`,
  `timeout`) are accepted and ignored; `http_client` / `max_retries` / `timeout` warn when
  passed (ops knobs a migrator likely tuned), while `default_headers` / `default_query`
  stay silent. Any other kwargs raise `TypeError`.

`create_lora_training_client` takes the same seven keyword arguments as tinker:

| Argument | Status |
| -------- | ------ |
| `base_model`, `rank` | Honored |
| `seed` | Honored (forwarded into the session LoRA config) |
| `train_unembed` | Honored (forwarded into the session LoRA config; defaults to `True`) |
| `train_mlp`, `train_attn` | Accepted; non-`True` values warn and are ignored (Together cannot select those modules independently) |
| `user_metadata` | Accepted and ignored |

Training and sampling methods:

- `TrainingClient.forward(data, loss_fn, loss_fn_config=None, *, return_loss_fn_outputs=True)` —
  a gradient-free scoring pass under `loss_fn`, returning a future of tinker's
  `ForwardBackwardOutput` whose per-datum `loss_fn_outputs[i]["logprobs"]` are the scores the
  loss produced. `loss_fn_config` shapes that loss exactly as it does on `forward_backward`, so
  a position the loss excludes — a zero-`weights` one, say — comes back as exactly `0.0` rather
  than a true log-probability.
- `TrainingClient.forward_backward(data, loss_fn, loss_fn_config=None)` — returns a future of
  tinker's `ForwardBackwardOutput`. The keyword-only `return_loss_fn_outputs=True` reads the same
  per-datum logprobs back alongside the gradient update, under the same masking; left unset it
  follows the service default. See [Loss functions](#loss-functions) for accepted values.
- `TrainingClient.forward_backward_custom(data, loss_fn, *, loss_type_input="logprobs")` —
  two-pass custom loss (forward logprobs → client loss → custom gradients). Requires PyTorch.
- `TrainingClient.optim_step(adam_params)` — Adam fields are forwarded as-is (including `grad_clip_norm`).
- `TrainingClient.save_weights_and_get_sampling_client(name=None, retry_config=None)` — publishes weights
  synchronously and returns a `SamplingClient`. Non-`None` `name` / `retry_config` warn and are
  ignored (no named checkpoints or caller-controlled retries).
- `SamplingClient.sample(prompt, num_samples, sampling_params, include_prompt_logprobs=False, topk_prompt_logprobs=0)` —
  both prompt-logprob flags are honored; `topk_prompt_logprobs` must be in `0..20` or a `ValueError` is raised.
- `SamplingClient.compute_logprobs(prompt)` — returns a future of `list[float | None]` with index 0 as `None`.
- `APIFuture` is Together's shared `OperationFuture`: `.id` exposes the submitted operation ID;
  `.result(timeout=None)`, `.result_async(timeout=None)`, and `await future` poll lazily and cache
  the result. Call `.result()` only outside a running event loop — notebook cells are exempt, as they
  are for the session's own blocking methods. A future awaited from a loop of your own (for example
  inside `asyncio.run(...)`) is bridged onto the shared process loop and polls concurrently, so gathering
  N of them takes about as long as the slowest one.

### Loss functions

The converter serializes genuine Tinker `TensorData` values directly into the generic
`loss_fn_inputs` request shape, preserving lowercase dtypes. Each `loss_fn` declares its own set of
accepted keys (see the table below). A Datum that omits a key the loss requires raises `ValueError`
client-side rather than failing as an opaque server rejection. A Datum carrying a key the loss does
not declare warns and is still sent: `loss_fn_inputs` is an open map on the wire, so an unrecognized
key may be a scratch key or a server input newer than this SDK, and rejecting it would put an SDK
release on the critical path of every new server input.

Tensors must be one-dimensional and dense; anything else raises. Tinker builds a 2-D tensor
whenever `target_tokens` or `weights` come from a 2-D torch tensor — CSR-encoded when that saves
space, dense otherwise — and training operations accept neither. `shape` is not sent: for a 1-D
tensor it is redundant with `len(data)`. Large payloads also strip it from the inline validation
body, where it would otherwise describe the full tensor beside a truncated `data`.

Omitted `loss_fn_config` keys fall through to Together's server defaults. Together's spec pins those
to match Tinker's documented ones (PPO `clip_low_threshold=0.8` / `clip_high_threshold=1.2`; CISPO
`0.0` / `4.0`), so the two backends agree without the client pinning them. Nothing
in this SDK observes those defaults, so the spec owns that guarantee. The current compatibility training client
exposes:

| `loss_fn` | Notes |
| --------- | ----- |
| `cross_entropy` | Datum requires `target_tokens` and `weights`; optional `mask`; no config keys |
| `importance_sampling` | Datum requires `target_tokens`, `logprobs`, `advantages`; optional `weights`, `mask`; no config keys |
| `ppo` | Same Datum keys as `importance_sampling`; optional `loss_fn_config`: `clip_low_threshold`, `clip_high_threshold` |
| `cispo` | Same Datum keys as `importance_sampling`; optional `loss_fn_config`: `clip_low_threshold`, `clip_high_threshold` |
| `dro` | Same Datum keys as `importance_sampling`; required `loss_fn_config`: `beta` |

Unknown `loss_fn_config` keys raise `ValueError` — unlike `loss_fn_inputs`, the config shape is
generated from the spec, so a key outside it is always a caller error.

### Limitations

- **Per-datum clip thresholds.** Tinker recognizes `clip_low_threshold` / `clip_high_threshold` as
  per-token `Datum.loss_fn_inputs` entries. Together takes them only as scalar `loss_fn_config`
  values, so a Datum carrying them draws an "Unsupported keys" `UserWarning` and is forwarded
  unread; pass them through `loss_fn_config` instead.
- **Fractional `weights` outside `cross_entropy`.** Tinker multiplies `weights` into the per-token
  loss for every loss function. Together honors fractional weights only for `cross_entropy`; for the
  policy losses a weight acts as a 0/1 mask (`0` excludes the token, anything non-zero includes it at
  full weight). A Datum carrying fractional `weights` under `importance_sampling`/`ppo`/`cispo`/`dro`
  is accepted and trains, but its gradients differ from Tinker's, so the wrapper warns once per
  call site (Python's default warning filter dedups repeats, so a loop that warns on step 1 will not
  warn again on step 200 — the condition has not gone away). Use `mask` for inclusion/exclusion, and keep
  fractional weighting to `cross_entropy`.
- **`loss_fn_outputs` carry the loss's masking.** Both training calls can return per-datum
  logprobs: `forward` asks for them by default, and `forward_backward` does when passed
  `return_loss_fn_outputs=True`, leaving `loss_fn_outputs` empty otherwise. Either way the
  numbers come out of the loss that scored the batch, so a position that loss excludes — a
  zero-`weights` one, say — reads exactly `0.0` instead of a true log-probability. Tinker's
  `forward` scored under no loss and masked nothing, so accesses like
  `result.loss_fn_outputs[i]["logprobs"]` (used in `tinker_cookbook/rl/train.py`,
  `supervised/train.py`, and several tutorials) only read back true logprobs at positions the
  loss keeps. `forward_backward(...).result()` is still a genuine `tinker.ForwardBackwardOutput`
  whose total loss is published as `metrics["loss:sum"]` (plus any Together-native metric keys),
  so scripts that only read `.metrics` keep working.
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
- **Async matches tinker.** Training `forward_async` / `forward_backward_async` /
  `forward_backward_custom_async` / `optim_step_async` return the same lazy `OperationFuture`
  (exported as `APIFuture`) as the sync methods. `SamplingClient.sample_async` /
  `compute_logprobs_async` await and return their values. `save_weights_and_get_sampling_client_async`
  returns a `SamplingClient`, and `ServiceClient.create_lora_training_client_async` returns a
  `TrainingClient`.
- **No checkpointing.** `save_state`, `load_state`, `create_training_client_from_state`, and
  `save_weights_for_sampler` are absent (deferred to a follow-up), as is `RestClient`.

### Resource lifecycle

Together-specific; tinker has no equivalent. Prefer an explicit close:

```python
with service_client.create_lora_training_client(base_model="Qwen/Qwen3-8B", rank=32) as training_client:
    ...
# or: training_client.close()
```

`TrainingClient.close()` (and the context manager) always stops the session this client created. If
`ServiceClient` provisioned the model resources, they are stopped too; if you passed
`model_resources_id=...`, they are only detached and left running. A notebook cell may call it, exactly
as it may call the session's own blocking methods.

Inside a running event loop, close asynchronously:

```python
async with await service_client.create_lora_training_client_async(base_model="Qwen/Qwen3-8B", rank=32) as training_client:
    ...
# or: await training_client.close_async()
```

An interpreter-exit fallback also stops owned resources from either construction path (registered so it
runs before the HTTP client's executor shuts down). SIGTERM on the main thread is translated to
`SystemExit` so that fallback can run. Explicit close remains preferable because it reports failures
immediately.

If automatic teardown fails, the GPUs stay allocated — release them with:

```python
from together.lib.beta.rl import ModelResourcesClient

ModelResourcesClient.attach(model_resources_id="...").stop()
```

## Session lifecycle

1. Provision resources with `ModelResourcesClient.create(...)`, then create a session with `resources.create_session(...)` (or `SessionClient.create(model_resources_id=...)`).
2. Use `session.generator` for `sample` and `session.trainer` for `forward_backward`, `optim_step`, and `weights_sync`.
3. Optionally call `create_inference_checkpoint()` to snapshot the model and
   `download_checkpoint(client, ...)` to pull weights locally.
4. To pause and resume later: `session.create_training_checkpoint()` → save `checkpoint_id`, `session.stop()`, then create a new session with `resume_from_checkpoint_id=...` over the same resources.
5. Close the session when finished (context manager or `stop()`), then stop its model resources.

Create more than one session on the same resources for multi-LoRA, and stop the resources after stopping the
sessions.

## Configuration notes

- Use `TOGETHER_RL_BASE_URL` or `base_url=...` to point to the RL service.
- `TOGETHER_RL_MAX_CONNECTIONS` (default `256`) caps the underlying httpx connection pool (both `max_connections` and `max_keepalive_connections`). Raise it when many operations run concurrently and you see requests queueing on the client.
- `TOGETHER_RL_THREAD_POOL_SIZE` widens the event loop's default thread pool used by multi-turn rollouts, which bridge synchronous, network-blocking env steps onto the loop via `asyncio.to_thread`. Set it to roughly your peak concurrent env steps when the default pool becomes the bottleneck; if unset, the asyncio default is used. It is read once, when the first handle in the process starts the background loop, and every handle then shares that one pool — set it before creating any handle, and size it for the whole process rather than per session.

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

A dataclass that owns a running session's lifecycle and checkpoint creation. Returned by `SessionClient.create(...)`
and `SessionClient.create_async(...)`.

#### Properties

| Property  | Type              | Description                                                            |
| --------- | ----------------- | ---------------------------------------------------------------------- |
| `trainer` | `Trainer` | Session-scoped forward, backward, and optimizer operations.            |
| `has_generator` | `bool` | Whether the session's MR has a generator. |
| `generator` | `Generator` | Session-scoped sampling operations. Raises `RuntimeError` when the MR has no generator. |

Client and event loop internals are private implementation details.

#### `session.retrieve()`

Fetches the current session state from the API, as a `Session` (see [Session state](#session-state)). Use
`retrieve_async()` in async workflows.

#### `session.generator.sample(...)`

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
| `prompt_logprobs` | `list[float] \| None`     | Teacher-forced logprobs for the prompt tokens, one per prompt token (entry 0 is always `0`); present only when `prompt_logprobs=True` was requested (see `session.generator.compute_logprobs`). |

Each `SampledSequence` has:

| Field         | Type                    | Description                                                          |
| ------------- | ----------------------- | -------------------------------------------------------------------- |
| `tokens`      | `list[str \| int]`      | Generated token IDs.                                                 |
| `logprobs`    | `list[float] \| None`   | Log probability for each generated token.                            |
| `stop_reason` | `StopReason`            | `"STOP_REASON_LENGTH"` or `"STOP_REASON_STOP"`.                      |

#### `session.generator.compute_logprobs(...)`

Teacher-force scores an existing token sequence on the generator, returning the log-probability
of each prompt token under the current policy. Unlike `session.generator.sample`, which reports logprobs
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

Use `session.generator.compute_logprobs_batch(prompts: Iterable[ModelInput]) -> list[list[float]]` to score
several sequences in one call (mirroring `sample` / `sample_batch`); it returns one list of
per-token logprobs per input prompt.

#### `session.trainer.forward_backward(...)`

Runs a forward and backward pass to compute gradients.

```python
def forward_backward(
    *,
    samples: Iterable[Sample],
    loss: LossConfig,
    return_loss_fn_outputs: bool | None = None,
) -> ForwardBackwardResult
```

| Parameter | Type                | Default      | Description                                                    |
| --------- | ------------------- | ------------ | -------------------------------------------------------------- |
| `samples` | `Iterable[Sample]`  | _(required)_ | Batch of training samples (see [Training sample](#training-sample)). |
| `loss`    | `LossConfig`   | _(required)_ | Loss configuration (see [Loss configs](#loss-configurations)). |
| `return_loss_fn_outputs` | `bool \| None` | `None` | Read the per-sample output tensors back with the update. Left unsent unless set, so the service default stands. |

`session.trainer.forward(...)` submits this same operation with `forward_only=True`, scoring a
batch under `loss` without accumulating gradients, and asks for `loss_fn_outputs` by default.

**Returns:** `ForwardBackwardResult`. The resolved value has:

| Field     | Type               | Description                                                                          |
| --------- | ------------------ | ------------------------------------------------------------------------------------ |
| `loss`    | `float`            | Scalar loss value for the batch.                                                     |
| `metrics` | `dict[str, float]` | Loss-specific metrics (e.g. `loss/clip/high_fraction`, `loss/kl_ref/mean` for GRPO). |
| `loss_fn_outputs` | `list[LossFnOutput] \| None` | Per-sample output tensors when `return_loss_fn_outputs` asked for them, else `None`. `tensors["logprobs"]` holds one score per position, masked by `loss`: a position the loss excludes (zero `weights`, for instance) is exactly `0.0`, not a true log-probability. |

#### `session.trainer.optim_step(...)`

Applies accumulated gradients and updates model parameters. Does not make the
updated parameters available for sampling — call `weights_sync` afterwards when
you want subsequent samples to use the updated policy.

**Migration:** `weight_sync_type` is no longer accepted on `optim_step` (passing it
raises `TypeError`). The old default was `WEIGHT_SYNC_TYPE_UNSPECIFIED` (also
removed from the enum); bare `optim_step()` calls previously still sent that
value on the wire. `optim_step` now only applies gradients — it does not publish
weights for sampling. Every loop that samples after an optim step must add
`session.trainer.weights_sync(weight_sync_type=...)` with an explicit mode
(`SYNCHRONOUS`, `BACKGROUND_PUBLISH`, or `PIPELINE`), even if it never named
`weight_sync_type` before. Without that call, subsequent samples keep using a
stale policy with no client-side error.

Also drop `policy_segments` from training `Sample`s (it is no longer a request
field; `SampleResult.policy_segments` on the response is unchanged). Replace the
removed named loss-input wrappers with `loss_fn_inputs`, using the exported
`TensorData` with a lowercase `dtype` (`"float32"` for floating-point weights,
`"int64"` for token IDs).

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

#### `session.trainer.weights_sync(...)`

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

### `download_checkpoint(...)`

Downloads all files for a checkpoint to a local directory using an existing root SDK client. The async equivalent is
`download_checkpoint_async(client: AsyncTogether, ...)`.

```python
def download_checkpoint(
    client: Together,
    checkpoint_id: str,
    *,
    variant: CheckpointVariant = "CHECKPOINT_VARIANT_MERGED",
    output_dir: str | Path = ".",
) -> list[Path]
```

| Parameter       | Type                | Default                       | Description                                                    |
| --------------- | ------------------- | ----------------------------- | -------------------------------------------------------------- |
| `client`        | `Together`          | _(required)_                  | Configured root SDK client used for the API and file requests. |
| `checkpoint_id` | `str`               | _(required)_                  | ID of the inference checkpoint to download.                    |
| `variant`       | `CheckpointVariant` | `"CHECKPOINT_VARIANT_MERGED"` | Download merged full model or adapter-only weights.            |
| `output_dir`    | `str \| Path`       | `"."`                         | Local directory to save files into. Created if it doesn't exist. |

**Returns:** list of `Path` objects pointing to the downloaded files.

Checkpoint metadata (type, base model, session, step, optional LoRA rank) is `client.beta.rl.checkpoints.retrieve(id)` and returns `Checkpoint`. `type` is `CheckpointType`: `CHECKPOINT_TYPE_TRAINING` or `CHECKPOINT_TYPE_INFERENCE`. Only inference checkpoints support download.

#### `session.stop()`

Stops the session and waits until it reaches `STOPPED`, `ERROR`, or `EXPIRED`. Called automatically when
using `SessionClient` as a context manager.

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
        session.generator.sample(prompt)
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

Stops the resources and waits until they reach `STOPPING`, when billing has stopped. Stop attached sessions
first. `force=True` also stops every attached session and should be reserved for sessions this process cannot
stop itself. Called automatically when using `ModelResourcesClient` as a context manager.

---

### Training sample

A training sample has the shape:

```python
from together.lib.beta.rl import TensorData

chunk = ModelInputChunk(
    encoded_text=EncodedTextChunk(
        tokens=[1, 2, 3],
    ),
)
Sample(
    model_input=ModelInput(chunks=[chunk]),
    loss_fn_inputs={
        "weights": TensorData(
            data=[0.0, 1.0, 1.0],
            dtype="float32",
        ),
        "target_tokens": TensorData(
            data=[2, 3, 0],
            dtype="int64",
        ),
    },
)
```

`Sample` fields:

| Field             | Type                          | When to use                                                                 |
| ----------------- | ----------------------------- | --------------------------------------------------------------------------- |
| `model_input` | `ModelInput` | Always required. The full token sequence (prompt + response) to train on. |
| `loss_fn_inputs` | `Mapping[str, TensorData]` | Always required. Per-token tensors keyed by the input names accepted by the selected loss. |
| `routed_experts` | `RoutedExperts` | Optional. Per-token expert routing for MoE models. |

Construct each `loss_fn_inputs` value with the exported `TensorData` TypedDict. Dtypes are lowercase: `{"data": [...], "dtype":
"int64"}` or `{"data": [...], "dtype": "float32"}`. Only one-dimensional dense
tensors are accepted, and `shape` is inferred from `data`. A dtype mismatch
raises client-side — worth knowing because Tinker infers the dtype by key name
for plain Python lists, but a numpy or torch array keeps its own.

`loss_fn_inputs` keys are flat, including for GRPO:

| Key | Tensor type | Required by | Description |
| --- | --- | --- | --- |
| `target_tokens` | `TensorData` (`int64`) | Every loss | Next-token targets, shifted by one position. |
| `weights` | `TensorData` (`int64` or `float32`) | Cross-entropy; optional for policy losses | Per-token non-negative weights. Cross-entropy honors fractional values; policy losses treat values as a 0/1 mask. Omission for a policy loss includes all tokens. |
| `mask` | `TensorData` (`int64` or `float32`) | Optional for every loss | Per-token inclusion mask. |
| `advantages` | `TensorData` (`float32`) | GRPO, PPO, CISPO, DRO, importance sampling | Per-token advantage values. |
| `logprobs` | `TensorData` (`float32`) | GRPO, PPO, CISPO, DRO, importance sampling | Per-token log probabilities from the generator policy. |
| `reference_logprobs` | `TensorData` (`float32`) | GRPO when `beta > 0` | Per-token reference-model log probabilities used for the KL penalty. |

Every training operation validates `loss_fn_inputs` client-side, before any upload or
submission:

- **Missing a key the loss requires** raises `ValueError` — the loss cannot be computed
  without it, so this is always a caller error.
- **A key outside the table above** emits a `UserWarning` and is sent anyway. The wire
  shape is an open `map<string, TensorData>`, so an unrecognized key may be a server
  input newer than this SDK; rejecting it would put an SDK release on the critical path
  of every new server input.
- **A dtype other than the one the table pins** raises `ValueError`.

`forward()` scores under a real loss, so it validates `loss_fn_inputs` against that loss just
as `forward_backward()` does: `cross_entropy` requires `weights`, and the policy losses require
`advantages` and `logprobs`. Only `custom_forward_backward()` carries no loss config, so it
requires just `target_tokens` and recognizes `weights` and `mask`; reusing a policy-loss batch
there warns about `advantages` and `logprobs` and still submits.

A `RoutedExperts` value carries exactly one source — an inline `data` buffer or an `object_uri` —
alongside `shape`; see the `RoutedExperts` entry in [`api.md`](api.md) for the field-level contract.

### Sampling params

Sampling parameters are passed as `SamplingParams` to `session.generator.sample(...)`:

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

Standard next-token prediction loss. Requires `weights` and `target_tokens` in
`loss_fn_inputs`.

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
| `beta`                | `float` | `0.0`                                      | KL penalty coefficient. When > 0, `reference_logprobs` must be provided in `loss_fn_inputs`. |
| `clip_low_threshold`  | `float` | _(server default)_                         | Lower bound the importance-sampling ratio is clamped to (e.g. `0.8`). Must be <= 1.       |
| `clip_high_threshold` | `float` | _(server default)_                         | Upper bound the importance-sampling ratio is clamped to (e.g. `1.2`). Must be >= 1.       |
| `ratio_type`          | `str`   | `GRPO_LOSS_RATIO_TYPE_TOKEN`               | Token-level ratios (standard GRPO) or `GRPO_LOSS_RATIO_TYPE_SEQUENCE` for GSPO-style loss. |

Aggregation types:

| Value                                      | Description                          |
| ------------------------------------------ | ------------------------------------ |
| `GRPO_LOSS_AGGREGATION_TYPE_FIXED_HORIZON` | Fixed-horizon aggregation (default). |
| `GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN`    | Mean over valid tokens.              |
| `GRPO_LOSS_AGGREGATION_TYPE_SEQUENCE_MEAN` | Mean over sequences.                 |

Requires the flat `target_tokens`, `advantages`, and `logprobs` keys in
`loss_fn_inputs`; `reference_logprobs` is required when `beta > 0`, while
`weights` and `mask` are optional.

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
[`download_checkpoint(...)`](#download_checkpoint), `resume_from_checkpoint_id`, or
`client.beta.rl.checkpoints.retrieve(id)` for `Checkpoint` metadata.
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
