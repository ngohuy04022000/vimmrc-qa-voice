"""Gom tín hiệu cho tinh chỉnh tham số: top-3 đoạn đã rerank + câu trả lời và điểm tin cậy của bộ đọc span trên từng đoạn.

Mỗi câu hỏi (220 answerable của eval_llm_assist + 30 unanswerable) lưu: câu hỏi, đáp án chuẩn, 3 đoạn với điểm reranker,
và với mỗi đoạn: span + điểm của bộ đọc, cùng kết quả khi cho phép "không có đáp án" (handle_impossible_answer).
Phân tích offline (scripts/tune_reader_signals.py) nên thử mọi công thức/ngưỡng mà không phải chạy lại mô hình.

Dùng (CPU): KB_RERANKER=BAAI/bge-reranker-v2-m3 MRC_CHECKPOINT=mrc-model_Huy/checkpoints/vi-mrc-large \
            python scripts/collect_reader_signals.py [--out reports/reader_signals.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
for folder in ("", "scripts", "retrieval-model_Huy", "mrc-model_Huy", "dialogue-manager_Huy"):
    sys.path.insert(0, str(ROOT / folder))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "reader_signals.json")
    ap.add_argument("--top", type=int, default=3)
    args = ap.parse_args()

    from api_server import get_qa_services
    from eval_llm_assist import UNANSWERABLE, answerable_set

    retriever, reader = get_qa_services()
    if not hasattr(reader, "qa"):
        sys.exit("MRC_CHECKPOINT phải là bộ đọc span (SpanReaderClient), ví dụ vi-mrc-large")
    items = [dict(it, kind="answerable") for it in answerable_set(100)]
    items += [{"src": "unans", "q": q, "refs": [], "kind": "unanswerable"} for q in UNANSWERABLE]
    done = {r["q"]: r for r in json.loads(args.out.read_text(encoding="utf-8"))} if args.out.exists() else {}
    rows, t0 = list(done.values()), time.time()
    for i, it in enumerate(items):
        if it["q"] in done:
            continue
        hits = retriever.search(it["q"], args.top)
        passages = []
        for h in hits:
            kw = dict(question=it["q"], context=h["passage"], max_seq_len=512, doc_stride=128, max_answer_len=48)
            a = reader.qa(**kw)
            n = reader.qa(**kw, handle_impossible_answer=True)
            passages.append({"id": h["id"], "score": h["score"], "passage": h["passage"],
                             "answer": (a.get("answer") or "").strip(" \t\n,;:-–—"), "reader_score": float(a["score"]),
                             "null_wins": not (n.get("answer") or "").strip(), "null_run_score": float(n["score"])})
        rows.append(dict(it, passages=passages))
        if len(rows) % 10 == 0:
            args.out.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
            print(len(rows), f"{time.time() - t0:.0f}s", flush=True)
    args.out.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    print("saved", len(rows), args.out)


if __name__ == "__main__":
    main()
