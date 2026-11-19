"""Khoảng tin cậy 95% (paired bootstrap, seed cố định) cho các so sánh chính của bài báo.

Dùng dữ liệu từng câu đã lưu trong reports/, không chạy lại mô hình:
  * đầu cuối: reports/llm_assist_*.json (đáp án đã lưu + tham chiếu dựng lại bằng eval_llm_assist.answerable_set);
    F1 là multiset giữ dấu (scripts/metrics.py). Câu trả lời lưu có thể bị cắt 160 ký tự trong báo cáo cũ
    (sai số cỡ 0,001, nhỏ hơn nhiều so với độ rộng khoảng tin cậy).
  * reader trên đoạn đúng: reports/reader_gold_*.json (predictions theo thứ tự test_vimmrc.json).

Kết quả: reports/bootstrap_ci.json. Mỗi so sánh có hiệu trung bình (A - B), khoảng 95% theo phân vị,
và tỉ lệ lần lấy mẫu có hiệu <= 0 (p một phía xấp xỉ). Lấy mẫu theo CÂU, ghép cặp.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mrc-model_Huy"))
from metrics import best_f1, token_f1_multiset  # noqa: E402


def paired_bootstrap(a: list[float], b: list[float], n: int = 10000, seed: int = 0) -> dict:
    assert len(a) == len(b) and a, "hai dãy phải cùng độ dài và khác rỗng"
    rng, m = random.Random(seed), len(a)
    d = [x - y for x, y in zip(a, b)]
    diffs = []
    for _ in range(n):
        idx = [rng.randrange(m) for _ in range(m)]
        diffs.append(sum(d[i] for i in idx) / m)
    diffs.sort()
    return {
        "n": m, "mean_a": round(sum(a) / m, 4), "mean_b": round(sum(b) / m, 4),
        "diff": round(sum(d) / m, 4), "ci95": [round(diffs[int(0.025 * n)], 4), round(diffs[int(0.975 * n) - 1], 4)],
        "p_diff_le_0": round(sum(x <= 0 for x in diffs) / n, 4),
        "significant_at_95": not (diffs[int(0.025 * n)] <= 0 <= diffs[int(0.975 * n) - 1]),
    }


def e2e_rows(path: Path, refs_by_q: dict[str, list[str]]) -> dict[str, dict]:
    cfg = json.loads(path.read_text(encoding="utf-8"))[0]
    out = {}
    for r in cfg["answerable"]:
        text = r.get("full_answer") or r["answer"]
        out[r["q"]] = {"f1": best_f1(text, refs_by_q[r["q"]], token_f1_multiset), "refused": float(r["kind"] == "unknown")}
    refusal = {r["q"]: float(r["kind"] == "unknown") for r in cfg["unanswerable"]}
    return {"ans": out, "unans": refusal}


def sim_rows(report: str, thr: float | None, refs_by_q: dict) -> dict:
    """Hàng từng câu của một lượt đo KHÔNG cổng sau khi phát lại cổng ở ngưỡng thr (scripts/simulate_gate.py)."""
    from simulate_gate import simulate
    cfg = json.loads((ROOT / "reports" / f"{report}.json").read_text(encoding="utf-8"))[0]
    sim = simulate(cfg, refs_by_q, thr)
    return {"ans": {r["q"]: {"f1": r["f1"], "refused": r["refused"]} for r in sim["_rows"]},
            "unans": {r["q"]: r["refused"] for r in sim["_urows"]}}


def compare_rows(label_a: str, label_b: str, A: dict, B: dict, n: int, seed: int) -> dict:
    qs = [q for q in A["ans"] if q in B["ans"]]
    uq = [q for q in A["unans"] if q in B["unans"]]
    return {
        "a": label_a, "b": label_b,
        "f1": paired_bootstrap([A["ans"][q]["f1"] for q in qs], [B["ans"][q]["f1"] for q in qs], n, seed),
        "false_refusal_rate": paired_bootstrap([A["ans"][q]["refused"] for q in qs], [B["ans"][q]["refused"] for q in qs], n, seed),
        "correct_refusal_rate": paired_bootstrap([A["unans"][q] for q in uq], [B["unans"][q] for q in uq], n, seed),
    }


def compare_e2e(name_a: str, name_b: str, refs_by_q: dict, n: int, seed: int) -> dict:
    A, B = (e2e_rows(ROOT / "reports" / f"{x}.json", refs_by_q) for x in (name_a, name_b))
    return compare_rows(name_a, name_b, A, B, n, seed)


def compare_reader_gold(a: str, b: str, n: int, seed: int) -> dict:
    from mrc_data import load_examples
    ex = load_examples(ROOT / "data" / "combined" / "test_vimmrc.json")
    pa = json.loads((ROOT / "reports" / f"reader_gold_{a}.json").read_text(encoding="utf-8"))["predictions"]
    pb = json.loads((ROOT / "reports" / f"reader_gold_{b}.json").read_text(encoding="utf-8"))["predictions"]
    assert len(ex) == len(pa) == len(pb), (len(ex), len(pa), len(pb))
    return {"a": a, "b": b, "token_f1_multiset": paired_bootstrap(
        [token_f1_multiset(p, e["answer"]) for p, e in zip(pa, ex)],
        [token_f1_multiset(p, e["answer"]) for p, e in zip(pb, ex)], n, seed)}


# (A, B): A là cấu hình đang dùng / được cho là tốt hơn, B là đối chứng.
E2E_PAIRS = [
    ("llm_assist_off_gate1", "llm_assist_off_vimrc"),            # cổng từ chối 1,0 so với không cổng (FP32, bộ đọc span)
    ("llm_assist_off_int8_gate1", "llm_assist_off_gate1"),       # INT8 so với FP32
    ("llm_assist_off_vimrc", "llm_assist_off_v3"),               # bộ đọc span vi-mrc-large so với ViT5
    ("llm_assist_off_int8_gate1", "llm_assist_off_int8_gate05"), # ngưỡng 1,0 so với 0,5 (INT8)
]


# (nhãn, báo cáo, ngưỡng) cho lượt đo 2026-11-09; "main" dùng bộ 220+30 câu, "heldout" dùng bộ held-out.
SIM_PAIRS = [
    ("main", ("INT8@1.0", "e2e_nogate_int8_main", 1.0), ("FP32@1.0", "e2e_nogate_fp32_main", 1.0)),   # INT8 so với FP32 (cùng cổng)
    ("main", ("FP32@1.0", "e2e_nogate_fp32_main", 1.0), ("FP32@none", "e2e_nogate_fp32_main", None)),  # tác dụng của cổng
    ("main", ("INT8@1.0", "e2e_nogate_int8_main", 1.0), ("INT8@none", "e2e_nogate_int8_main", None)),
    ("main", ("INT8@1.0", "e2e_nogate_int8_main", 1.0), ("INT8@0.5", "e2e_nogate_int8_main", 0.5)),
    ("main", ("INT8@2.0", "e2e_nogate_int8_main", 2.0), ("INT8@1.0", "e2e_nogate_int8_main", 1.0)),
    ("main", ("span@none", "e2e_nogate_fp32_main", None), ("ViT5@none", "e2e_nogate_vit5_fp32_main", None)),  # bộ đọc span so với ViT5
    ("heldout", ("INT8@1.0", "e2e_nogate_int8_heldout", 1.0), ("INT8@none", "e2e_nogate_int8_heldout", None)),
    ("heldout", ("INT8@2.0", "e2e_nogate_int8_heldout", 2.0), ("INT8@1.0", "e2e_nogate_int8_heldout", 1.0)),
]


# Lượt đo CÓ cổng thật (rerun_live_gate.sh) và lượt không cổng (rerun_e2e_gate.sh); (A, B, bộ).
LIVE_PAIRS = [
    ("e2e_gate1_int8_main", "e2e_gate1_fp32_main", "main"),        # INT8 (triển khai) so với FP32, cùng cổng 1,0
    ("e2e_gate1_fp32_main", "e2e_nogate_fp32_main", "main"),       # tác dụng của cổng, FP32
    ("e2e_gate1_int8_main", "e2e_nogate_int8_main", "main"),       # tác dụng của cổng, INT8
    ("e2e_nogate_fp32_main", "e2e_nogate_vit5_fp32_main", "main"), # bộ đọc span so với ViT5, không cổng
    ("e2e_gate1_int8_heldout", "e2e_nogate_int8_heldout", "heldout"),  # cổng trên bộ held-out
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "bootstrap_ci.json")
    ap.add_argument("--pairs", nargs="*", help="a,b ... (tên file trong reports/ không có .json); mặc định E2E_PAIRS")
    args = ap.parse_args()
    import eval_llm_assist  # chỉ dùng answerable_set; nạp chậm (~9 s)
    refs_by_q = {it["q"]: it["refs"] for it in eval_llm_assist.answerable_set(100)}
    refs_held = {it["q"]: it["refs"] for it in eval_llm_assist.answerable_set(100, offset=100, suites=False)}
    pairs = [tuple(p.split(",")) for p in args.pairs] if args.pairs else E2E_PAIRS
    sim = []
    for split, (la, ra, ta), (lb, rb, tb) in SIM_PAIRS:
        refs = refs_held if split == "heldout" else refs_by_q
        sim.append(dict(split=split, **compare_rows(la, lb, sim_rows(ra, ta, refs), sim_rows(rb, tb, refs), args.n, args.seed)))
    live = [dict(split=split, **compare_e2e(a, b, refs_held if split == "heldout" else refs_by_q, args.n, args.seed))
            for a, b, split in LIVE_PAIRS]
    result = {"bootstrap": {"resamples": args.n, "seed": args.seed, "unit": "câu hỏi, ghép cặp"},
              "e2e_live_2026-11-09": live,
              "e2e_gate_replay_2026-11-09": sim,
              "e2e_stored_reports": [compare_e2e(a, b, refs_by_q, args.n, args.seed) for a, b in pairs],
              "reader_gold": compare_reader_gold("vi-mrc-large", "vit5-combined-cont", args.n, args.seed)}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in live + sim + result["e2e_stored_reports"]:
        f, fr, cr = c["f1"], c["false_refusal_rate"], c["correct_refusal_rate"]
        print(f"[{c.get('split', 'stored')}] {c['a']} - {c['b']}: F1 {f['diff']:+} CI{f['ci95']} sig={f['significant_at_95']} | "
              f"từ chối nhầm {fr['diff']:+} CI{fr['ci95']} | từ chối đúng {cr['diff']:+} CI{cr['ci95']}")
    g = result["reader_gold"]["token_f1_multiset"]
    print(f"reader gold vi-mrc-large - vit5: {g['diff']:+} CI{g['ci95']} sig={g['significant_at_95']} (n={g['n']})")
    print("ghi", args.out)


if __name__ == "__main__":
    main()
