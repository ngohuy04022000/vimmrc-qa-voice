"""BM25 ratio routing vs dense (e5) pooled routing, end to end (answer F1) on the eval_routing sets.

A: dev questions whose passage is in tier 1.  B: ViQuAD test questions with contexts removed from tier 1.
Candidates per question: tier-1 BM25 top-k, wiki BM25 top-k, wiki dense top-k; every rule picks one passage.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "retrieval-model_Huy"), str(ROOT / "mrc-model_Huy")]
from eval_e2e import Reader, eval_rows  # noqa: E402
from kb_retriever import DenseKB, Encoder, load_kb_dir  # noqa: E402
from mrc_data import load_articles, normalize_text, token_f1  # noqa: E402
from retrieval_client import Retriever  # noqa: E402

POOL = 5


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--checkpoint", type=Path, default=ROOT / "mrc-model_Huy/checkpoints/vit5-combined-cont")
    ap.add_argument("--output", type=Path, default=ROOT / "reports/dense_routing_e2e.json")
    args = ap.parse_args()

    kb = Retriever.load(ROOT / "data/kb_index.json")
    wiki_dir = ROOT / "data/kb_wiki_full"
    wiki = load_kb_dir(wiki_dir)
    model = (sorted(wiki_dir.glob("shard_*"))[0] / "dense_model.txt").read_text(encoding="utf-8").strip()
    enc = Encoder(model)  # CPU: CUDA hit cudaErrorUnknown under memory pressure next to ViT5
    dense = DenseKB(wiki_dir, wiki, enc)

    rng = random.Random(0)
    rows_a = eval_rows("dev", kb, None)
    rng.shuffle(rows_a)
    set_a = [(r["question"], [r["answer"]]) for r in rows_a[:args.n]]
    held = [a for a in load_articles(ROOT / "data/combined/test_vimmrc.json") if "answer_texts" in a]
    held_text = {a["article"].strip() for a in held}
    kb_b = Retriever([p for p in kb.passages if p["passage"].split(". ", 1)[-1].strip() not in held_text
                      and p["passage"].strip() not in held_text], k1=kb.k1, b=kb.b,
                     query_stopwords=kb.query_stopwords, bigram_boost=kb.bigram_boost)
    set_b = [(q, ans) for a in held for q, ans in zip(a["questions"], a["answer_texts"])]
    rng.shuffle(set_b)
    set_b = set_b[:args.n]

    reader = Reader(args.checkpoint)
    rules = ["bm25_ratio_0.4", "wiki_dense_top1"] + [f"pooled_cos_k{k}" for k in (1, 3, 5)] \
        + [f"pooled_cos_k{k}_kbmargin" for k in (1, 3)] \
        + [f"ratio_{r}_then_wiki_dense" for r in (0.4, 0.3, 0.2)] + [f"ratio_{r}_then_wiki_bestcos" for r in (0.4, 0.3, 0.2)]
    report = {}
    for name, rows, tier1 in (("A_in_kb", set_a, kb), ("B_open", set_b, kb_b)):
        f1 = {r: 0.0 for r in rules}
        has = {r: 0 for r in rules}
        for i, (q, golds) in enumerate(rows):
            qv = enc.queries([q])[0]
            k = tier1.search(q, POOL)
            wb = wiki.search(q, POOL)
            wd = dense.search_vec(qv, POOL)
            sparse = [dict(h, src="kb", rank=j) for j, h in enumerate(k)] + \
                     [dict(h, src="wb", rank=j) for j, h in enumerate(wb)]
            if sparse:
                for h, s in zip(sparse, enc.passages([h["passage"] for h in sparse]) @ qv):
                    h["cos"] = float(s)
            pool = sparse + [dict(h, src="wd", rank=j, cos=h["score"]) for j, h in enumerate(wd)]

            def best(kk, kb_margin=0.0):
                c = [h for h in pool if h["rank"] < kk]
                return max(c, key=lambda h: h["cos"] + (kb_margin if h["src"] == "kb" else 0)) if c else None

            picks = {
                "bm25_ratio_0.4": (wb[0] if wb and (not k or wb[0]["score"] > 0.4 * k[0]["score"]) else (k[0] if k else None)),
                "wiki_dense_top1": wd[0] if wd else None,
                "pooled_cos_k1": best(1), "pooled_cos_k3": best(3), "pooled_cos_k5": best(5),
                "pooled_cos_k1_kbmargin": best(1, 0.02), "pooled_cos_k3_kbmargin": best(3, 0.02),
            }
            # hybrid: BM25 ratio decides the tier (keeps tier-1 accuracy); dense picks the wiki passage
            wiki_best = max([h for h in pool if h["src"] in ("wb", "wd") and h["rank"] == 0],
                            key=lambda h: h["cos"], default=None)
            for r in (0.4, 0.3, 0.2):
                go_wiki = not k or (wb and wb[0]["score"] > r * k[0]["score"])
                kb1 = k[0] if k else None
                picks[f"ratio_{r}_then_wiki_dense"] = (wd[0] if wd else None) if go_wiki else kb1
                picks[f"ratio_{r}_then_wiki_bestcos"] = wiki_best if go_wiki else kb1
            for rule, h in picks.items():
                if not h:
                    continue
                ans, _ = reader.read(q, h["passage"], "head")
                f1[rule] += max(token_f1(ans, g) for g in golds)
                text = normalize_text(h["passage"])
                has[rule] += any(normalize_text(g) and normalize_text(g) in text for g in golds)
            if i % 100 == 0:
                print(name, i, flush=True)
        report[name] = {r: {"F1": round(f1[r] / len(rows), 4), "answer_in_passage": round(has[r] / len(rows), 4)}
                        for r in rules}
        print(name, json.dumps(report[name], indent=1), flush=True)
    args.output.write_text(json.dumps({"n_per_set": args.n, "pool": POOL, "dense_model": model, **report},
                                      indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
