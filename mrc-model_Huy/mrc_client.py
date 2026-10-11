"""Inference clients. MRCClient requires a fine-tuned local checkpoint."""

from __future__ import annotations

import re
import json
from pathlib import Path

from mrc_data import build_input, normalize_text
from context_selection import encode_input


class MRCClient:
    """Generate a free-text answer from a trained ViT5 checkpoint."""

    def __init__(self, model_path: str | Path, *, device: str | None = None,
                 max_input_tokens: int | None = None, max_new_tokens: int | None = None,
                 context_strategy: str | None = None):
        path = Path(model_path)
        if not path.is_dir() or not (path / "config.json").exists() or not any(
            (path / name).exists() for name in (
                "model.safetensors", "pytorch_model.bin", "model.safetensors.index.json",
                "pytorch_model.bin.index.json",
            )
        ):
            raise FileNotFoundError(
                f"No fine-tuned checkpoint at {path}. Run train.py first; "
                "the offline demo uses LexicalBaselineClient."
            )
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(str(path), local_files_only=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(str(path), local_files_only=True)
        self.model.to(self.device).eval()
        settings = json.loads((path / "mrc_config.json").read_text(encoding="utf-8")) if (
            path / "mrc_config.json").exists() else {}
        self.max_input_tokens = max_input_tokens or settings.get("max_input_tokens", 512)
        self.max_new_tokens = max_new_tokens or settings.get("max_target_tokens", 64)
        self.context_strategy = context_strategy or settings.get("context_strategy", "head")

    def answer_question(self, question: str, passage: str) -> str:
        import torch

        encoded = encode_input(question, passage, self.tokenizer, self.max_input_tokens,
                               self.context_strategy, return_tensors="pt").to(self.device)
        with torch.inference_mode():
            tokens = self.model.generate(**encoded, max_new_tokens=self.max_new_tokens,
                                         num_beams=4)
        return self.tokenizer.decode(tokens[0], skip_special_tokens=True).strip()


class LexicalBaselineClient:
    """Offline smoke demo only: return the passage sentence matching question words."""

    _stop = {"là", "gì", "ai", "ở", "đâu", "nào", "có", "của", "và", "được", "theo", "trong"}

    def answer_question(self, question: str, passage: str) -> str:
        build_input(question, passage)
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", passage) if part.strip()]
        words = set(normalize_text(question).split()) - self._stop
        return max(sentences, key=lambda sentence: len(words & set(normalize_text(sentence).split())))
