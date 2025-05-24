import os

import pytest

from together import Together
from together.types.completion_chunk import Choice, ChoiceDelta, CompletionChunk, ChatCompletionUsage

from .generate_hyperparameters import (
    random_top_k,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_top_p,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_max_tokens,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_temperature,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_repetition_penalty,  # noqa: F401 # pyright: ignore[reportUnusedImport]
)


class TestTogetherCompletionStream:
    @pytest.fixture
    def sync_together_client(self) -> Together:
        """
        Initialize object with mocked API key
        """
        TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        return Together(api_key=TOGETHER_API_KEY)

    def test_create(
        self,
        sync_together_client: Together,
        random_max_tokens: int,
        random_temperature: float,
        random_top_p: float,
        random_top_k: int,
        random_repetition_penalty: float,
    ) -> None:
        prompt = "The space robots have"
        model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        stop = ["</s>"]

        # max_tokens should be a reasonable number for this test
        assert 0 < random_max_tokens < 1024

        assert 0 <= random_temperature <= 2

        assert 0 <= random_top_p <= 1

        assert 1 <= random_top_k <= 100

        assert 0 <= random_repetition_penalty <= 2

        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=stop,
            max_tokens=random_max_tokens,
            temperature=random_temperature,
            top_p=random_top_p,
            top_k=random_top_k,
            repetition_penalty=random_repetition_penalty,
            stream=True,
        )

        usage = None

        for chunk in response:
            assert isinstance(chunk, CompletionChunk)
            assert isinstance(chunk.id, str)
            assert isinstance(chunk.created, int)
            assert chunk.object == "completion.chunk"
            assert isinstance(chunk.choices[0], Choice)
            assert isinstance(chunk.choices[0].index, int)
            assert isinstance(chunk.choices[0].delta, ChoiceDelta)
            assert isinstance(chunk.choices[0].delta.content, str)

            usage = chunk.usage

        assert isinstance(usage, ChatCompletionUsage)
        assert isinstance(usage.prompt_tokens, int)
        assert isinstance(usage.completion_tokens, int)
        assert isinstance(usage.total_tokens, int)
        assert usage.prompt_tokens + usage.completion_tokens == usage.total_tokens

    def test_prompt(self):
        pass

    def test_no_prompt(self):
        pass

    def test_model(self):
        pass

    def test_no_model(self):
        pass

    def test_max_tokens(self):
        pass

    def test_no_max_tokens(self):
        pass

    def test_high_max_tokens(self):
        pass

    def test_stop(self):
        pass

    def test_no_stop(self):
        pass

    def test_temperature(self):
        pass

    def test_top_p(self):
        pass

    def test_top_k(self):
        pass

    def test_repetition_penalty(self):
        pass

    def test_echo(self):
        pass

    def test_n(self):
        pass

    def test_safety_model(self):
        pass
