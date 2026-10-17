"""Merge a Whisper LoRA adapter into its base Transformers checkpoint."""

import argparse
from pathlib import Path

import torch
from peft import PeftModel
from transformers import WhisperForConditionalGeneration, WhisperProcessor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", default="openai/whisper-small")
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "vimmrc-training/models/whisper-small-vi-merged",
    )
    args = parser.parse_args()

    base_model = WhisperForConditionalGeneration.from_pretrained(
        args.base_model, dtype=torch.float32, low_cpu_mem_usage=True
    )
    model = PeftModel.from_pretrained(base_model, str(args.adapter)).merge_and_unload()
    processor = WhisperProcessor.from_pretrained(str(args.adapter))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(args.output_dir), safe_serialization=True)
    processor.save_pretrained(str(args.output_dir))
    print(f"Merged model saved to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()