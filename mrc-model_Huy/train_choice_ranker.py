"""Train and evaluate a CPU-light four-choice ranker; never reads test split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.model_selection import GroupShuffleSplit

from choice_ranker import ChoiceRanker, lexical_baseline
from mrc_data import load_examples


def accuracy(predictions: list[dict], examples: list[dict]) -> float:
    return sum(pred["label"] == row["answer_letter"]
               for pred, row in zip(predictions, examples)) / len(examples)


def group_holdout(examples: list[dict], seed: int = 42) -> tuple[list[dict], list[dict]]:
    """Split by article ID, so sibling questions never cross the boundary."""
    groups = [row["id"].split(":", 1)[0] for row in examples]
    train_index, valid_index = next(GroupShuffleSplit(
        n_splits=1, test_size=0.2, random_state=seed
    ).split(examples, groups=groups))
    return ([examples[index] for index in train_index],
            [examples[index] for index in valid_index])


def run(train_path: Path, dev_path: Path, output_dir: Path, seed: int = 42) -> dict:
    if train_path.resolve() == dev_path.resolve():
        raise ValueError("train and dev paths must be different")
    train = load_examples(train_path)
    dev = load_examples(dev_path)
    train_articles = {row["passage"] for row in train}
    if train_articles & {row["passage"] for row in dev}:
        raise ValueError("train/dev passages overlap")

    inner_train, inner_valid = group_holdout(train, seed)
    assert not {row["passage"] for row in inner_train} & {
        row["passage"] for row in inner_valid
    }
    tuning = []
    for c in (0.1, 1.0, 10.0):
        ranker = ChoiceRanker(c=c).fit(inner_train)
        score = accuracy(ranker.predict_many(inner_valid), inner_valid)
        tuning.append({"c": c, "inner_valid_accuracy": score})
        print(f"C={c:g}: inner train article holdout accuracy={score:.4f}", flush=True)
    best = max(tuning, key=lambda item: item["inner_valid_accuracy"])

    ranker = ChoiceRanker(c=best["c"]).fit(train)
    learned_predictions = ranker.predict_many(dev)
    lexical_predictions = [lexical_baseline(row["question"], row["passage"], row["options"])
                           for row in dev]
    rng = np.random.default_rng(seed)
    random_labels = ["ABCD"[rng.choice([index for index, option in enumerate(row["options"])
                                        if option.strip()])] for row in dev]
    report = {
        "task": "four-choice answer selection; options required",
        "train_examples": len(train), "inner_train_examples": len(inner_train),
        "inner_valid_examples": len(inner_valid), "dev_examples": len(dev),
        "seed": seed, "tuning": tuning, "selected_c": best["c"],
        "inner_valid_accuracy": best["inner_valid_accuracy"],
        "dev_ranker_accuracy": accuracy(learned_predictions, dev),
        "dev_lexical_accuracy": accuracy(lexical_predictions, dev),
        "dev_seeded_random_accuracy": sum(a == row["answer_letter"]
                                          for a, row in zip(random_labels, dev)) / len(dev),
        "nominal_random_chance": 0.25,
        "test_evaluated": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    ranker.save(output_dir)
    (output_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "model_card.md").write_text(
        "# ViMMRC four-choice TF-IDF ranker\n\n"
        "This CPU model selects among exactly four supplied options. It cannot answer free-form "
        "questions without options. Training used only `train_vimmrc.json`; C was chosen "
        "using an article-group holdout within train. The separate dev split was evaluated "
        "once after selection. The test split was not read.\n\n"
        f"- Seed: {seed}; selected C: {best['c']}\n"
        f"- Inner holdout accuracy: {best['inner_valid_accuracy']:.4f}\n"
        f"- Dev accuracy: ranker {report['dev_ranker_accuracy']:.4f}; "
        f"lexical baseline {report['dev_lexical_accuracy']:.4f}; "
        f"seeded random {report['dev_seeded_random_accuracy']:.4f}\n\n"
        "Features: character TF-IDF similarities between options and passage, question, "
        "or question-overlap sentence; token overlap and option length. A logistic regression "
        "scores each option; empty choices are excluded. The random nominal chance is 25%, "
        "but blank distractors make the seeded random result a more relevant comparator.\n\n"
        "This artifact is a joblib pickle. Load only a trusted locally generated checkpoint.\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    data_dir = Path(__file__).resolve().parents[1] / "data"
    parser.add_argument("--train", type=Path, default=data_dir / "train_vimmrc.json")
    parser.add_argument("--dev", type=Path, default=data_dir / "dev_vimmrc.json")
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parent / "checkpoints" / "choice_ranker")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)
    run(args.train, args.dev, args.output_dir, args.seed)


if __name__ == "__main__":
    main()
