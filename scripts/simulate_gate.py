"""Mô phỏng cổng từ chối DIALOGUE_MIN_RERANK ở nhiều ngưỡng từ MỘT lượt đo không cổng (thay cho phép tính ad-hoc
trước đây của reports/rerank_confidence_gate.json, vốn không có script).

Cổng chỉ áp dụng cho nhánh hỏi-đáp thường (kind == "qa"; dialogue.py: `hit.score < min_rerank` => "unknown"), nên có thể
phát lại chính xác trên điểm reranker đã lưu (`rerank_score`) của lượt đo không cổng, không cần chạy lại mô hình.

    python scripts/simulate_gate.py reports/e2e_nogate_int8_main.json [--heldout] [--out reports/gate_sim_int8_main.json]
    python scripts/simulate_gate.py reports/e2e_nogate_int8_main.json --check reports/llm_assist_off_int8_gate1.json
      (--check: đối chiếu kết quả mô phỏng ở ngưỡng 1,0 với một lượt đo CÓ cổng thật)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in ("scripts", "mrc-model_Huy", "dialogue-manager_Huy"):
    sys.path.insert(0, str(ROOT / folder))
from bootstrap_ci import paired_bootstrap  # noqa: E402
from dialogue import UNKNOWN_ANSWER  # noqa: E402
from metrics import best_f1, token_f1_multiset  # noqa: E402

THRESHOLDS = [None, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else 0.0


def simulate(cfg: dict, refs_by_q: dict[str, list[str]], thr: float | None) -> dict:
    rows, per_src = [], {}
    for r in cfg["answerable"]:
        gated = thr is not None and r["kind"] == "qa" and r.get("rerank_score") is not None and r["rerank_score"] < thr
        refused = r["kind"] == "unknown" or gated
        text = UNKNOWN_ANSWER if gated else (r.get("full_answer") or r["answer"])
        f1 = best_f1(text, refs_by_q[r["q"]], token_f1_multiset)
        rows.append({"q": r["q"], "f1": f1, "refused": float(refused)})
        per_src.setdefault(r["src"], []).append(f1)
    urows = [{"q": u["q"], "refused": float(u["kind"] == "unknown" or (
        thr is not None and u["kind"] == "qa" and u.get("rerank_score") is not None and u["rerank_score"] < thr))}
        for u in cfg["unanswerable"]]
    return {"threshold": thr, "f1_all": mean([x["f1"] for x in rows]),
            "f1_by_src": {k: mean(v) for k, v in sorted(per_src.items())},
            "false_refusal": f"{int(sum(x['refused'] for x in rows))}/{len(rows)}",
            "correct_refusal": f"{int(sum(x['refused'] for x in urows))}/{len(urows)}",
            "_rows": rows, "_urows": urows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("report", type=Path)
    ap.add_argument("--heldout", action="store_true", help="bộ held-out (test[100:200]); mặc định bộ chính 220 câu")
    ap.add_argument("--check", type=Path, help="báo cáo CÓ cổng thật để đối chiếu ở ngưỡng 1,0")
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    import eval_llm_assist
    items = eval_llm_assist.answerable_set(100, offset=100, suites=False) if args.heldout else eval_llm_assist.answerable_set(100)
    refs_by_q = {it["q"]: it["refs"] for it in items}
    cfg = json.loads(args.report.read_text(encoding="utf-8"))[0]
    sims = [simulate(cfg, refs_by_q, t) for t in THRESHOLDS]
    base = sims[0]
    out = {"report": args.report.name, "heldout": args.heldout, "n_answerable": len(cfg["answerable"]),
           "n_unanswerable": len(cfg["unanswerable"]), "thresholds": []}
    for s in sims:
        entry = {k: v for k, v in s.items() if not k.startswith("_")}
        if s["threshold"] is not None:
            entry["vs_no_gate"] = {
                "f1": paired_bootstrap([x["f1"] for x in s["_rows"]], [x["f1"] for x in base["_rows"]], args.n),
                "false_refusal_rate": paired_bootstrap([x["refused"] for x in s["_rows"]], [x["refused"] for x in base["_rows"]], args.n),
                "correct_refusal_rate": paired_bootstrap([x["refused"] for x in s["_urows"]], [x["refused"] for x in base["_urows"]], args.n),
            }
        out["thresholds"].append(entry)
        print(f"thr={s['threshold']}: F1 {s['f1_all']} | từ chối nhầm {s['false_refusal']} | từ chối đúng {s['correct_refusal']}")
    if args.check:
        real = json.loads(args.check.read_text(encoding="utf-8"))[0]
        sim1 = next(s for s in sims if s["threshold"] == 1.0)
        out["check_vs_real_gate"] = {"real_false_refusal": real["false_refusal"], "real_correct_refusal": real["correct_refusal"],
                                     "sim_false_refusal": sim1["false_refusal"], "sim_correct_refusal": sim1["correct_refusal"]}
        print("đối chiếu với lượt có cổng thật:", out["check_vs_real_gate"])
    if args.out:
        args.out.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print("ghi", args.out)


if __name__ == "__main__":
    main()
