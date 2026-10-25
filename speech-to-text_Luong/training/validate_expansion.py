"""Validate that an expanded dataset preserves its fixed evaluation splits."""

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", type=Path, required=True)
    parser.add_argument("--expanded-dir", type=Path, required=True)
    return parser.parse_args()


def read_manifest(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def comparable(record: dict) -> dict:
    return {key: value for key, value in record.items() if key != "audio_path"}


def main() -> None:
    args = parse_args()
    records = {
        split: read_manifest(args.expanded_dir / f"{split}.jsonl")
        for split in ("train", "validation", "test")
    }
    for split in ("validation", "test"):
        base = [comparable(record) for record in read_manifest(args.base_dir / f"{split}.jsonl")]
        expanded = [comparable(record) for record in records[split]]
        if expanded != base:
            raise AssertionError(f"Expanded {split} manifest differs from the fixed base manifest")

    groups = {
        split: {str(record["group"]) for record in split_records}
        for split, split_records in records.items()
    }
    overlaps = {
        "train_validation": len(groups["train"] & groups["validation"]),
        "train_test": len(groups["train"] & groups["test"]),
        "validation_test": len(groups["validation"] & groups["test"]),
    }
    if any(overlaps.values()):
        raise AssertionError(f"Split group overlap detected: {overlaps}")

    result = {
        "samples": {split: len(split_records) for split, split_records in records.items()},
        "group_overlaps": overlaps,
        "fixed_evaluation_manifests": True,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()