import os
from itertools import product

import pytest

from together import (
    Together,
    BadRequestError,
    UnprocessableEntityError,
)
from together.types import Completion
from together.types.completion import (
    Choice,
    ChatCompletionUsage,
)

from ..constants import (
    completion_prompt_list,
    completion_test_model_list,
    moderation_test_model_list,
)
from .generate_hyperparameters import (
    random_min_p,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_top_k,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_top_p,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_max_tokens,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_temperature,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_presence_penalty,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_frequency_penalty,  # noqa: F401 # pyright: ignore[reportUnusedImport]
    random_repetition_penalty,  # noqa: F401 # pyright: ignore[reportUnusedImport]
)

STOP = ["</s>"]


class TestTogetherCompletion:
    @pytest.fixture
    def sync_together_client(self) -> Together:
        """
        Initialize object with mocked API key
        """
        TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        return Together(api_key=TOGETHER_API_KEY)

    @pytest.mark.parametrize(
        "model,prompt",
        product(completion_test_model_list, completion_prompt_list),
    )
    def test_create(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
        random_max_tokens: int,
        random_temperature: float,
        random_top_p: float,
        random_top_k: int,
        random_presence_penalty: float,
        random_frequency_penalty: float,
        random_min_p: float,
    ) -> None:
        """
        Tests structure and typing
        """
        prompt = "The space robots have"

        # max_tokens should be a reasonable number for this test
        assert 0 < random_max_tokens < 1024

        assert 0 <= random_temperature <= 2

        assert 0 <= random_top_p <= 1

        assert 1 <= random_top_k <= 100

        assert -2 <= random_presence_penalty <= 2

        assert -2 <= random_frequency_penalty <= 2

        assert 0 <= random_min_p <= 1

        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=random_max_tokens,
            temperature=random_temperature,
            top_p=random_top_p,
            top_k=random_top_k,
            presence_penalty=random_presence_penalty,
            frequency_penalty=random_frequency_penalty,
            min_p=random_min_p,
            logit_bias={"1024": 10},
            echo=True,
        )

        assert isinstance(response, Completion)

        assert isinstance(response.id, str)
        assert isinstance(response.created, int)
        assert response.object == "text.completion"
        assert isinstance(response.choices, list)
        assert isinstance(response.choices[0], Choice)
        assert isinstance(response.choices[0].text, str)
        assert isinstance(response.prompt, list)
        assert isinstance(response.prompt[0].text, str)
        assert isinstance(response.usage, ChatCompletionUsage)
        assert isinstance(response.usage.prompt_tokens, int)
        assert isinstance(response.usage.completion_tokens, int)
        assert isinstance(response.usage.total_tokens, int)
        assert response.usage.prompt_tokens + response.usage.completion_tokens == response.usage.total_tokens

    @pytest.mark.parametrize(
        "model,prompt",
        product(completion_test_model_list, completion_prompt_list),
    )
    def test_prompt(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=10,
            echo=True,
        )

        assert isinstance(response, Completion)

        assert isinstance(response.prompt, list)
        assert response.prompt[0].text == prompt

    @pytest.mark.parametrize(
        "model,prompt",
        product(completion_test_model_list, completion_prompt_list),
    )
    def test_no_prompt(
        self,
        model: str,
        prompt: str,  # noqa
        sync_together_client: Together,
    ):
        with pytest.raises(TypeError):
            _ = sync_together_client.completions.create(  # pyright: ignore[reportCallIssue, reportUnknownVariableType]
                model=model,
                stop=STOP,
                max_tokens=10,
                echo=True,
            )

    @pytest.mark.parametrize(
        "model,prompt",
        product(completion_test_model_list, completion_prompt_list),
    )
    def test_model(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=10,
            echo=True,
        )

        assert isinstance(response, Completion)

    @pytest.mark.parametrize(
        "model,prompt",
        product(completion_test_model_list, completion_prompt_list),
    )
    def test_no_model(
        self,
        model: str,  # noqa
        prompt: str,
        sync_together_client: Together,
    ):
        with pytest.raises(TypeError):
            _ = sync_together_client.completions.create(  # pyright: ignore[reportCallIssue, reportUnknownVariableType]
                prompt=prompt,
                stop=STOP,
                max_tokens=10,
                echo=True,
            )

    @pytest.mark.parametrize(
        "model,prompt",
        product(completion_test_model_list, completion_prompt_list),
    )
    def test_max_tokens(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=1,
        )

        assert isinstance(response, Completion)

        assert response.usage is not None
        assert response.usage.completion_tokens == 1

    @pytest.mark.parametrize(
        "model,prompt,max_tokens",
        product(
            completion_test_model_list,
            completion_prompt_list,
            [200000, 400000, 500000],
        ),
    )
    def test_high_max_tokens(
        self,
        model: str,
        prompt: str,
        max_tokens: int,
        sync_together_client: Together,
    ):
        with pytest.raises(UnprocessableEntityError):
            _ = sync_together_client.completions.create(
                prompt=prompt,
                model=model,
                stop=STOP,
                max_tokens=max_tokens,
            )

    @pytest.mark.parametrize(
        "model,prompt",
        product(completion_test_model_list, completion_prompt_list),
    )
    def test_echo(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt, model=model, stop=STOP, max_tokens=1, echo=True, logprobs=1
        )

        assert isinstance(response, Completion)

        assert response.prompt is not None
        assert response.prompt[0].text == prompt
        assert response.prompt[0].logprobs is not None
        assert isinstance(response.prompt[0].logprobs.tokens, list)
        assert isinstance(response.prompt[0].logprobs.token_logprobs, list)

    @pytest.mark.parametrize(
        "model,prompt,n",
        product(completion_test_model_list, completion_prompt_list, [1, 2, 3, 4]),
    )
    def test_n(
        self,
        model: str,
        prompt: str,
        n: int,
        sync_together_client: Together,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt, model=model, stop=STOP, max_tokens=1, n=n, temperature=0.5
        )

        assert isinstance(response, Completion)

        assert len(response.choices) == n

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_high_n(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        MAX_N = 128
        n = MAX_N + 1

        with pytest.raises(BadRequestError):
            _ = sync_together_client.completions.create(
                prompt=prompt,
                model=model,
                stop=STOP,
                max_tokens=1,
                n=n,
                temperature=0.1,
            )

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_n_with_no_sample(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        MAX_N = 128
        n = MAX_N + 1

        with pytest.raises(BadRequestError):
            _ = sync_together_client.completions.create(
                prompt=prompt,
                model=model,
                stop=STOP,
                max_tokens=1,
                n=n,
            )

    @pytest.mark.parametrize(
        "model,prompt,safety_model",
        product(
            completion_test_model_list,
            completion_prompt_list,
            moderation_test_model_list,
        ),
    )
    def test_safety_model(
        self,
        model: str,
        prompt: str,
        safety_model: str,
        sync_together_client: Together,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=1,
            safety_model=safety_model,
        )

        assert isinstance(response, Completion)

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_repetition_penalty(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
        random_repetition_penalty: float,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=10,
            repetition_penalty=random_repetition_penalty,
        )

        assert isinstance(response, Completion)

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_presence_penalty(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
        random_presence_penalty: float,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=10,
            presence_penalty=random_presence_penalty,
        )

        assert isinstance(response, Completion)

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_high_presence_penalty(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        with pytest.raises(BadRequestError):
            _ = sync_together_client.completions.create(
                prompt=prompt,
                model=model,
                stop=STOP,
                max_tokens=10,
                presence_penalty=2.1,
            )

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_frequency_penalty(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
        random_frequency_penalty: float,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=10,
            frequency_penalty=random_frequency_penalty,
        )

        assert isinstance(response, Completion)

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_high_frequency_penalty(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        with pytest.raises(BadRequestError):
            _ = sync_together_client.completions.create(
                prompt=prompt,
                model=model,
                stop=STOP,
                max_tokens=10,
                frequency_penalty=2.1,
            )

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_min_p(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
        random_min_p: float,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=10,
            min_p=random_min_p,
        )

        assert isinstance(response, Completion)

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_high_min_p(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        with pytest.raises(BadRequestError):
            _ = sync_together_client.completions.create(
                prompt=prompt,
                model=model,
                stop=STOP,
                max_tokens=10,
                min_p=1.1,
            )

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_logit_bias(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=1,
            logit_bias={"1024": 10},
        )

        assert isinstance(response, Completion)

    @pytest.mark.parametrize(
        "model,prompt",
        product(
            completion_test_model_list,
            completion_prompt_list,
        ),
    )
    def test_seed(
        self,
        model: str,
        prompt: str,
        sync_together_client: Together,
    ):
        response = sync_together_client.completions.create(
            prompt=prompt,
            model=model,
            stop=STOP,
            max_tokens=1,
            seed=4242,
        )

        assert isinstance(response, Completion)
        assert response.choices[0].seed == 4242
