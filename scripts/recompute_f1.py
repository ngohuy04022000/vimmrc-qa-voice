"""Tính lại F1 đầu cuối từ các câu trả lời ĐÃ LƯU trong reports/llm_assist_*.json (không chạy lại mô hình).

Đáp án tham chiếu dựng lại bằng eval_llm_assist.answerable_set(100) (xác định, seed 7), khớp theo câu hỏi.
Với mỗi báo cáo in/ghi: F1 cũ (tập hợp, bỏ dấu), F1 chuẩn (multiset, giữ dấu), theo nguồn, và số hàng bị từ chối
mà vẫn nhận F1 > 0 (bài báo nói "từ chối được 0 điểm"). Cảnh báo nếu câu trả lời lưu bị cắt ở 160 ký tự.

    python scripts/recompute_f1.py reports/llm_assist_off_gate1.json ... --out reports/f1_recomputed.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from metrics import best_f1, token_f1_multiset, token_f1_set_noaccent  # noqa: E402

DEFAULT = [
    "llm_assist_off_gate1", "llm_assist_off_int8_gate1", "llm_assist_off_int8_gate05",
    "llm_assist_off_short_recall", "llm_assist_off_detail", "llm_assist_off_detail_v2", "llm_assist_off_detail_v3",
]
mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else 0.0


def recompute(path: Path, refs_by_q: dict[str, list[str]]) -> dict:
    cfg = json.loads(path.read_text(encoding="utf-8"))[0]
    rows, per_src, miss, trunc = [], {}, 0, 0
    for r in cfg["answerable"]:
        refs = refs_by_q.get(r["q"])
        if refs is None:
            miss += 1
            continue
        text = r.get("full_answer") or r["answer"]
        trunc += (not r.get("full_answer")) and len(r["answer"]) >= 160
        old, new = best_f1(text, refs, token_f1_set_noaccent), best_f1(text, refs, token_f1_multiset)
        rows.append({"src": r["src"], "kind": r["kind"], "old": old, "new": new, "stored": r["f1"]})
        per_src.setdefault(r["src"], []).append(new)
    answered = [x for x in rows if x["kind"] != "unknown"]
    refused = [x for x in rows if x["kind"] == "unknown"]
    return {
        "stored_f1_all": cfg["f1_all"],
        "f1_set_noaccent_recomputed": mean([x["old"] for x in rows]),
        "f1_multiset": mean([x["new"] for x in rows]),
        "f1_multiset_when_answered": mean([x["new"] for x in answered]),
        "f1_multiset_by_src": {k: mean(v) for k, v in sorted(per_src.items())},
        "refused_rows": len(refused),
        "refused_rows_with_f1_gt0_old_metric": sum(x["old"] > 0 for x in refused),
        "refused_rows_with_f1_gt0_new_metric": sum(x["new"] > 0 for x in refused),
        "n": len(rows), "refs_not_found": miss, "answers_possibly_truncated_at_160": trunc,
        "false_refusal": cfg.get("false_refusal"), "correct_refusal": cfg.get("correct_refusal"),
        "reproduces_stored_old_f1": abs(mean([x["old"] for x in rows]) - cfg.get("f1_set_noaccent_all", cfg["f1_all"])) < 5e-4,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("reports", nargs="*", type=Path)
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "f1_recomputed.json")
    args = ap.parse_args()
    import eval_llm_assist  # nặng (~9 s) vì nạp cả api_server; chỉ dùng answerable_set
    refs_by_q = {it["q"]: it["refs"] for it in eval_llm_assist.answerable_set(100)}
    paths = args.reports or [ROOT / "reports" / f"{n}.json" for n in DEFAULT]
    result = {p.stem: recompute(p, refs_by_q) for p in paths}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    for name, v in result.items():
        print(f"{name}: cũ(đã lưu) {v['stored_f1_all']} | cũ(tính lại) {v['f1_set_noaccent_recomputed']} | "
              f"multiset {v['f1_multiset']} | khi_trả_lời {v['f1_multiset_when_answered']} | từ chối {v['refused_rows']} "
              f"(F1>0: cũ {v['refused_rows_with_f1_gt0_old_metric']}, mới {v['refused_rows_with_f1_gt0_new_metric']}) | "
              f"tái lập số cũ: {v['reproduces_stored_old_f1']} | cắt160: {v['answers_possibly_truncated_at_160']}")
    print("ghi", args.out)


if __name__ == "__main__":
    main()
