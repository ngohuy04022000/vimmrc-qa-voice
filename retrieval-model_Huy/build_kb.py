"""Build the RAG knowledge base (bm25s index) from passage text only, never questions/answers.

Sources: ViMMRC passages (existing index) + every UIT-ViQuAD2.0 Wikipedia context, and with
--wiki the lead section of each Vietnamese Wikipedia article (wikimedia/wikipedia 20231101.vi).
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from kb_retriever import KBRetriever

ROOT = Path(__file__).resolve().parents[1]
VIQUAD_REPO = "taidng/UIT-ViQuAD2.0"
VIQUAD_FILES = ("data/train-00000-of-00001.parquet", "data/validation-00000-of-00001.parquet",
                "data/test-00000-of-00001.parquet")
WIKI_REPO, WIKI_DIR, WIKI_SHARDS = "wikimedia/wikipedia", "20231101.vi", 4


def viquad_passages(known: set[str]) -> list[dict]:
    import pandas as pd
    from huggingface_hub import hf_hub_download
    out = []
    for filename in VIQUAD_FILES:
        frame = pd.read_parquet(hf_hub_download(VIQUAD_REPO, filename, repo_type="dataset"))
        for title, context in zip(frame["title"], frame["context"]):
            text = context.strip()
            if text and text not in known:
                known.add(text)
                out.append({"id": f"viquad:{len(out):05d}", "passage": f"{title}. {text}" if title else text})
    return out


def lead(text: str, max_chars: int) -> str:
    """First paragraphs up to max_chars, cut at a sentence end when possible."""
    out = ""
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            continue
        if out and len(out) + len(para) > max_chars:
            break
        out = f"{out} {para}".strip()
    if len(out) > max_chars:
        cut = out.rfind(". ", 0, max_chars)
        out = out[:cut + 1] if cut > max_chars // 2 else out[:max_chars]
    return out


def chunks(text: str, max_chars: int, limit: int) -> list[str]:
    """Split a full article into paragraph-aligned chunks of at most ~max_chars."""
    out, cur = [], ""
    for para in (p.strip() for p in text.split("\n")):
        if not para:
            continue
        if cur and len(cur) + len(para) > max_chars:
            out.append(cur)
            cur = ""
            if len(out) >= limit:
                return out
        cur = f"{cur} {para}".strip()[: max_chars * 2]
    if cur:
        out.append(cur)
    return out[:limit]


def wiki_passages(min_chars: int, max_chars: int, full: bool = False, per_article: int = 20) -> list[dict]:
    import pyarrow.parquet as pq
    from huggingface_hub import hf_hub_download
    out = []
    for shard in range(WIKI_SHARDS):
        path = hf_hub_download(WIKI_REPO, f"{WIKI_DIR}/train-{shard:05d}-of-{WIKI_SHARDS:05d}.parquet",
                               repo_type="dataset")
        table = pq.read_table(path, columns=["title", "text"])
        for title, text in zip(table.column("title").to_pylist(), table.column("text").to_pylist()):
            bodies = chunks(text or "", max_chars, per_article) if full else [lead(text or "", max_chars)]
            for body in bodies:
                if len(body) >= min_chars:
                    out.append({"id": f"wiki:{len(out):07d}", "passage": f"{title}. {body}"})
        del table
        print(f"wiki shard {shard}: {len(out)} passages so far", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base-index", type=Path, default=ROOT / "data" / "vimmrc_index.json")
    ap.add_argument("--kb-output", type=Path, default=ROOT / "data" / "kb_index.json",
                    help="tier 1: ViMMRC + ViQuAD, legacy BM25 with bigram boost")
    ap.add_argument("--wiki-output", type=Path, default=ROOT / "data" / "kb_wiki",
                    help="tier 2: Wikipedia leads, bm25s")
    ap.add_argument("--wiki", action="store_true")
    ap.add_argument("--wiki-min-chars", type=int, default=300)
    ap.add_argument("--wiki-max-chars", type=int, default=800)
    ap.add_argument("--wiki-full", action="store_true", help="index whole articles in chunks, not just leads")
    ap.add_argument("--skip-tier1", action="store_true")
    ap.add_argument("--shard-size", type=int, default=400_000)
    args = ap.parse_args()

    if not args.skip_tier1:
        from retrieval_client import Retriever
        base_json = json.loads(args.base_index.read_text(encoding="utf-8"))
        base = base_json["passages"]
        passages = [{"id": p["id"], "passage": p["passage"]} for p in base]
        viquad = viquad_passages({p["passage"].strip() for p in passages})
        settings = {k: base_json[k] for k in ("k1", "b", "query_stopwords", "bigram_boost") if k in base_json}
        Retriever(passages + viquad, **settings).save(args.kb_output)
        print(f"tier 1 {args.kb_output}: {len(base)} ViMMRC + {len(viquad)} ViQuAD", flush=True)

    if args.wiki:
        import gc
        wiki = wiki_passages(args.wiki_min_chars, args.wiki_max_chars, args.wiki_full)
        t = time.perf_counter()
        for n, start in enumerate(range(0, len(wiki), args.shard_size)):
            KBRetriever(wiki[start:start + args.shard_size]).save(args.wiki_output / f"shard_{n}")
            gc.collect()
            print(f"shard {n} saved", flush=True)
        print(f"tier 2 {args.wiki_output}: {len(wiki)} Wikipedia passages (indexed in {time.perf_counter() - t:.0f}s)")


if __name__ == "__main__":
    main()
