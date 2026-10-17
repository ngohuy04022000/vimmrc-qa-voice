"""Evaluate one or more Whisper checkpoints on a shared JSONL manifest."""

import argparse
import json
from pathlib import Path

import librosa
import torch
from jiwer import cer, wer
from transformers import pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path.home() / "vimmrc-training/data/vietspeech_20h/test.jsonl",
    )
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--output", type=Path, default=Path("reports/stt_model_comparison.json"))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=8)
    return parser.parse_args()


def read_manifest(path: Path, limit: int | None) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        rows = [json.loads(line) for line in file if line.strip()]
    return rows[:limit]


def main() -> None:
    args = parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for evaluation")
    rows = read_manifest(args.manifest, args.limit)
    references = [row["transcription"] for row in rows]
    results = []

    for model_id in args.models:
        recognizer = pipeline(
            "automatic-speech-recognition",
            model=model_id,
            device=0,
            dtype=torch.bfloat16,
        )
        predictions = []
        for start in range(0, len(rows), args.batch_size):
            batch = []
            for row in rows[start : start + args.batch_size]:
                audio, _ = librosa.load(row["audio_path"], sr=16_000, mono=True)
                batch.append({"array": audio, "sampling_rate": 16_000})
            outputs = recognizer(
                batch,
                batch_size=args.batch_size,
                generate_kwargs={"language": "vi", "task": "transcribe"},
            )
            predictions.extend(output["text"].strip() for output in outputs)

        result = {
            "model": model_id,
            "samples": len(rows),
            "wer": 100 * wer(references, predictions),
            "cer": 100 * cer(references, predictions),
        }
        results.append(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        del recognizer
        torch.cuda.empty_cache()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()