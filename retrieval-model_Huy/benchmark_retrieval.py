"""Reproducible train-only tuning followed by one dev comparison."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import time

from retrieval_client import BASELINE_CONFIG, Retriever, tokenize
from retrieval_cli import read_json, vimmrc_passages, vimmrc_queries


SEED = 42
TRAIN_QUERY_LIMIT = 800


def sample_queries(queries: list[dict[str, object]]) -> list[dict[str, object]]:
    selected = sorted(random.Random(SEED).sample(range(len(queries)), min(TRAIN_QUERY_LIMIT, len(queries))))
    return [queries[index] for index in selected]


def measure(retriever: Retriever, queries: list[dict[str, object]]) -> dict[str, float | int]:
    top1 = top5 = mrr5 = 0.0
    started = time.perf_counter()
    for query in queries:
        hits = retriever.search(query["question"], top_k=5)
        gold = set(query["relevant_ids"])
        ids = [hit["id"] for hit in hits]
        top1 += bool(ids and ids[0] in gold)
        top5 += bool(gold.intersection(ids))
        mrr5 += next((1 / rank for rank, passage_id in enumerate(ids, 1) if passage_id in gold), 0.0)
    elapsed = time.perf_counter() - started
    n = len(queries)
    return {"queries": n, "recall@1": top1 / n, "recall@5": top5 / n,
            "mrr@5": mrr5 / n, "query_seconds": round(elapsed, 4)}


def naive_search_ids(retriever: Retriever, question: str, top_k: int = 5) -> list[str]:
    """Reference scan from the original BM25 algorithm, for speed/equivalence checks."""
    terms = set(tokenize(question))
    n = len(retriever.passages)
    document_frequency = {term: len(retriever._postings.get(term, ())) for term in terms}
    ranked = []
    for index, counts in enumerate(retriever._counts):
        score = 0.0
        for term in terms:
            frequency = counts.get(term, 0)
            if frequency:
                df = document_frequency[term]
                idf = math.log1p((n - df + 0.5) / (df + 0.5))
                score += idf * frequency * (retriever.k1 + 1) / (frequency + retriever._length_norm[index])
        if score > 0:
            ranked.append((index, score))
    ranked.sort(key=lambda item: (-item[1], item[0]))
    return [retriever.passages[index]["id"] for index, _ in ranked[:top_k]]


def speed_check(retriever: Retriever, queries: list[dict[str, object]]) -> dict[str, float | int]:
    questions = [query["question"] for query in queries[:200]]
    for question in questions:
        assert naive_search_ids(retriever, question) == [hit["id"] for hit in retriever.search(question)]
    started = time.perf_counter()
    for question in questions:
        naive_search_ids(retriever, question)
    scan_seconds = time.perf_counter() - started
    started = time.perf_counter()
    for question in questions:
        retriever.search(question)
    postings_seconds = time.perf_counter() - started
    return {"queries": len(questions), "scan_seconds": round(scan_seconds, 4),
            "postings_seconds": round(postings_seconds, 4), "speedup": round(scan_seconds / postings_seconds, 2)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", default="../data/train_vimmrc.json")
    parser.add_argument("--dev", default="../data/dev_vimmrc.json")
    parser.add_argument("--output", default="reports/lexical_benchmark.json")
    args = parser.parse_args()

    train_records = read_json(args.train)
    train_passages = vimmrc_passages(train_records, "train")
    train_queries = sample_queries(vimmrc_queries(train_records, "train"))
    candidates = []

    def assess(config: dict[str, float | bool]) -> None:
        retriever = Retriever(train_passages, **config)
        candidates.append({"config": config, "train": measure(retriever, train_queries)})

    # Fix this search space before reading dev data.
    for k1 in (0.9, 1.5, 2.1):
        for b in (0.4, 0.75, 1.0):
            assess({"k1": k1, "b": b, "query_stopwords": False, "bigram_boost": 0.0})

    def quality(item: dict[str, object]) -> tuple[float, float, float]:
        metrics = item["train"]
        return (metrics["recall@1"], metrics["mrr@5"], metrics["recall@5"])

    best_base = max(candidates, key=quality)["config"]
    for stopwords in (False, True):
        for boost in (0.4, 0.8, 1.2):
            assess({**best_base, "query_stopwords": stopwords, "bigram_boost": boost})
    assess({**best_base, "query_stopwords": True, "bigram_boost": 0.0})
    winner = max(candidates, key=quality)

    # Dev is read only after the train winner is frozen.
    dev_records = read_json(args.dev)
    dev_passages = vimmrc_passages(dev_records, "dev")
    dev_queries = vimmrc_queries(dev_records, "dev", dev_passages)
    baseline_retriever = Retriever(dev_passages, **BASELINE_CONFIG)
    winner_retriever = Retriever(dev_passages, **winner["config"])
    report = {
        "protocol": {"seed": SEED, "train_query_limit": TRAIN_QUERY_LIMIT,
                     "train_articles": len(train_passages), "dev_articles": len(dev_passages),
                     "selection": "max train Recall@1, then MRR@5, then Recall@5; first candidate breaks ties",
                     "dev_use": "single frozen-winner comparison; no test split"},
        "baseline_config": BASELINE_CONFIG,
        "train_candidates": candidates,
        "train_winner_config": winner["config"],
        "dev_baseline": measure(baseline_retriever, dev_queries),
        "dev_winner": measure(winner_retriever, dev_queries),
        "speed_check_train": speed_check(Retriever(train_passages, **BASELINE_CONFIG), train_queries),
    }
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"train_winner_config": report["train_winner_config"],
                      "dev_baseline": report["dev_baseline"], "dev_winner": report["dev_winner"],
                      "speed_check_train": report["speed_check_train"]}, indent=2))


if __name__ == "__main__":
    main()
