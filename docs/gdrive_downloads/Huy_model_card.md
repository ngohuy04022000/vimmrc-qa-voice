# ViMMRC four-choice TF-IDF ranker

This CPU model selects among exactly four supplied options. It cannot answer free-form questions without options. Training used only `train_vimmrc.json`; C was chosen using an article-group holdout within train. The separate dev split was evaluated once after selection. The test split was not read.

- Seed: 42; selected C: 10.0
- Inner holdout accuracy: 0.5394
- Dev accuracy: ranker 0.5195; lexical baseline 0.4362; seeded random 0.2518

Features: character TF-IDF similarities between options and passage, question, or question-overlap sentence; token overlap and option length. A logistic regression scores each option; empty choices are excluded. The random nominal chance is 25%, but blank distractors make the seeded random result a more relevant comparator.

This artifact is a joblib pickle. Load only a trusted locally generated checkpoint.
