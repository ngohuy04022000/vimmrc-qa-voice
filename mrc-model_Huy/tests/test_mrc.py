import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mrc_client import LexicalBaselineClient, MRCClient
from mrc_data import evaluate_predictions, exact_match, flatten_articles, load_examples, token_f1
from train import validate_split_disjoint

ROOT = Path(__file__).resolve().parents[1]


def test_actual_schema_and_answer_conversion():
    examples = load_examples(ROOT / "examples" / "sample_vimmrc.json")
    assert [row["answer"] for row in examples] == ["Hà Nội", "miền Bắc"]
    assert evaluate_predictions(["Hà Nội", "miền Bắc"], examples) == {
        "exact_match": 1.0, "token_f1": 1.0
    }


def test_bad_alignment_rejected():
    article = json.loads((ROOT / "examples" / "sample_vimmrc.json").read_text(encoding="utf-8"))[0]
    article["answers"] = ["A"]
    with pytest.raises(ValueError, match="lengths differ"):
        flatten_articles([article])


@pytest.mark.parametrize("invalid", ["", "AB", "E"])
def test_bad_answer_label_rejected(invalid):
    article = json.loads((ROOT / "examples" / "sample_vimmrc.json").read_text(encoding="utf-8"))[0]
    article["answers"][0] = invalid
    with pytest.raises(ValueError, match="expected answer"):
        flatten_articles([article])


def test_vietnamese_metrics_and_empty_prediction():
    assert exact_match("HÀ NỘI!", "Hà Nội") == 1.0
    assert token_f1("Hà Nội", "Hà Nội ở miền Bắc") == pytest.approx(4 / 7)
    assert token_f1("", "Hà Nội") == 0.0


def test_baseline_is_available_without_model():
    answer = LexicalBaselineClient().answer_question(
        "Thành phố nằm ở miền nào?", "Hà Nội là thủ đô. Thành phố nằm ở miền Bắc."
    )
    assert answer == "Thành phố nằm ở miền Bắc."
    with pytest.raises(FileNotFoundError, match="fine-tuned checkpoint"):
        MRCClient(ROOT / "missing-checkpoint")


def test_load_reader_picks_client_by_architecture(tmp_path, monkeypatch):
    import mrc_client

    seen = {}
    monkeypatch.setattr(mrc_client, "SpanReaderClient", lambda p: seen.setdefault("span", p))
    monkeypatch.setattr(mrc_client, "MRCClient", lambda p, **kw: seen.setdefault("seq2seq", p))
    for name, arch in (("qa", "XLMRobertaForQuestionAnswering"), ("t5", "T5ForConditionalGeneration")):
        (tmp_path / name).mkdir()
        (tmp_path / name / "config.json").write_text(json.dumps({"architectures": [arch]}), encoding="utf-8")
        mrc_client.load_reader(tmp_path / name)
    assert seen == {"span": tmp_path / "qa", "seq2seq": tmp_path / "t5"}


def test_span_reader_strips_clause_punctuation():
    from mrc_client import SpanReaderClient

    client = SpanReaderClient.__new__(SpanReaderClient)  # skip loading the 2 GB model
    client.max_answer_len = 48
    client.qa = lambda **kw: {"answer": " cuối năm 1945, "}
    assert client.answer_question("Khi nào?", "Chính phủ được thành lập cuối năm 1945, sau đó.") == "cuối năm 1945"
    assert client.answer_question("Khi nào?", "  ") == ""


def test_flatten_articles_accepts_free_form_answer_texts():
    """UIT-ViQuAD2.0-shaped article: no options/answers, has answer_texts per question."""
    article = {
        "article": "Hà Nội là thủ đô của Việt Nam.",
        "questions": ["Thủ đô của Việt Nam là gì?"],
        "answer_texts": [["Hà Nội", "hà nội"]],
    }
    examples = flatten_articles([article])
    assert examples == [{
        "id": "0:0", "passage": "Hà Nội là thủ đô của Việt Nam.",
        "question": "Thủ đô của Việt Nam là gì?", "answer": "Hà Nội",
    }]


def test_flatten_articles_rejects_empty_answer_texts():
    article = {"article": "x" * 10, "questions": ["q?"], "answer_texts": [[]]}
    with pytest.raises(ValueError, match="answer_texts"):
        flatten_articles([article])


def test_real_splits_have_no_article_leakage():
    data = ROOT.parent / "data"
    if not all((data / f"{name}_vimmrc.json").exists() for name in ("train", "dev", "test")):
        pytest.skip("Licensed dataset is not available")
    validate_split_disjoint({name: data / f"{name}_vimmrc.json" for name in ("train", "dev", "test")})
    assert [len(load_examples(data / f"{name}_vimmrc.json")) for name in ("train", "dev", "test")] == [3600, 564, 1109]
