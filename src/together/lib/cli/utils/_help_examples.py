## Top-level commands

TOP_LEVEL_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Fine tune a model for your dataset:
  [primary]tg ft create --model Qwen/Qwen2-1.5B --training-file ./my-dataset.jsonl --lora[/primary]

[dim]-[/dim] Deploy a model to a dedicated endpoint:
  [dim]Create an endpoint and deploy the model to it.
  After the endpoint is created, you can run inference against it with the fully qualified endpoint name.[/dim]
  [primary]tg endpoints deploy Qwen/Qwen2.5-7B --endpoint my-custom-endpoint-name[/primary]

[dim]-[/dim] Upload an external model to Together:
  [dim]First create a model record and reference compatible base model.
  You can find model IDs of the supported base models with `tg models public`.[/dim]
  [primary]$ tg models create --name my-model --base-model ml_xxxxxxxxxxxx[/primary]

  [dim]Upload from a local file/directory to the model record created above.[/dim]
  [primary]$ tg models upload ml_yyyyyyyyyyy ./path/to/my-model[/primary]
"""

## Files API commands

FILES_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Upload a file for fine-tuning:
  [primary]tg files upload ./my-dataset.jsonl --purpose fine-tune[/primary]

[dim]-[/dim] Check a local file for issues:
  [primary]tg files check ./my-dataset.jsonl[/primary]

[dim]-[/dim] Remove a file from Together:
  [primary]tg files delete <file-id>[/primary]

[dim]-[/dim] Download a file:
  [primary]tg files download <file-id> --output ./datasets[/primary]
"""

FILES_UPLOAD_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Upload a file for fine-tuning:
  [primary]tg files upload ./my-dataset.jsonl --purpose fine-tune[/primary]

[dim]-[/dim] Upload a file for evals:
  [primary]tg files upload ./my-dataset.jsonl --purpose evals[/primary]

[dim]-[/dim] Skip file checks:
  [primary]tg files upload ./my-dataset.jsonl --no-check[/primary]
"""

FILES_RETRIEVE_CONTENT_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Download a file:
  [primary]tg files download <file-id> --output ./datasets[/primary]

[dim]-[/dim] Print file contents to stdout:
  [primary]tg files download <file-id> --stdout[/primary]
"""

## Projects
PROJECTS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List projects you can access:
  [primary]tg projects list[/primary]

[dim]-[/dim] Switch the saved login token to one of them:
  [primary]tg switch[/primary]
  [primary]tg switch <project-id>[/primary]
"""

## Fine-tuning API commands
FINE_TUNING_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create a fine-tuning job:
  [primary]tg ft create --model Qwen/Qwen2-1.5B --training-file ./my-dataset.jsonl[/primary]

[dim]-[/dim] Retrieve a fine-tuning job details:
  [primary]tg ft <ft-job-id>[/primary]

[dim]-[/dim] Download a fine-tuned model's weights:
  [primary]tg ft download <ft-job-id> --output-dir ./my-model[/primary]

[dim]-[/dim] Download the generated tokenized dataset archive:
  [primary]tg ft download-tokenized-dataset <ft-job-id> --output-dir ./tokenized[/primary]

[dim]-[/dim] List checkpoints for a fine-tuning job:
  [primary]tg ft list-checkpoints <ft-job-id>[/primary]

[dim]-[/dim] Cancel a fine-tuning job:
  [primary]tg ft cancel <ft-job-id>[/primary]

[dim]-[/dim] Preview how a training file will be tokenized:
  [primary]tg ft preview --model Qwen/Qwen2-1.5B --training-file <file-id>[/primary]

[dim]-[/dim] Get fine-tuning limits for a model:
  [primary]tg ft model-limits Qwen/Qwen2-1.5B[/primary]
"""

FINE_TUNING_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Start a supervised fine-tuning job:
  [primary]tg ft create -M Qwen/Qwen2-1.5B -t ./my-dataset.jsonl[/primary]

[dim]-[/dim] Start a preference fine-tuning job:
  [primary]tg ft create -m dpo -M Qwen/Qwen2-1.5B -t ./dpo_train_file.jsonl[/primary]

[dim]-[/dim] Start a fine-tuning job from a checkpoint:
  [primary]tg ft create --from-checkpoint JOB_ID/OUTPUT_MODEL_NAME:STEP --training-file ./updated-dataset.jsonl[/primary]

[dim]-[/dim] Specify the number of checkpoints to save:
  [primary]tg ft create --n-checkpoints 3 -M Qwen/Qwen2-1.5B --training-file ./my-dataset.jsonl[/primary]
"""

FINE_TUNING_LIST_METRICS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Retrieve metrics for a fine-tuning job:
  [primary]tg ft list-metrics <ft-job-id>[/primary]

[dim]-[/dim] Retrieve metrics from a specific global step range:
  [primary]tg ft list-metrics <ft-job-id> --global-step-from 100 --global-step-to 500[/primary]

[dim]-[/dim] Retrieve metrics logged within a time range:
  [primary]tg ft list-metrics <ft-job-id> --logged-at-from 2024-01-01T00:00:00 --logged-at-to 2024-01-02T00:00:00[/primary]

[dim]-[/dim] Retrieve a fixed number of data points as JSON:
  [primary]tg ft list-metrics <ft-job-id> --resolution 50 --json[/primary]

[dim]-[/dim] Save raw metrics to a file:
  [primary]tg ft list-metrics <ft-job-id> --json > metrics.json[/primary]

[dim]-[/dim] Save ASCII plots to a file:
  [primary]tg ft list-metrics <ft-job-id> > plots.txt[/primary]
"""

FINE_TUNING_PREVIEW_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Preview tokenization for the first rows in a training file:
  [primary]tg ft preview --model Qwen/Qwen2-1.5B --training-file <file-id>[/primary]

[dim]-[/dim] Preview more rows and include prompt tokens in training loss:
  [primary]tg ft preview -M Qwen/Qwen2-1.5B -t <file-id> --top-k 10 --train-on-inputs[/primary]

[dim]-[/dim] Save the raw preview response:
  [primary]tg ft preview -M Qwen/Qwen2-1.5B -t <file-id> --json > preview.json[/primary]
"""

FINE_TUNING_MODEL_LIMITS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Get fine-tuning limits for a model:
  [primary]tg ft model-limits Qwen/Qwen2-1.5B[/primary]
"""

FINE_TUNING_DOWNLOAD_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Download a fine-tuned model's weights:
  [primary]tg ft download <ft-job-id> --output-dir ./my-model[/primary]

[dim]-[/dim] Download a fine-tuned model's weights from a specific checkpoint:
  [primary]tg ft download <ft-job-id> --checkpoint-step 1 --output-dir ./my-model[/primary]
"""

FINE_TUNING_DOWNLOAD_TOKENIZED_DATASET_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Download the tokenized dataset archive generated for a fine-tuning job:
  [primary]tg ft download-tokenized-dataset <ft-job-id> --output-dir ./tokenized[/primary]

[dim]-[/dim] Save download metadata as JSON:
  [primary]tg ft download-tokenized-dataset <ft-job-id> --output-dir ./tokenized --json[/primary]
"""

## Batches API commands

BATCHES_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Submit a chat completions batch from a local file:
  [primary]tg batches submit ./requests.jsonl chat.completions[/primary]

[dim]-[/dim] List batch jobs:
  [primary]tg batches ls[/primary]

[dim]-[/dim] Get details of a batch job:
  [primary]tg batches <batch-id>[/primary]

[dim]-[/dim] Print batch results to stdout:
  [primary]tg batches download <batch-id>[/primary]

[dim]-[/dim] Cancel a batch job:
  [primary]tg batches cancel <batch-id>[/primary]
"""

BATCHES_SUBMIT_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Submit a chat completions batch from a local JSONL file:
  [primary]tg batches submit ./requests.jsonl chat.completions[/primary]

[dim]-[/dim] Submit using a previously uploaded file ID:
  [primary]tg batches submit file-abc123 --api chat.completions[/primary]

[dim]-[/dim] Submit an audio transcription batch:
  [primary]tg batches submit ./audio.jsonl --api audio.transcriptions[/primary]
"""

BATCHES_DOWNLOAD_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Print batch output to stdout:
  [primary]tg batches download <batch-id>[/primary]

[dim]-[/dim] Download batch output to a file:
  [primary]tg batches download <batch-id> --output ./results.jsonl[/primary]
"""

## Evals API commands

EVALS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Look at the examples for creating an evaluation job:
  [primary]tg evals create --help[/primary]

[dim]-[/dim] List all evaluation jobs:
  [primary]tg evals ls[/primary]

[dim]-[/dim] Check the status of an evaluation job:
  [primary]tg evals status <eval-id>[/primary]

[dim]-[/dim] Get details of an evaluation job:
  [primary]tg evals <eval-id>[/primary]
"""

EVALS_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Run a classification evaluation:
  [primary]tg evals create \\
    --type classify \\
    --judge-model deepseek-ai/DeepSeek-V3.1 \\
    --judge-model-source serverless \\
    --judge-system-template "You are a helpful assistant" \\
    --input-data-file-path ./data.jsonl \\
    --model-to-evaluate deepseek-ai/DeepSeek-V3.1 \\
    --model-to-evaluate-source serverless \\
    --model-to-evaluate-system-template "Respond to the following comment. You can be informal but maintain a respectful tone." \\
    --model-to-evaluate-input-template "Here's a comment I saw online. How would you respond to it?\\n\\n{{question}}" \\
    --labels 'Toxic,Non-toxic' \\
    --pass-labels 'Non-toxic'[/primary]

[dim]-[/dim] Run a score evaluation:
  [primary]tg evals create \\
    --type score \\
    --judge-model deepseek-ai/DeepSeek-V3.1 \\
    --judge-model-source serverless \\
    --judge-system-template "Rate the given response on a scale from 1 to 10, where 1 is generic and 10 is unique." \\
    --input-data-file-path ./data.jsonl  \\
    --model-to-evaluate deepseek-ai/DeepSeek-V3.1 \\
    --model-to-evaluate-source serverless \\
    --model-to-evaluate-system-template "You are a helpful assistant." \\
    --model-to-evaluate-input-template $'Please respond:\\n\\n{{prompt}}' \\
    --model-to-evaluate-max-tokens 512 \\
    --model-to-evaluate-temperature 0.7 \\
    --min-score 1 \\
    --max-score 10 \\
    --pass-threshold 7
    [/primary]

[dim]-[/dim] Run a compare evaluation:
  [primary]tg evals create \\
    --type compare \\
    --judge-model deepseek-ai/DeepSeek-V3.1 \\
    --judge-model-source serverless \\
    --judge-system-template "You are an expert judge. Given the user task and two model responses, say which is better and why." \\
    --input-data-file-path ./examples/eval_compare_sample.jsonl \\
    --model-a deepseek-ai/DeepSeek-V3.1 \\
    --model-a-source serverless \\
    --model-a-system-template "You are a helpful assistant." \\
    --model-a-input-template $'Answer the following:\\n\\n{{prompt}}' \\
    --model-b deepseek-ai/DeepSeek-V3.1 \\
    --model-b-source serverless \\
    --model-b-system-template "You are a concise assistant." \\
    --model-b-input-template $'Answer the following:\\n\\n{{prompt}}' \\
    --disable-position-bias-correction[/primary]
"""

## Endpoints API commands

ENDPOINTS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Deploy a public model to a new dedicated endpoint:
  [dim]Note: This command can be used to create a new endpoint or add a deployment to an existing endpoint.[/dim]
  [primary]tg endpoints deploy Qwen/Qwen2.5-7B --endpoint my-endpoint[/primary]

[dim]-[/dim] List endpoints in the current project:
  [primary]tg endpoints ls[/primary]

[dim]-[/dim] Inspect an endpoint or deployment:
  [primary]tg endpoints <endpoint-or-deployment-name-or-id>[/primary]

[dim]-[/dim] Scale a deployment and adjust its traffic weight:
  [primary]tg endpoints update <deployment-id> --min-replicas 2 --max-replicas 8 --traffic-weight 1[/primary]

[dim]-[/dim] Split live traffic to a new variant (A/B):
  [primary]tg endpoints ab Qwen/Qwen2.5-7B --control <deployment-id> --percent 10[/primary]

[dim]-[/dim] Mirror live traffic to a shadow deployment:
  [primary]tg endpoints shadow Qwen/Qwen2.5-7B --endpoint <endpoint-name-or-id> --rate 0.1[/primary]

[dim]-[/dim] Delete a deployment, adapter, experiment, rollout, or entire endpoint:
  [primary]tg endpoints rm <ep_|dep_|dad_|abx_|exp_|rol_...>[/primary]

[dim]-[/dim] Roll out a deployment onto live traffic:
  [primary]tg endpoints rollout <deployment-id> --rolling[/primary]
"""

ENDPOINTS_ROLLOUT_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Rolling (capacity-preserving batch swap):
  [primary]tg endpoints rollout my-deployment --rolling[/primary]

[dim]-[/dim] Blue-green cutover:
  [primary]tg endpoints rollout my-deployment --blue-green[/primary]

[dim]-[/dim] Canary (server-default steps/interval):
  [primary]tg endpoints rollout my-deployment --canary[/primary]

[dim]-[/dim] Canary with custom steps and interval:
  [primary]tg endpoints rollout my-deployment --canary \\
    --steps 5,25,50,100 --interval 30s[/primary]

[dim]-[/dim] Canary with a metric gate (threshold or regression):
  [primary]tg endpoints rollout my-deployment --canary \\
    --metric router_latency --metric-stat p99 \\
    --metric-threshold 500 --metric-operator lte[/primary]
  [primary]tg endpoints rollout my-deployment --canary \\
    --metric router_error_rate --metric-direction higher-is-worse[/primary]

[dim]-[/dim] Roll out a deployment from an active shadow or a/b experiment:
  [primary]tg endpoints rollout shadow-deployment --rolling --detach[/primary]

[dim]-[/dim] Control an in-progress rollout (endpoint ID preferred; also accepts
  endpoint name, deployment ID/name, or rollout ID — one active rollout per endpoint):
  [primary]tg endpoints rollout ep_xxxxxxxxxxxx --pause[/primary]
  [primary]tg endpoints rollout ep_xxxxxxxxxxxx --resume[/primary]
  [primary]tg endpoints rollout ep_xxxxxxxxxxxx --promote[/primary]
  [primary]tg endpoints rollout ep_xxxxxxxxxxxx --cancel --reason "freezing mid-canary"[/primary]
  [primary]tg endpoints rollout ep_xxxxxxxxxxxx --cancel revert[/primary]
"""

ENDPOINTS_DEPLOY_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Deploy a public model onto a new endpoint:
  [primary]tg endpoints deploy Qwen/Qwen2.5-7B --endpoint my-endpoint[/primary]

[dim]-[/dim] Deploy a private model by ID onto an existing endpoint:
  [primary]tg endpoints deploy ml_xxxxxxxxxxxx --endpoint ep_yyyyyyyyyyyy[/primary]

[dim]-[/dim] Deploy a LoRA adapter onto a dynamic (preferred) or fixed base-model deployment:
  [primary]tg endpoints deploy ml_adapter --endpoint my-endpoint[/primary]

[dim]-[/dim] Pin a config and start with autoscaling:
  [primary]tg endpoints deploy Qwen/Qwen2.5-7B --endpoint my-endpoint \\
    --config cr_xxxxxxxxxxxx --min-replicas 1 --max-replicas 4 \\
    --scaling-metric inflight_requests --scaling-target 10[/primary]

[dim]-[/dim] Deploy with no live traffic yet:
  [primary]tg endpoints deploy ml_xxxxxxxxxxxx --endpoint my-endpoint \\
    --traffic-weight 0[/primary]

[dim]-[/dim] Create the endpoint stopped (scale later with update):
  [primary]tg endpoints deploy Qwen/Qwen2.5-7B --endpoint my-endpoint \\
    --min-replicas 0 --max-replicas 0[/primary]
"""

ENDPOINTS_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Change replica bounds:
  [primary]tg endpoints update <deployment-id> --min-replicas 2 --max-replicas 8[/primary]

[dim]-[/dim] Stop a deployment (scale to zero):
  [primary]tg endpoints update <deployment-id> --min-replicas 0 --max-replicas 0[/primary]

[dim]-[/dim] Set autoscaling on TTFT p95:
  [primary]tg endpoints update <deployment-id> \\
    --scaling-metric ttft --scaling-target 200 --scaling-percentile p95[/primary]

[dim]-[/dim] Shift live traffic weight (relative to other deployments):
  [primary]tg endpoints update <deployment-id> --traffic-weight 2[/primary]

[dim]-[/dim] Set an A/B variant percent (takes from or returns to control):
  [primary]tg endpoints update <variant-deployment-id> --ab-percent 20[/primary]
"""

ENDPOINTS_AB_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Send 10% of live traffic to a new variant of a public model:
  [primary]tg endpoints ab Qwen/Qwen2.5-7B --control <deployment-id> --percent 10[/primary]

[dim]-[/dim] A/B a private model with an explicit config:
  [primary]tg endpoints ab ml_xxxxxxxxxxxx --control <deployment-id> \\
    --percent 25 --config cr_yyyyyyyyyyyy[/primary]

[dim]-[/dim] Name the variant deployment:
  [primary]tg endpoints ab ml_xxxxxxxxxxxx --control <deployment-id> \\
    --percent 5 --name my-variant[/primary]
"""

ENDPOINTS_SHADOW_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Mirror 10% of live requests to a shadow deployment:
  [primary]tg endpoints shadow Qwen/Qwen2.5-7B --endpoint <endpoint-name-or-id> \\
    --rate 0.1[/primary]

[dim]-[/dim] Adaptive sampling to a target QPS:
  [primary]tg endpoints shadow zai-org/GLM-5.1 --endpoint <endpoint-name-or-id> \\
    --target-qps 5[/primary]

[dim]-[/dim] Sticky key-based sampling on a request field:
  [primary]tg endpoints shadow deepseek-ai/DeepSeek-V4-Flash --endpoint <endpoint-name-or-id> \\
    --rate 0.2 --key user_id[/primary]

[dim]-[/dim] Shadow a private model with an explicit config:
  [primary]tg endpoints shadow ml_xxxxxxxxxxxx --endpoint <endpoint-name-or-id> \\
    --config cr_yyyyyyyyyyyy --rate 0.05 --name my-shadow[/primary]

[dim]Note:[/dim] Shadow targets cannot be live traffic-split members or active rollout participants.
"""

ENDPOINTS_RM_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Delete a deployment:
  [primary]tg endpoints rm dep_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Detach an adapter from the deployment it belongs to:
  [primary]tg endpoints rm dad_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Delete an A/B or shadow experiment:
  [primary]tg endpoints rm abx_xxxxxxxxxxxx[/primary]
  [primary]tg endpoints rm exp_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Delete a rollout:
  [primary]tg endpoints rm rol_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Delete an empty endpoint:
  [primary]tg endpoints rm ep_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Force-delete an endpoint and all child deployments:
  [primary]tg endpoints rm ep_xxxxxxxxxxxx --force[/primary]
"""

ENDPOINTS_LS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List endpoints in the current project:
  [primary]tg endpoints ls[/primary]

[dim]-[/dim] List org-scoped endpoints:
  [primary]tg endpoints ls --org[/primary]

[dim]-[/dim] Paginate:
  [primary]tg endpoints ls --after <cursor>[/primary]
"""

ENDPOINTS_GET_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Get endpoint details by name or ID (includes deployments and traffic split):
  [primary]tg endpoints my-endpoint[/primary]
  [primary]tg endpoints ep_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Get a single deployment by name or ID:
  [primary]tg endpoints control[/primary]
  [primary]tg endpoints dep_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Machine-readable output:
  [primary]tg endpoints my-endpoint --json[/primary]
"""

## Models API commands

MODELS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Deploy a model to a dedicated endpoint:
  [primary]tg models deploy Qwen/Qwen2.5-7B --endpoint my-endpoint[/primary]

[dim]-[/dim] Find a supported base model, then register your own:
  [primary]tg models public --search Qwen[/primary]
  [primary]tg models create --name my-model --base-model ml_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Upload weights from disk (or import remotely):
  [primary]tg models upload ml_yyyyyyyyyyyy ./path/to/my-model[/primary]
  [primary]tg models remote-uploads create ml_yyyyyyyyyyyy --from https://huggingface.co/org/model[/primary]

[dim]-[/dim] List project models and inspect one:
  [primary]tg models ls[/primary]
  [primary]tg models ml_yyyyyyyyyyyy[/primary]

[dim]-[/dim] List configs for a model to be used with [primary]tg models deploy --config[/primary]:
  [primary]tg models configs ml_yyyyyyyyyyyy[/primary]

[dim]-[/dim] Download a revision locally:
  [primary]tg models download ml_yyyyyyyyyyyy ./out --format hf[/primary]
"""

MODELS_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Register a full model (find names/IDs with [primary]tg models public[/primary]):
  [primary]tg models create --name my-model --base-model ml_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Or pass a deploy model name instead of an id:
  [primary]tg models create --name my-model --base-model Qwen/Qwen3.5-9B-FP8[/primary]

[dim]-[/dim] Register a LoRA adapter record:
  [primary]tg models create --name my-adapter --base-model ml_xxxxxxxxxxxx --type adapter[/primary]
"""

MODELS_UPLOAD_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Upload a local directory into an existing model record:
  [primary]tg models upload ml_xxxxxxxxxxxx ./path/to/my-model[/primary]

[dim]-[/dim] Upload a single file:
  [primary]tg models upload ml_xxxxxxxxxxxx ./model.safetensors[/primary]
"""

MODELS_DOWNLOAD_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Download the latest revision:
  [primary]tg models download ml_xxxxxxxxxxxx ./out[/primary]

[dim]-[/dim] Download a specific revision as a Hugging Face snapshot:
  [primary]tg models download ml_xxxxxxxxxxxx ./out --revision <revision-id> --format hf[/primary]

[dim]-[/dim] Download only selected paths:
  [primary]tg models download ml_xxxxxxxxxxxx ./out --files config.json --files tokenizer.json[/primary]
"""

MODELS_PUBLIC_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Search supported base models:
  [primary]tg models public --search Qwen[/primary]

[dim]-[/dim] Filter by modality / product:
  [primary]tg models public --modality text --product dedicated[/primary]

[dim]-[/dim] Paginate:
  [primary]tg models public --after <cursor>[/primary]
"""

MODELS_CONFIGS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List configs you can pass to [primary]tg models deploy --config[/primary]:
  [primary]tg models configs ml_xxxxxxxxxxxx[/primary]
"""

MODELS_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Rename a model:
  [primary]tg models update ml_xxxxxxxxxxxx --name my-model-v2[/primary]

[dim]-[/dim] Update description:
  [primary]tg models update ml_xxxxxxxxxxxx --description "Production weights"[/primary]
"""

MODELS_REMOTE_UPLOADS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Import from Hugging Face into an existing model record:
  [primary]tg models remote-uploads create ml_xxxxxxxxxxxx \\
    --from https://huggingface.co/org/model[/primary]

[dim]-[/dim] List and inspect jobs:
  [primary]tg models remote-uploads ls[/primary]
  [primary]tg models remote-uploads get <job-id>[/primary]
"""

MODELS_REMOTE_UPLOADS_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Import a public Hugging Face repo:
  [primary]tg models remote-uploads create ml_xxxxxxxxxxxx \\
    --from https://huggingface.co/org/model[/primary]

[dim]-[/dim] Import a gated/private HF repo:
  [primary]tg models remote-uploads create ml_xxxxxxxxxxxx \\
    --from https://huggingface.co/org/private-model --token "$HF_TOKEN"[/primary]

[dim]-[/dim] Import from a presigned archive URL:
  [primary]tg models remote-uploads create ml_xxxxxxxxxxxx \\
    --from "https://bucket.s3.amazonaws.com/model.tar.gz?X-Amz-Signature=..."[/primary]
"""

## Clusters API commands

CLUSTERS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List clusters and regions:
  [primary]tg clusters list[/primary]
  [primary]tg clusters list-regions[/primary]

[dim]-[/dim] Write kubeconfig for a cluster (default ~/.kube/config):
  [primary]tg clusters get-credentials <cluster-id>[/primary]

[dim]-[/dim] Print kubeconfig to stdout:
  [primary]tg clusters get-credentials <cluster-id> --file -[/primary]

[dim]-[/dim] Non-interactive cluster create (see [primary]tg clusters create --help[/primary] for flags):
  [primary]tg clusters create --non-interactive \\
    --name my-cluster --cluster-type KUBERNETES --gpu-type H100_SXM \\
    --region us-central-8 --num-gpus 8 --billing-type ON_DEMAND \\
    --nvidia-version-id <nvidia-version-id> --volume <volume-id>[/primary]

[dim]-[/dim] Update or delete a cluster:
  [primary]tg clusters update <cluster-id> --num-gpus 16 --cluster-type KUBERNETES[/primary]
  [primary]tg clusters delete <cluster-id>[/primary]

[dim]-[/dim] Manage node remediations:
  [primary]tg clusters remediations ls <cluster-id>[/primary]
  [primary]tg clusters remediations create <cluster-id> <instance-id> --mode VM_ONLY[/primary]

[dim]-[/dim] SSH into a cluster (OIDC-signed certificate; see [primary]tg clusters ssh --help[/primary]):
  [primary]tg clusters ssh https://dex.<base>/<cluster-id> --login <username>[/primary]
"""

CLUSTERS_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create interactively (prompts for region, GPUs, drivers, etc.):
  [primary]tg clusters create[/primary]

[dim]-[/dim] Create without prompts (supply every required field):
  [primary]tg clusters create --non-interactive \\
    --name my-cluster \\
    --cluster-type KUBERNETES \\
    --gpu-type H100_SXM \\
    --region us-central-8 \\
    --num-gpus 8 \\
    --billing-type ON_DEMAND \\
    --nvidia-version-id <nvidia-version-id> \\
    --volume <volume-id>[/primary]
"""

CLUSTERS_GET_CREDENTIALS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Merge cluster kubeconfig into the default file ([primary]~/.kube/config[/primary]):
  [primary]tg clusters get-credentials <cluster-id>[/primary]

[dim]-[/dim] Write to a specific path:
  [primary]tg clusters get-credentials <cluster-id> --file ./my-kubeconfig[/primary]

[dim]-[/dim] Print kubeconfig to stdout (no file write):
  [primary]tg clusters get-credentials <cluster-id> --file -[/primary]

[dim]-[/dim] Use a custom context name in the merged kubeconfig:
  [primary]tg clusters get-credentials <cluster-id> --context-name my-prod-k8s[/primary]

[dim]-[/dim] On name conflicts with an existing kubeconfig, replace the entry:
  [primary]tg clusters get-credentials <cluster-id> --overwrite-existing[/primary]

[dim]-[/dim] Set this cluster as the default kube context after merge:
  [primary]tg clusters get-credentials <cluster-id> --set-default-context[/primary]
"""

CLUSTERS_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Change GPU count:
  [primary]tg clusters update <cluster-id> --num-gpus 16[/primary]

[dim]-[/dim] Change cluster type:
  [primary]tg clusters update <cluster-id> --cluster-type KUBERNETES[/primary]

[dim]-[/dim] Update both:
  [primary]tg clusters update <cluster-id> --num-gpus 16 --cluster-type KUBERNETES[/primary]
"""

CLUSTERS_STORAGE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List storage volumes:
  [primary]tg clusters storage list[/primary]

[dim]-[/dim] Create or resize a volume (see subcommand help for options):
  [primary]tg clusters storage create --region us-east-1 --size-tib 1 --volume-name my-data[/primary]
  [primary]tg clusters storage update <volume-id> --size-tib 4[/primary]

[dim]-[/dim] Use a volume when creating a cluster:
  [primary]tg clusters create --non-interactive ... --volume <volume-id>[/primary]
"""

CLUSTERS_STORAGE_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create a 1 TiB volume in a region ([primary]tg clusters list-regions[/primary] lists regions):
  [primary]tg clusters storage create \\
    --region us-east-1 \\
    --size-tib 1 \\
    --volume-name my-training-data[/primary]

[dim]-[/dim] Attach the volume when creating a cluster:
  [primary]tg clusters create --non-interactive ... --volume <volume-id>[/primary]
"""

CLUSTERS_STORAGE_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Grow a volume to 4 TiB:
  [primary]tg clusters storage update <volume-id> --size-tib 4[/primary]
"""

CLUSTERS_REMEDIATIONS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List all remediations for a cluster:
  [primary]tg clusters remediations ls <cluster-id>[/primary]

[dim]-[/dim] List remediations for one instance:
  [primary]tg clusters remediations ls <cluster-id> <instance-id>[/primary]

[dim]-[/dim] List automated remediations by mode:
  [primary]tg clusters remediations ls <cluster-id> --mode VM_ONLY --mode REBOOT_VM --trigger AUTOMATED[/primary]

[dim]-[/dim] Create a remediation:
  [primary]tg clusters remediations create <cluster-id> <instance-id> --mode VM_ONLY --reason "node unhealthy"[/primary]

[dim]-[/dim] Get remediation details:
  [primary]tg clusters remediations <remediation-id>[/primary]

[dim]-[/dim] Review automated remediations:
  [primary]tg clusters remediations approve <remediation-id>[/primary]
  [primary]tg clusters remediations reject <remediation-id> --comment "already handled"[/primary]
  [primary]tg clusters remediations cancel <remediation-id>[/primary]
"""

CLUSTERS_REMEDIATIONS_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create a VM-only remediation:
  [primary]tg clusters remediations create <cluster-id> <instance-id> --mode VM_ONLY[/primary]

[dim]-[/dim] Create a host-aware remediation:
  [primary]tg clusters remediations create <cluster-id> <instance-id> --mode HOST_AWARE[/primary]

[dim]-[/dim] Create a eviction-without-replacement remediation:
  [primary]tg clusters remediations create <cluster-id> <instance-id> --mode EVICT_WITHOUT_REPLACEMENT[/primary]

[dim]-[/dim] Create a reboot-vm remediation:
  [primary]tg clusters remediations create <cluster-id> <instance-id> --mode REBOOT_VM[/primary]
"""

## Training commands

TRAINING_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List model resources:
  [primary]tg training ls-resources[/primary]

[dim]-[/dim] List training sessions you created:
  [primary]tg training ls-sessions --created-by me[/primary]

[dim]-[/dim] List inference checkpoints for one session:
  [primary]tg training ls-checkpoints --type inference --session <session-id>[/primary]

[dim]-[/dim] List training checkpoints:
  [primary]tg training ls-checkpoints --type training[/primary]

[dim]-[/dim] Fetch a model resource, training session, or checkpoint by ID:
  [primary]tg training get <id>[/primary]

[dim]-[/dim] Prepare a fine-tuned model for FP4 inference:
  [primary]tg training fp4 create <model-object-id>[/primary]
"""

## Beta > Jig commands

JIG_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Bootstrap config and deploy from the current directory:
  [primary]tg beta jig init[/primary]
  [primary]tg beta jig deploy[/primary]

[dim]-[/dim] Inspect a deployment and stream logs:
  [primary]tg beta jig status[/primary]
  [primary]tg beta jig logs --follow[/primary]

[dim]-[/dim] List deployments or tear one down:
  [primary]tg beta jig list[/primary]
  [primary]tg beta jig destroy[/primary]
"""

JIG_SECRETS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Add or rotate a secret for this deployment:
  [primary]tg beta jig secrets set HF_TOKEN "$HF_TOKEN"[/primary]

[dim]-[/dim] List secrets and sync status:
  [primary]tg beta jig secrets list[/primary]

[dim]-[/dim] Remove a secret remotely and locally:
  [primary]tg beta jig secrets delete OLD_KEY[/primary]
"""

JIG_VOLUMES_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create a volume and upload a directory:
  [primary]tg beta jig volumes create --name model-weights --source ./weights[/primary]

[dim]-[/dim] Create a volume from your S3 bucket:
  [primary]tg beta jig volumes create --name model-weights --source s3://my-bucket/weights --aws-oidc-role-arn arn:aws:iam::123456789012:role/together[/primary]

[dim]-[/dim] List volumes for the deployment:
  [primary]tg beta jig volumes list[/primary]

[dim]-[/dim] Refresh volume contents from disk:
  [primary]tg beta jig volumes update --name model-weights --source ./weights[/primary]
"""

JIG_BUILD_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Build with default tag ([primary]latest[/primary]):
  [primary]tg beta jig build[/primary]

[dim]-[/dim] Build a tagged image with warmup (torch compile cache):
  [primary]tg beta jig build --tag v1 --warmup[/primary]

[dim]-[/dim] Pass extra Docker build arguments:
  [primary]tg beta jig build --docker-args '--no-cache'[/primary]
"""

JIG_PUSH_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Push the default ([primary]latest[/primary]) image:
  [primary]tg beta jig push[/primary]

[dim]-[/dim] Push a specific tag:
  [primary]tg beta jig push --tag v1[/primary]
"""

JIG_DEPLOY_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Build, push, and deploy from config in the current directory:
  [primary]tg beta jig deploy[/primary]

[dim]-[/dim] Deploy using an image that is already in the registry (skip build/push):
  [primary]tg beta jig deploy --image my-registry.example.com/my-org/my-model:abc123[/primary]

[dim]-[/dim] Only build and push; do not update the deployment:
  [primary]tg beta jig deploy --build-only[/primary]

[dim]-[/dim] Start deploy and return immediately without waiting:
  [primary]tg beta jig deploy --detach[/primary]
"""

JIG_DESTROY_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Tear down the deployment for this project ([primary]jig.toml[/primary] / [primary]pyproject.toml[/primary]):
  [primary]tg beta jig destroy[/primary]
"""

JIG_LOGS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Print recent logs once:
  [primary]tg beta jig logs[/primary]

[dim]-[/dim] Stream logs ([primary]Ctrl+C[/primary] to stop):
  [primary]tg beta jig logs --follow[/primary]

[dim]-[/dim] Filter logs by replica and deployment revision:
  [primary]tg beta jig logs --replica-id <replica-id> --revision <revision-id> --image-version <tag>[/primary]
"""

JIG_SUBMIT_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Submit a simple prompt job:
  [primary]tg beta jig submit --prompt "Hello, world!"[/primary]

[dim]-[/dim] Submit with a JSON payload (advanced request body):
  [primary]tg beta jig submit --payload '{"prompt":"Explain transformers","max_tokens":256}'[/primary]

[dim]-[/dim] Submit and poll until the job finishes:
  [primary]tg beta jig submit --prompt "Summarize this README." --watch[/primary]
"""

JIG_JOB_STATUS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Look up a job by request ID (from submit output):
  [primary]tg beta jig job-status --request-id <request-id>[/primary]

[dim]-[/dim] Machine-readable status:
  [primary]tg beta jig job-status --request-id <request-id> --json[/primary]
"""

JIG_SECRETS_SET_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create or update a secret from the shell:
  [primary]tg beta jig secrets set HF_TOKEN "$HF_TOKEN"[/primary]

[dim]-[/dim] Set a secret with a description (shown in listings):
  [primary]tg beta jig secrets set API_KEY "$API_KEY" --description "Third-party API credentials"[/primary]
"""

JIG_SECRETS_UNSET_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Drop a secret from local state only (does not delete remotely):
  [primary]tg beta jig secrets unset OLD_KEY[/primary]
"""

JIG_SECRETS_DELETE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Delete the secret on the server and remove it locally:
  [primary]tg beta jig secrets delete REVOKED_KEY[/primary]
"""

JIG_VOLUMES_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create a volume and upload files from a directory:
  [primary]tg beta jig volumes create --name model-weights --source ./weights[/primary]

[dim]-[/dim] Same using positional arguments:
  [primary]tg beta jig volumes create model-weights ./weights[/primary]

[dim]-[/dim] Sync files from your S3 bucket and wait until the volume is ready:
  [primary]tg beta jig volumes create --name model-weights --source s3://my-bucket/weights --aws-oidc-role-arn arn:aws:iam::123456789012:role/together --watch[/primary]
"""

JIG_VOLUMES_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Upload a new directory tree as the next volume version:
  [primary]tg beta jig volumes update --name model-weights --source ./weights[/primary]

[dim]-[/dim] Positional form:
  [primary]tg beta jig volumes update model-weights ./weights[/primary]

[dim]-[/dim] Snapshot your S3 bucket again as the next volume version:
  [primary]tg beta jig volumes update --name model-weights --source s3://my-bucket/weights --aws-oidc-role-arn arn:aws:iam::123456789012:role/together[/primary]
"""

TRAINING_FP4_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Estimate the price of preparing a fine-tuned model:
  [primary]tg training fp4 estimate <model-object-id>[/primary]

[dim]-[/dim] Prepare a model and wait for the job to finish:
  [primary]tg training fp4 create <model-object-id> --watch[/primary]

[dim]-[/dim] Follow a running job:
  [primary]tg training fp4 get <job-id> --watch[/primary]

[dim]-[/dim] Cancel a job:
  [primary]tg training fp4 cancel <job-id>[/primary]
"""

TRAINING_FP4_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Prepare the model's current revision:
  [primary]tg training fp4 create <model-object-id>[/primary]

[dim]-[/dim] Prepare a specific revision without the confirmation prompt, and wait for it:
  [primary]tg training fp4 create <model-object-id> -r <revision-id> -y --watch[/primary]
"""
