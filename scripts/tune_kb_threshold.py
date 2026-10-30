"""Pick the tier-1 -> Wikipedia fallback threshold.

A: dev questions whose passage is in tier 1 -> want tier-1 hit at rank 1 (R@1).
B: ViQuAD test questions with their contexts removed from tier 1 (unseen knowledge)
   -> want the routed top-1 passage to contain a gold answer string.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "retrieval-model_Huy"), str(ROOT / "mrc-model_Huy")]
from eval_e2e import eval_rows  # noqa: E402
from kb_retriever import load_kb_dir  # noqa: E402
from mrc_data import load_articles, normalize_text  # noqa: E402
from retrieval_client import Retriever  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kb", type=Path, default=ROOT / "data/kb_index.json")
    ap.add_argument("--wiki", type=Path, default=ROOT / "data/kb_wiki")
    ap.add_argument("--n-b", type=int, default=600)
    ap.add_argument("--output", type=Path, default=ROOT / "reports/kb_threshold.json")
    args = ap.parse_args()

    kb = Retriever.load(args.kb)
    rows_a = eval_rows("dev", kb, None)
    held = [a for a in load_articles(ROOT / "data/combined/test_vimmrc.json") if "answer_texts" in a]
    held_text = {a["article"].strip() for a in held}
    kb_b = Retriever([p for p in kb.passages if p["passage"].split(". ", 1)[-1].strip() not in held_text
                      and p["passage"].strip() not in held_text], k1=kb.k1, b=kb.b,
                     query_stopwords=kb.query_stopwords, bigram_boost=kb.bigram_boost)
    rows_b = [(q, [normalize_text(t) for t in ans]) for a in held
              for q, ans in zip(a["questions"], a["answer_texts"])][:args.n_b]
    wiki = load_kb_dir(args.wiki)

    a_hits = [kb.search(r["question"], 1) for r in rows_a]
    b_kb = [kb_b.search(q, 1) for q, _ in rows_b]
    b_wiki = [wiki.search(q, 1) for q, _ in rows_b]

    def contains(hit, answers):
        return bool(hit) and any(t and t in normalize_text(hit[0]["passage"]) for t in answers)

    table = []
    for tau in [0, 5, 10, 15, 20, 25, 30, 40, 1e9]:
        a_ok = sum(bool(h) and h[0]["score"] >= tau and h[0]["id"] == r["passage_id"] for h, r in zip(a_hits, rows_a))
        b_ok = sum(contains(k if (k and k[0]["score"] >= tau) else (w or k), ans)
                   for k, w, (_, ans) in zip(b_kb, b_wiki, rows_b))
        table.append({"threshold": tau, "A_kb_R@1": round(a_ok / len(rows_a), 4),
                      "B_answer_in_top1": round(b_ok / len(rows_b), 4)})
        print(table[-1], flush=True)
    a_wiki = [wiki.search(r["question"], 1) for r in rows_a]
    ratio_table = []
    for ratio in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]:
        def pick(k, w):
            return w if w and (not k or w[0]["score"] > ratio * k[0]["score"]) else k
        a_ok = sum(bool(k) and pick(k, w) is k and k[0]["id"] == r["passage_id"]
                   for k, w, r in zip(a_hits, a_wiki, rows_a))
        b_ok = sum(contains(pick(k, w), ans) for k, w, (_, ans) in zip(b_kb, b_wiki, rows_b))
        ratio_table.append({"wiki_if_score_ratio_above": ratio, "A_kb_R@1": round(a_ok / len(rows_a), 4),
                            "B_answer_in_top1": round(b_ok / len(rows_b), 4)})
        print(ratio_table[-1], flush=True)
    args.output.write_text(json.dumps({"A_n": len(rows_a), "B_n": len(rows_b), "threshold_table": table,
                                       "ratio_table": ratio_table}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
