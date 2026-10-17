import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_combined_dataset import split_by_passage


def _fake_articles(n: int, questions_per_article: int = 5) -> list[dict]:
    return [
        {"article": f"passage {i}", "questions": [f"q{i}-{j}" for j in range(questions_per_article)]}
        for i in range(n)
    ]


def test_split_by_passage_keeps_each_article_in_exactly_one_split():
    articles = _fake_articles(40)
    buckets = split_by_passage(articles, seed=0, ratios=(0.8, 0.1, 0.1))
    all_passages = [a["article"] for name in buckets for a in buckets[name]]
    assert sorted(all_passages) == sorted(a["article"] for a in articles)
    assert len(set(all_passages)) == len(all_passages)  # no passage duplicated across splits


def test_split_by_passage_question_ratio_is_close_to_target():
    articles = _fake_articles(200, questions_per_article=3)
    buckets = split_by_passage(articles, seed=1, ratios=(0.8, 0.1, 0.1))
    total = sum(len(a["questions"]) for a in articles)
    counts = {name: sum(len(a["questions"]) for a in rows) for name, rows in buckets.items()}
    assert counts["train"] / total == pytest.approx(0.8, abs=0.05)
    assert counts["dev"] / total == pytest.approx(0.1, abs=0.05)
    assert counts["test"] / total == pytest.approx(0.1, abs=0.05)


def test_split_by_passage_is_deterministic_for_same_seed():
    articles = _fake_articles(30)
    first = split_by_passage(articles, seed=7, ratios=(0.8, 0.1, 0.1))
    second = split_by_passage(articles, seed=7, ratios=(0.8, 0.1, 0.1))
    assert [a["article"] for a in first["train"]] == [a["article"] for a in second["train"]]
