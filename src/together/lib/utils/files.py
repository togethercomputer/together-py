from __future__ import annotations

import os
import csv
import json
from typing import IO, Any, Dict, Callable, Iterator
from pathlib import Path
from traceback import format_exc
from dataclasses import dataclass

from together.types import FilePurpose
from together.lib.constants import (
    MIN_SAMPLES,
    NUM_BYTES_IN_GB,
    MAX_FILE_SIZE_GB,
    PARQUET_EXPECTED_COLUMNS,
)

CHECK_PROGRESS_STEP_BYTES = 1024 * 1024


class InvalidFileFormatError(ValueError):
    """Exception raised for invalid file formats during file checks."""

    def __init__(
        self,
        message: str = "",
        line_number: int | None = None,
        error_source: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.line_number = line_number
        self.error_source = error_source


@dataclass(frozen=True)
class FileCheckProgress:
    """Byte-level validation progress reported while scanning a file."""

    processed_bytes: int
    total_bytes: int
    phase: str


CheckProgressCallback = Callable[[FileCheckProgress], None]


def _notify_check_progress(
    progress_callback: CheckProgressCallback | None,
    processed_bytes: int,
    total_bytes: int,
    phase: str,
) -> None:
    if progress_callback is not None:
        progress_callback(FileCheckProgress(processed_bytes=processed_bytes, total_bytes=total_bytes, phase=phase))


def _encoded_line_size(file_handle: IO[str], line: str) -> int:
    """Byte length of a text line without calling ``tell()``.

    ``TextIOWrapper.tell()`` raises ``OSError: telling position disabled by next() call``
    while the file is being iterated, and text-mode ``tell()`` is an opaque cookie anyway.

    Default text mode (``newline=None``) translates ``\\r\\n`` → ``\\n``, so a naive
    re-encode undercounts CRLF files by one byte per line. Restore the stripped CR
    when the stream has observed CRLF and this line was translated to a bare ``\\n``.
    """

    encoding = getattr(file_handle, "encoding", None) or "utf-8"
    errors = getattr(file_handle, "errors", None) or "strict"
    try:
        size = len(line.encode(encoding, errors))
    except (LookupError, UnicodeError):
        size = len(line.encode("utf-8", "replace"))

    if line.endswith("\n") and not line.endswith("\r\n"):
        observed = getattr(file_handle, "newlines", None)
        if observed == "\r\n" or observed == ("\r\n",):
            size += 1
        elif isinstance(observed, tuple) and "\r\n" in observed and "\n" not in observed:
            size += 1
    return size


def _iter_lines_with_progress(
    file_handle: IO[str],
    *,
    total_bytes: int,
    progress_callback: CheckProgressCallback,
    phase: str,
) -> Iterator[str]:
    """Yield lines while reporting processed bytes from encoded line lengths."""

    last_reported = 0
    pos = 0
    _notify_check_progress(progress_callback, 0, total_bytes, phase)
    while True:
        line = file_handle.readline()
        if not line:
            break
        pos += _encoded_line_size(file_handle, line)
        yield line
        if pos - last_reported >= CHECK_PROGRESS_STEP_BYTES:
            _notify_check_progress(progress_callback, min(pos, total_bytes), total_bytes, phase)
            last_reported = pos
    _notify_check_progress(progress_callback, total_bytes, total_bytes, phase)


def _enumerate_lines(
    file_handle: IO[str],
    *,
    total_bytes: int,
    progress_callback: CheckProgressCallback | None,
    phase: str,
) -> Iterator[tuple[int, str]]:
    """Yield ``(index, line)`` and optionally report scan progress.

    When ``progress_callback`` is None this is just ``enumerate``.
    """

    if progress_callback is None:
        yield from enumerate(file_handle)
        return

    yield from enumerate(
        _iter_lines_with_progress(
            file_handle,
            total_bytes=total_bytes,
            progress_callback=progress_callback,
            phase=phase,
        )
    )


def check_file(
    file: Path | str,
    purpose: FilePurpose | str = "fine-tune",
    *,
    progress_callback: CheckProgressCallback | None = None,
) -> Dict[str, Any]:
    if not isinstance(file, Path):
        file = Path(file)

    report_dict: Dict[str, Any] = {
        "is_check_passed": True,
        "message": "Checks passed",
        "found": None,
        "file_size": None,
        "utf8": None,
        "line_type": None,
        "text_field": None,
        "key_value": None,
        "has_min_samples": None,
        "num_samples": None,
        "load_json": None,
        "load_csv": None,
    }

    if not file.is_file():
        report_dict["found"] = False
        report_dict["is_check_passed"] = False
        report_dict["message"] = f"File not found or path is not a regular file: {file}"
        return report_dict
    else:
        report_dict["found"] = True

    file_size = os.stat(file.as_posix()).st_size

    if file_size > MAX_FILE_SIZE_GB * NUM_BYTES_IN_GB:
        report_dict["message"] = (
            f"Maximum supported file size is {MAX_FILE_SIZE_GB} GB. Found file with size of {round(file_size / NUM_BYTES_IN_GB, 3)} GB."
        )
        report_dict["is_check_passed"] = False
    elif file_size == 0:
        report_dict["message"] = "File is empty"
        report_dict["file_size"] = 0
        report_dict["is_check_passed"] = False
        return report_dict
    else:
        report_dict["file_size"] = file_size

    data_report_dict = {}
    if file.suffix == ".jsonl":
        report_dict["filetype"] = "jsonl"
        data_report_dict = _check_jsonl(file, purpose, progress_callback=progress_callback, total_bytes=file_size)
    elif file.suffix == ".parquet":
        report_dict["filetype"] = "parquet"
        data_report_dict = _check_parquet(file, purpose, progress_callback=progress_callback, total_bytes=file_size)
    elif file.suffix == ".csv":
        report_dict["filetype"] = "csv"
        data_report_dict = _check_csv(file, purpose, progress_callback=progress_callback, total_bytes=file_size)
    else:
        unknown_ext_msg = (
            f"Unknown extension of file {file}. Only files with extensions .jsonl, .parquet, and .csv are supported."
        )
        report_dict["filetype"] = unknown_ext_msg
        report_dict["message"] = unknown_ext_msg
        report_dict["is_check_passed"] = False

    report_dict.update(data_report_dict)

    return report_dict


def _check_utf8(
    file: Path,
    *,
    progress_callback: CheckProgressCallback | None = None,
    total_bytes: int = 0,
) -> Dict[str, Any]:
    """Check if the file is UTF-8 encoded.

    Args:
        file (Path): Path to the file to check.
    Returns:
        Dict[str, Any]: A dictionary with the results of the check.
    """
    report_dict: Dict[str, Any] = {}
    try:
        # Dry-run UTF-8 decode by iterating through the file to avoid loading it entirely into memory
        with file.open(encoding="utf-8", newline="") as f:
            for _ in _enumerate_lines(f, total_bytes=total_bytes, progress_callback=progress_callback, phase="utf8"):
                pass
        report_dict["utf8"] = True
    except UnicodeDecodeError as e:
        report_dict["utf8"] = False
        report_dict["message"] = f"File is not UTF-8 encoded. Error raised: {e}."
        report_dict["is_check_passed"] = False
    return report_dict


def _check_samples_count(file: Path, report_dict: Dict[str, Any], idx: int) -> Dict[str, Any]:
    if idx + 1 < MIN_SAMPLES:
        report_dict["has_min_samples"] = False
        report_dict["message"] = (
            f"Processing {file} resulted in only {idx + 1} samples. Our minimum is {MIN_SAMPLES} samples. "
        )
        report_dict["is_check_passed"] = False
    else:
        report_dict["num_samples"] = idx + 1
        report_dict["has_min_samples"] = True

    return report_dict


def _check_csv(
    file: Path,
    purpose: FilePurpose | str,
    *,
    progress_callback: CheckProgressCallback | None = None,
    total_bytes: int = 0,
) -> Dict[str, Any]:
    """Check if the file is a valid CSV file.

    Args:
        file (Path): Path to the file to check.
        purpose (FilePurpose | str): Purpose of the file, used to determine if the file should be checked for specific columns.

    Returns:
        Dict[str, Any]: A dictionary with the results of the check.
    """
    report_dict: Dict[str, Any] = {}
    if purpose != "eval":
        report_dict["is_check_passed"] = False
        report_dict["message"] = (
            f"CSV files are not supported for {purpose}. Only JSONL and Parquet files are supported."
        )
        return report_dict

    report_dict.update(_check_utf8(file, progress_callback=progress_callback, total_bytes=total_bytes))

    if not report_dict["utf8"]:
        return report_dict

    with file.open(encoding="utf-8", newline="") as f:
        source: IO[str] | Iterator[str]
        if progress_callback is None:
            source = f
        else:
            source = _iter_lines_with_progress(
                f, total_bytes=total_bytes, progress_callback=progress_callback, phase="csv"
            )
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            report_dict["message"] = "CSV file is empty or has no header."
            report_dict["is_check_passed"] = False
            return report_dict
        idx = -1

        try:
            for idx, item in enumerate(reader):
                if None in item.keys() or None in item.values():
                    raise InvalidFileFormatError(
                        message=f"CSV file is malformed or the number of columns found on line {idx + 1} is inconsistent with the header",
                        line_number=idx + 1,
                        error_source="format",
                    )

            report_dict.update(_check_samples_count(file, report_dict, idx))
            report_dict["load_csv"] = True

        except InvalidFileFormatError as e:
            report_dict["load_csv"] = False
            report_dict["is_check_passed"] = False
            report_dict["message"] = e.message
            if e.line_number is not None:
                report_dict["line_number"] = e.line_number
            if e.error_source is not None:
                report_dict[e.error_source] = False
        except ValueError:
            report_dict["load_csv"] = False
            if idx < 0:
                report_dict["message"] = "Unable to decode file. File may be empty or in an unsupported format. "
            else:
                report_dict["message"] = f"Error parsing the CSV file. Unexpected format on line {idx + 1}."
            report_dict["is_check_passed"] = False

    return report_dict


def _check_jsonl(
    file: Path,
    purpose: FilePurpose | str,
    *,
    progress_callback: CheckProgressCallback | None = None,
    total_bytes: int = 0,
) -> Dict[str, Any]:
    # JSONL rules are the same for eval and fine-tune: skip blank lines, require a
    # JSON object per non-empty line. Semantic checks run on the server after upload.
    _ = purpose
    report_dict: Dict[str, Any] = {}
    report_dict.update(_check_utf8(file, progress_callback=progress_callback, total_bytes=total_bytes))
    if not report_dict["utf8"]:
        return report_dict

    with file.open(encoding="utf-8", newline="") as f:
        line_index = -1
        sample_count = 0
        try:
            for line_index, raw_line in _enumerate_lines(
                f, total_bytes=total_bytes, progress_callback=progress_callback, phase="jsonl"
            ):
                line = raw_line.strip()
                if not line:
                    continue
                json_line = json.loads(line)

                if not isinstance(json_line, dict):
                    raise InvalidFileFormatError(
                        message=(
                            f"Error parsing file. Invalid format on line {line_index + 1} of the input file. "
                            "Each line must be a JSON object. Dataset requirements are described at "
                            "https://docs.together.ai/docs/fine-tuning-data-preparation. "
                            "Full validation runs on the server after upload."
                        ),
                        line_number=line_index + 1,
                        error_source="line_type",
                    )
                sample_count += 1

            report_dict.update(_check_samples_count(file, report_dict, sample_count - 1 if sample_count else -1))
            report_dict["load_json"] = True

        except InvalidFileFormatError as e:
            report_dict["load_json"] = False
            report_dict["is_check_passed"] = False
            report_dict["message"] = e.message
            if e.line_number is not None:
                report_dict["line_number"] = e.line_number
            if e.error_source is not None:
                report_dict[e.error_source] = False
        except ValueError:
            report_dict["load_json"] = False
            if line_index < 0:
                report_dict["message"] = "Unable to decode file. File may be empty or in an unsupported format. "
            else:
                report_dict["message"] = f"Error parsing json payload. Unexpected format on line {line_index + 1}."
            report_dict["is_check_passed"] = False

    if "text_field" not in report_dict:
        report_dict["text_field"] = True
    if "line_type" not in report_dict:
        report_dict["line_type"] = True
    if "key_value" not in report_dict:
        report_dict["key_value"] = True
    return report_dict


def _check_parquet(
    file: Path,
    purpose: FilePurpose | str,
    *,
    progress_callback: CheckProgressCallback | None = None,
    total_bytes: int = 0,
) -> Dict[str, Any]:
    try:
        # Pyarrow is optional as it's large (~80MB) and isn't compatible with older systems.
        from pyarrow import ArrowInvalid, parquet
    except ImportError as e:
        raise ImportError(
            "pyarrow is not installed and is required to use parquet files. Please install it via `pip install together[pyarrow]`"
        ) from e

    report_dict: Dict[str, Any] = {}
    if purpose == "eval":
        report_dict["is_check_passed"] = False
        report_dict["message"] = (
            f"Parquet files are not supported for {purpose}. Only JSONL and CSV files are supported."
        )
        return report_dict

    try:
        _notify_check_progress(progress_callback, 0, total_bytes, "parquet")
        table = parquet.read_table(str(file), memory_map=True)  # type: ignore[reportUnknownMemberType]
        _notify_check_progress(progress_callback, total_bytes, total_bytes, "parquet")
    except ArrowInvalid:
        report_dict["load_parquet"] = (
            f"An exception has occurred when loading the Parquet file {file}. Please check the file for corruption. "
            f"Exception trace:\n{format_exc()}"
        )
        report_dict["is_check_passed"] = False
        return report_dict

    column_names = table.schema.names
    if "input_ids" not in column_names:
        report_dict["load_parquet"] = f"Parquet file {file} does not contain the `input_ids` column."
        report_dict["is_check_passed"] = False
        return report_dict

    # Don't check for eval
    for column_name in column_names:
        if column_name not in PARQUET_EXPECTED_COLUMNS:
            report_dict["load_parquet"] = (
                f"Parquet file {file} contains an unexpected column {column_name}. "
                f"Only columns {PARQUET_EXPECTED_COLUMNS} are supported."
            )
            report_dict["is_check_passed"] = False
            return report_dict

    num_samples = table.num_rows
    if num_samples < MIN_SAMPLES:
        report_dict["has_min_samples"] = False
        report_dict["message"] = (
            f"Processing {file} resulted in only {num_samples} samples. Our minimum is {MIN_SAMPLES} samples. "
        )
        report_dict["is_check_passed"] = False
        return report_dict
    else:
        report_dict["num_samples"] = num_samples

    report_dict["is_check_passed"] = True

    return report_dict
