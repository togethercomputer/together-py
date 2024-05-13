# Chat

## Completions

Types:

```python
from together_ai.types.chat import ChatCompletion, ChatCompletionChunk, Usage
```

Methods:

- <code title="post /chat/completions">client.chat.completions.<a href="./src/together_ai/resources/chat/completions.py">create</a>(\*\*<a href="src/together_ai/types/chat/completion_create_params.py">params</a>) -> <a href="./src/together_ai/types/chat/chat_completion.py">ChatCompletion</a></code>

# Completions

Types:

```python
from together_ai.types import CompletionResponse
```

Methods:

- <code title="post /completions">client.completions.<a href="./src/together_ai/resources/completions.py">create</a>(\*\*<a href="src/together_ai/types/completion_create_params.py">params</a>) -> <a href="./src/together_ai/types/completion_response.py">CompletionResponse</a></code>

# Embeddings

Types:

```python
from together_ai.types import EmbeddingsResponse
```

Methods:

- <code title="post /embeddings">client.embeddings.<a href="./src/together_ai/resources/embeddings.py">create</a>(\*\*<a href="src/together_ai/types/embedding_create_params.py">params</a>) -> <a href="./src/together_ai/types/embeddings_response.py">EmbeddingsResponse</a></code>

# Files

Types:

```python
from together_ai.types import FileRetrieveResponse, FileListResponse, FileDeleteResponse
```

Methods:

- <code title="get /files/{id}">client.files.<a href="./src/together_ai/resources/files.py">retrieve</a>(id) -> <a href="./src/together_ai/types/file_retrieve_response.py">FileRetrieveResponse</a></code>
- <code title="get /files">client.files.<a href="./src/together_ai/resources/files.py">list</a>() -> <a href="./src/together_ai/types/file_list_response.py">FileListResponse</a></code>
- <code title="delete /files/{id}">client.files.<a href="./src/together_ai/resources/files.py">delete</a>(id) -> <a href="./src/together_ai/types/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="get /files/{id}/content">client.files.<a href="./src/together_ai/resources/files.py">content</a>(id) -> BinaryAPIResponse</code>

# FineTune

Types:

```python
from together_ai.types import FineTune, FineTuneListResponse, FineTuneListEventsResponse
```

Methods:

- <code title="post /fine-tunes">client.fine_tune.<a href="./src/together_ai/resources/fine_tune.py">create</a>(\*\*<a href="src/together_ai/types/fine_tune_create_params.py">params</a>) -> <a href="./src/together_ai/types/fine_tune.py">FineTune</a></code>
- <code title="get /fine-tunes/{id}">client.fine_tune.<a href="./src/together_ai/resources/fine_tune.py">retrieve</a>(id) -> <a href="./src/together_ai/types/fine_tune.py">FineTune</a></code>
- <code title="get /fine-tunes">client.fine_tune.<a href="./src/together_ai/resources/fine_tune.py">list</a>() -> <a href="./src/together_ai/types/fine_tune_list_response.py">FineTuneListResponse</a></code>
- <code title="post /fine-tunes/{id}/cancel">client.fine_tune.<a href="./src/together_ai/resources/fine_tune.py">cancel</a>(id) -> <a href="./src/together_ai/types/fine_tune.py">FineTune</a></code>
- <code title="get /fine-tunes/{id}/events">client.fine_tune.<a href="./src/together_ai/resources/fine_tune.py">list_events</a>(id) -> <a href="./src/together_ai/types/fine_tune_list_events_response.py">FineTuneListEventsResponse</a></code>

# Images

Types:

```python
from together_ai.types import ImagesResponse
```

Methods:

- <code title="post /images/generations">client.images.<a href="./src/together_ai/resources/images.py">create</a>(\*\*<a href="src/together_ai/types/image_create_params.py">params</a>) -> <a href="./src/together_ai/types/images_response.py">ImagesResponse</a></code>

# Models

Types:

```python
from together_ai.types import ModelListResponse
```

Methods:

- <code title="get /models">client.models.<a href="./src/together_ai/resources/models.py">list</a>() -> <a href="./src/together_ai/types/model_list_response.py">ModelListResponse</a></code>
