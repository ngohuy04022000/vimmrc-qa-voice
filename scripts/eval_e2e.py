"""End-to-end QA accuracy on the deployed corpus: retrieval -> (rerank) -> ViT5 reader.

Rows = ViMMRC questions from the combined dev/test split whose passage is in the production
index, so the reader never saw them in training and retrieval runs over all 552 passages.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for folder in ("retrieval-model_Huy", "mrc-model_Huy"):
    sys.path.insert(0, str(ROOT / folder))

from mrc_data import exact_match, load_examples, token_f1  # noqa: E402
from kb_retriever import load_any  # noqa: E402
from retrieval_client import Retriever  # noqa: E402


def eval_rows(split: str, index: Retriever, limit: int | None) -> list[dict]:
    by_text = {}
    for p in index.passages:
        text = p["passage"].strip()
        by_text[text] = p["id"]
        if p["id"].startswith("viquad:") and ". " in text:  # KB stores "title. context"
            by_text[text.split(". ", 1)[1]] = p["id"]
    rows = [dict(r, passage_id=by_text[r["passage"]],
                 source="viquad" if by_text[r["passage"]].startswith("viquad:") else "vimmrc")
            for r in load_examples(ROOT / "data" / "combined" / f"{split}_vimmrc.json")
            if r["passage"] in by_text]
    return rows[:limit] if limit else rows


class Reader:
    def __init__(self, checkpoint: Path):
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        from context_selection import encode_input
        self.torch, self.encode = torch, encode_input
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tok = AutoTokenizer.from_pretrained(str(checkpoint))
        self.model = AutoModelForSeq2SeqLM.from_pretrained(str(checkpoint)).to(self.device).eval()
        self.cache = {}

    def read(self, question: str, passage: str, strategy: str) -> tuple[str, float]:
        key = (question, passage, strategy)
        if key not in self.cache:
            enc = self.encode(question, passage, self.tok, 512, strategy, return_tensors="pt").to(self.device)
            with self.torch.inference_mode():
                out = self.model.generate(**enc, max_new_tokens=64, num_beams=4,
                                          return_dict_in_generate=True, output_scores=True)
            self.cache[key] = (self.tok.decode(out.sequences[0], skip_special_tokens=True).strip(),
                               float(out.sequences_scores[0]))
        return self.cache[key]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--checkpoint", type=Path, default=ROOT / "mrc-model_Huy/checkpoints/vit5-combined-cont")
    ap.add_argument("--index", type=Path, default=ROOT / "data/vimmrc_index.json")
    ap.add_argument("--reranker", default="BAAI/bge-reranker-v2-m3")
    ap.add_argument("--rerank-pool", type=int, default=10)
    ap.add_argument("--no-rerank", action="store_true")
    ap.add_argument("--wiki", type=Path, help="tier-2 Wikipedia KB directory")
    ap.add_argument("--wiki-ratio", type=float, default=0.5)
    ap.add_argument("--strategies", nargs="+", default=["head", "question_chunks"])
    ap.add_argument("--no-top3", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    index = load_any(args.index, args.wiki, args.wiki_ratio)
    rows = eval_rows(args.split, index, args.limit)
    print(f"{len(rows)} questions ({args.split}), corpus {len(index.passages)} passages", flush=True)

    t = time.perf_counter()
    bm25 = [index.search(r["question"], top_k=args.rerank_pool) for r in rows]
    bm25_ms = (time.perf_counter() - t) / len(rows) * 1000

    retrievers = [("bm25", bm25, bm25_ms)]
    if not args.no_rerank:
        from sentence_transformers import CrossEncoder
        ce = CrossEncoder(args.reranker, max_length=512, device="cuda")
        t = time.perf_counter()
        reranked = []
        for r, hits in zip(rows, bm25):
            scores = ce.predict([(r["question"], h["passage"]) for h in hits], batch_size=16)
            reranked.append([h for _, h in sorted(zip(scores, hits), key=lambda x: -x[0])])
        retrievers.append(("bm25+rerank", reranked, (time.perf_counter() - t) / len(rows) * 1000))
        del ce

    def recall(ranked, k, src="all"):
        pairs = [(r, hs) for r, hs in zip(rows, ranked) if src == "all" or r["source"] == src]
        return round(sum(r["passage_id"] in [h["id"] for h in hs[:k]] for r, hs in pairs) / max(len(pairs), 1), 4)

    report = {"split": args.split, "questions": len(rows),
              "retrieval": {name: {src: {"R@1": recall(rk, 1, src), "R@5": recall(rk, 5, src)}
                                   for src in ("all", "vimmrc", "viquad")} | {"ms_per_q": ms}
                            for name, rk, ms in retrievers}}
    print(json.dumps(report["retrieval"], indent=2), flush=True)

    reader = Reader(args.checkpoint)

    def score(preds):
        out = {}
        for src in ("all", "vimmrc", "viquad"):
            pairs = [(p, r) for p, r in zip(preds, rows) if src == "all" or r["source"] == src]
            if pairs:
                out[src] = {"n": len(pairs),
                            "EM": sum(exact_match(p, r["answer"]) for p, r in pairs) / len(pairs),
                            "F1": sum(token_f1(p, r["answer"]) for p, r in pairs) / len(pairs)}
        return out

    qa = {}
    for strategy in args.strategies:
        qa[f"gold_passage/{strategy}"] = score([reader.read(r["question"], r["passage"], strategy)[0] for r in rows])
        for name, ranked, _ in retrievers:
            qa[f"{name}/top1/{strategy}"] = score(
                [reader.read(r["question"], hs[0]["passage"], strategy)[0] for r, hs in zip(rows, ranked)])
            if args.no_top3:
                continue
            qa[f"{name}/top3-maxscore/{strategy}"] = score(
                [max((reader.read(r["question"], h["passage"], strategy) for h in hs[:3]), key=lambda x: x[1])[0]
                 for r, hs in zip(rows, ranked)])
        print(json.dumps({k: v for k, v in qa.items() if k.endswith(strategy)}, indent=2), flush=True)
    report["qa"] = qa

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
