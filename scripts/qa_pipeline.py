"""Standalone integration of Huy's retrieval and MRC modules."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
for folder in ("retrieval-model_Huy", "mrc-model_Huy"):
    sys.path.insert(0, str(ROOT / folder))

from retrieval_client import Retriever
from mrc_client import LexicalBaselineClient, MRCClient


class QAPipeline:
    """Adapters need only search(question, top_k) and answer_question(question, passage)."""

    def __init__(self, retriever, reader):
        self.retriever = retriever
        self.reader = reader

    def predict(self, question: str, options: list[str] | None = None) -> dict:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be non-empty text")
        if options is not None and (not isinstance(options, list) or len(options) != 4
                                    or any(not isinstance(item, str) for item in options)
                                    or not any(item.strip() for item in options)):
            raise ValueError("options must contain four strings and at least one nonempty option")
        hits = self.retriever.search(question, top_k=1)
        if not hits or hits[0]["score"] <= 0:
            return {"question": question, "answer": "Không tìm thấy đoạn văn phù hợp.",
                    "passage_id": None, "passage": "", "retrieval_score": 0.0}
        hit = hits[0]
        choice = self.reader.predict(question, hit["passage"], options) if options is not None else None
        return {"question": question,
                "answer": choice["answer"] if choice is not None else self.reader.answer_question(question, hit["passage"]),
                "passage_id": hit["id"], "passage": hit["passage"],
                "retrieval_score": hit["score"],
                **({"choice_label": choice["label"], "choice_scores": choice["scores"]}
                   if choice is not None else {})}

    def answer_question(self, question: str, options: list[str] | None = None) -> str:
        """Plain text contract for STT/web input and TTS output."""
        return self.predict(question, options)["answer"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", default="Thủ đô của Việt Nam là gì?")
    parser.add_argument("--index", type=Path, help="Index saved by Retriever.save")
    parser.add_argument("--options", nargs=4, metavar=("A", "B", "C", "D"), help="Four choices for --choice-model")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Synthetic corpus + lexical baseline; no trained model")
    mode.add_argument("--model", type=Path, help="Fine-tuned checkpoint directory")
    mode.add_argument("--choice-model", type=Path, help="Trained CPU choice-ranker directory")
    args = parser.parse_args()
    if (args.model or args.choice_model) and not args.index:
        parser.error("--model and --choice-model require --index")
    if bool(args.options) != bool(args.choice_model):
        parser.error("--choice-model and --options must be used together")
    retriever = Retriever.load(args.index) if args.index else Retriever([
        {"id": "demo:capital", "passage": "Hà Nội là thủ đô của Việt Nam. Thành phố nằm ở miền Bắc."},
        {"id": "demo:river", "passage": "Sông Cửu Long chảy qua vùng đồng bằng Nam Bộ."},
    ])
    if args.choice_model:
        from choice_ranker import ChoiceRanker
        reader = ChoiceRanker.load(args.choice_model)
    else:
        reader = LexicalBaselineClient() if args.demo else MRCClient(str(args.model))
    result = QAPipeline(retriever, reader).predict(args.question, args.options)
    result["mode"] = "trained_choice_ranker" if args.choice_model else (
        "lexical_baseline_demo" if args.demo else "finetuned_mrc")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
