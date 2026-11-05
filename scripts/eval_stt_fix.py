"""Vòng lặp giọng nói: câu hỏi -> TTS (Matcha) -> STT (Whisper LoRA) -> [LLM sửa lỗi] -> hỏi đáp.

So sánh trên cùng bộ câu: văn bản gốc (trần), STT thô, STT đã qua LLM sửa. Đo CER của câu hỏi
và token F1 của câu trả lời, để biết bước sửa lỗi bằng Ollama có đáng bật hay không.

Dùng: python scripts/eval_stt_fix.py [--n 40] [--out reports/stt_fix_ab.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
for folder in ("", "scripts", "retrieval-model_Huy", "mrc-model_Huy", "dialogue-manager_Huy", "text-to-speech_Duy",
               "text-to-speech_Duy/src", "speech-to-text_Luong"):
    sys.path.insert(0, str(ROOT / folder))

from eval_hard_and_multiturn import compute_token_f1  # noqa: E402
from eval_llm_assist import answerable_set  # noqa: E402
from eval_out_of_dataset import compute_cer  # noqa: E402
from llm_assist import LLMAssist  # noqa: E402
from api_server import get_qa_services  # noqa: E402
from dialogue import DialogueManager  # noqa: E402
from synthesize import synthesize  # noqa: E402
import stt_server  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--out", default=str(ROOT / "reports" / "stt_fix_ab.json"))
    args = ap.parse_args()

    assist = LLMAssist()
    if not assist.available():
        sys.exit("Ollama không dùng được")
    retriever, reader = get_qa_services()
    manager = DialogueManager(retriever, reader)  # đo riêng bước sửa STT, không bật cổng/kiểm chứng
    items = [i for i in answerable_set(0) if i["src"] != "test"][: args.n]

    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for n, it in enumerate(items):
            wav = synthesize(it["q"], output_path=str(Path(tmp) / f"q{n}.wav"))
            raw = stt_server.transcribe(wav)
            fixed = assist.fix_transcript(raw)
            row = {"q": it["q"], "raw": raw, "fixed": fixed,
                   "cer_raw": round(compute_cer(it["q"], raw), 4), "cer_fixed": round(compute_cer(it["q"], fixed), 4)}
            for tag, text in (("clean", it["q"]), ("raw", raw), ("fixed", fixed)):
                row[f"f1_{tag}"] = round(max(compute_token_f1(manager.respond(text, None)["answer"], r) for r in it["refs"]), 4)
            rows.append(row)
            print(n, row["cer_raw"], row["cer_fixed"], "|", raw, "=>", fixed, flush=True)

    mean = lambda k: round(sum(r[k] for r in rows) / len(rows), 4)
    summary = {k: mean(k) for k in ("cer_raw", "cer_fixed", "f1_clean", "f1_raw", "f1_fixed")}
    summary["changed"] = sum(r["raw"] != r["fixed"] for r in rows)
    print(summary)
    Path(args.out).write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
