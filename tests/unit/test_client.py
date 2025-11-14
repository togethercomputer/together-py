import os
from unittest.mock import patch

import pytest

from together import Together, TogetherError


class TestTogether:
    @pytest.fixture
    def sync_together_instance(self) -> Together:
        """
        Initialize object with mocked API key
        """

        with patch.dict("os.environ", {"TOGETHER_API_KEY": "fake_api_key"}, clear=True):
            return Together()

    def test_init_with_api_key(self, sync_together_instance: Together):
        """
        Test API key from environment works
        """
        assert sync_together_instance.api_key == "fake_api_key"

    def test_init_without_api_key(self):
        """
        Test init without API key raises TogetherError
        """

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(TogetherError):
                Together()

    def test_init_with_base_url_from_env(self):
        """
        Test base_url from environment
        """

        with patch.dict("os.environ", {"TOGETHER_BASE_URL": "https://example.com"}):
            sync_together = Together(api_key="fake_api_key")

            assert sync_together.base_url == "https://example.com"

    def test_init_with_default_base_url(self):
        """
        Test default base_url
        """

        with patch.dict("os.environ", clear=True):
            sync_together = Together(api_key="fake_api_key")

            assert sync_together.base_url == "https://api.together.xyz/v1/"

    def test_init_with_default_headers(self):
        """
        Test initializing with default_headers
        """

        default_headers = {"header1": "value1", "header2": "value2"}

        sync_together = Together(api_key="fake_api_key", default_headers=default_headers)

        assert default_headers.items() <= sync_together.default_headers.items()

    def test_completions_initialized(self, sync_together_instance: Together):
        """
        Test initializing completions
        """

        assert sync_together_instance.completions is not None

        assert isinstance(sync_together_instance.completions._client, Together)

    def test_chat_initialized(self, sync_together_instance: Together):
        """
        Test initializing chat
        """

        assert sync_together_instance.chat is not None

        assert isinstance(sync_together_instance.chat._client, Together)

        assert isinstance(sync_together_instance.chat.completions._client, Together)

    def test_embeddings_initialized(self, sync_together_instance: Together):
        """
        Test initializing embeddings
        """

        assert sync_together_instance.embeddings is not None

        assert isinstance(sync_together_instance.embeddings._client, Together)

    def test_files_initialized(self, sync_together_instance: Together):
        """
        Test initializing files
        """

        assert sync_together_instance.files is not None

        assert isinstance(sync_together_instance.files._client, Together)

    def test_fine_tuning_initialized(self, sync_together_instance: Together):
        """
        Test initializing fine_tuning
        """

        assert sync_together_instance.fine_tuning is not None

        assert isinstance(sync_together_instance.fine_tuning._client, Together)
