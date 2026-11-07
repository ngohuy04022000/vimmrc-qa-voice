"""Vector-search retriever dùng embedding tiếng Việt (Ollama qwen3-embed-vi) thay BM25.

Cùng hợp đồng với Retriever (retrieval_client.py): .search(question, top_k) ->
list[{id, passage, score}], nên QAPipeline dùng được cả hai không cần đổi code.
Không kế thừa Retriever vì cách tính điểm hoàn toàn khác (cosine similarity thay
BM25); giữ 2 lớp độc lập để BM25 vẫn chạy không cần Ollama.

Embed toàn bộ tầng 1 (5.879 đoạn) mất vài phút trên CPU; lưu lại bằng save()
để không phải embed lại mỗi lần load.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import requests

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "qwen3-embed-vi:latest"


def embed_texts(texts: list[str], *, batch_size: int = 16, timeout: int = 60) -> np.ndarray:
    """Gọi Ollama embed theo batch nhỏ (model embedding không hỗ trợ batch lớn ổn định
    qua HTTP); trả về ma trận (n, dim) đã L2-normalize để dùng dot product = cosine."""
    if not texts:
        return np.zeros((0, 0), dtype=np.float32)
    vectors = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        resp = requests.post(OLLAMA_URL, json={"model": EMBED_MODEL, "input": batch}, timeout=timeout)
        resp.raise_for_status()
        vectors.extend(resp.json()["embeddings"])
    matrix = np.array(vectors, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


_sentence_transformer_cache: dict[str, object] = {}


def embed_texts_sentence_transformers(texts: list[str], *, model_name: str = "intfloat/multilingual-e5-base") -> np.ndarray:
    """Embed bằng sentence-transformers chạy local (không qua Ollama) — để so sánh với
    qwen3-embed-vi khi cần model embedding đa ngôn ngữ khác. multilingual-e5-base khuyến
    nghị tiền tố "query: "/"passage: " cho câu hỏi/văn bản, cải thiện recall đáng kể."""
    if not texts:
        return np.zeros((0, 0), dtype=np.float32)
    if model_name not in _sentence_transformer_cache:
        from sentence_transformers import SentenceTransformer
        _sentence_transformer_cache[model_name] = SentenceTransformer(model_name)
    model = _sentence_transformer_cache[model_name]
    matrix = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(matrix, dtype=np.float32)


class EmbeddingRetriever:
    """Rank passages bằng cosine similarity trên embedding.

    backend="ollama" (mặc định): qwen3-embed-vi qua Ollama server local.
    backend="sentence_transformers": model đa ngôn ngữ chạy local (ví dụ
    intfloat/multilingual-e5-base), tự thêm tiền tố "query: "/"passage: " theo
    chuẩn họ model e5 — bỏ qua nếu dùng model khác không cần tiền tố này."""

    def __init__(self, passages: list[dict[str, str]], embeddings: np.ndarray | None = None,
                 backend: str = "ollama", model_name: str | None = None):
        if not isinstance(passages, list) or not all(
            isinstance(p, dict) and "id" in p and "passage" in p for p in passages
        ):
            raise ValueError("passages must be a list of {id, passage} dicts")
        if backend not in ("ollama", "sentence_transformers"):
            raise ValueError("backend must be 'ollama' or 'sentence_transformers'")
        self.passages = passages
        self.backend = backend
        self.model_name = model_name or ("intfloat/multilingual-e5-base" if backend == "sentence_transformers" else EMBED_MODEL)
        self.embeddings = embeddings if embeddings is not None else self._embed(
            [self._passage_text(p["passage"]) for p in passages]
        )
        if self.embeddings.shape[0] != len(passages):
            raise ValueError("embeddings row count must match passages count")

    def _passage_text(self, text: str) -> str:
        return f"passage: {text}" if self.backend == "sentence_transformers" else text

    def _query_text(self, text: str) -> str:
        return f"query: {text}" if self.backend == "sentence_transformers" else text

    def _embed(self, texts: list[str]) -> np.ndarray:
        if self.backend == "sentence_transformers":
            return embed_texts_sentence_transformers(texts, model_name=self.model_name)
        return embed_texts(texts)

    def search(self, question: str, top_k: int = 5) -> list[dict[str, str | float]]:
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
            raise ValueError("top_k must be a positive integer")
        if not self.passages:
            return []
        query_vec = self._embed([self._query_text(question)])[0]
        scores = self.embeddings @ query_vec  # cosine similarity (đã normalize)
        order = np.argsort(-scores)[:top_k]
        return [
            {"id": self.passages[i]["id"], "passage": self.passages[i]["passage"], "score": float(scores[i])}
            for i in order
        ]

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        np.savez(target, embeddings=self.embeddings,
                 passages=json.dumps(self.passages, ensure_ascii=False),
                 backend=self.backend, model_name=self.model_name)

    @classmethod
    def load(cls, path: str | Path) -> EmbeddingRetriever:
        data = np.load(path, allow_pickle=False)
        passages = json.loads(str(data["passages"]))
        backend = str(data["backend"]) if "backend" in data else "ollama"
        model_name = str(data["model_name"]) if "model_name" in data else None
        return cls(passages, embeddings=data["embeddings"], backend=backend, model_name=model_name)
