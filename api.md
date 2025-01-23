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
    ChatCompletionUsage,
)
```

Methods:

- <code title="post /chat/completions">client.chat.completions.<a href="./src/together/resources/chat/completions.py">create</a>(\*\*<a href="src/together/types/chat/completion_create_params.py">params</a>) -> <a href="./src/together/types/chat/chat_completion.py">ChatCompletion</a></code>

# Completions

Types:

```python
from together.types import Completion, LogProbs, ToolChoice, Tools
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
from together.types import FileObject, FileRetrieveResponse, FileListResponse, FileDeleteResponse
```

Methods:

- <code title="get /files/{id}">client.files.<a href="./src/together/resources/files.py">retrieve</a>(id) -> <a href="./src/together/types/file_retrieve_response.py">FileRetrieveResponse</a></code>
- <code title="get /files">client.files.<a href="./src/together/resources/files.py">list</a>() -> <a href="./src/together/types/file_list_response.py">FileListResponse</a></code>
- <code title="delete /files/{id}">client.files.<a href="./src/together/resources/files.py">delete</a>(id) -> <a href="./src/together/types/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="get /files/{id}/content">client.files.<a href="./src/together/resources/files.py">content</a>(id) -> BinaryAPIResponse</code>

# FineTune

Types:

```python
from together.types import FineTune, FineTuneEvent, FineTuneListResponse, FineTuneDownloadResponse
```

Methods:

- <code title="post /fine-tunes">client.fine_tune.<a href="./src/together/resources/fine_tune.py">create</a>(\*\*<a href="src/together/types/fine_tune_create_params.py">params</a>) -> <a href="./src/together/types/fine_tune.py">FineTune</a></code>
- <code title="get /fine-tunes/{id}">client.fine_tune.<a href="./src/together/resources/fine_tune.py">retrieve</a>(id) -> <a href="./src/together/types/fine_tune.py">FineTune</a></code>
- <code title="get /fine-tunes">client.fine_tune.<a href="./src/together/resources/fine_tune.py">list</a>() -> <a href="./src/together/types/fine_tune_list_response.py">FineTuneListResponse</a></code>
- <code title="post /fine-tunes/{id}/cancel">client.fine_tune.<a href="./src/together/resources/fine_tune.py">cancel</a>(id) -> <a href="./src/together/types/fine_tune.py">FineTune</a></code>
- <code title="get /finetune/download">client.fine_tune.<a href="./src/together/resources/fine_tune.py">download</a>(\*\*<a href="src/together/types/fine_tune_download_params.py">params</a>) -> <a href="./src/together/types/fine_tune_download_response.py">FineTuneDownloadResponse</a></code>
- <code title="get /fine-tunes/{id}/events">client.fine_tune.<a href="./src/together/resources/fine_tune.py">list_events</a>(id) -> <a href="./src/together/types/fine_tune_event.py">FineTuneEvent</a></code>

# Images

Types:

```python
from together.types import ImageFile
```

Methods:

- <code title="post /images/generations">client.images.<a href="./src/together/resources/images.py">create</a>(\*\*<a href="src/together/types/image_create_params.py">params</a>) -> <a href="./src/together/types/image_file.py">ImageFile</a></code>

# Audio

Types:

```python
from together.types import AudioFile
```

Methods:

- <code title="post /audio/speech">client.audio.<a href="./src/together/resources/audio.py">create</a>(\*\*<a href="src/together/types/audio_create_params.py">params</a>) -> BinaryAPIResponse</code>

# Models

Types:

```python
from together.types import ModelListResponse
```

Methods:

- <code title="get /models">client.models.<a href="./src/together/resources/models.py">list</a>() -> <a href="./src/together/types/model_list_response.py">ModelListResponse</a></code>
