## Top-level commands

TOP_LEVEL_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Fine tune a model for your dataset:
  [primary]tg ft create --model Qwen/Qwen2-1.5B --training-file ./my-dataset.jsonl --lora[/primary]

[dim]-[/dim] Deploy a model to a dedicated endpoint:
  [dim]Create an endpoint and deploy the model to it.
  After the endpoint is created, you can run inference against it with the fully qualified endpoint name.[/dim]
  [primary]tg beta endpoints deploy Qwen/Qwen2.5-7B --endpoint my-custom-endpoint-name[/primary]

[dim]-[/dim] Upload an external model to Together:
  [dim]First create a model record and reference compatible base model.
  You can find model IDs of the supported base models with `tg beta models public`.[/dim]
  [primary]$ tg beta models create --name my-model --base-model ml_xxxxxxxxxxxx[/primary]

  [dim]Upload from a local file/directory to the model record created above.[/dim]
  [primary]$ tg beta models upload ml_yyyyyyyyyyy ./path/to/my-model[/primary]
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

## Models API commands
MODELS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List all models:
  [primary]tg models list[/primary]

[dim]-[/dim] Upload a model:
  [primary]tg models upload --model-name my-model --model-source s3-or-hugging-face[/primary]
"""

MODELS_UPLOAD_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Upload a model from S3:
  [primary]tg models upload \\
    --model-name my-model \\
    --model-source $(aws s3 presign s3://my-bucket/my-model)[/primary]

[dim]-[/dim] Upload private model from Hugging Face:
  [primary]tg models upload \\
    --model-name my-model \\
    --model-source my-org/model-name \\
    --hf-token $HUGGING_FACE_TOKEN[/primary]
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

## Endpoints API commands

ENDPOINTS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create a new endpoint:
  [primary]tg endpoints create --model Qwen/Qwen2.5-7B --hardware 2x_nvidia_h100_80gb_sxm --wait[/primary]

[dim]-[/dim] Lookup available hardware for a model:
  [primary]tg endpoints hardware --model Qwen/Qwen2.5-7B --available[/primary]

[dim]-[/dim] List your endpoints:
  [primary]tg endpoints list[/primary]

[dim]-[/dim] Get details of an endpoint:
  [primary]tg endpoints retrieve <endpoint-id>[/primary]

[dim]-[/dim] Stop an endpoint:
  [primary]tg endpoints stop <endpoint-id>[/primary]

[dim]-[/dim] Change the autoscaling configuration for an endpoint:
  [primary]tg endpoints update <endpoint-id> --min-replicas 4 --max-replicas 8[/primary]
"""

ENDPOINTS_HARDWARE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List all hardware configurations:
  [primary]tg endpoints hardware[/primary]

[dim]-[/dim] List all hardware configurations for a model:
  [primary]tg endpoints hardware --model Qwen/Qwen2.5-7B[/primary]

[dim]-[/dim] List all available hardware configurations for a model:
  [primary]tg endpoints hardware --model Qwen/Qwen2.5-7B --available[/primary]

[dim]-[/dim] Grab the cheapest hardware configuration for a model:
  [primary]tg endpoints hardware --model meta-llama/Meta-Llama-3-8B-Instruct --available --json | jq -r 'sort_by(.pricing.cents_per_minute) | .[0].id'[/primary]
"""

ENDPOINTS_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Deploy your model with specific autoscaling configuration:
  [primary]tg endpoints create --model MODEL --hardware HARDWARE --min-replicas 2 --max-replicas 4[/primary]

[dim]-[/dim] Deploy your fine tuned model:
  [primary]tg endpoints create --model $(tg ft $MY_FT_JOB_ID --json | jq -r '.model_output_name') --hardware HARDWARE[/primary]

[dim]-[/dim] Create an endpoint to be started later:
  [primary]tg endpoints create --model MODEL --hardware HARDWARE --no-auto-start[/primary]
"""

ENDPOINTS_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Change the autoscaling configuration for an endpoint:
  [primary]tg endpoints update ENDPOINT_ID --min-replicas 4 --max-replicas 8[/primary]

[dim]-[/dim] Change the auto-stop timeout for an endpoint:
  [primary]tg endpoints update ENDPOINT_ID --inactive-timeout 30[/primary]
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

## Beta endpoints API commands

BETA_ENDPOINTS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Deploy a public model to a new dedicated endpoint:
  [dim]Note: This command can be used to create a new endpoint or add a deployment to an existing endpoint.[/dim]
  [primary]tg beta endpoints deploy Qwen/Qwen2.5-7B --endpoint my-endpoint[/primary]

[dim]-[/dim] List endpoints in the current project:
  [primary]tg beta endpoints ls[/primary]

[dim]-[/dim] Inspect an endpoint or deployment:
  [primary]tg beta endpoints <endpoint-or-deployment-name-or-id>[/primary]

[dim]-[/dim] Scale a deployment and adjust its traffic weight:
  [primary]tg beta endpoints update <deployment-id> --min-replicas 2 --max-replicas 8 --traffic-weight 1[/primary]

[dim]-[/dim] Split live traffic to a new variant (A/B):
  [primary]tg beta endpoints ab Qwen/Qwen2.5-7B --control <deployment-id> --percent 10[/primary]

[dim]-[/dim] Mirror live traffic to a shadow deployment:
  [primary]tg beta endpoints shadow my-endpoint Qwen/Qwen2.5-7B --rate 0.1[/primary]

[dim]-[/dim] Delete a deployment, experiment, or entire endpoint:
  [primary]tg beta endpoints rm <ep_|dep_|abx_|exp_...>[/primary]
"""

BETA_ENDPOINTS_DEPLOY_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Deploy a public model onto a new endpoint:
  [primary]tg beta endpoints deploy Qwen/Qwen2.5-7B --endpoint my-endpoint[/primary]

[dim]-[/dim] Deploy a private model by ID onto an existing endpoint:
  [primary]tg beta endpoints deploy ml_xxxxxxxxxxxx --endpoint ep_yyyyyyyyyyyy[/primary]

[dim]-[/dim] Pin a config and start with autoscaling:
  [primary]tg beta endpoints deploy Qwen/Qwen2.5-7B --endpoint my-endpoint \\
    --config cr_xxxxxxxxxxxx --min-replicas 1 --max-replicas 4 \\
    --scaling-metric inflight_requests --scaling-target 10[/primary]

[dim]-[/dim] Deploy with LoRA support and no live traffic yet:
  [primary]tg beta endpoints deploy ml_xxxxxxxxxxxx --endpoint my-endpoint \\
    --enable-lora --traffic-weight 0[/primary]

[dim]-[/dim] Create the endpoint stopped (scale later with update):
  [primary]tg beta endpoints deploy Qwen/Qwen2.5-7B --endpoint my-endpoint \\
    --min-replicas 0 --max-replicas 0[/primary]
"""

BETA_ENDPOINTS_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Change replica bounds:
  [primary]tg beta endpoints update <deployment-id> --min-replicas 2 --max-replicas 8[/primary]

[dim]-[/dim] Stop a deployment (scale to zero):
  [primary]tg beta endpoints update <deployment-id> --min-replicas 0 --max-replicas 0[/primary]

[dim]-[/dim] Set autoscaling on TTFT p95:
  [primary]tg beta endpoints update <deployment-id> \\
    --scaling-metric ttft --scaling-target 200 --scaling-percentile p95[/primary]

[dim]-[/dim] Shift live traffic weight (relative to other deployments):
  [primary]tg beta endpoints update <deployment-id> --traffic-weight 2[/primary]

[dim]-[/dim] Set an A/B variant percent (takes from or returns to control):
  [primary]tg beta endpoints update <variant-deployment-id> --ab-percent 20[/primary]
"""

BETA_ENDPOINTS_AB_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Send 10% of live traffic to a new variant of a public model:
  [primary]tg beta endpoints ab Qwen/Qwen2.5-7B --control <deployment-id> --percent 10[/primary]

[dim]-[/dim] A/B a private model with an explicit config:
  [primary]tg beta endpoints ab ml_xxxxxxxxxxxx --control <deployment-id> \\
    --percent 25 --config cr_yyyyyyyyyyyy[/primary]

[dim]-[/dim] Variant with LoRA kernel enabled:
  [primary]tg beta endpoints ab ml_xxxxxxxxxxxx --control <deployment-id> \\
    --percent 5 --enable-lora --name my-variant[/primary]
"""

BETA_ENDPOINTS_SHADOW_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Mirror 10% of live requests to a shadow deployment:
  [primary]tg beta endpoints shadow my-endpoint Qwen/Qwen2.5-7B --rate 0.1[/primary]

[dim]-[/dim] Adaptive sampling to a target QPS:
  [primary]tg beta endpoints shadow ep_xxxxxxxxxxxx Qwen/Qwen2.5-7B --target-qps 5[/primary]

[dim]-[/dim] Sticky key-based sampling on a request field:
  [primary]tg beta endpoints shadow my-endpoint ml_xxxxxxxxxxxx --rate 0.2 --key user_id[/primary]

[dim]-[/dim] Shadow a private model with an explicit config:
  [primary]tg beta endpoints shadow my-endpoint ml_xxxxxxxxxxxx \\
    --config cr_yyyyyyyyyyyy --rate 0.05 --name my-shadow[/primary]

[dim]Note:[/dim] Shadow targets cannot be live traffic-split members or active rollout participants.
"""

BETA_ENDPOINTS_RM_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Delete a deployment:
  [primary]tg beta endpoints rm dep_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Delete an A/B or shadow experiment:
  [primary]tg beta endpoints rm abx_xxxxxxxxxxxx[/primary]
  [primary]tg beta endpoints rm exp_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Delete an empty endpoint:
  [primary]tg beta endpoints rm ep_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Force-delete an endpoint and all child deployments:
  [primary]tg beta endpoints rm ep_xxxxxxxxxxxx --force[/primary]
"""

BETA_ENDPOINTS_LS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List endpoints in the current project:
  [primary]tg beta endpoints ls[/primary]

[dim]-[/dim] List org-scoped endpoints:
  [primary]tg beta endpoints ls --org[/primary]

[dim]-[/dim] Paginate:
  [primary]tg beta endpoints ls --after <cursor>[/primary]
"""

BETA_ENDPOINTS_GET_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Get endpoint details by name or ID (includes deployments and traffic split):
  [primary]tg beta endpoints my-endpoint[/primary]
  [primary]tg beta endpoints ep_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Get a single deployment by name or ID:
  [primary]tg beta endpoints control[/primary]
  [primary]tg beta endpoints dep_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Machine-readable output:
  [primary]tg beta endpoints my-endpoint --json[/primary]
"""

## Beta models API commands

BETA_MODELS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Find a supported base model, then register your own:
  [primary]tg beta models public --search Qwen[/primary]
  [primary]tg beta models create --name my-model --base-model ml_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Upload weights from disk (or import remotely):
  [primary]tg beta models upload ml_yyyyyyyyyyyy ./path/to/my-model[/primary]
  [primary]tg beta models remote-uploads create ml_yyyyyyyyyyyy --from https://huggingface.co/org/model[/primary]

[dim]-[/dim] List project models and inspect one:
  [primary]tg beta models ls[/primary]
  [primary]tg beta models ml_yyyyyyyyyyyy[/primary]

[dim]-[/dim] List configs for a model to be used with [primary]tg beta endpoints deploy --config[/primary]:
  [primary]tg beta models configs ml_yyyyyyyyyyyy[/primary]

[dim]-[/dim] Download a revision locally:
  [primary]tg beta models download ml_yyyyyyyyyyyy ./out --format hf[/primary]
"""

BETA_MODELS_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Register a full model (find names/IDs with [primary]tg beta models public[/primary]):
  [primary]tg beta models create --name my-model --base-model ml_xxxxxxxxxxxx[/primary]

[dim]-[/dim] Or pass a deploy model name instead of an id:
  [primary]tg beta models create --name my-model --base-model Qwen/Qwen3.5-9B-FP8[/primary]

[dim]-[/dim] Register a LoRA adapter record:
  [primary]tg beta models create --name my-adapter --base-model ml_xxxxxxxxxxxx --type adapter[/primary]
"""

BETA_MODELS_UPLOAD_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Upload a local directory into an existing model record:
  [primary]tg beta models upload ml_xxxxxxxxxxxx ./path/to/my-model[/primary]

[dim]-[/dim] Upload a single file:
  [primary]tg beta models upload ml_xxxxxxxxxxxx ./model.safetensors[/primary]
"""

BETA_MODELS_DOWNLOAD_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Download the latest revision:
  [primary]tg beta models download ml_xxxxxxxxxxxx ./out[/primary]

[dim]-[/dim] Download a specific revision as a Hugging Face snapshot:
  [primary]tg beta models download ml_xxxxxxxxxxxx ./out --revision <revision-id> --format hf[/primary]

[dim]-[/dim] Download only selected paths:
  [primary]tg beta models download ml_xxxxxxxxxxxx ./out --files config.json --files tokenizer.json[/primary]
"""

BETA_MODELS_PUBLIC_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Search supported base models:
  [primary]tg beta models public --search Qwen[/primary]

[dim]-[/dim] Filter by modality / product:
  [primary]tg beta models public --modality text --product dedicated[/primary]

[dim]-[/dim] Paginate:
  [primary]tg beta models public --after <cursor>[/primary]
"""

BETA_MODELS_CONFIGS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List configs you can pass to [primary]tg beta endpoints deploy --config[/primary]:
  [primary]tg beta models configs ml_xxxxxxxxxxxx[/primary]
"""

BETA_MODELS_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Rename a model:
  [primary]tg beta models update ml_xxxxxxxxxxxx --name my-model-v2[/primary]

[dim]-[/dim] Update description:
  [primary]tg beta models update ml_xxxxxxxxxxxx --description "Production weights"[/primary]
"""

BETA_MODELS_REMOTE_UPLOADS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Import from Hugging Face into an existing model record:
  [primary]tg beta models remote-uploads create ml_xxxxxxxxxxxx \\
    --from https://huggingface.co/org/model[/primary]

[dim]-[/dim] List and inspect jobs:
  [primary]tg beta models remote-uploads ls[/primary]
  [primary]tg beta models remote-uploads get <job-id>[/primary]
"""

BETA_MODELS_REMOTE_UPLOADS_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Import a public Hugging Face repo:
  [primary]tg beta models remote-uploads create ml_xxxxxxxxxxxx \\
    --from https://huggingface.co/org/model[/primary]

[dim]-[/dim] Import a gated/private HF repo:
  [primary]tg beta models remote-uploads create ml_xxxxxxxxxxxx \\
    --from https://huggingface.co/org/private-model --token "$HF_TOKEN"[/primary]

[dim]-[/dim] Import from a presigned archive URL:
  [primary]tg beta models remote-uploads create ml_xxxxxxxxxxxx \\
    --from "https://bucket.s3.amazonaws.com/model.tar.gz?X-Amz-Signature=..."[/primary]
"""

## Beta clusters API commands

BETA_CLUSTERS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List clusters and regions:
  [primary]tg beta clusters list[/primary]
  [primary]tg beta clusters list-regions[/primary]

[dim]-[/dim] Write kubeconfig for a cluster (default ~/.kube/config):
  [primary]tg beta clusters get-credentials <cluster-id>[/primary]

[dim]-[/dim] Print kubeconfig to stdout:
  [primary]tg beta clusters get-credentials <cluster-id> --file -[/primary]

[dim]-[/dim] Non-interactive cluster create (see [primary]tg beta clusters create --help[/primary] for flags):
  [primary]tg beta clusters create --non-interactive \\
    --name my-cluster --cluster-type KUBERNETES --gpu-type H100_SXM \\
    --region us-central-8 --num-gpus 8 --billing-type ON_DEMAND \\
    --nvidia-version-id <nvidia-version-id> --volume <volume-id>[/primary]

[dim]-[/dim] Update or delete a cluster:
  [primary]tg beta clusters update <cluster-id> --num-gpus 16 --cluster-type KUBERNETES[/primary]
  [primary]tg beta clusters delete <cluster-id>[/primary]

[dim]-[/dim] Manage node remediations:
  [primary]tg beta clusters remediations ls <cluster-id>[/primary]
  [primary]tg beta clusters remediations create <cluster-id> <instance-id> --mode VM_ONLY[/primary]

[dim]-[/dim] SSH into a cluster (OIDC-signed certificate; see [primary]tg beta clusters ssh --help[/primary]):
  [primary]tg beta clusters ssh https://dex.<base>/<cluster-id> --login <username>[/primary]
"""

BETA_CLUSTERS_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create interactively (prompts for region, GPUs, drivers, etc.):
  [primary]tg beta clusters create[/primary]

[dim]-[/dim] Create without prompts (supply every required field):
  [primary]tg beta clusters create --non-interactive \\
    --name my-cluster \\
    --cluster-type KUBERNETES \\
    --gpu-type H100_SXM \\
    --region us-central-8 \\
    --num-gpus 8 \\
    --billing-type ON_DEMAND \\
    --nvidia-version-id <nvidia-version-id> \\
    --volume <volume-id>[/primary]
"""

BETA_CLUSTERS_GET_CREDENTIALS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Merge cluster kubeconfig into the default file ([primary]~/.kube/config[/primary]):
  [primary]tg beta clusters get-credentials <cluster-id>[/primary]

[dim]-[/dim] Write to a specific path:
  [primary]tg beta clusters get-credentials <cluster-id> --file ./my-kubeconfig[/primary]

[dim]-[/dim] Print kubeconfig to stdout (no file write):
  [primary]tg beta clusters get-credentials <cluster-id> --file -[/primary]

[dim]-[/dim] Use a custom context name in the merged kubeconfig:
  [primary]tg beta clusters get-credentials <cluster-id> --context-name my-prod-k8s[/primary]

[dim]-[/dim] On name conflicts with an existing kubeconfig, replace the entry:
  [primary]tg beta clusters get-credentials <cluster-id> --overwrite-existing[/primary]

[dim]-[/dim] Set this cluster as the default kube context after merge:
  [primary]tg beta clusters get-credentials <cluster-id> --set-default-context[/primary]
"""

BETA_CLUSTERS_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Change GPU count:
  [primary]tg beta clusters update <cluster-id> --num-gpus 16[/primary]

[dim]-[/dim] Change cluster type:
  [primary]tg beta clusters update <cluster-id> --cluster-type KUBERNETES[/primary]

[dim]-[/dim] Update both:
  [primary]tg beta clusters update <cluster-id> --num-gpus 16 --cluster-type KUBERNETES[/primary]
"""

BETA_CLUSTERS_STORAGE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List storage volumes:
  [primary]tg beta clusters storage list[/primary]

[dim]-[/dim] Create or resize a volume (see subcommand help for options):
  [primary]tg beta clusters storage create --region us-east-1 --size-tib 1 --volume-name my-data[/primary]
  [primary]tg beta clusters storage update <volume-id> --size-tib 4[/primary]

[dim]-[/dim] Use a volume when creating a cluster:
  [primary]tg beta clusters create --non-interactive ... --volume <volume-id>[/primary]
"""

BETA_CLUSTERS_STORAGE_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create a 1 TiB volume in a region ([primary]tg beta clusters list-regions[/primary] lists regions):
  [primary]tg beta clusters storage create \\
    --region us-east-1 \\
    --size-tib 1 \\
    --volume-name my-training-data[/primary]

[dim]-[/dim] Attach the volume when creating a cluster:
  [primary]tg beta clusters create --non-interactive ... --volume <volume-id>[/primary]
"""

BETA_CLUSTERS_STORAGE_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Grow a volume to 4 TiB:
  [primary]tg beta clusters storage update <volume-id> --size-tib 4[/primary]
"""

BETA_CLUSTERS_REMEDIATIONS_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] List all remediations for a cluster:
  [primary]tg beta clusters remediations ls <cluster-id>[/primary]

[dim]-[/dim] List remediations for one instance:
  [primary]tg beta clusters remediations ls <cluster-id> <instance-id>[/primary]

[dim]-[/dim] List automated remediations by mode:
  [primary]tg beta clusters remediations ls <cluster-id> --mode VM_ONLY --mode REBOOT_VM --trigger AUTOMATED[/primary]

[dim]-[/dim] Create a remediation:
  [primary]tg beta clusters remediations create <cluster-id> <instance-id> --mode VM_ONLY --reason "node unhealthy"[/primary]

[dim]-[/dim] Get remediation details:
  [primary]tg beta clusters remediations <remediation-id>[/primary]

[dim]-[/dim] Review automated remediations:
  [primary]tg beta clusters remediations approve <remediation-id>[/primary]
  [primary]tg beta clusters remediations reject <remediation-id> --comment "already handled"[/primary]
  [primary]tg beta clusters remediations cancel <remediation-id>[/primary]
"""

BETA_CLUSTERS_REMEDIATIONS_CREATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Create a VM-only remediation:
  [primary]tg beta clusters remediations create <cluster-id> <instance-id> --mode VM_ONLY[/primary]

[dim]-[/dim] Create a host-aware remediation:
  [primary]tg beta clusters remediations create <cluster-id> <instance-id> --mode HOST_AWARE[/primary]

[dim]-[/dim] Create a eviction-without-replacement remediation:
  [primary]tg beta clusters remediations create <cluster-id> <instance-id> --mode EVICT_WITHOUT_REPLACEMENT[/primary]

[dim]-[/dim] Create a reboot-vm remediation:
  [primary]tg beta clusters remediations create <cluster-id> <instance-id> --mode REBOOT_VM[/primary]
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
"""

JIG_VOLUMES_UPDATE_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Upload a new directory tree as the next volume version:
  [primary]tg beta jig volumes update --name model-weights --source ./weights[/primary]

[dim]-[/dim] Positional form:
  [primary]tg beta jig volumes update model-weights ./weights[/primary]
"""
