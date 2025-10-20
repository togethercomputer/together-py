# Together

Types:

```python
from together.types import RerankResponse
```

Methods:

- <code title="post /rerank">client.<a href="./src/together/_client.py">rerank</a>(\*\*<a href="src/together/types/client_rerank_params.py">params</a>) -> <a href="./src/together/types/rerank_response.py">RerankResponse</a></code>

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
    FileObject,
    FilePurpose,
    FileType,
    FileRetrieveResponse,
    FileListResponse,
    FileDeleteResponse,
    FileUploadResponse,
)
```

Methods:

- <code title="get /files/{id}">client.files.<a href="./src/together/resources/files.py">retrieve</a>(id) -> <a href="./src/together/types/file_retrieve_response.py">FileRetrieveResponse</a></code>
- <code title="get /files">client.files.<a href="./src/together/resources/files.py">list</a>() -> <a href="./src/together/types/file_list_response.py">FileListResponse</a></code>
- <code title="delete /files/{id}">client.files.<a href="./src/together/resources/files.py">delete</a>(id) -> <a href="./src/together/types/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="get /files/{id}/content">client.files.<a href="./src/together/resources/files.py">content</a>(id) -> BinaryAPIResponse</code>
- <code title="post /files/upload">client.files.<a href="./src/together/resources/files.py">upload</a>(\*\*<a href="src/together/types/file_upload_params.py">params</a>) -> <a href="./src/together/types/file_upload_response.py">FileUploadResponse</a></code>

# FineTune

Types:

```python
from together.types import (
    CosineLrSchedulerArgs,
    FineTune,
    FineTuneEvent,
    FullTrainingType,
    LinearLrSchedulerArgs,
    LoRaTrainingType,
    LrScheduler,
    TrainingMethodDpo,
    TrainingMethodSft,
    FineTuneCreateResponse,
    FineTuneListResponse,
    FineTuneCancelResponse,
    FineTuneDownloadResponse,
    FineTuneListEventsResponse,
    FineTuneRetrieveCheckpointsResponse,
)
```

Methods:

- <code title="post /fine-tunes">client.fine_tune.<a href="./src/together/resources/fine_tune.py">create</a>(\*\*<a href="src/together/types/fine_tune_create_params.py">params</a>) -> <a href="./src/together/types/fine_tune_create_response.py">FineTuneCreateResponse</a></code>
- <code title="get /fine-tunes/{id}">client.fine_tune.<a href="./src/together/resources/fine_tune.py">retrieve</a>(id) -> <a href="./src/together/types/fine_tune.py">FineTune</a></code>
- <code title="get /fine-tunes">client.fine_tune.<a href="./src/together/resources/fine_tune.py">list</a>() -> <a href="./src/together/types/fine_tune_list_response.py">FineTuneListResponse</a></code>
- <code title="post /fine-tunes/{id}/cancel">client.fine_tune.<a href="./src/together/resources/fine_tune.py">cancel</a>(id) -> <a href="./src/together/types/fine_tune_cancel_response.py">FineTuneCancelResponse</a></code>
- <code title="get /finetune/download">client.fine_tune.<a href="./src/together/resources/fine_tune.py">download</a>(\*\*<a href="src/together/types/fine_tune_download_params.py">params</a>) -> <a href="./src/together/types/fine_tune_download_response.py">FineTuneDownloadResponse</a></code>
- <code title="get /fine-tunes/{id}/events">client.fine_tune.<a href="./src/together/resources/fine_tune.py">list_events</a>(id) -> <a href="./src/together/types/fine_tune_list_events_response.py">FineTuneListEventsResponse</a></code>
- <code title="get /fine-tunes/{id}/checkpoints">client.fine_tune.<a href="./src/together/resources/fine_tune.py">retrieve_checkpoints</a>(id) -> <a href="./src/together/types/fine_tune_retrieve_checkpoints_response.py">FineTuneRetrieveCheckpointsResponse</a></code>

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

- <code title="post /images/generations">client.images.<a href="./src/together/resources/images.py">create</a>(\*\*<a href="src/together/types/image_create_params.py">params</a>) -> <a href="./src/together/types/image_file.py">ImageFile</a></code>

# Videos

Types:

```python
from together.types import VideoCreateResponse, VideoRetrieveResponse
```

Methods:

- <code title="post /videos">client.videos.<a href="./src/together/resources/videos.py">create</a>(\*\*<a href="src/together/types/video_create_params.py">params</a>) -> <a href="./src/together/types/video_create_response.py">VideoCreateResponse</a></code>
- <code title="get /videos/{id}">client.videos.<a href="./src/together/resources/videos.py">retrieve</a>(id) -> <a href="./src/together/types/video_retrieve_response.py">VideoRetrieveResponse</a></code>

# Audio

Types:

```python
from together.types import AudioFile, AudioSpeechStreamChunk
```

Methods:

- <code title="post /audio/speech">client.audio.<a href="./src/together/resources/audio/audio.py">create</a>(\*\*<a href="src/together/types/audio_create_params.py">params</a>) -> BinaryAPIResponse</code>

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
from together.types import ModelListResponse, ModelUploadResponse
```

Methods:

- <code title="get /models">client.models.<a href="./src/together/resources/models.py">list</a>() -> <a href="./src/together/types/model_list_response.py">ModelListResponse</a></code>
- <code title="post /models">client.models.<a href="./src/together/resources/models.py">upload</a>(\*\*<a href="src/together/types/model_upload_params.py">params</a>) -> <a href="./src/together/types/model_upload_response.py">ModelUploadResponse</a></code>

# Jobs

Types:

```python
from together.types import JobRetrieveResponse, JobListResponse
```

Methods:

- <code title="get /jobs/{jobId}">client.jobs.<a href="./src/together/resources/jobs.py">retrieve</a>(job_id) -> <a href="./src/together/types/job_retrieve_response.py">JobRetrieveResponse</a></code>
- <code title="get /jobs">client.jobs.<a href="./src/together/resources/jobs.py">list</a>() -> <a href="./src/together/types/job_list_response.py">JobListResponse</a></code>

# Endpoints

Types:

```python
from together.types import (
    Autoscaling,
    EndpointCreateResponse,
    EndpointRetrieveResponse,
    EndpointUpdateResponse,
    EndpointListResponse,
)
```

Methods:

- <code title="post /endpoints">client.endpoints.<a href="./src/together/resources/endpoints.py">create</a>(\*\*<a href="src/together/types/endpoint_create_params.py">params</a>) -> <a href="./src/together/types/endpoint_create_response.py">EndpointCreateResponse</a></code>
- <code title="get /endpoints/{endpointId}">client.endpoints.<a href="./src/together/resources/endpoints.py">retrieve</a>(endpoint_id) -> <a href="./src/together/types/endpoint_retrieve_response.py">EndpointRetrieveResponse</a></code>
- <code title="patch /endpoints/{endpointId}">client.endpoints.<a href="./src/together/resources/endpoints.py">update</a>(endpoint_id, \*\*<a href="src/together/types/endpoint_update_params.py">params</a>) -> <a href="./src/together/types/endpoint_update_response.py">EndpointUpdateResponse</a></code>
- <code title="get /endpoints">client.endpoints.<a href="./src/together/resources/endpoints.py">list</a>(\*\*<a href="src/together/types/endpoint_list_params.py">params</a>) -> <a href="./src/together/types/endpoint_list_response.py">EndpointListResponse</a></code>
- <code title="delete /endpoints/{endpointId}">client.endpoints.<a href="./src/together/resources/endpoints.py">delete</a>(endpoint_id) -> None</code>

# Hardware

Types:

```python
from together.types import HardwareListResponse
```

Methods:

- <code title="get /hardware">client.hardware.<a href="./src/together/resources/hardware.py">list</a>(\*\*<a href="src/together/types/hardware_list_params.py">params</a>) -> <a href="./src/together/types/hardware_list_response.py">HardwareListResponse</a></code>

# Batches

Types:

```python
from together.types import BatchCreateResponse, BatchRetrieveResponse, BatchListResponse
```

Methods:

- <code title="post /batches">client.batches.<a href="./src/together/resources/batches.py">create</a>(\*\*<a href="src/together/types/batch_create_params.py">params</a>) -> <a href="./src/together/types/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="get /batches/{id}">client.batches.<a href="./src/together/resources/batches.py">retrieve</a>(id) -> <a href="./src/together/types/batch_retrieve_response.py">BatchRetrieveResponse</a></code>
- <code title="get /batches">client.batches.<a href="./src/together/resources/batches.py">list</a>() -> <a href="./src/together/types/batch_list_response.py">BatchListResponse</a></code>

# Evaluations

Types:

```python
from together.types import (
    EvaluationJudgeModelConfig,
    EvaluationModelRequest,
    EvaluationRetrieveResponse,
    EvaluationListResponse,
    EvaluationGetAllowedModelsResponse,
    EvaluationGetStatusResponse,
)
```

Methods:

- <code title="get /evaluation/{id}">client.evaluations.<a href="./src/together/resources/evaluations.py">retrieve</a>(id) -> <a href="./src/together/types/evaluation_retrieve_response.py">EvaluationRetrieveResponse</a></code>
- <code title="get /evaluations">client.evaluations.<a href="./src/together/resources/evaluations.py">list</a>(\*\*<a href="src/together/types/evaluation_list_params.py">params</a>) -> <a href="./src/together/types/evaluation_list_response.py">EvaluationListResponse</a></code>
- <code title="get /evaluations/model-list">client.evaluations.<a href="./src/together/resources/evaluations.py">get_allowed_models</a>() -> <a href="./src/together/types/evaluation_get_allowed_models_response.py">EvaluationGetAllowedModelsResponse</a></code>
- <code title="get /evaluation/{id}/status">client.evaluations.<a href="./src/together/resources/evaluations.py">get_status</a>(id) -> <a href="./src/together/types/evaluation_get_status_response.py">EvaluationGetStatusResponse</a></code>
