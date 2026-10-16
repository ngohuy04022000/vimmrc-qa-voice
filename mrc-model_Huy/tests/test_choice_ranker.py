import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from choice_ranker import ChoiceRanker, lexical_baseline, validate_options
from mrc_data import flatten_articles
from train_choice_ranker import accuracy, group_holdout

ROOT = Path(__file__).resolve().parents[1]


def synthetic_articles():
    base = json.loads((ROOT / "examples" / "sample_vimmrc.json").read_text(encoding="utf-8"))[0]
    return [{**base, "article": f"Bài {index}. " + base["article"]}
            for index in range(8)]


def test_articlegroup_holdout_has_no_sibling_leakage():
    examples = flatten_articles(synthetic_articles())
    train, valid = group_holdout(examples, seed=42)
    assert train and valid
    assert {row["passage"] for row in train}.isdisjoint(
        {row["passage"] for row in valid})
    assert len(train) + len(valid) == len(examples)


def test_trained_ranker_persistence_and_empty_options(tmp_path):
    examples = flatten_articles(synthetic_articles())
    ranker = ChoiceRanker(max_features=1000).fit(examples)
    example = examples[0]
    before = ranker.predict(example["question"], example["passage"], example["options"])
    ranker.save(tmp_path)
    restored = ChoiceRanker.load(tmp_path)
    after = restored.predict(example["question"], example["passage"], example["options"])
    assert before["label"] == after["label"]
    assert before["scores"] == pytest.approx(after["scores"])
    assert restored.answer_question(example["question"], example["passage"],
                                    example["options"]) == after["answer"]
    blank = restored.predict(example["question"], example["passage"],
                             ["", "Hà Nội", "", "Cần Thơ"])
    assert blank["label"] in {"B", "D"}
    assert blank["scores"]["A"] == float("-inf")
    assert accuracy([before], [example]) in {0.0, 1.0}


def test_option_validation_and_baseline():
    with pytest.raises(ValueError, match="exactly four"):
        validate_options(["a", "b"])
    with pytest.raises(ValueError, match="nonempty"):
        validate_options(["", "", "", ""])
    result = lexical_baseline("Thủ đô?", "Hà Nội là thủ đô.",
                              ["", "Hà Nội", "Đà Nẵng", "Cần Thơ"])
    assert result["label"] == "B"


def test_training_protocol_reads_only_train_and_dev(monkeypatch, tmp_path):
    import train_choice_ranker

    train = flatten_articles(synthetic_articles())
    dev_article = synthetic_articles()[0]
    dev_article["article"] = "Bài dev riêng. " + dev_article["article"]
    dev = flatten_articles([dev_article])
    read_paths = []

    def fake_load(path):
        read_paths.append(path.name)
        if path.name == "train_vimmrc.json":
            return train
        if path.name == "dev_vimmrc.json":
            return dev
        raise AssertionError("Unexpected dataset read")

    monkeypatch.setattr(train_choice_ranker, "load_examples", fake_load)
    report = train_choice_ranker.run(tmp_path / "train_vimmrc.json",
                                     tmp_path / "dev_vimmrc.json",
                                     tmp_path / "model", seed=42)
    assert read_paths == ["train_vimmrc.json", "dev_vimmrc.json"]
    assert report["test_evaluated"] is False
    assert (tmp_path / "model" / "ranker.joblib").exists()
