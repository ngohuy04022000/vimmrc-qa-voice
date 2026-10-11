"""Small dependency-free Vietnamese passage retriever using BM25."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import re
import unicodedata


TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)
QUERY_STOPWORDS = frozenset({
    "ai", "bao", "cho", "có", "của", "đã", "đâu", "được", "gì", "hay",
    "khi", "là", "một", "nào", "như", "những", "ở", "sao", "thế", "trong",
    "từ", "và", "với",
})
BASELINE_CONFIG = {"k1": 1.5, "b": 0.75, "query_stopwords": False, "bigram_boost": 0.0}
OPTIMIZED_CONFIG = {"k1": 2.1, "b": 1.0, "query_stopwords": True, "bigram_boost": 0.4}
TUNED_CONFIG = OPTIMIZED_CONFIG


def tokenize(text: str) -> list[str]:
    """Normalize Unicode and split into case-insensitive word tokens."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return TOKEN_PATTERN.findall(unicodedata.normalize("NFC", text).casefold())


class Retriever:
    """Rank passages with BM25; expose plain text to downstream MRC."""

    def __init__(self, passages: list[dict[str, str]], k1: float = 2.1, b: float = 1.0,
                 query_stopwords: bool = True, bigram_boost: float = 0.4):
        if not isinstance(passages, list):
            raise TypeError("passages must be a list")
        if not (isinstance(k1, (int, float)) and math.isfinite(k1) and k1 > 0):
            raise ValueError("k1 must be a finite positive number")
        if not (isinstance(b, (int, float)) and math.isfinite(b) and 0 <= b <= 1):
            raise ValueError("b must be between 0 and 1")
        if not isinstance(query_stopwords, bool):
            raise ValueError("query_stopwords must be a boolean")
        if not (isinstance(bigram_boost, (int, float)) and math.isfinite(bigram_boost) and bigram_boost >= 0):
            raise ValueError("bigram_boost must be a finite nonnegative number")

        self.passages: list[dict[str, str]] = []
        seen_ids: set[str] = set()
        for record in passages:
            if not isinstance(record, dict):
                raise ValueError("each passage must be an object")
            passage_id, passage = record.get("id"), record.get("passage")
            if not isinstance(passage_id, str) or not passage_id.strip():
                raise ValueError("passage id must be a nonempty string")
            if not isinstance(passage, str) or not passage.strip():
                raise ValueError("passage must be a nonempty string")
            if not tokenize(passage):
                raise ValueError("passage must contain at least one searchable token")
            if passage_id in seen_ids:
                raise ValueError(f"duplicate passage id: {passage_id}")
            seen_ids.add(passage_id)
            self.passages.append({"id": passage_id, "passage": passage})

        self.k1 = float(k1)
        self.b = float(b)
        self.query_stopwords = query_stopwords
        self.bigram_boost = float(bigram_boost)
        token_lists = [tokenize(p["passage"]) for p in self.passages]
        self._counts = [Counter(tokens) for tokens in token_lists]
        self._lengths = [sum(counts.values()) for counts in self._counts]
        self._avg_length = sum(self._lengths) / len(self._lengths) if self._lengths else 0.0
        self._length_norm = [self.k1 * (1 - self.b + self.b * length / self._avg_length)
                             for length in self._lengths]
        self._postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        self._bigram_postings: dict[tuple[str, str], list[tuple[int, int]]] = defaultdict(list)
        for index, (tokens, counts) in enumerate(zip(token_lists, self._counts)):
            for term, frequency in counts.items():
                self._postings[term].append((index, frequency))
            if self.bigram_boost:
                for pair, frequency in Counter(zip(tokens, tokens[1:])).items():
                    self._bigram_postings[pair].append((index, frequency))

    def search(self, question: str, top_k: int = 5) -> list[dict[str, str | float]]:
        """Return ranked hits with id, passage and BM25 score; no overlap gives []."""
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
            raise ValueError("top_k must be a positive integer")
        tokens = tokenize(question)
        if not tokens or not self.passages:
            return []
        terms = {term for term in tokens if term not in QUERY_STOPWORDS} if self.query_stopwords else set(tokens)
        if not terms:
            terms = set(tokens)
        n = len(self.passages)
        scores: dict[int, float] = defaultdict(float)
        for term in terms:
            postings = self._postings.get(term, ())
            if not postings:
                continue
            idf = math.log1p((n - len(postings) + 0.5) / (len(postings) + 0.5))
            for index, frequency in postings:
                scores[index] += idf * frequency * (self.k1 + 1) / (frequency + self._length_norm[index])
        if self.bigram_boost:
            for pair in set(zip(tokens, tokens[1:])):
                postings = self._bigram_postings.get(pair, ())
                if not postings:
                    continue
                idf = math.log1p((n - len(postings) + 0.5) / (len(postings) + 0.5))
                for index, frequency in postings:
                    scores[index] += self.bigram_boost * idf * frequency * (self.k1 + 1) / (frequency + self._length_norm[index])
        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        return [
            {"id": self.passages[index]["id"], "passage": self.passages[index]["passage"], "score": score}
            for index, score in ranked[:top_k]
        ]

    def retrieve(self, question: str) -> str:
        """Return the best passage as plain text, or empty text if none matches."""
        hits = self.search(question, top_k=1)
        return str(hits[0]["passage"]) if hits else ""

    def save(self, path: str | Path) -> None:
        """Save the corpus and BM25 parameters as UTF-8 JSON."""
        payload = {"passages": self.passages, "k1": self.k1, "b": self.b,
                   "query_stopwords": self.query_stopwords, "bigram_boost": self.bigram_boost}
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> Retriever:
        """Load a corpus saved by save()."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or "passages" not in payload:
            raise ValueError("index JSON must contain passages")
        return cls(payload["passages"], k1=payload.get("k1", 1.5), b=payload.get("b", 0.75),
                   query_stopwords=payload.get("query_stopwords", False),
                   bigram_boost=payload.get("bigram_boost", 0.0))
