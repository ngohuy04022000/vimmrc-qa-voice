"""Small supervised four-choice ViMMRC ranker. Requires supplied answer options."""

from __future__ import annotations

import re
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from mrc_data import LETTERS, normalize_text


def _tokens(text: str) -> set[str]:
    return set(normalize_text(text).split())


def _sentences(passage: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+|\n+", passage)
            if sentence.strip()] or [passage]


def _overlap(option: set[str], context: set[str]) -> float:
    return len(option & context) / len(option) if option else 0.0


def validate_options(options: list[str]) -> None:
    if not isinstance(options, (list, tuple)) or len(options) != 4 or any(
        not isinstance(option, str) for option in options
    ):
        raise ValueError("options must contain exactly four strings in A-D order")
    if not any(option.strip() for option in options):
        raise ValueError("at least one option must be nonempty")


def lexical_baseline(question: str, passage: str, options: list[str]) -> dict:
    """Untrained comparator: choose option with most words present in passage."""
    validate_options(options)
    if not question.strip() or not passage.strip():
        raise ValueError("question and passage must be nonempty")
    passage_tokens = _tokens(passage)
    scores = [_overlap(_tokens(option), passage_tokens) if option.strip() else -1.0
              for option in options]
    index = int(np.argmax(scores))
    return {"label": LETTERS[index], "answer": options[index].strip(),
            "scores": dict(zip(LETTERS, scores))}


class ChoiceRanker:
    """TF-IDF similarity plus lexical evidence, fitted with logistic regression."""

    FEATURE_NAMES = (
        "tfidf_passage", "tfidf_query_sentence", "tfidf_question",
        "word_passage", "word_query_sentence", "max_sentence_word_overlap",
        "exact_phrase_in_passage", "option_token_count", "option_char_length",
        "word_question", "relative_option_length",
    )

    def __init__(self, *, c: float = 1.0, max_features: int = 60000):
        self.c = c
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb", ngram_range=(2, 4), min_df=2,
            max_features=max_features, sublinear_tf=True, dtype=np.float32,
        )
        self.model = make_pipeline(
            StandardScaler(), LogisticRegression(C=c, max_iter=1000, class_weight="balanced")
        )
        self.fitted = False

    def _features(self, examples: list[dict]) -> np.ndarray:
        questions, options, passages, selected = [], [], [], []
        lexical = []
        passage_cache = {}
        for row in examples:
            question, passage, choices = row["question"], row["passage"], row["options"]
            validate_options(choices)
            if not question.strip() or not passage.strip():
                raise ValueError("question and passage must be nonempty")
            if passage not in passage_cache:
                sentences = _sentences(passage)
                passage_cache[passage] = (_tokens(passage), sentences,
                                          [_tokens(sentence) for sentence in sentences])
            passage_words, sentences, sentence_words = passage_cache[passage]
            question_words = _tokens(question)
            best_sentence = max(range(len(sentences)),
                                key=lambda i: len(question_words & sentence_words[i]))
            selected_text = sentences[best_sentence]
            selected_words = sentence_words[best_sentence]
            lengths = [len(_tokens(choice)) for choice in choices if choice.strip()]
            mean_length = sum(lengths) / len(lengths)
            normalized_passage = normalize_text(passage)
            for option in choices:
                words = _tokens(option)
                questions.append(question)
                passages.append(passage)
                selected.append(selected_text)
                options.append(option if option.strip() else " ")
                lexical.append([
                    _overlap(words, passage_words),
                    _overlap(words, selected_words),
                    max(_overlap(words, terms) for terms in sentence_words),
                    float(bool(words) and normalize_text(option) in normalized_passage),
                    np.log1p(len(words)),
                    np.log1p(len(option.strip())),
                    _overlap(words, question_words),
                    len(words) / mean_length if mean_length else 0.0,
                ])

        # Repeated passages are transformed once, which matters for long articles.
        unique_passages = list(dict.fromkeys(passages))
        passage_lookup = {passage: index for index, passage in enumerate(unique_passages)}
        passage_matrix = self.vectorizer.transform(unique_passages)[
            [passage_lookup[passage] for passage in passages]
        ]
        option_matrix = self.vectorizer.transform(options)
        query_matrix = self.vectorizer.transform(questions)
        selected_matrix = self.vectorizer.transform(selected)

        def cosine(left, right):
            return np.asarray(left.multiply(right).sum(axis=1)).ravel()

        return np.column_stack((
            cosine(passage_matrix, option_matrix),
            cosine(selected_matrix, option_matrix),
            cosine(query_matrix, option_matrix),
            np.asarray(lexical, dtype=np.float32),
        )).astype(np.float32)

    def fit(self, examples: list[dict]) -> "ChoiceRanker":
        if not examples:
            raise ValueError("training examples must be nonempty")
        texts = [row["question"] for row in examples]
        texts += [row["passage"] for row in examples]
        texts += [option for row in examples for option in row["options"]]
        self.vectorizer.fit(texts)
        features = self._features(examples)
        labels = np.asarray([
            index == LETTERS.index(row["answer_letter"])
            for row in examples for index in range(4)
        ], dtype=np.int8)
        self.model.fit(features, labels)
        self.fitted = True
        return self

    def predict_many(self, examples: list[dict]) -> list[dict]:
        if not self.fitted:
            raise RuntimeError("ranker is not fitted")
        features = self._features(examples)
        probabilities = self.model.predict_proba(features)[:, 1].reshape(-1, 4)
        predictions = []
        for row, scores in zip(examples, probabilities):
            scores = [float(score) if option.strip() else float("-inf")
                      for score, option in zip(scores, row["options"])]
            index = int(np.argmax(scores))
            predictions.append({
                "label": LETTERS[index], "answer": row["options"][index].strip(),
                "scores": dict(zip(LETTERS, scores)),
            })
        return predictions

    def predict(self, question: str, passage: str, options: list[str]) -> dict:
        return self.predict_many([{"question": question, "passage": passage,
                                   "options": options}])[0]

    def answer_question(self, question: str, passage: str, options: list[str]) -> str:
        return self.predict(question, passage, options)["answer"]

    def save(self, path: str | Path) -> None:
        if not self.fitted:
            raise RuntimeError("ranker is not fitted")
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path / "ranker.joblib")

    @classmethod
    def load(cls, path: str | Path) -> "ChoiceRanker":
        """Only load artifacts you created or trust; joblib uses pickle."""
        path = Path(path)
        artifact = joblib.load(path / "ranker.joblib")
        if not isinstance(artifact, cls) or not artifact.fitted:
            raise ValueError("invalid ChoiceRanker artifact")
        return artifact
