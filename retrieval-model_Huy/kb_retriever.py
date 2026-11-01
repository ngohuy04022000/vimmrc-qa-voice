"""Scalable BM25 retriever (bm25s sparse index) for the RAG knowledge base.

Same search() contract, word tokenizer, query stopwords, k1 and b as Retriever (no bigram
boost: indexing bigrams for 340k Wikipedia passages does not fit in laptop RAM).
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

from retrieval_client import QUERY_STOPWORDS, tokenize

TOKEN_PATTERN = r"(?u)\b\w+\b"


def terms(text: str) -> list[str]:
    words = tokenize(text)
    return [w for w in words if w not in QUERY_STOPWORDS] or words


class KBRetriever:
    def __init__(self, passages: list[dict], k1: float = 2.1, b: float = 1.0):
        import bm25s
        self.passages = passages
        tokens = bm25s.tokenize([unicodedata.normalize("NFC", p["passage"]).casefold() for p in passages],
                                lower=False, token_pattern=TOKEN_PATTERN, stopwords=None, show_progress=False)
        self.bm25 = bm25s.BM25(k1=k1, b=b, method="lucene")
        self.bm25.index(tokens, show_progress=False)
        self.vocab = tokens.vocab

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer")
        ids = [self.vocab[t] for t in dict.fromkeys(terms(question)) if t in self.vocab]
        if not ids:
            return []
        scores = self.bm25.get_scores(ids)
        import numpy as np
        k = min(top_k, len(scores))
        top = np.argpartition(-scores, k - 1)[:k]
        top = top[np.argsort(-scores[top], kind="stable")]
        return [dict(self._passage(int(i)), score=float(scores[i])) for i in top if scores[i] > 0]

    def _passage(self, i: int) -> dict:
        if self.passages is not None:
            return {"id": self.passages[i]["id"], "passage": self.passages[i]["passage"]}
        self._file.seek(int(self._offsets[i]))
        return json.loads(self._file.readline())

    def retrieve(self, question: str) -> str:
        hits = self.search(question, 1)
        return hits[0]["passage"] if hits else ""

    def save(self, directory: str | Path) -> None:
        import numpy as np
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.bm25.vocab_dict = self.vocab
        self.bm25.save(str(directory / "bm25"))
        offsets = []
        with (directory / "passages.jsonl").open("wb") as f:
            for p in self.passages:
                offsets.append(f.tell())
                f.write((json.dumps({"id": p["id"], "passage": p["passage"]}, ensure_ascii=False) + "\n").encode())
        np.save(directory / "offsets.npy", np.asarray(offsets, dtype=np.int64))

    @classmethod
    def load(cls, directory: str | Path) -> "KBRetriever":
        """Passage text stays on disk; only the hits are read, so millions of passages fit."""
        import bm25s
        import numpy as np
        directory = Path(directory)
        self = cls.__new__(cls)
        self.bm25 = bm25s.BM25.load(str(directory / "bm25"), mmap=True)
        self.vocab = self.bm25.vocab_dict
        self.passages = None
        self._offsets = np.load(directory / "offsets.npy")
        self._file = (directory / "passages.jsonl").open("rb")
        return self


class ShardedKB:
    """Several KBRetriever shards queried together (IDF per shard; shards are large, so close enough)."""

    def __init__(self, shards: list[KBRetriever]):
        self.shards = shards

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        hits = [h for shard in self.shards for h in shard.search(question, top_k)]
        return sorted(hits, key=lambda h: -h["score"])[:top_k]

    @classmethod
    def load(cls, directory: str | Path) -> "ShardedKB":
        return cls([KBRetriever.load(d) for d in sorted(Path(directory).glob("shard_*"))])


def load_kb_dir(directory: str | Path):
    directory = Path(directory)
    return ShardedKB.load(directory) if any(directory.glob("shard_*")) else KBRetriever.load(directory)


class TieredRetriever:
    """Curated KB first; use Wikipedia when its best score beats ratio x the KB's best.

    Scores come from different indexes (KB adds a bigram boost), so they are compared with a
    tuned ratio, not directly (scripts/tune_kb_threshold.py, reports/kb_threshold_full.json).
    """

    def __init__(self, primary, secondary, ratio: float = 0.4, secondary_dense=None,
                 reranker=None, kb_bonus: float = 0.25, pool: int = 3):
        self.primary, self.secondary, self.ratio = primary, secondary, ratio
        # With a cross-encoder: rerank top-3 of tier-1 BM25, wiki BM25 and wiki dense together,
        # tier-1 gets +kb_bonus. F1 in-KB 57.9 -> 60.7, open-domain 16.9 -> 24.3 (reports/rerank_routing_e2e.json)
        self.reranker, self.kb_bonus, self.pool = reranker, kb_bonus, pool
        # BM25 ratio picks the tier; the e5 index (if built) picks the wiki passage:
        # same tier-1 F1, open-domain F1 15.4 -> 16.9 (reports/dense_routing_e2e.json)
        self.secondary_dense = secondary_dense
        self.passages = primary.passages

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        if self.reranker:
            return self._rerank(question, top_k)
        hits = self.primary.search(question, top_k)
        wiki = self.secondary.search(question, top_k)
        if wiki and (not hits or wiki[0]["score"] > self.ratio * hits[0]["score"]):
            return self.secondary_dense.search(question, top_k) if self.secondary_dense else wiki
        return hits

    def _rerank(self, question: str, top_k: int) -> list[dict]:
        kb = self.primary.search(question, self.pool)
        wiki = self.secondary.search(question, self.pool)
        dense = self.secondary_dense.search(question, self.pool) if self.secondary_dense else []
        cands = list({h["id"]: dict(h) for h in kb + wiki + dense}.values())
        if not cands:
            return []
        kb_ids = {h["id"] for h in kb}
        raw_scores = self.reranker.predict([(question, h["passage"]) for h in cands], batch_size=16)
        for h, s in zip(cands, raw_scores):
            raw = float(s)
            # Dynamic gated bonus: only apply kb_bonus if the candidate has plausible semantic relevance
            # (raw cross-encoder score > -2.0). This prevents low-confidence KB false positives
            # from overriding high-relevance Wikipedia passages on open-domain questions.
            bonus = self.kb_bonus if (h["id"] in kb_ids and raw > -2.0) else 0.0
            h["score"] = raw + bonus
        return sorted(cands, key=lambda h: -h["score"])[:top_k]

    def retrieve(self, question: str) -> str:
        hits = self.search(question, 1)
        return hits[0]["passage"] if hits else ""


class Encoder:
    """e5 sentence encoder (CPU unless told otherwise); query/passage prefixes as the model expects."""

    def __init__(self, model_name: str, device: str = "cpu"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name, device=device)
        self.model.max_seq_length = 256

    def queries(self, texts):
        return self.model.encode(["query: " + t for t in texts], normalize_embeddings=True, convert_to_numpy=True)

    def passages(self, texts):
        return self.model.encode(["passage: " + t for t in texts], normalize_embeddings=True, convert_to_numpy=True)


class DenseKB:
    """Cosine search over shard_*/embeddings.npy (from build_dense.py); passage text read from the BM25 shard."""

    def __init__(self, directory: str | Path, bm25_kb, encoder: Encoder | None = None):
        import numpy as np
        dirs = sorted(Path(directory).glob("shard_*")) or [Path(directory)]
        shards = bm25_kb.shards if isinstance(bm25_kb, ShardedKB) else [bm25_kb]
        self.shards = shards
        # float16 mmap (1.1 GB on disk for 1.48M x 384); a float32 copy in RAM ran a laptop out of memory
        self.emb = [np.load(d / "embeddings.npy", mmap_mode="r") for d in dirs]
        model = (dirs[0] / "dense_model.txt").read_text(encoding="utf-8").strip()
        self.encoder = encoder or Encoder(model)

    def search_vec(self, qv, top_k: int = 5) -> list[dict]:
        import numpy as np
        hits = []
        for shard, emb in zip(self.shards, self.emb):
            # numpy float16 matmul is slow: upcast in 100k-row blocks
            q32 = np.asarray(qv, dtype=np.float32)
            scores = np.concatenate([np.asarray(emb[s:s + 100_000], dtype=np.float32) @ q32
                                     for s in range(0, len(emb), 100_000)])
            top = np.argpartition(-scores, top_k - 1)[:top_k]
            hits += [dict(shard._passage(int(i)), score=float(scores[i])) for i in top]
        return sorted(hits, key=lambda h: -h["score"])[:top_k]

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        return self.search_vec(self.encoder.queries([question])[0], top_k)


def load_any(path: str | Path, wiki_dir: str | Path | None = None, ratio: float = 0.4,
             reranker: str | None = None):
    """Directory -> KBRetriever; JSON file -> legacy Retriever; with wiki_dir -> two tiers."""
    path = Path(path)
    if path.is_dir():
        primary = load_kb_dir(path)
    else:
        from retrieval_client import Retriever
        primary = Retriever.load(path)
    if wiki_dir and Path(wiki_dir).is_dir():
        wiki = load_kb_dir(wiki_dir)
        dense = None
        if any(Path(wiki_dir).glob("**/embeddings.npy")):
            try:
                dense = DenseKB(wiki_dir, wiki)
            except ImportError:  # sentence-transformers not installed: BM25 wiki only
                pass
        ce = None
        if reranker:
            from sentence_transformers import CrossEncoder
            ce = CrossEncoder(reranker, max_length=512, device="cpu")
        return TieredRetriever(primary, wiki, ratio, dense, ce)
    return primary


if __name__ == "__main__":
    kb = KBRetriever([{"id": "a", "passage": "Hà Nội là thủ đô của Việt Nam."},
                      {"id": "b", "passage": "Sông Cửu Long chảy qua Nam Bộ."}])
    assert kb.search("Thủ đô Việt Nam là gì?", 1)[0]["id"] == "a"
    assert kb.search("zzzz", 1) == []
    import tempfile
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:  # mmap keeps files open on Windows
        kb.save(Path(tmp) / "shard_0")
        loaded = load_kb_dir(tmp)
        assert loaded.search("Sông Cửu Long ở đâu?", 1)[0]["passage"].startswith("Sông Cửu Long")
        for shard in loaded.shards:
            shard._file.close()
    print("ok")
