"""Fine-tune openai/whisper-small for Vietnamese ASR with LoRA."""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import evaluate
import librosa
import numpy as np
import soundfile as sf
import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import (
    EarlyStoppingCallback,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    WhisperForConditionalGeneration,
    WhisperProcessor,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="openai/whisper-small")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path.home() / "vimmrc-training/data/vietspeech_20h",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "vimmrc-training/checkpoints/whisper-small-vi-lora",
    )
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--gradient-accumulation", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--eval-steps", type=int, default=250)
    parser.add_argument("--save-steps", type=int, default=250)
    parser.add_argument("--preprocessing-workers", type=int, default=1)
    parser.add_argument("--preprocessing-writer-batch-size", type=int, default=100)
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument("--early-stopping-patience", type=int, default=3)
    parser.add_argument("--early-stopping-threshold", type=float, default=0.2)
    return parser.parse_args()


@dataclass
class WhisperDataCollator:
    processor: WhisperProcessor

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, torch.Tensor]:
        inputs = [
            {
                "input_features": feature["input_features"],
                "attention_mask": feature["attention_mask"],
            }
            for feature in features
        ]
        batch = self.processor.feature_extractor.pad(inputs, return_tensors="pt")
        labels = [{"input_ids": feature["labels"]} for feature in features]
        labels_batch = self.processor.tokenizer.pad(labels, return_tensors="pt")
        label_ids = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        if (label_ids[:, 0] == self.processor.tokenizer.bos_token_id).all().cpu().item():
            label_ids = label_ids[:, 1:]
        batch["labels"] = label_ids
        return batch


def main() -> None:
    args = parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for training")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("This configuration requires BF16 support")

    processor = WhisperProcessor.from_pretrained(args.model, language="vi", task="transcribe")
    files = {
        "train": str(args.data_dir / "train.jsonl"),
        "validation": str(args.data_dir / "validation.jsonl"),
    }
    dataset = load_dataset(
        "json",
        data_files=files,
        cache_dir=str(args.cache_dir) if args.cache_dir else None,
    )

    def preprocess(example: dict[str, Any]) -> dict[str, Any]:
        audio, sample_rate = sf.read(example["audio_path"], dtype="float32", always_2d=False)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if sample_rate != 16_000:
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16_000)
        inputs = processor.feature_extractor(
            audio,
            sampling_rate=16_000,
            return_attention_mask=True,
        )
        labels = processor.tokenizer(example["transcription"]).input_ids
        return {
            "input_features": inputs.input_features[0],
            "attention_mask": inputs.attention_mask[0],
            "labels": labels,
        }

    dataset = dataset.map(
        preprocess,
        remove_columns=dataset["train"].column_names,
        num_proc=args.preprocessing_workers,
        writer_batch_size=args.preprocessing_writer_batch_size,
        desc="Extracting Whisper features",
    )
    model = WhisperForConditionalGeneration.from_pretrained(args.model)
    model.generation_config.language = "vi"
    model.generation_config.task = "transcribe"
    model.generation_config.forced_decoder_ids = None
    model.config.use_cache = False
    model = get_peft_model(
        model,
        LoraConfig(
            r=16,
            lora_alpha=32,
            lora_dropout=0.05,
            bias="none",
            target_modules=["q_proj", "v_proj"],
        ),
    )
    model.print_trainable_parameters()
    wer_metric = evaluate.load("wer")
    cer_metric = evaluate.load("cer")

    def compute_metrics(prediction: Any) -> dict[str, float]:
        predictions = prediction.predictions
        labels = prediction.label_ids
        labels[labels == -100] = processor.tokenizer.pad_token_id
        prediction_text = processor.tokenizer.batch_decode(predictions, skip_special_tokens=True)
        reference_text = processor.tokenizer.batch_decode(labels, skip_special_tokens=True)
        return {
            "wer": 100 * wer_metric.compute(predictions=prediction_text, references=reference_text),
            "cer": 100 * cer_metric.compute(predictions=prediction_text, references=reference_text),
        }

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(args.output_dir),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps if args.max_steps is not None else -1,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation,
        learning_rate=args.learning_rate,
        warmup_ratio=0.05,
        bf16=True,
        eval_strategy="steps",
        eval_steps=args.eval_steps,
        save_strategy="steps",
        save_steps=args.save_steps,
        save_total_limit=3,
        logging_steps=25,
        report_to=["tensorboard"],
        predict_with_generate=True,
        generation_max_length=225,
        load_best_model_at_end=True,
        metric_for_best_model="wer",
        greater_is_better=False,
        remove_unused_columns=False,
        dataloader_num_workers=4,
        label_names=["labels"],
    )
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        data_collator=WhisperDataCollator(processor),
        compute_metrics=compute_metrics,
        processing_class=processor,
        callbacks=[
            EarlyStoppingCallback(
                early_stopping_patience=args.early_stopping_patience,
                early_stopping_threshold=args.early_stopping_threshold,
            )
        ],
    )
    trainer.train()
    trainer.save_model(str(args.output_dir / "best_adapter"))
    processor.save_pretrained(str(args.output_dir / "best_adapter"))


if __name__ == "__main__":
    main()