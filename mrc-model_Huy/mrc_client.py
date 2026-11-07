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
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(str(path), local_files_only=True)
        except Exception:
            from transformers import PreTrainedTokenizerFast
            self.tokenizer = PreTrainedTokenizerFast(
                tokenizer_file=str(path / "tokenizer.json"),
                eos_token="</s>",
                pad_token="<pad>",
                unk_token="<unk>",
            )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(str(path), local_files_only=True)
        self.model.to(self.device).eval()
        settings = json.loads((path / "mrc_config.json").read_text(encoding="utf-8")) if (
            path / "mrc_config.json").exists() else {}
        self.max_input_tokens = max_input_tokens or settings.get("max_input_tokens", 512)
        self.max_new_tokens = max_new_tokens or settings.get("max_target_tokens", 64)
        self.context_strategy = context_strategy or settings.get("context_strategy", "head")

    def answer_question(self, question: str, passage: str) -> str:
        return self.answer_candidates(question, passage, num_candidates=1)[0]

    def answer_candidates(self, question: str, passage: str, num_candidates: int = 5) -> list[str]:
        """Beam search'in top candidates, best-first, for re-ranking (e.g. by an LLM judge)
        instead of trusting the single best-beam answer. Same beam count as answer_question
        (4) when num_candidates<=4; widens beams to match num_candidates otherwise so every
        candidate still comes from a real, distinct beam rather than sampling noise."""
        import torch

        encoded = encode_input(question, passage, self.tokenizer, self.max_input_tokens,
                               self.context_strategy, return_tensors="pt").to(self.device)
        num_beams = max(4, num_candidates)
        with torch.inference_mode():
            tokens = self.model.generate(**encoded, max_new_tokens=self.max_new_tokens,
                                         num_beams=num_beams, num_return_sequences=num_candidates)
        return [self.tokenizer.decode(seq, skip_special_tokens=True).strip() for seq in tokens]


class SpanReaderClient:
    """Extractive reader (XLM-R/RoBERTa QA head, e.g. nguyenvulebinh/vi-mrc-large): returns a span of the passage.

    On the 220-question reader bench it beat the ViT5 checkpoints (composed F1 0.468 vs 0.446; 0.510 vs 0.368 on
    'why' questions) at ~0.6 s/question on CPU (reports/reader_bench.json).
    """

    def __init__(self, model_path: str | Path, *, max_answer_len: int = 48, **_ignored):
        from transformers import pipeline

        path = Path(model_path)
        if not (path / "config.json").exists():
            raise FileNotFoundError(f"No span-reader checkpoint at {path}")
        self.max_answer_len = max_answer_len
        self.qa = pipeline("question-answering", model=str(path), tokenizer=str(path), device=-1)

    def answer_question(self, question: str, passage: str) -> str:
        if not passage.strip():
            return ""
        out = self.qa(question=question, context=passage, max_seq_len=512, doc_stride=128,
                      max_answer_len=self.max_answer_len)
        return (out.get("answer") or "").strip() if out else ""


def load_reader(model_path: str | Path, **kwargs):
    """SpanReaderClient for *ForQuestionAnswering checkpoints, MRCClient (seq2seq ViT5) otherwise."""
    config = Path(model_path) / "config.json"
    archs = json.loads(config.read_text(encoding="utf-8")).get("architectures", []) if config.exists() else []
    if any("QuestionAnswering" in a for a in archs):
        return SpanReaderClient(model_path)
    return MRCClient(model_path, **kwargs)


class LexicalBaselineClient:
    """Offline smoke demo only: return the passage sentence matching question words."""

    _stop = {"là", "gì", "ai", "ở", "đâu", "nào", "có", "của", "và", "được", "theo", "trong"}

    def answer_question(self, question: str, passage: str) -> str:
        build_input(question, passage)
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", passage) if part.strip()]
        words = set(normalize_text(question).split()) - self._stop
        return max(sentences, key=lambda sentence: len(words & set(normalize_text(sentence).split())))
