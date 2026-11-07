"""Tinh chỉnh offline cách chọn đoạn và luật từ chối từ reports/reader_signals.json (scripts/collect_reader_signals.py).

Chiến lược chọn đoạn: top1 (hiện tại) | reader (điểm bộ đọc cao nhất) | combo{w} (điểm reranker + w * logit điểm bộ đọc).
Luật từ chối: điểm reranker của đoạn chọn < t1, điểm bộ đọc < t2, hoặc (dùng null) bộ đọc nghiêng về "không có đáp án".
Chỉ số: F1 token của câu trả lời thô (từ chối = 0), số câu có đáp án bị từ chối, số câu ngoài kho bị từ chối
(26 câu "thật sự" không có đáp án, bỏ 4 câu mà Wikipedia trả lời được). Kiểm chống quá khớp: chọn trên nửa chẵn, đo trên nửa lẻ.

Dùng: python scripts/tune_reader_signals.py [--max-f1-drop 0.01]
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mrc-model_Huy"))
from mrc_data import token_f1  # noqa: E402

ANSWERABLE_BY_WIKI = ("Eiffel", "axit sunfuric", "Sao Hỏa có bao nhiêu", "Hãy trao cho anh")
logit = lambda p: math.log(max(p, 1e-9) / max(1 - p, 1e-9))


def choose(row: dict, strategy: str) -> dict:
    ps = row["passages"]
    if strategy == "top1":
        return ps[0]
    if strategy == "reader":
        return max(ps, key=lambda p: p["reader_score"])
    w = float(strategy[5:])
    return max(ps, key=lambda p: p["score"] + w * logit(p["reader_score"]))


def evaluate(rows: list[dict], strategy: str, t1: float, t2: float, use_null: bool) -> dict:
    f1 = ref_a = ref_u = n_a = n_u = ref_strict = n_strict = 0
    for r in rows:
        p = choose(r, strategy)
        refused = p["score"] < t1 or p["reader_score"] < t2 or (use_null and p["null_wins"]) or not p["answer"]
        if r["kind"] == "answerable":
            n_a += 1
            ref_a += refused
            f1 += 0 if refused else max(token_f1(p["answer"], g) for g in r["refs"])
        else:
            n_u += 1
            ref_u += refused
            if not any(k in r["q"] for k in ANSWERABLE_BY_WIKI):
                n_strict += 1
                ref_strict += refused
    return {"f1": f1 / max(n_a, 1), "false_refusal": ref_a, "n_a": n_a, "unans_refused": ref_u, "n_u": n_u,
            "strict_refused": ref_strict, "n_strict": n_strict}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--signals", type=Path, default=ROOT / "reports" / "reader_signals.json")
    ap.add_argument("--max-f1-drop", type=float, default=0.01, help="F1 được phép thấp hơn top1 không từ chối")
    args = ap.parse_args()
    rows = json.loads(args.signals.read_text(encoding="utf-8"))
    strategies = ["top1", "reader"] + [f"combo{w}" for w in (0.25, 0.5, 1.0, 2.0)]
    grid = list(itertools.product(strategies, (-99, 0, 1, 2), (0, 0.05, 0.1, 0.2, 0.3, 0.5), (False, True)))
    base = evaluate(rows, "top1", -99, 0, False)
    print(f"mốc (top1, không từ chối): F1 {base['f1']:.4f}  ngoài kho bị từ chối {base['unans_refused']}/{base['n_u']}")
    results = [(g, evaluate(rows, *g)) for g in grid]
    ok = [(g, m) for g, m in results if m["f1"] >= base["f1"] - args.max_f1_drop]
    ok.sort(key=lambda gm: (-gm[1]["strict_refused"], -gm[1]["f1"]))
    print(f"\nTốt nhất (F1 >= mốc - {args.max_f1_drop}), xếp theo số câu ngoài kho thật sự bị từ chối:")
    print("strategy   t1  t2    null   F1     false_ref  unans  strict")
    for g, m in ok[:12]:
        print(f"{g[0]:9s} {g[1]:3d} {g[2]:5.2f} {str(g[3]):5s} {m['f1']:.4f}  {m['false_refusal']:3d}/{m['n_a']}  "
              f"{m['unans_refused']:2d}/{m['n_u']}  {m['strict_refused']:2d}/{m['n_strict']}")
    print("\nChỉ đổi cách chọn đoạn, không từ chối thêm (t1=-99, t2=0, không null):")
    for s in strategies:
        m = evaluate(rows, s, -99, 0, False)
        print(f"  {s:9s} F1 {m['f1']:.4f}")
    even, odd = rows[0::2], rows[1::2]
    best_even = max(((g, evaluate(even, *g)) for g in grid
                     if evaluate(even, "top1", -99, 0, False)["f1"] - evaluate(even, *g)["f1"] <= args.max_f1_drop),
                    key=lambda gm: (gm[1]["strict_refused"], gm[1]["f1"]))
    g = best_even[0]
    o_base, o = evaluate(odd, "top1", -99, 0, False), evaluate(odd, *g)
    print(f"\nChống quá khớp: chọn trên nửa chẵn -> {g}; nửa lẻ: F1 {o['f1']:.4f} (mốc {o_base['f1']:.4f}), "
          f"từ chối ngoài kho thật sự {o['strict_refused']}/{o['n_strict']}, từ chối nhầm {o['false_refusal']}/{o['n_a']}")


if __name__ == "__main__":
    main()
