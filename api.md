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
