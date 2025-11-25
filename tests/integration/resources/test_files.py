import os
import json
from pathlib import Path

import pytest

from together import Together
from together.types import (
    FileResponse,
)


class TestTogetherFiles:
    @pytest.fixture
    def sync_together_client(self) -> Together:
        """
        Initialize object with mocked API key
        """
        TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        return Together(api_key=TOGETHER_API_KEY)

    def test_file_upload(
        self,
        sync_together_client: Together,
        tmp_path: Path,
    ):
        # Mock the post method directly on the client
        files = sync_together_client.files

        # Make a temporary file object
        file = tmp_path / "valid.jsonl"
        content = [{"text": "Hello, world!"}, {"text": "How are you?"}]
        with file.open("w") as f:
            f.write("\n".join(json.dumps(item) for item in content))

        # Test run method
        response = files.upload(
            file,
        )

        # Verify the response
        assert isinstance(response, FileResponse)
        assert response.filename == "valid.jsonl"
        assert response.file_type == "jsonl"
        assert response.line_count == 0
        assert response.object == "file"
        assert response.processed == True
        assert response.purpose == "fine-tune"
