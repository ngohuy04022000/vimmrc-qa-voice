"""Evaluate a known corpus: retrieval, gold-passage reader, and retrieved-passage QA."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from qa_pipeline import QAPipeline, Retriever, LexicalBaselineClient, MRCClient
from mrc_data import load_articles, flatten_articles, exact_match, token_f1
from retrieval_cli import vimmrc_passages, vimmrc_queries, evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--split", default="dev")
    parser.add_argument("--output", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--baseline", action="store_true")
    mode.add_argument("--model", type=Path)
    args = parser.parse_args()
    articles = load_articles(args.data)
    rows = flatten_articles(articles)
    if not rows:
        parser.error("dataset has no questions")
    retriever = Retriever(vimmrc_passages(articles, args.split))
    reader = LexicalBaselineClient() if args.baseline else MRCClient(args.model)
    pipeline = QAPipeline(retriever, reader)
    queries = vimmrc_queries(articles, args.split, retriever.passages)
    sums = dict(gold_exact_match=0., gold_token_f1=0., pipeline_exact_match=0., pipeline_token_f1=0.)
    for row in rows:
        gold = reader.answer_question(row["question"], row["passage"])
        predicted = pipeline.answer_question(row["question"])
        sums["gold_exact_match"] += exact_match(gold, row["answer"])
        sums["gold_token_f1"] += token_f1(gold, row["answer"])
        sums["pipeline_exact_match"] += exact_match(predicted, row["answer"])
        sums["pipeline_token_f1"] += token_f1(predicted, row["answer"])
    report = {
        "mode": "lexical_baseline_not_trained" if args.baseline else "finetuned_mrc",
        "protocol": "closed_corpus: index contains only passages of the evaluated split",
        "split": args.split, "articles": len(articles), "questions": len(rows),
        "dataset_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
        "retrieval_top1": evaluate(retriever, queries, top_k=1),
        "retrieval_top5": evaluate(retriever, queries, top_k=5),
        "qa": {key: value / len(rows) for key, value in sums.items()},
        "note": "Whitespace token F1; no multiple-choice accuracy. No answer labels enter retrieval.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
