"""Command line interface for BM25 corpus preparation, search and evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import unicodedata

from retrieval_client import Retriever


def read_json(path: str) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def vimmrc_passages(records: object, split: str) -> list[dict[str, str]]:
    """Extract articles only; question, option and answer fields never enter the index."""
    if not isinstance(records, list):
        raise ValueError("ViMMRC data must be a list of article records")
    passages = []
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("article"), str):
            raise ValueError(f"record {index} has no article text")
        passages.append({"id": f"{split}:{index:04d}", "passage": record["article"]})
    return passages


def vimmrc_queries(records: object, split: str, corpus_passages: list[dict[str, str]] | None = None) -> list[dict[str, object]]:
    if not isinstance(records, list):
        raise ValueError("ViMMRC data must be a list of article records")

    def article_key(text: str) -> str:
        return unicodedata.normalize("NFC", " ".join(text.split()))

    queries = []
    passage_ids_by_text: dict[str, list[str]] = {}
    corpus_ids: set[str] = set()
    if corpus_passages is not None:
        for passage in corpus_passages:
            corpus_ids.add(passage["id"])
            passage_ids_by_text.setdefault(article_key(passage["passage"]), []).append(passage["id"])
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("questions"), list):
            raise ValueError(f"record {index} has no questions list")
        if corpus_passages is None:
            relevant_ids = [f"{split}:{index:04d}"]
        else:
            article = record.get("article")
            if not isinstance(article, str):
                raise ValueError(f"record {index} has no article text")
            matching_ids = passage_ids_by_text.get(article_key(article), [])
            if matching_ids:
                relevant_ids = matching_ids
            else:
                missing_id = f"__unavailable__:{split}:{index:04d}"
                while missing_id in corpus_ids:
                    missing_id += "_"
                relevant_ids = [missing_id]
        for question in record["questions"]:
            if not isinstance(question, str):
                raise ValueError(f"record {index} has a non-text question")
            queries.append({"question": question, "relevant_ids": relevant_ids})
    return queries


def evaluate(retriever: Retriever, queries: object, top_k: int = 5) -> dict[str, float | int]:
    """Compute average Recall@k and MRR@k from IDs, without answer labels."""
    if not isinstance(queries, list) or not queries:
        raise ValueError("queries must be a nonempty list")
    corpus_ids = {record["id"] for record in retriever.passages}
    recall_sum = reciprocal_rank_sum = 0.0
    covered = 0
    for index, query in enumerate(queries):
        if not isinstance(query, dict) or not isinstance(query.get("question"), str):
            raise ValueError(f"query {index} needs question text")
        relevant = query.get("relevant_ids")
        if not isinstance(relevant, list) or not relevant or any(not isinstance(x, str) for x in relevant):
            raise ValueError(f"query {index} needs nonempty relevant_ids")
        relevant_ids = set(relevant)
        covered += bool(relevant_ids & corpus_ids)
        hits = retriever.search(query["question"], top_k=top_k)
        hit_ids = [str(hit["id"]) for hit in hits]
        recall_sum += len(relevant_ids.intersection(hit_ids)) / len(relevant_ids)
        reciprocal_rank_sum += next((1 / rank for rank, hit_id in enumerate(hit_ids, 1) if hit_id in relevant_ids), 0.0)
    n = len(queries)
    return {
        "queries": n,
        "covered_queries": covered,
        "corpus_coverage": covered / n,
        f"recall@{top_k}": recall_sum / n,
        f"mrr@{top_k}": reciprocal_rank_sum / n,
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="search bundled synthetic passages")
    demo.add_argument("question", nargs="?", default="Hành tinh nào gần Mặt Trời nhất?")
    index = sub.add_parser("index", help="build an index from [{id, passage}, ...] JSON")
    index.add_argument("--input", required=True)
    index.add_argument("--output", required=True)
    prepare = sub.add_parser("prepare-vimmrc", help="index only article fields from ViMMRC JSON")
    prepare.add_argument("--input", required=True)
    prepare.add_argument("--output", required=True)
    prepare.add_argument("--split", required=True, help="ID prefix, e.g. train or dev")
    query = sub.add_parser("query", help="search an existing index")
    query.add_argument("--index", required=True)
    query.add_argument("--question", required=True)
    query.add_argument("--top-k", type=int, default=5)
    evaluation = sub.add_parser("evaluate", help="evaluate [{question, relevant_ids}] JSON")
    evaluation.add_argument("--index", required=True)
    evaluation.add_argument("--queries", required=True)
    evaluation.add_argument("--top-k", type=int, default=5)
    eval_vimmrc = sub.add_parser("evaluate-vimmrc", help="evaluate article retrieval on ViMMRC questions")
    eval_vimmrc.add_argument("--index", required=True)
    eval_vimmrc.add_argument("--data", required=True)
    eval_vimmrc.add_argument("--split", required=True)
    eval_vimmrc.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    if args.command == "demo":
        retriever = Retriever(read_json(str(Path(__file__).with_name("synthetic_passages.json"))))
        print(json.dumps(retriever.search(args.question, 3), ensure_ascii=False, indent=2))
    elif args.command == "index":
        retriever = Retriever(read_json(args.input))
        retriever.save(args.output)
        print(f"Indexed {len(retriever.passages)} passages: {args.output}")
    elif args.command == "prepare-vimmrc":
        retriever = Retriever(vimmrc_passages(read_json(args.input), args.split))
        retriever.save(args.output)
        print(f"Indexed {len(retriever.passages)} articles: {args.output}")
    elif args.command == "query":
        hits = Retriever.load(args.index).search(args.question, args.top_k)
        print(json.dumps(hits, ensure_ascii=False, indent=2))
    elif args.command in {"evaluate", "evaluate-vimmrc"}:
        retriever = Retriever.load(args.index)
        queries = read_json(args.queries) if args.command == "evaluate" else vimmrc_queries(read_json(args.data), args.split, retriever.passages)
        metrics = evaluate(retriever, queries, args.top_k)
        print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
