import math
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from together.lib.constants import NUM_BYTES_IN_GB, MAX_FILE_SIZE_GB, TARGET_PART_SIZE_MB
from together.lib.types.error import FileTypeError
from together.lib.resources.files import MultipartUploadManager, _calculate_parts


def test_calculate_parts_medium_file():
    """Ensure 500MB files are split into two 250MB parts."""

    file_size = 500 * 1024 * 1024  # 500MB
    part_size, num_parts = _calculate_parts(file_size)

    expected_part_size = TARGET_PART_SIZE_MB * 1024 * 1024

    assert num_parts == 2
    assert part_size == expected_part_size


def test_calculate_parts_large_file():
    """Ensure 50GB files respect the 205-part cap with ~250MB chunks."""

    file_size = 50 * 1024 * 1024 * 1024  # 50GB
    part_size, num_parts = _calculate_parts(file_size)

    expected_parts = math.ceil(file_size / (TARGET_PART_SIZE_MB * 1024 * 1024))  # 50GB / 250MB ~= 205

    assert num_parts == expected_parts
    assert part_size >= TARGET_PART_SIZE_MB * 1024 * 1024 - (1 * 1024 * 1024)


@patch("together.lib.resources.files.os.stat")
def test_file_size_exceeds_limit_raises_error(mock_stat: MagicMock):
    """Uploading a file above 50.1GB should raise FileTypeError."""

    mock_stat.return_value.st_size = int((MAX_FILE_SIZE_GB + 1) * NUM_BYTES_IN_GB)
    manager = MultipartUploadManager(MagicMock())

    with pytest.raises(FileTypeError) as exc_info:
        manager.upload("/files", Path("too_large.jsonl"), "fine-tune")

    assert "exceeds maximum supported size" in str(exc_info.value)
