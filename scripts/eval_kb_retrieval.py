"""Retrieval-only comparison of knowledge bases, split by question source (CPU only)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "retrieval-model_Huy"), str(ROOT / "mrc-model_Huy")]
from eval_e2e import eval_rows  # noqa: E402
from kb_retriever import load_any  # noqa: E402

configs = {
    "vimmrc_552": (ROOT / "data/vimmrc_index.json", None),
    "kb_vimmrc+viquad": (ROOT / "data/kb_index.json", None),
    "kb+wiki_full(ratio 0.5)": (ROOT / "data/kb_index.json", ROOT / "data/kb_wiki_full"),
}
split = sys.argv[1] if len(sys.argv) > 1 else "dev"
rows = eval_rows(split, load_any(ROOT / "data/kb_index.json"), None)
report = {}
for name, (index, wiki) in configs.items():
    r = load_any(index, wiki, 0.5)
    out = {}
    for src in ("vimmrc", "viquad"):
        sub = [x for x in rows if x["source"] == src]
        hits = [r.search(x["question"], 1) for x in sub]
        out[src] = {"n": len(sub), "R@1": round(sum(bool(h) and h[0]["id"] == x["passage_id"]
                                                    for h, x in zip(hits, sub)) / len(sub), 4)}
    report[name] = out
    print(name, out, flush=True)
(ROOT / f"reports/kb_retrieval_{split}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
