"""ViMMRC 2.0 schema normalization; no machine learning dependencies."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

LETTERS = "ABCD"


def load_articles(path: str | Path) -> list[dict]:
    with Path(path).open(encoding="utf-8") as stream:
        articles = json.load(stream)
    if not isinstance(articles, list):
        raise ValueError(f"{path}: expected a JSON array of articles")
    return articles


def flatten_articles(articles: list[dict]) -> list[dict]:
    """One row per question; target is correct option text, never its letter.

    Two article shapes are accepted:
    - ViMMRC multiple-choice: has "options" (4 choices/question) and "answers" (A-D).
      Row gets "options" and "answer_letter" in addition to "answer".
    - Free-form extractive (e.g. UIT-ViQuAD2.0): has "answer_texts" (list of accepted
      answer strings per question) instead of "options"/"answers". Row has no
      "options"/"answer_letter"; ChoiceRanker and choice_accuracy skip these rows.
    """
    examples = []
    for article_index, article in enumerate(articles):
        if not isinstance(article, dict):
            raise ValueError(f"article {article_index}: expected object")
        passage = article.get("article")
        questions = article.get("questions")
        if not isinstance(passage, str) or not passage.strip():
            raise ValueError(f"article {article_index}: missing article text")
        if not isinstance(questions, list):
            raise ValueError(f"article {article_index}: questions must be a list")

        if "answer_texts" in article:
            answer_texts = article.get("answer_texts")
            if not isinstance(answer_texts, list) or len(answer_texts) != len(questions):
                raise ValueError(f"article {article_index}: answer_texts must match questions length")
            for question_index, (question, candidates) in enumerate(zip(questions, answer_texts)):
                location = f"article {article_index}, question {question_index}"
                if not isinstance(question, str) or not question.strip():
                    raise ValueError(f"{location}: missing question")
                if not isinstance(candidates, list) or not candidates or any(
                    not isinstance(candidate, str) or not candidate.strip() for candidate in candidates
                ):
                    raise ValueError(f"{location}: expected at least one nonempty answer_texts string")
                examples.append({
                    "id": f"{article_index}:{question_index}",
                    "passage": passage.strip(),
                    "question": question.strip(),
                    "answer": candidates[0].strip(),
                })
            continue

        options = article.get("options")
        answers = article.get("answers")
        if any(not isinstance(x, list) for x in (options, answers)):
            raise ValueError(f"article {article_index}: questions/options/answers must be lists")
        if not (len(questions) == len(options) == len(answers)):
            raise ValueError(f"article {article_index}: question/option/answer lengths differ")
        for question_index, (question, choices, label) in enumerate(zip(questions, options, answers)):
            location = f"article {article_index}, question {question_index}"
            if not isinstance(question, str) or not question.strip():
                raise ValueError(f"{location}: missing question")
            if not isinstance(choices, list) or len(choices) != 4 or any(
                not isinstance(choice, str) for choice in choices
            ):
                raise ValueError(f"{location}: expected four option strings")
            if not isinstance(label, str) or label.strip().upper() not in set(LETTERS):
                raise ValueError(f"{location}: expected answer A, B, C, or D")
            correct = label.strip().upper()
            if not choices[LETTERS.index(correct)].strip():
                raise ValueError(f"{location}: correct option is empty")
            examples.append({
                "id": f"{article_index}:{question_index}",
                "passage": passage.strip(),
                "question": question.strip(),
                "options": [choice.strip() for choice in choices],
                "answer_letter": correct,
                "answer": choices[LETTERS.index(correct)].strip(),
            })
    return examples


def load_examples(path: str | Path) -> list[dict]:
    return flatten_articles(load_articles(path))


def build_input(question: str, passage: str) -> str:
    if not question.strip() or not passage.strip():
        raise ValueError("question and passage must be nonempty")
    return f"Trả lời câu hỏi dựa trên đoạn văn. Câu hỏi: {question.strip()} Đoạn văn: {passage.strip()}"


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower()
    text = "".join(" " if unicodedata.category(char).startswith("P") else char for char in text)
    return re.sub(r"\s+", " ", text).strip()


def exact_match(prediction: str, reference: str) -> float:
    return float(normalize_text(prediction) == normalize_text(reference))


def token_f1(prediction: str, reference: str) -> float:
    predicted = normalize_text(prediction).split()
    expected = normalize_text(reference).split()
    if not predicted or not expected:
        return float(predicted == expected)
    common = sum((Counter(predicted) & Counter(expected)).values())
    return 2 * common / (len(predicted) + len(expected)) if common else 0.0


def evaluate_predictions(predictions: list[str], examples: list[dict]) -> dict[str, float]:
    if len(predictions) != len(examples) or not examples:
        raise ValueError("predictions and nonempty examples must have the same length")
    count = len(examples)
    result = {
        "exact_match": sum(exact_match(pred, row["answer"]) for pred, row in zip(predictions, examples)) / count,
        "token_f1": sum(token_f1(pred, row["answer"]) for pred, row in zip(predictions, examples)) / count,
    }
    if all("options" in row for row in examples):
        correct_choices = 0
        for prediction, row in zip(predictions, examples):
            scores = [token_f1(prediction, option) for option in row["options"]]
            if max(scores) > 0 and scores.index(max(scores)) == LETTERS.index(row["answer_letter"]):
                correct_choices += 1
        result["choice_accuracy"] = correct_choices / count
    return result
