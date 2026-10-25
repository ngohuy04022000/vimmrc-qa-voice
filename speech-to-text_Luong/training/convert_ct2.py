"""Convert a merged Transformers Whisper model to CTranslate2 int8."""

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "vimmrc-training/models/whisper-small-vi-ct2",
    )
    parser.add_argument("--quantization", default="int8")
    args = parser.parse_args()

    command = [
        sys.executable,
        "-m",
        "ctranslate2.converters.transformers",
        "--model",
        str(args.model),
        "--output_dir",
        str(args.output_dir),
        "--copy_files",
        "tokenizer.json",
        "preprocessor_config.json",
        "--quantization",
        args.quantization,
        "--force",
    ]
    subprocess.run(command, check=True)
    print(f"CTranslate2 model saved to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()