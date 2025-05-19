import enum

# Minimum number of samples required for fine-tuning file
MIN_SAMPLES = 1

# the number of bytes in a gigabyte, used to convert bytes to GB for readable comparison
NUM_BYTES_IN_GB = 2**30

# maximum number of GB sized files we support finetuning for
MAX_FILE_SIZE_GB = 4.9

# expected columns for Parquet files
PARQUET_EXPECTED_COLUMNS = ["input_ids", "attention_mask", "labels"]


class DatasetFormat(enum.Enum):
    """Dataset format enum."""

    GENERAL = "general"
    CONVERSATION = "conversation"
    INSTRUCTION = "instruction"
    PREFERENCE_OPENAI = "preference_openai"


JSONL_REQUIRED_COLUMNS_MAP = {
    DatasetFormat.GENERAL: ["text"],
    DatasetFormat.CONVERSATION: ["messages"],
    DatasetFormat.INSTRUCTION: ["prompt", "completion"],
    DatasetFormat.PREFERENCE_OPENAI: [
        "input",
        "preferred_output",
        "non_preferred_output",
    ],
}
REQUIRED_COLUMNS_MESSAGE = ["role", "content"]
POSSIBLE_ROLES_CONVERSATION = ["system", "user", "assistant"]
