import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from context_selection import select_context, encode_input
from train import EncodedExamples


class WordTokenizer:
    """Readable tokens make boundary assertions independent of model downloads."""
    def __call__(self, text=None, text_target=None, truncation=False, max_length=None, **kwargs):
        ids = (text if text is not None else text_target).split()
        return {"input_ids": ids[:max_length] if truncation else ids}

    def decode(self, ids, **kwargs):
        return " ".join(ids)


def test_tail_evidence_retained_and_input_bounded():
    tokenizer = WordTokenizer()
    passage = "Cây xanh mọc trong vườn. " * 100 + "Mật khẩu két sắt là SAO_KIM."
    old = encode_input("Mật khẩu két sắt là gì?", passage, tokenizer, 96, "head")
    new = encode_input("Mật khẩu két sắt là gì?", passage, tokenizer, 96, "question_chunks")
    assert "SAO_KIM." not in old["input_ids"]
    assert "SAO_KIM." in new["input_ids"]
    assert len(new["input_ids"]) <= 96


def test_short_passage_unchanged():
    assert select_context("Thủ đô?", "Hà Nội là thủ đô.", WordTokenizer(), 96,
                          "question_chunks") == "Hà Nội là thủ đô."


def test_training_and_inference_use_same_context_without_target_leakage():
    tokenizer = WordTokenizer()
    row = {"question": "Mật khẩu?", "passage": "cây xanh " * 100 + "Mật khẩu SAO_KIM.",
           "answer": "secret_target_not_in_passage"}
    encoded = EncodedExamples([row], tokenizer, 96, 16, "question_chunks")[0]
    expected = encode_input(row["question"], row["passage"], tokenizer, 96, "question_chunks")
    assert encoded["input_ids"] == expected["input_ids"]
    assert row["answer"] not in encoded["input_ids"]
    assert encoded["labels"] == [row["answer"]]


def test_question_budget_and_unknown_strategy_rejected():
    with pytest.raises(ValueError, match="Question"):
        select_context("word " * 100, "context " * 100, WordTokenizer(), 64, "question_chunks")
    with pytest.raises(ValueError, match="strategy"):
        select_context("q", "p", WordTokenizer(), 64, "unknown")
