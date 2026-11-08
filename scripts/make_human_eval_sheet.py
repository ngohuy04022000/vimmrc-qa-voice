"""Xuất phiếu chấm tay cho chế độ câu trả lời dài kèm nguồn (nghiên cứu cần đánh giá người, không chỉ token F1).

Lấy mẫu phân tầng theo nguồn câu hỏi từ reports/llm_assist_off_detail_v3.json (cần trường full_answer), ghi CSV UTF-8
có BOM để Excel đọc đúng tiếng Việt. Các cột bỏ trống do người chấm điền theo docs/human_eval_protocol.md.

Dùng: python scripts/make_human_eval_sheet.py --per-src 20 --seed 0
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, default=ROOT / "reports/llm_assist_off_detail_v3.json")
    ap.add_argument("--per-src", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, default=ROOT / "reports/human_eval_sheet.csv")
    args = ap.parse_args()

    rows = json.loads(args.report.read_text(encoding="utf-8"))[0]["answerable"]
    answered = [r for r in rows if r["kind"] == "qa" and r.get("full_answer")]
    rng = random.Random(args.seed)
    picked = []
    for src in sorted({r["src"] for r in answered}):
        pool = [r for r in answered if r["src"] == src]
        picked += rng.sample(pool, min(args.per_src, len(pool)))
    rng.shuffle(picked)  # người chấm không biết nhóm câu hỏi
    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "question", "answer_with_evidence_and_source", "cited_source",
                    "correct(0/1)", "evidence_relevant(0/1/2)", "source_supports_answer(0/1)", "natural_to_hear(1-5)", "notes",
                    "_hidden_src", "_hidden_token_f1"])
        for i, r in enumerate(picked, 1):
            w.writerow([i, r["q"], r["full_answer"], r.get("source", ""), "", "", "", "", "", r["src"], r["f1"]])
    print(f"wrote {len(picked)} rows to {args.out}")


if __name__ == "__main__":
    main()
