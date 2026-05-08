## Top-level commands

TOP_LEVEL_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Fine tune a model for your dataset:
  [primary]tg ft create --model Qwen/Qwen2-1.5B --training-file ./my-dataset.jsonl --lora[/primary]

[dim]-[/dim] Deploy a model to a dedicated endpoint:
  [primary]tg endpoints create --model Qwen/Qwen2.5-7B --hardware 2x_nvidia_h100_80gb_sxm --wait[/primary]

[dim]-[/dim] Upload an external model to Together:
  [primary]tg models upload --model-name my-org/my-model --model-source s3-or-hugging-face[/primary]
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

[dim]-[/dim] List checkpoints for a fine-tuning job:
  [primary]tg ft list-checkpoints <ft-job-id>[/primary]

[dim]-[/dim] Cancel a fine-tuning job:
  [primary]tg ft cancel <ft-job-id>[/primary]
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

FINE_TUNING_DOWNLOAD_HELP_EXAMPLES = """[dim]Examples:[/dim]
[dim]-[/dim] Download a fine-tuned model's weights:
  [primary]tg ft download <ft-job-id> --output-dir ./my-model[/primary]

[dim]-[/dim] Download a fine-tuned model's weights from a specific checkpoint:
  [primary]tg ft download <ft-job-id> --checkpoint-step 1 --output-dir ./my-model[/primary]
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
    --model-b-input-template $'Answer the following:\\n\\n{{prompt}}'[/primary]
"""
