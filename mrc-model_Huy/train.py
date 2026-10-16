"""Fine-tune ViT5 on the licensed ViMMRC splits. Requires GPU and data access."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

from mrc_data import build_input, evaluate_predictions, load_articles, load_examples
from context_selection import encode_input


def validate_split_disjoint(paths: dict[str, Path]) -> None:
    """Check article-level leakage before any model download or training."""
    fingerprints = {}
    for name, path in paths.items():
        fingerprints[name] = {
            hashlib.sha256(article["article"].encode("utf-8")).hexdigest()
            for article in load_articles(path)
        }
    for left, right in (("train", "dev"), ("train", "test"), ("dev", "test")):
        if fingerprints[left] & fingerprints[right]:
            raise ValueError(f"Article overlap between {left} and {right} splits")


class EncodedExamples:
    def __init__(self, examples: list[dict], tokenizer, max_input_tokens: int,
                 max_target_tokens: int, context_strategy: str = "head"):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_input_tokens = max_input_tokens
        self.max_target_tokens = max_target_tokens
        self.context_strategy = context_strategy

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, index):
        row = self.examples[index]
        inputs = encode_input(row["question"], row["passage"], self.tokenizer,
                              self.max_input_tokens, self.context_strategy)
        labels = self.tokenizer(
            text_target=row["answer"], truncation=True, max_length=self.max_target_tokens,
        )
        inputs["labels"] = labels["input_ids"]
        inputs.pop("token_type_ids", None)
        return inputs


def truncation_report(examples: dict[str, list[dict]], tokenizer,
                      max_input_tokens: int, max_target_tokens: int) -> dict:
    """Count truncation before training; long passages can hide answer evidence."""
    report = {}
    for split, rows in examples.items():
        input_cut = target_cut = 0
        for row in rows:
            input_cut += len(tokenizer(build_input(row["question"], row["passage"]),
                                       truncation=False)["input_ids"]) > max_input_tokens
            target_cut += len(tokenizer(text_target=row["answer"],
                                        truncation=False)["input_ids"]) > max_target_tokens
        report[split] = {"total": len(rows), "input_truncated": input_cut,
                         "target_truncated": target_cut}
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "checkpoints" / "vit5-vimmrc")
    parser.add_argument("--model-name", default="VietAI/vit5-base")
    parser.add_argument("--epochs", type=float, default=3)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=3e-5)
    parser.add_argument("--max-input-tokens", type=int, default=512)
    parser.add_argument("--max-target-tokens", type=int, default=64)
    parser.add_argument("--context-strategy", choices=["head", "question_chunks"], default="head",
                        help="Use question_chunks to select evidence throughout long passages")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true", help="Validate licensed splits without loading a model")
    args = parser.parse_args(argv)

    paths = {split: args.data_dir / f"{file}_vimmrc.json" for split, file in
             (("train", "train"), ("dev", "dev"), ("test", "test"))}
    validate_split_disjoint(paths)
    examples = {name: load_examples(path) for name, path in paths.items()}
    print({name: len(rows) for name, rows in examples.items()})
    if args.dry_run:
        print("Schema and article-disjoint split validation passed; no model loaded.")
        return

    import numpy as np
    import torch
    from transformers import (AutoModelForSeq2SeqLM, AutoTokenizer, DataCollatorForSeq2Seq,
                              Seq2SeqTrainer, Seq2SeqTrainingArguments, set_seed)

    if not torch.cuda.is_available():
        raise RuntimeError("Full ViT5 training requires a CUDA GPU. Use --dry-run for CPU validation.")
    random.seed(args.seed)
    np.random.seed(args.seed)
    set_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    print("Truncation report:", truncation_report(
        examples, tokenizer, args.max_input_tokens, args.max_target_tokens))
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)
    encoded = {name: EncodedExamples(rows, tokenizer, args.max_input_tokens,
                                     args.max_target_tokens, args.context_strategy) for name, rows in examples.items()}

    def compute_metrics(result):
        predictions = result.predictions[0] if isinstance(result.predictions, tuple) else result.predictions
        labels = np.where(result.label_ids == -100, tokenizer.pad_token_id, result.label_ids)
        answers = tokenizer.batch_decode(predictions, skip_special_tokens=True)
        gold = tokenizer.batch_decode(labels, skip_special_tokens=True)
        from mrc_data import exact_match, token_f1
        return {
            "exact_match": sum(exact_match(a, b) for a, b in zip(answers, gold)) / len(gold),
            "token_f1": sum(token_f1(a, b) for a, b in zip(answers, gold)) / len(gold),
        }

    train_args = Seq2SeqTrainingArguments(
        output_dir=str(args.output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation,
        learning_rate=args.learning_rate,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="exact_match",
        greater_is_better=True,
        predict_with_generate=True,
        generation_max_length=args.max_target_tokens,
        bf16=torch.cuda.is_bf16_supported(),
        fp16=False,
        gradient_checkpointing=True,
        dataloader_num_workers=0,
        save_total_limit=2,
        report_to="none",
        seed=args.seed,
        data_seed=args.seed,
    )
    trainer = Seq2SeqTrainer(
        model=model,
        args=train_args,
        train_dataset=encoded["train"],
        eval_dataset=encoded["dev"],
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model, label_pad_token_id=-100),
        processing_class=tokenizer,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    (args.output_dir / "mrc_config.json").write_text(
        json.dumps({"max_input_tokens": args.max_input_tokens,
                    "max_target_tokens": args.max_target_tokens,
                    "context_strategy": args.context_strategy,
                    "base_model": args.model_name, "seed": args.seed}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    prediction = trainer.predict(encoded["test"], metric_key_prefix="test")
    generated = prediction.predictions[0] if isinstance(prediction.predictions, tuple) else prediction.predictions
    answers = tokenizer.batch_decode(generated, skip_special_tokens=True)
    metrics = evaluate_predictions(answers, examples["test"])
    print("Held-out test metrics:", metrics)
    (args.output_dir / "test_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
