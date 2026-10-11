"""Question-only context selection shared by training and inference.

This is a lexical evidence heuristic, not a learned reader. Gold answers and
multiple-choice options never enter this module.
"""
from collections import Counter
from functools import lru_cache
import math

from mrc_data import build_input, normalize_text

STOP_WORDS = frozenset("là gì ai ở đâu nào có của và được theo trong một những các với cho đã thì mà về hãy em bài văn tác giả câu chuyện đoạn".split())


@lru_cache(maxsize=128)
def _chunks(passage, tokenizer, width):
    ids = tokenizer(passage, add_special_tokens=False, truncation=False)["input_ids"]
    return tuple(tokenizer.decode(ids[start:start + width], skip_special_tokens=True)
                 for start in range(0, len(ids), width))


def select_context(question, passage, tokenizer, max_input_tokens=512, strategy="head"):
    """Return context text, selecting token chunks for long passages if requested."""
    build_input(question, passage)
    if strategy not in {"head", "question_chunks"}:
        raise ValueError("context strategy must be head or question_chunks")
    if not isinstance(max_input_tokens, int) or max_input_tokens < 32:
        raise ValueError("max_input_tokens must be an integer >= 32")
    if strategy == "head":
        return passage
    full = build_input(question, passage)
    if len(tokenizer(full, truncation=False)["input_ids"]) <= max_input_tokens:
        return passage
    prefix = build_input(question, " … ")
    budget = max_input_tokens - len(tokenizer(prefix)["input_ids"]) - 8
    if budget < 16:
        raise ValueError("Question leaves too little token budget for passage evidence")
    chunks = _chunks(passage, tokenizer, min(96, budget))
    terms = set(normalize_text(question).split()) - STOP_WORDS
    if not terms:
        return passage
    counts = [Counter(normalize_text(chunk).split()) for chunk in chunks]
    df = Counter(term for count in counts for term in count)
    scores = [sum(math.log1p(len(chunks) / (1 + df[term])) * min(count[term], 3)
                  for term in terms) / math.sqrt(max(1, sum(count.values())))
              for count in counts]
    if not any(scores):
        return passage
    ranking = sorted(range(len(chunks)), key=lambda index: (-scores[index], index))
    selected = []
    for index in ranking:
        trial = sorted(selected + [index])
        candidate = "\n...\n".join(chunks[item] for item in trial)
        if len(tokenizer(build_input(question, candidate))["input_ids"]) <= max_input_tokens:
            selected = trial
    if not selected:
        # A single chunk can exceed the conservative estimate for unusual tokenizers.
        return chunks[ranking[0]]
    return "\n...\n".join(chunks[index] for index in selected)


def encode_input(question, passage, tokenizer, max_input_tokens=512, strategy="head", **kwargs):
    context = select_context(question, passage, tokenizer, max_input_tokens, strategy)
    return tokenizer(build_input(question, context), truncation=True,
                     max_length=max_input_tokens, **kwargs)
