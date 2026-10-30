"""Standalone integration of Huy's retrieval and MRC modules."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
for folder in ("retrieval-model_Huy", "mrc-model_Huy", "text-to-speech_Duy", "text-to-speech_Duy/src"):
    path_str = str(ROOT / folder)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from retrieval_client import Retriever
from mrc_client import LexicalBaselineClient, MRCClient


class QAPipeline:
    """Adapters need only search(question, top_k) and answer_question(question, passage)."""

    def __init__(self, retriever, reader):
        self.retriever = retriever
        self.reader = reader

    def predict(self, question: str) -> dict:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be non-empty text")
        hits = self.retriever.search(question, top_k=1)
        if not hits or hits[0]["score"] <= 0:
            return {"question": question, "answer": "Không tìm thấy đoạn văn phù hợp.",
                    "passage_id": None, "passage": "", "retrieval_score": 0.0}
        hit = hits[0]
        return {"question": question,
                "answer": self.reader.answer_question(question, hit["passage"]),
                "passage_id": hit["id"], "passage": hit["passage"],
                "retrieval_score": hit["score"]}

    def answer_question(self, question: str) -> str:
        """Plain text contract for STT/web input and TTS output."""
        return self.predict(question)["answer"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", default="Thủ đô của Việt Nam là gì?")
    parser.add_argument("--index", type=Path, help="Index saved by Retriever.save")
    parser.add_argument("--tts", action="store_true", help="Synthesize the answer into speech using TTS")
    parser.add_argument("--tts-engine", default="edge", choices=["matcha", "vits", "edge", "gtts"], help="TTS engine")
    parser.add_argument("--tts-voice", default="vi-VN-HoaiMyNeural", help="Voice name or alias ('nu', 'nam')")
    parser.add_argument("--output-audio", type=Path, default=None, help="Output path for synthesized audio")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Synthetic corpus + lexical baseline; no trained model")
    mode.add_argument("--model", type=Path, help="Fine-tuned checkpoint directory")
    args = parser.parse_args()
    if args.model and not args.index:
        parser.error("--model requires --index")
    retriever = Retriever.load(args.index) if args.index else Retriever([
        {"id": "demo:capital", "passage": "Hà Nội là thủ đô của Việt Nam. Thành phố nằm ở miền Bắc."},
        {"id": "demo:river", "passage": "Sông Cửu Long chảy qua vùng đồng bằng Nam Bộ."},
    ])
    reader = LexicalBaselineClient() if args.demo else MRCClient(str(args.model))
    result = QAPipeline(retriever, reader).predict(args.question)
    result["mode"] = "lexical_baseline_demo" if args.demo else "finetuned_mrc"

    if args.tts:
        from synthesize import synthesize as tts_synthesize
        audio_path = tts_synthesize(
            text=result["answer"],
            output_path=str(args.output_audio) if args.output_audio else None,
            voice=args.tts_voice,
            engine=args.tts_engine,
        )
        result["audio_path"] = audio_path

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
