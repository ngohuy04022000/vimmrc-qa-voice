"""Stream a fixed-duration VietSpeech subset into local FLAC manifests."""

import argparse
import hashlib
import io
import json
import os
import re
import sys
from collections.abc import Mapping
from pathlib import Path

import numpy as np
import soundfile as sf
from datasets import Audio, load_dataset
from huggingface_hub.errors import LocalTokenNotFoundError

SPLIT_RANGES = (("train", 80), ("validation", 90), ("test", 100))
GROUP_FIELDS = ("speaker_id", "speaker", "source_id", "source", "url", "video_id")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="NhutP/VietSpeech")
    parser.add_argument("--dataset-split", default="train")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "vimmrc-training/data/vietspeech_20h",
    )
    parser.add_argument("--hours", type=float, default=20.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--shuffle-buffer", type=int, default=10_000)
    parser.add_argument("--min-seconds", type=float, default=0.5)
    parser.add_argument("--max-seconds", type=float, default=30.0)
    parser.add_argument("--group-field", default=None)
    return parser.parse_args()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def decode_audio(audio: object) -> tuple[np.ndarray, int]:
    if isinstance(audio, Mapping) and "array" in audio:
        return np.asarray(audio["array"], dtype=np.float32), int(audio["sampling_rate"])

    if isinstance(audio, Mapping):
        source = io.BytesIO(audio["bytes"]) if audio.get("bytes") else audio.get("path")
        if source is None:
            raise ValueError("Audio sample contains neither bytes nor path")
        array, sample_rate = sf.read(source, dtype="float32", always_2d=False)
        return np.asarray(array, dtype=np.float32), int(sample_rate)

    raise TypeError(f"Unsupported audio value: {type(audio)!r}")


def choose_group_field(columns: list[str], requested: str | None) -> str | None:
    if requested:
        if requested not in columns:
            raise ValueError(f"Group field '{requested}' is not in dataset columns: {columns}")
        return requested
    return next((field for field in GROUP_FIELDS if field in columns), None)


def split_for(group_key: str) -> str:
    bucket = int(hashlib.sha1(group_key.encode("utf-8")).hexdigest()[:8], 16) % 100
    for split, upper_bound in SPLIT_RANGES:
        if bucket < upper_bound:
            return split
    raise AssertionError("Unreachable split bucket")


def main() -> None:
    args = parse_args()
    if args.hours <= 0:
        raise ValueError("--hours must be positive")

    try:
        dataset = load_dataset(
            args.dataset,
            split=args.dataset_split,
            streaming=True,
            token=True,
        ).cast_column("audio", Audio(decode=False))
        dataset = dataset.shuffle(seed=args.seed, buffer_size=args.shuffle_buffer)
    except LocalTokenNotFoundError as exc:
        raise SystemExit(
            "VietSpeech requires Hugging Face access. Accept its conditions, "
            "then run `hf auth login` in WSL."
        ) from exc
    columns = list(dataset.column_names or [])
    group_field = choose_group_field(columns, args.group_field)
    split_strategy = group_field or "normalized_transcription_hash"

    output_dir = args.output_dir.resolve()
    audio_dir = output_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    manifest_paths = {split: output_dir / f"{split}.jsonl" for split, _ in SPLIT_RANGES}
    manifests = {split: path.open("w", encoding="utf-8") for split, path in manifest_paths.items()}
    target_seconds = {
        "train": args.hours * 3600 * 0.8,
        "validation": args.hours * 3600 * 0.1,
        "test": args.hours * 3600 * 0.1,
    }
    totals = {split: {"seconds": 0.0, "samples": 0} for split, _ in SPLIT_RANGES}
    rejected = 0
    stream = iter(dataset)

    try:
        for index, example in enumerate(stream):
            if all(totals[split]["seconds"] >= target for split, target in target_seconds.items()):
                break

            text = normalize_text(str(example.get("transcription") or ""))
            if not text:
                rejected += 1
                continue

            group_value = example.get(group_field) if group_field else text.lower()
            group_key = normalize_text(str(group_value or text)).lower()
            split = split_for(group_key)
            if totals[split]["seconds"] >= target_seconds[split]:
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

            sample_id = hashlib.sha1(f"{index}:{text}".encode("utf-8")).hexdigest()[:20]
            audio_path = audio_dir / f"{sample_id}.flac"
            sf.write(audio_path, array, sample_rate, format="FLAC")
            record = {
                "audio_path": str(audio_path),
                "transcription": text,
                "duration": duration,
                "group": group_key,
            }
            manifests[split].write(json.dumps(record, ensure_ascii=False) + "\n")
            totals[split]["seconds"] += duration
            totals[split]["samples"] += 1
    finally:
        close_stream = getattr(stream, "close", None)
        if close_stream:
            close_stream()
        for manifest in manifests.values():
            manifest.close()

    stats = {
        "dataset": args.dataset,
        "requested_hours": args.hours,
        "group_field": group_field,
        "split_strategy": split_strategy,
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