"""Encode every passage of a KB directory (shard_*/passages.jsonl) into embeddings.npy (float16, L2-normalised).

Resumable: shards that already have embeddings.npy are skipped.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

DEFAULT_MODEL = "intfloat/multilingual-e5-small"


def shard_dirs(kb_dir: Path) -> list[Path]:
    shards = sorted(kb_dir.glob("shard_*"))
    return shards or [kb_dir]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("kb_dir", type=Path)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--max-seq-length", type=int, default=256)
    args = ap.parse_args()

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(args.model, device="cuda")
    model.half()
    model.max_seq_length = args.max_seq_length
    for shard in shard_dirs(args.kb_dir):
        out = shard / "embeddings.npy"
        if out.exists():
            print(shard.name, "done, skip", flush=True)
            continue
        with (shard / "passages.jsonl").open(encoding="utf-8") as f:
            texts = ["passage: " + json.loads(line)["passage"] for line in f]
        # sort by length so batches pad little; restore order afterwards
        order = np.argsort([len(t) for t in texts])
        emb = model.encode([texts[i] for i in order], batch_size=args.batch_size, normalize_embeddings=True,
                           convert_to_numpy=True, show_progress_bar=True).astype(np.float16)
        result = np.empty_like(emb)
        result[order] = emb
        np.save(shard / "embeddings.tmp.npy", result)
        (shard / "embeddings.tmp.npy").replace(out)
        (shard / "dense_model.txt").write_text(args.model, encoding="utf-8")
        print(shard.name, result.shape, flush=True)


if __name__ == "__main__":
    main()
