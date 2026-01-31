# Beta

## Jig

Types:

```python
from together.types.beta import Deployment, DeploymentLogs, JigListResponse
```

Methods:

- <code title="get /deployments/{id}">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">retrieve</a>(id) -> <a href="./src/together/types/beta/deployment.py">Deployment</a></code>
- <code title="patch /deployments/{id}">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">update</a>(id, \*\*<a href="src/together/types/beta/jig_update_params.py">params</a>) -> <a href="./src/together/types/beta/deployment.py">Deployment</a></code>
- <code title="get /deployments">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">list</a>() -> <a href="./src/together/types/beta/jig_list_response.py">JigListResponse</a></code>
- <code title="post /deployments">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">deploy</a>(\*\*<a href="src/together/types/beta/jig_deploy_params.py">params</a>) -> <a href="./src/together/types/beta/deployment.py">Deployment</a></code>
- <code title="delete /deployments/{id}">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">destroy</a>(id) -> object</code>
- <code title="get /deployments/{id}/logs">client.beta.jig.<a href="./src/together/resources/beta/jig/jig.py">retrieve_logs</a>(id, \*\*<a href="src/together/types/beta/jig_retrieve_logs_params.py">params</a>) -> <a href="./src/together/types/beta/deployment_logs.py">DeploymentLogs</a></code>

### Queue

Types:

```python
from together.types.beta.jig import (
    QueueRetrieveResponse,
    QueueCancelResponse,
    QueueMetricsResponse,
    QueueSubmitResponse,
)
```

Methods:

- <code title="get /queue/status">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">retrieve</a>(\*\*<a href="src/together/types/beta/jig/queue_retrieve_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_retrieve_response.py">QueueRetrieveResponse</a></code>
- <code title="post /queue/cancel">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">cancel</a>(\*\*<a href="src/together/types/beta/jig/queue_cancel_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_cancel_response.py">QueueCancelResponse</a></code>
- <code title="get /queue/metrics">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">metrics</a>(\*\*<a href="src/together/types/beta/jig/queue_metrics_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_metrics_response.py">QueueMetricsResponse</a></code>
- <code title="post /queue/submit">client.beta.jig.queue.<a href="./src/together/resources/beta/jig/queue.py">submit</a>(\*\*<a href="src/together/types/beta/jig/queue_submit_params.py">params</a>) -> <a href="./src/together/types/beta/jig/queue_submit_response.py">QueueSubmitResponse</a></code>

### Volumes

Types:

```python
from together.types.beta.jig import Volume, VolumeListResponse
```

Methods:

- <code title="post /deployments/storage/volumes">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">create</a>(\*\*<a href="src/together/types/beta/jig/volume_create_params.py">params</a>) -> <a href="./src/together/types/beta/jig/volume.py">Volume</a></code>
- <code title="get /deployments/storage/volumes/{id}">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">retrieve</a>(id) -> <a href="./src/together/types/beta/jig/volume.py">Volume</a></code>
- <code title="patch /deployments/storage/volumes/{id}">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">update</a>(id, \*\*<a href="src/together/types/beta/jig/volume_update_params.py">params</a>) -> <a href="./src/together/types/beta/jig/volume.py">Volume</a></code>
- <code title="get /deployments/storage/volumes">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">list</a>() -> <a href="./src/together/types/beta/jig/volume_list_response.py">VolumeListResponse</a></code>
- <code title="delete /deployments/storage/volumes/{id}">client.beta.jig.volumes.<a href="./src/together/resources/beta/jig/volumes.py">delete</a>(id) -> object</code>

### Secrets

Types:

```python
from together.types.beta.jig import Secret, SecretListResponse
```

Methods:

- <code title="post /deployments/secrets">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">create</a>(\*\*<a href="src/together/types/beta/jig/secret_create_params.py">params</a>) -> <a href="./src/together/types/beta/jig/secret.py">Secret</a></code>
- <code title="get /deployments/secrets/{id}">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">retrieve</a>(id) -> <a href="./src/together/types/beta/jig/secret.py">Secret</a></code>
- <code title="patch /deployments/secrets/{id}">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">update</a>(id, \*\*<a href="src/together/types/beta/jig/secret_update_params.py">params</a>) -> <a href="./src/together/types/beta/jig/secret.py">Secret</a></code>
- <code title="get /deployments/secrets">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">list</a>() -> <a href="./src/together/types/beta/jig/secret_list_response.py">SecretListResponse</a></code>
- <code title="delete /deployments/secrets/{id}">client.beta.jig.secrets.<a href="./src/together/resources/beta/jig/secrets.py">delete</a>(id) -> object</code>

## Clusters

Types:

```python
from together.types.beta import (
    Cluster,
    ClusterListResponse,
    ClusterDeleteResponse,
    ClusterListRegionsResponse,
)
```

Methods:

- <code title="post /compute/clusters">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">create</a>(\*\*<a href="src/together/types/beta/cluster_create_params.py">params</a>) -> <a href="./src/together/types/beta/cluster.py">Cluster</a></code>
- <code title="get /compute/clusters/{cluster_id}">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">retrieve</a>(cluster_id) -> <a href="./src/together/types/beta/cluster.py">Cluster</a></code>
- <code title="put /compute/clusters/{cluster_id}">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">update</a>(cluster_id, \*\*<a href="src/together/types/beta/cluster_update_params.py">params</a>) -> <a href="./src/together/types/beta/cluster.py">Cluster</a></code>
- <code title="get /compute/clusters">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">list</a>() -> <a href="./src/together/types/beta/cluster_list_response.py">ClusterListResponse</a></code>
- <code title="delete /compute/clusters/{cluster_id}">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">delete</a>(cluster_id) -> <a href="./src/together/types/beta/cluster_delete_response.py">ClusterDeleteResponse</a></code>
- <code title="get /compute/regions">client.beta.clusters.<a href="./src/together/resources/beta/clusters/clusters.py">list_regions</a>() -> <a href="./src/together/types/beta/cluster_list_regions_response.py">ClusterListRegionsResponse</a></code>

### Storage

Types:

```python
from together.types.beta.clusters import ClusterStorage, StorageListResponse, StorageDeleteResponse
```

Methods:

- <code title="post /compute/clusters/storage/volumes">client.beta.clusters.storage.<a href="./src/together/resources/beta/clusters/storage.py">create</a>(\*\*<a href="src/together/types/beta/clusters/storage_create_params.py">params</a>) -> <a href="./src/together/types/beta/clusters/cluster_storage.py">ClusterStorage</a></code>
- <code title="get /compute/clusters/storage/volumes/{volume_id}">client.beta.clusters.storage.<a href="./src/together/resources/beta/clusters/storage.py">retrieve</a>(volume_id) -> <a href="./src/together/types/beta/clusters/cluster_storage.py">ClusterStorage</a></code>
- <code title="put /compute/clusters/storage/volumes">client.beta.clusters.storage.<a href="./src/together/resources/beta/clusters/storage.py">update</a>(\*\*<a href="src/together/types/beta/clusters/storage_update_params.py">params</a>) -> <a href="./src/together/types/beta/clusters/cluster_storage.py">ClusterStorage</a></code>
- <code title="get /compute/clusters/storage/volumes">client.beta.clusters.storage.<a href="./src/together/resources/beta/clusters/storage.py">list</a>() -> <a href="./src/together/types/beta/clusters/storage_list_response.py">StorageListResponse</a></code>
- <code title="delete /compute/clusters/storage/volumes/{volume_id}">client.beta.clusters.storage.<a href="./src/together/resources/beta/clusters/storage.py">delete</a>(volume_id) -> <a href="./src/together/types/beta/clusters/storage_delete_response.py">StorageDeleteResponse</a></code>

# Chat

## Completions

Types:

```python
from together.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionStructuredMessageImageURL,
    ChatCompletionStructuredMessageText,
    ChatCompletionStructuredMessageVideoURL,
    ChatCompletionUsage,
    ChatCompletionWarning,
)
```

Methods:

- <code title="post /chat/completions">client.chat.completions.<a href="./src/together/resources/chat/completions.py">create</a>(\*\*<a href="src/together/types/chat/completion_create_params.py">params</a>) -> <a href="./src/together/types/chat/chat_completion.py">ChatCompletion</a></code>

# Completions

Types:

```python
from together.types import Completion, CompletionChunk, LogProbs, ToolChoice, Tools
```

Methods:

- <code title="post /completions">client.completions.<a href="./src/together/resources/completions.py">create</a>(\*\*<a href="src/together/types/completion_create_params.py">params</a>) -> <a href="./src/together/types/completion.py">Completion</a></code>

# Embeddings

Types:

```python
from together.types import Embedding
```

Methods:

- <code title="post /embeddings">client.embeddings.<a href="./src/together/resources/embeddings.py">create</a>(\*\*<a href="src/together/types/embedding_create_params.py">params</a>) -> <a href="./src/together/types/embedding.py">Embedding</a></code>

# Files

Types:

```python
from together.types import (
    FileList,
    FileObject,
    FilePurpose,
    FileResponse,
    FileType,
    FileDeleteResponse,
)
```

Methods:

- <code title="get /files/{id}">client.files.<a href="./src/together/resources/files.py">retrieve</a>(id) -> <a href="./src/together/types/file_response.py">FileResponse</a></code>
- <code title="get /files">client.files.<a href="./src/together/resources/files.py">list</a>() -> <a href="./src/together/types/file_list.py">FileList</a></code>
- <code title="delete /files/{id}">client.files.<a href="./src/together/resources/files.py">delete</a>(id) -> <a href="./src/together/types/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="get /files/{id}/content">client.files.<a href="./src/together/resources/files.py">content</a>(id) -> BinaryAPIResponse</code>

# FineTuning

Types:

```python
from together.types import (
    FinetuneEvent,
    FinetuneEventType,
    FinetuneResponse,
    FineTuningListResponse,
    FineTuningDeleteResponse,
    FineTuningCancelResponse,
    FineTuningEstimatePriceResponse,
    FineTuningListCheckpointsResponse,
    FineTuningListEventsResponse,
)
```

Methods:

- <code title="get /fine-tunes/{id}">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">retrieve</a>(id) -> <a href="./src/together/types/finetune_response.py">FinetuneResponse</a></code>
- <code title="get /fine-tunes">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list</a>() -> <a href="./src/together/types/fine_tuning_list_response.py">FineTuningListResponse</a></code>
- <code title="delete /fine-tunes/{id}">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">delete</a>(id, \*\*<a href="src/together/types/fine_tuning_delete_params.py">params</a>) -> <a href="./src/together/types/fine_tuning_delete_response.py">FineTuningDeleteResponse</a></code>
- <code title="post /fine-tunes/{id}/cancel">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">cancel</a>(id) -> <a href="./src/together/types/fine_tuning_cancel_response.py">FineTuningCancelResponse</a></code>
- <code title="get /finetune/download">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">content</a>(\*\*<a href="src/together/types/fine_tuning_content_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="post /fine-tunes/estimate-price">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">estimate_price</a>(\*\*<a href="src/together/types/fine_tuning_estimate_price_params.py">params</a>) -> <a href="./src/together/types/fine_tuning_estimate_price_response.py">FineTuningEstimatePriceResponse</a></code>
- <code title="get /fine-tunes/{id}/checkpoints">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list_checkpoints</a>(id) -> <a href="./src/together/types/fine_tuning_list_checkpoints_response.py">FineTuningListCheckpointsResponse</a></code>
- <code title="get /fine-tunes/{id}/events">client.fine_tuning.<a href="./src/together/resources/fine_tuning.py">list_events</a>(id) -> <a href="./src/together/types/fine_tuning_list_events_response.py">FineTuningListEventsResponse</a></code>

# CodeInterpreter

Types:

```python
from together.types import ExecuteResponse
```

Methods:

- <code title="post /tci/execute">client.code_interpreter.<a href="./src/together/resources/code_interpreter/code_interpreter.py">execute</a>(\*\*<a href="src/together/types/code_interpreter_execute_params.py">params</a>) -> <a href="./src/together/types/execute_response.py">ExecuteResponse</a></code>

## Sessions

Types:

```python
from together.types.code_interpreter import SessionListResponse
```

Methods:

- <code title="get /tci/sessions">client.code_interpreter.sessions.<a href="./src/together/resources/code_interpreter/sessions.py">list</a>() -> <a href="./src/together/types/code_interpreter/session_list_response.py">SessionListResponse</a></code>

# Images

Types:

```python
from together.types import ImageDataB64, ImageDataURL, ImageFile
```

Methods:

- <code title="post /images/generations">client.images.<a href="./src/together/resources/images.py">generate</a>(\*\*<a href="src/together/types/image_generate_params.py">params</a>) -> <a href="./src/together/types/image_file.py">ImageFile</a></code>

# Videos

Types:

```python
from together.types import VideoJob
```

Methods:

- <code title="post /videos">client.videos.<a href="./src/together/resources/videos.py">create</a>(\*\*<a href="src/together/types/video_create_params.py">params</a>) -> <a href="./src/together/types/video_job.py">VideoJob</a></code>
- <code title="get /videos/{id}">client.videos.<a href="./src/together/resources/videos.py">retrieve</a>(id) -> <a href="./src/together/types/video_job.py">VideoJob</a></code>

# Audio

Types:

```python
from together.types import AudioFile, AudioSpeechStreamChunk
```

## Speech

Methods:

- <code title="post /audio/speech">client.audio.speech.<a href="./src/together/resources/audio/speech.py">create</a>(\*\*<a href="src/together/types/audio/speech_create_params.py">params</a>) -> BinaryAPIResponse</code>

## Voices

Types:

```python
from together.types.audio import VoiceListResponse
```

Methods:

- <code title="get /voices">client.audio.voices.<a href="./src/together/resources/audio/voices.py">list</a>() -> <a href="./src/together/types/audio/voice_list_response.py">VoiceListResponse</a></code>

## Transcriptions

Types:

```python
from together.types.audio import TranscriptionCreateResponse
```

Methods:

- <code title="post /audio/transcriptions">client.audio.transcriptions.<a href="./src/together/resources/audio/transcriptions.py">create</a>(\*\*<a href="src/together/types/audio/transcription_create_params.py">params</a>) -> <a href="./src/together/types/audio/transcription_create_response.py">TranscriptionCreateResponse</a></code>

## Translations

Types:

```python
from together.types.audio import TranslationCreateResponse
```

Methods:

- <code title="post /audio/translations">client.audio.translations.<a href="./src/together/resources/audio/translations.py">create</a>(\*\*<a href="src/together/types/audio/translation_create_params.py">params</a>) -> <a href="./src/together/types/audio/translation_create_response.py">TranslationCreateResponse</a></code>

# Models

Types:

```python
from together.types import ModelObject, ModelListResponse, ModelUploadResponse
```

Methods:

- <code title="get /models">client.models.<a href="./src/together/resources/models/models.py">list</a>(\*\*<a href="src/together/types/model_list_params.py">params</a>) -> <a href="./src/together/types/model_list_response.py">ModelListResponse</a></code>
- <code title="post /models">client.models.<a href="./src/together/resources/models/models.py">upload</a>(\*\*<a href="src/together/types/model_upload_params.py">params</a>) -> <a href="./src/together/types/model_upload_response.py">ModelUploadResponse</a></code>

## Uploads

Types:

```python
from together.types.models import UploadStatusResponse
```

Methods:

- <code title="get /jobs/{jobId}">client.models.uploads.<a href="./src/together/resources/models/uploads.py">status</a>(job_id) -> <a href="./src/together/types/models/upload_status_response.py">UploadStatusResponse</a></code>

# Endpoints

Types:

```python
from together.types import (
    Autoscaling,
    DedicatedEndpoint,
    EndpointListResponse,
    EndpointListAvzonesResponse,
)
```

Methods:

- <code title="post /endpoints">client.endpoints.<a href="./src/together/resources/endpoints.py">create</a>(\*\*<a href="src/together/types/endpoint_create_params.py">params</a>) -> <a href="./src/together/types/dedicated_endpoint.py">DedicatedEndpoint</a></code>
- <code title="get /endpoints/{endpointId}">client.endpoints.<a href="./src/together/resources/endpoints.py">retrieve</a>(endpoint_id) -> <a href="./src/together/types/dedicated_endpoint.py">DedicatedEndpoint</a></code>
- <code title="patch /endpoints/{endpointId}">client.endpoints.<a href="./src/together/resources/endpoints.py">update</a>(endpoint_id, \*\*<a href="src/together/types/endpoint_update_params.py">params</a>) -> <a href="./src/together/types/dedicated_endpoint.py">DedicatedEndpoint</a></code>
- <code title="get /endpoints">client.endpoints.<a href="./src/together/resources/endpoints.py">list</a>(\*\*<a href="src/together/types/endpoint_list_params.py">params</a>) -> <a href="./src/together/types/endpoint_list_response.py">EndpointListResponse</a></code>
- <code title="delete /endpoints/{endpointId}">client.endpoints.<a href="./src/together/resources/endpoints.py">delete</a>(endpoint_id) -> None</code>
- <code title="get /clusters/availability-zones">client.endpoints.<a href="./src/together/resources/endpoints.py">list_avzones</a>() -> <a href="./src/together/types/endpoint_list_avzones_response.py">EndpointListAvzonesResponse</a></code>

# Hardware

Types:

```python
from together.types import HardwareListResponse
```

Methods:

- <code title="get /hardware">client.hardware.<a href="./src/together/resources/hardware.py">list</a>(\*\*<a href="src/together/types/hardware_list_params.py">params</a>) -> <a href="./src/together/types/hardware_list_response.py">HardwareListResponse</a></code>

# Rerank

Types:

```python
from together.types import RerankCreateResponse
```

Methods:

- <code title="post /rerank">client.rerank.<a href="./src/together/resources/rerank.py">create</a>(\*\*<a href="src/together/types/rerank_create_params.py">params</a>) -> <a href="./src/together/types/rerank_create_response.py">RerankCreateResponse</a></code>

# Batches

Types:

```python
from together.types import BatchJob, BatchCreateResponse, BatchListResponse
```

Methods:

- <code title="post /batches">client.batches.<a href="./src/together/resources/batches.py">create</a>(\*\*<a href="src/together/types/batch_create_params.py">params</a>) -> <a href="./src/together/types/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="get /batches/{id}">client.batches.<a href="./src/together/resources/batches.py">retrieve</a>(id) -> <a href="./src/together/types/batch_job.py">BatchJob</a></code>
- <code title="get /batches">client.batches.<a href="./src/together/resources/batches.py">list</a>() -> <a href="./src/together/types/batch_list_response.py">BatchListResponse</a></code>
- <code title="post /batches/{id}/cancel">client.batches.<a href="./src/together/resources/batches.py">cancel</a>(id) -> <a href="./src/together/types/batch_job.py">BatchJob</a></code>

# Evals

Types:

```python
from together.types import EvaluationJob, EvalCreateResponse, EvalListResponse, EvalStatusResponse
```

Methods:

- <code title="post /evaluation">client.evals.<a href="./src/together/resources/evals.py">create</a>(\*\*<a href="src/together/types/eval_create_params.py">params</a>) -> <a href="./src/together/types/eval_create_response.py">EvalCreateResponse</a></code>
- <code title="get /evaluation/{id}">client.evals.<a href="./src/together/resources/evals.py">retrieve</a>(id) -> <a href="./src/together/types/evaluation_job.py">EvaluationJob</a></code>
- <code title="get /evaluation">client.evals.<a href="./src/together/resources/evals.py">list</a>(\*\*<a href="src/together/types/eval_list_params.py">params</a>) -> <a href="./src/together/types/eval_list_response.py">EvalListResponse</a></code>
- <code title="get /evaluation/{id}/status">client.evals.<a href="./src/together/resources/evals.py">status</a>(id) -> <a href="./src/together/types/eval_status_response.py">EvalStatusResponse</a></code>
