"""Tính lại F1 của reports/reader_bench.json bằng F1 chuẩn (multiset, giữ dấu) mà không chạy lại bộ đọc nào.

`items[].raw` là câu thô của bộ đọc; câu đã soạn = answer_composer.compose_answer(q, raw, passage) (hàm tất định),
đoạn văn lấy từ reports/reader_bench_passages.json. In bảng cũ (set, bỏ dấu) và mới, kèm paired bootstrap giữa
bộ đọc triển khai (vi-mrc-large) và ViT5 trên câu đã soạn.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
for folder in ("scripts", "retrieval-model_Huy", "mrc-model_Huy", "dialogue-manager_Huy"):
    sys.path.insert(0, str(ROOT / folder))
from answer_composer import compose_answer  # noqa: E402
from bootstrap_ci import paired_bootstrap  # noqa: E402
from metrics import best_f1, token_f1_multiset  # noqa: E402

mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else 0.0


def main() -> None:
    bench = json.loads((ROOT / "reports" / "reader_bench.json").read_text(encoding="utf-8"))
    rows = json.loads((ROOT / "reports" / "reader_bench_passages.json").read_text(encoding="utf-8"))
    by_q = {r["q"]: r for r in rows}
    out, per_item = {}, {}
    for name, res in bench.items():
        its = []
        for it in res["items"]:
            r = by_q[it["q"]]
            raw = it["raw"]
            composed = compose_answer(r["q"], raw, r["passage"]) if raw else ""
            its.append({"src": it["src"], "gold": it["gold_in_passage"],
                        "raw": best_f1(raw, r["refs"], token_f1_multiset),
                        "composed": best_f1(composed, r["refs"], token_f1_multiset)})
        cov = [i for i in its if i["gold"]]
        old = res["summary"]
        out[name] = {
            "n": len(its), "n_gold_in_passage": len(cov),
            "old_set_noaccent": {"f1_raw": old["f1_raw"], "f1_composed": old["f1_composed"],
                                 "f1_raw_gold": old["f1_raw_gold_in_passage"], "f1_composed_gold": old["f1_composed_gold_in_passage"]},
            "multiset": {"f1_raw": mean([i["raw"] for i in its]), "f1_composed": mean([i["composed"] for i in its]),
                         "f1_raw_gold": mean([i["raw"] for i in cov]), "f1_composed_gold": mean([i["composed"] for i in cov]),
                         "by_src_composed": {s: mean([i["composed"] for i in its if i["src"] == s]) for s in ("ood", "hard", "test")}},
        }
        per_item[name] = its
        m = out[name]["multiset"]
        print(f"{name:42s} cũ composed {old['f1_composed']:.4f} raw {old['f1_raw']:.4f} | multiset composed {m['f1_composed']:.4f} "
              f"raw {m['f1_raw']:.4f} | gold: composed {m['f1_composed_gold']:.4f} raw {m['f1_raw_gold']:.4f}")
    a, b = "nguyenvulebinh/vi-mrc-large", "vit5-combined-cont"
    out["_paired_bootstrap_vi-mrc-large_minus_vit5"] = {
        "composed_all": paired_bootstrap([i["composed"] for i in per_item[a]], [i["composed"] for i in per_item[b]]),
        "composed_gold_in_passage": paired_bootstrap([i["composed"] for i in per_item[a] if i["gold"]],
                                                     [i["composed"] for i in per_item[b] if i["gold"]]),
        "raw_gold_in_passage": paired_bootstrap([i["raw"] for i in per_item[a] if i["gold"]],
                                                [i["raw"] for i in per_item[b] if i["gold"]]),
    }
    for k, v in out["_paired_bootstrap_vi-mrc-large_minus_vit5"].items():
        print(f"vi-mrc-large - vit5 [{k}]: {v['diff']:+} CI{v['ci95']} sig={v['significant_at_95']} n={v['n']}")
    (ROOT / "reports" / "reader_bench_multiset.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ghi reports/reader_bench_multiset.json")


if __name__ == "__main__":
    main()
