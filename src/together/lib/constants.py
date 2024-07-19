# Minimum number of samples required for fine-tuning file
MIN_SAMPLES = 100

# the number of bytes in a gigabyte, used to convert bytes to GB for readable comparison
NUM_BYTES_IN_GB = 2**30

# maximum number of GB sized files we support finetuning for
MAX_FILE_SIZE_GB = 4.9

# expected columns for Parquet files
PARQUET_EXPECTED_COLUMNS = ["input_ids", "attention_mask", "labels"]
