"""Compare tier-routing rules end to end (answer F1), on two question sets.

A: dev questions whose passage is in tier 1 (in-KB knowledge).
B: ViQuAD test questions with their contexts removed from tier 1 (unseen, open-domain).
Each question is read twice (tier-1 top1, wiki top1); every rule just picks one of the two answers.
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
from kb_retriever import load_kb_dir  # noqa: E402
from mrc_data import load_articles, token_f1  # noqa: E402
from retrieval_client import Retriever  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--checkpoint", type=Path, default=ROOT / "mrc-model_Huy/checkpoints/vit5-combined-cont")
    ap.add_argument("--output", type=Path, default=ROOT / "reports/routing_e2e.json")
    args = ap.parse_args()

    kb = Retriever.load(ROOT / "data/kb_index.json")
    wiki = load_kb_dir(ROOT / "data/kb_wiki_full")
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
    data = {}
    for name, rows, tier1 in (("A_in_kb", set_a, kb), ("B_open", set_b, kb_b)):
        recs = []
        for i, (q, golds) in enumerate(rows):
            k, w = tier1.search(q, 1), wiki.search(q, 1)
            ak, sk = reader.read(q, k[0]["passage"], "head") if k else ("", -1e9)
            aw, sw = reader.read(q, w[0]["passage"], "head") if w else ("", -1e9)
            recs.append({"kb_bm25": k[0]["score"] if k else 0, "wiki_bm25": w[0]["score"] if w else 0,
                         "kb_seq": sk, "wiki_seq": sw,
                         "kb_f1": max(token_f1(ak, g) for g in golds), "wiki_f1": max(token_f1(aw, g) for g in golds)})
            if i % 100 == 0:
                print(name, i, flush=True)
        data[name] = recs

    def f1(recs, use_wiki):
        return round(sum(r["wiki_f1"] if use_wiki(r) else r["kb_f1"] for r in recs) / len(recs), 4)

    rules = {"kb_only": lambda r: False, "wiki_only": lambda r: True}
    for ratio in (0.5, 0.4, 0.3, 0.2):
        rules[f"bm25_ratio_{ratio}"] = lambda r, x=ratio: r["wiki_bm25"] > x * r["kb_bm25"]
    for d in (0.0, 0.1, 0.2, 0.3, 0.5):
        rules[f"reader_conf_margin_{d}"] = lambda r, x=d: r["wiki_seq"] > r["kb_seq"] + x
    table = []
    for rule, fn in rules.items():
        row = {"rule": rule, **{s: f1(data[s], fn) for s in data}}
        row["mean"] = round((row["A_in_kb"] + row["B_open"]) / 2, 4)
        table.append(row)
        print(row, flush=True)
    args.output.write_text(json.dumps({"n_per_set": args.n, "table": table}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
