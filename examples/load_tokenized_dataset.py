#!/usr/bin/env -S uv run python
"""Load a fine-tuning job's tokenized dataset sample (≤100 rows).

Requires: pip install together[datasets]
"""

from __future__ import annotations

import os
import sys

from together import Together


def main() -> None:
    fine_tune_id = os.environ.get("FINE_TUNE_ID") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not fine_tune_id:
        print("Usage: FINE_TUNE_ID=ft-... ./examples/load_tokenized_dataset.py", file=sys.stderr)
        print("   or: ./examples/load_tokenized_dataset.py ft-...", file=sys.stderr)
        raise SystemExit(2)

    client = Together()
    dataset = client.fine_tuning.download_tokenized_dataset(
        ft_id=fine_tune_id,
        return_dataset_object=True,
    )
    print(f"splits: {list(dataset.keys())}")
    print(f"train rows: {len(dataset['train'])}")
    if "validation" in dataset:
        print(f"validation rows: {len(dataset['validation'])}")
    print("first train example:", dataset["train"][0])


if __name__ == "__main__":
    main()
