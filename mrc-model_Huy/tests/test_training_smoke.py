"""One CPU optimizer step with a randomly initialized tiny T5; no download."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mrc_data import load_examples
from train import EncodedExamples, truncation_report


def test_trainer_one_step_and_label_mask(tmp_path):
    pytest.importorskip("torch")
    pytest.importorskip("transformers")
    pytest.importorskip("accelerate")
    from tokenizers import Tokenizer, models, pre_tokenizers
    from transformers import (DataCollatorForSeq2Seq, PreTrainedTokenizerFast,
                              Seq2SeqTrainer, Seq2SeqTrainingArguments, T5Config,
                              T5ForConditionalGeneration)

    backend = Tokenizer(models.WordLevel({"[PAD]": 0, "</s>": 1, "[UNK]": 2,
                                         "Hà": 3, "Nội": 4, "miền": 5, "Bắc": 6},
                                        unk_token="[UNK]"))
    backend.pre_tokenizer = pre_tokenizers.Whitespace()
    tokenizer = PreTrainedTokenizerFast(tokenizer_object=backend, pad_token="[PAD]",
                                         eos_token="</s>", unk_token="[UNK]")
    examples = load_examples(Path(__file__).resolve().parents[1] / "examples" / "sample_vimmrc.json")
    examples[1]["answer"] = "Bắc"
    encoded = EncodedExamples(examples, tokenizer, 64, 8)
    assert truncation_report({"sample": examples}, tokenizer, 64, 8)["sample"]["total"] == 2

    model = T5ForConditionalGeneration(T5Config(
        vocab_size=7, d_model=32, d_ff=64, num_layers=1, num_decoder_layers=1,
        num_heads=2, pad_token_id=0, decoder_start_token_id=0, eos_token_id=1,
    ))
    collator = DataCollatorForSeq2Seq(tokenizer, model=model, label_pad_token_id=-100)
    batch = collator([encoded[0], encoded[1]])
    assert (batch["labels"] == -100).any().item()

    args = Seq2SeqTrainingArguments(
        output_dir=str(tmp_path), max_steps=1, per_device_train_batch_size=2,
        report_to="none", save_strategy="no", eval_strategy="no", use_cpu=True,
        dataloader_pin_memory=False,
    )
    trainer = Seq2SeqTrainer(model=model, args=args, train_dataset=encoded,
                             data_collator=collator, processing_class=tokenizer)
    assert trainer.train().global_step == 1
