"""Đo bộ đọc trên tập test có đoạn văn đúng (gold passage): EM / token F1, cùng cách đo với bảng ViT5 trong bài báo.

Dùng (CPU): python scripts/eval_reader_gold.py --checkpoint mrc-model_Huy/checkpoints/vi-mrc-large [--limit 0] [--out reports/reader_gold_vi-mrc-large.json]
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
sys.path.insert(0, str(ROOT / "mrc-model_Huy"))
from mrc_client import load_reader  # noqa: E402
from mrc_data import evaluate_predictions, load_examples  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--test", type=Path, default=ROOT / "data" / "combined" / "test_vimmrc.json")
    ap.add_argument("--limit", type=int, default=0, help="0 = toàn bộ")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    examples = load_examples(args.test)
    if args.limit:
        examples = examples[: args.limit]
    reader = load_reader(args.checkpoint)
    preds, t0 = [], time.time()
    for i, e in enumerate(examples):
        preds.append(reader.answer_question(e["question"], e["passage"]))
        if (i + 1) % 200 == 0:
            print(i + 1, f"{time.time() - t0:.0f}s", flush=True)
    metrics = evaluate_predictions(preds, examples)
    metrics.update(n=len(examples), checkpoint=str(args.checkpoint), seconds_per_q=round((time.time() - t0) / len(examples), 3))
    # Tách theo nguồn: bài đọc ViMMRC khớp nguyên văn với đoạn của kho (đáp án là văn bản phương án, không phải cụm trích);
    # phần còn lại là ViQuAD (kho giữ chúng ở dạng đã cắt nên không khớp nguyên văn; đáp án là cụm trích, có lợi cho bộ đọc span).
    kb_path = ROOT / "data" / "kb_index.json"
    if kb_path.exists():
        kb = json.loads(kb_path.read_text(encoding="utf-8"))
        kb = kb["passages"] if isinstance(kb, dict) else kb
        norm = lambda s: " ".join(s.split())  # noqa: E731
        vimmrc_texts = {norm(p["passage"]) for p in kb if not p["id"].startswith("viquad")}
        groups: dict[str, list[int]] = {}
        for i, e in enumerate(examples):
            groups.setdefault("vimmrc" if norm(e["passage"]) in vimmrc_texts else "viquad", []).append(i)
        metrics["by_source"] = {g: dict(n=len(ix), **evaluate_predictions([preds[i] for i in ix], [examples[i] for i in ix]))
                                for g, ix in sorted(groups.items())}
    print(json.dumps(metrics, ensure_ascii=False))
    if args.out:
        args.out.write_text(json.dumps({"metrics": metrics, "predictions": preds}, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
