"""Expand an existing VietSpeech experiment while preserving validation/test."""

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

from datasets import Audio, load_dataset
from huggingface_hub.errors import LocalTokenNotFoundError

from prepare_vietspeech import (
    choose_group_field,
    decode_audio,
    normalize_text,
    split_for,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="NhutP/VietSpeech")
    parser.add_argument("--dataset-split", default="train")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.home() / "vimmrc-training/data/vietspeech_20h",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "vimmrc-training/data/vietspeech_50h",
    )
    parser.add_argument("--total-hours", type=float, default=50.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--shuffle-buffer", type=int, default=10_000)
    parser.add_argument("--min-seconds", type=float, default=0.5)
    parser.add_argument("--max-seconds", type=float, default=30.0)
    parser.add_argument("--group-field", default=None)
    return parser.parse_args()


def read_manifest(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def link_audio(source: Path, destination: Path) -> None:
    if destination.exists():
        return
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def main() -> None:
    args = parse_args()
    base_dir = args.base_dir.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir == base_dir:
        raise ValueError("--output-dir must differ from --base-dir")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output_dir}")

    base_records = {
        split: read_manifest(base_dir / f"{split}.jsonl")
        for split in ("train", "validation", "test")
    }
    fixed_seconds = sum(
        float(record["duration"])
        for split in ("validation", "test")
        for record in base_records[split]
    )
    target_train_seconds = args.total_hours * 3600 - fixed_seconds
    initial_train_seconds = sum(float(record["duration"]) for record in base_records["train"])
    if target_train_seconds <= initial_train_seconds:
        raise ValueError("Target total hours must exceed the existing experiment duration")

    audio_dir = output_dir / "audio"
    audio_dir.mkdir(parents=True)
    manifests = {
        split: (output_dir / f"{split}.jsonl").open("w", encoding="utf-8")
        for split in ("train", "validation", "test")
    }
    existing_ids: set[str] = set()
    fixed_groups = {
        str(record["group"])
        for split in ("validation", "test")
        for record in base_records[split]
    }
    totals = {
        split: {
            "seconds": sum(float(record["duration"]) for record in records),
            "samples": len(records),
        }
        for split, records in base_records.items()
    }

    for split, records in base_records.items():
        for record in records:
            source = Path(record["audio_path"])
            destination = audio_dir / source.name
            link_audio(source, destination)
            existing_ids.add(source.stem)
            copied_record = {**record, "audio_path": str(destination)}
            manifests[split].write(json.dumps(copied_record, ensure_ascii=False) + "\n")

    try:
        dataset = load_dataset(
            args.dataset,
            split=args.dataset_split,
            streaming=True,
            token=True,
        ).cast_column("audio", Audio(decode=False))
        dataset = dataset.shuffle(seed=args.seed, buffer_size=args.shuffle_buffer)
    except LocalTokenNotFoundError as exc:
        raise SystemExit("Run `hf auth login` in WSL before streaming VietSpeech.") from exc

    columns = list(dataset.column_names or [])
    group_field = choose_group_field(columns, args.group_field)
    rejected = 0
    added = 0
    stream = iter(dataset)
    try:
        for index, example in enumerate(stream):
            if totals["train"]["seconds"] >= target_train_seconds:
                break

            text = normalize_text(str(example.get("transcription") or ""))
            if not text:
                rejected += 1
                continue
            group_value = example.get(group_field) if group_field else text.lower()
            group_key = normalize_text(str(group_value or text)).lower()
            if group_key in fixed_groups or split_for(group_key) != "train":
                continue

            sample_id = hashlib.sha1(f"{index}:{text}".encode("utf-8")).hexdigest()[:20]
            if sample_id in existing_ids:
                continue
            try:
                array, sample_rate = decode_audio(example["audio"])
            except Exception:
                rejected += 1
                continue
            if array.ndim > 1:
                array = array.mean(axis=0)
            duration = len(array) / sample_rate
            if not args.min_seconds <= duration <= args.max_seconds:
                rejected += 1
                continue

            audio_path = audio_dir / f"{sample_id}.flac"
            import soundfile as sf

            sf.write(audio_path, array, sample_rate, format="FLAC")
            record = {
                "audio_path": str(audio_path),
                "transcription": text,
                "duration": duration,
                "group": group_key,
            }
            manifests["train"].write(json.dumps(record, ensure_ascii=False) + "\n")
            existing_ids.add(sample_id)
            totals["train"]["seconds"] += duration
            totals["train"]["samples"] += 1
            added += 1
    finally:
        close_stream = getattr(stream, "close", None)
        if close_stream:
            close_stream()
        for manifest in manifests.values():
            manifest.close()

    stats = {
        "dataset": args.dataset,
        "requested_total_hours": args.total_hours,
        "base_dir": str(base_dir),
        "fixed_validation_test": True,
        "group_field": group_field,
        "split_strategy": group_field or "normalized_transcription_hash",
        "new_train_samples": added,
        "rejected_samples": rejected,
        "splits": {
            split: {
                "samples": values["samples"],
                "hours": round(values["seconds"] / 3600, 4),
            }
            for split, values in totals.items()
        },
    }
    (output_dir / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)