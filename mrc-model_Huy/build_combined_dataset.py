"""Gộp ViMMRC 2.0 (trắc nghiệm) và UIT-ViQuAD2.0 (tự luận, Wikipedia) thành 3 split
train/dev/test theo tỷ lệ cố định 80/10/10, chia theo passage để không rò rỉ giữa
các split (một đoạn văn chỉ xuất hiện ở đúng một split).

Chạy:
    python build_combined_dataset.py --data-dir ../data --out-dir ../data/combined

Mỗi split ghi ra một JSON mảng "article" theo đúng schema ViMMRC gốc, ngoại trừ các
article nguồn ViQuAD không có "options"/"answers" (câu hỏi tự luận) — thay vào đó
mỗi câu hỏi có "answer_texts" (list câu trả lời tự luận). mrc_data.flatten_articles
đọc được cả hai dạng.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from huggingface_hub import hf_hub_download

VIQUAD_REPO = "taidng/UIT-ViQuAD2.0"
VIQUAD_FILES = {
    "train": "data/train-00000-of-00001.parquet",
    "validation": "data/validation-00000-of-00001.parquet",
    "test": "data/test-00000-of-00001.parquet",
}


def load_vimmrc_pool(data_dir: Path) -> list[dict]:
    """Tất cả article ViMMRC (train+dev+test gốc) thành một pool để chia lại."""
    pool = []
    for split in ("train", "dev", "test"):
        path = data_dir / f"{split}_vimmrc.json"
        with path.open(encoding="utf-8") as stream:
            pool.extend(json.load(stream))
    return pool


def load_viquad_pool() -> list[dict]:
    """Tất cả context/question ViQuAD (train+validation+test gốc), gộp theo context,
    bỏ câu hỏi không có đáp án (is_impossible) vì MRC tự luận cần câu trả lời thật."""
    import pandas as pd

    by_context: dict[str, dict] = {}
    for split, filename in VIQUAD_FILES.items():
        path = hf_hub_download(repo_id=VIQUAD_REPO, repo_type="dataset", filename=filename)
        frame = pd.read_parquet(path)
        for row in frame.itertuples(index=False):
            if row.is_impossible or row.answers is None:
                continue
            raw_texts = row.answers.get("text") if isinstance(row.answers, dict) else None
            if raw_texts is None or len(raw_texts) == 0:
                continue
            answer_texts = [text for text in raw_texts if isinstance(text, str) and text.strip()]
            if not answer_texts:
                continue
            article = by_context.setdefault(row.context, {
                "article": row.context,
                "title": row.title,
                "author": "UIT-ViQuAD2.0",
                "questions": [],
                "answer_texts_per_question": [],
            })
            article["questions"].append(row.question)
            article["answer_texts_per_question"].append(answer_texts)
    return list(by_context.values())


def split_by_passage(articles: list[dict], seed: int, ratios: tuple[float, float, float]) -> dict[str, list[dict]]:
    """Chia danh sách article theo tỷ lệ số CÂU HỎI mong muốn (không phải số article),
    bằng cách luôn gán article tiếp theo cho split đang thiếu hụt câu hỏi nhiều nhất
    so với mục tiêu — giữ mỗi article trọn vẹn trong một split duy nhất."""
    rng = random.Random(seed)
    shuffled = articles[:]
    rng.shuffle(shuffled)

    total_questions = sum(len(a["questions"]) for a in shuffled)
    targets = {name: total_questions * ratio for name, ratio in zip(("train", "dev", "test"), ratios)}
    assigned_questions = {"train": 0, "dev": 0, "test": 0}
    buckets: dict[str, list[dict]] = {"train": [], "dev": [], "test": []}

    for article in shuffled:
        deficit = {name: targets[name] - assigned_questions[name] for name in buckets}
        target_split = max(deficit, key=deficit.get)
        buckets[target_split].append(article)
        assigned_questions[target_split] += len(article["questions"])
    return buckets


def viquad_article_to_vimmrc_schema(article: dict) -> dict:
    return {
        "article": article["article"],
        "title": article["title"],
        "author": article["author"],
        "grade": None,
        "isProse": True,
        "questions": article["questions"],
        "answer_texts": article["answer_texts_per_question"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "combined")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ratios", type=float, nargs=3, default=(0.8, 0.1, 0.1), metavar=("TRAIN", "DEV", "TEST"))
    args = parser.parse_args(argv)
    if abs(sum(args.ratios) - 1.0) > 1e-6:
        raise ValueError("--ratios phải cộng lại bằng 1.0")

    vimmrc_articles = load_vimmrc_pool(args.data_dir)
    viquad_articles = [viquad_article_to_vimmrc_schema(a) for a in load_viquad_pool()]
    print(f"ViMMRC: {len(vimmrc_articles)} article, "
          f"{sum(len(a['questions']) for a in vimmrc_articles)} câu hỏi")
    print(f"ViQuAD: {len(viquad_articles)} article, "
          f"{sum(len(a['questions']) for a in viquad_articles)} câu hỏi")

    vimmrc_split = split_by_passage(vimmrc_articles, args.seed, tuple(args.ratios))
    viquad_split = split_by_passage(viquad_articles, args.seed + 1, tuple(args.ratios))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for split in ("train", "dev", "test"):
        combined = vimmrc_split[split] + viquad_split[split]
        out_path = args.out_dir / f"{split}_vimmrc.json"
        out_path.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
        n_questions = sum(len(a["questions"]) for a in combined)
        print(f"{split}: {len(combined)} article, {n_questions} câu hỏi -> {out_path}")


if __name__ == "__main__":
    main()
