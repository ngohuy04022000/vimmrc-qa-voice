"""Measure a context-selection proxy with the real tokenizer, not model accuracy."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mrc-model_Huy"))
from context_selection import encode_input
from mrc_data import build_input, load_examples, normalize_text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/dev_vimmrc.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/context_dev.json")
    parser.add_argument("--tokenizer", default="VietAI/vit5-base")
    parser.add_argument("--max-input-tokens", type=int, default=512)
    args = parser.parse_args()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True)
    rows = load_examples(args.data)
    metrics = {strategy: {"answer_text_visible": 0, "total_encoded_tokens": 0}
               for strategy in ("head", "question_chunks")}
    long_count = present_count = 0
    for row in rows:
        target = normalize_text(row["answer"])
        present_count += target in normalize_text(row["passage"])
        long_count += len(tokenizer(build_input(row["question"], row["passage"]),
                                   truncation=False)["input_ids"]) > args.max_input_tokens
        for strategy in metrics:
            ids = encode_input(row["question"], row["passage"], tokenizer,
                               args.max_input_tokens, strategy)["input_ids"]
            visible = normalize_text(tokenizer.decode(ids, skip_special_tokens=True))
            metrics[strategy]["answer_text_visible"] += target in visible
            metrics[strategy]["total_encoded_tokens"] += len(ids)
    report = {"questions": len(rows), "over_budget_inputs": long_count,
              "answer_text_present_in_full_passage": present_count,
              "max_input_tokens": args.max_input_tokens, "tokenizer": args.tokenizer,
              "dataset_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
              "strategies": metrics,
              "limitation": "Exact answer-text visibility in input is a diagnostic proxy, not answer accuracy. Some answers are abstractive. Selector never sees targets; no model inference was run."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
