"""Tune the ViMMRC -> ViQuAD tier ratio on dev (retrieval R@1 per source, CPU only)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "retrieval-model_Huy"), str(ROOT / "mrc-model_Huy")]
from eval_e2e import eval_rows  # noqa: E402
from retrieval_client import Retriever  # noqa: E402

kb = Retriever.load(ROOT / "data/kb_index.json")
vim = Retriever.load(ROOT / "data/vimmrc_index.json")
viq = Retriever([p for p in kb.passages if p["id"].startswith("viquad:")], k1=kb.k1, b=kb.b,
                query_stopwords=kb.query_stopwords, bigram_boost=kb.bigram_boost)
viq.save(ROOT / "data/viquad_index.json")
rows = eval_rows("dev", kb, None)
h_vim = [vim.search(r["question"], 1) for r in rows]
h_viq = [viq.search(r["question"], 1) for r in rows]
table = []
for ratio in [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 2.0, 3.0]:
    out = {"ratio": ratio}
    for src in ("vimmrc", "viquad"):
        ok = n = 0
        for r, a, b in zip(rows, h_vim, h_viq):
            if r["source"] != src:
                continue
            pick = b if b and (not a or b[0]["score"] > ratio * a[0]["score"]) else a
            ok += bool(pick) and pick[0]["id"] == r["passage_id"]
            n += 1
        out[src] = round(ok / n, 4)
    table.append(out)
    print(out, flush=True)
(ROOT / "reports/tier_ratio_dev.json").write_text(json.dumps(table, indent=2) + "\n", encoding="utf-8")
