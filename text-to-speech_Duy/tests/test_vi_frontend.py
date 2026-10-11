"""Kiểm thử frontend tiếng Việt dùng chung cho huấn luyện (notebooks/02_train_matcha_colab.ipynb) và suy luận (matcha_engine).

Chạy lệnh:
    python -m pytest tests/test_vi_frontend.py -q
"""

import json
import os
import sys

_test_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_test_dir)
_src_dir = os.path.join(_root_dir, "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from vi_frontend import SYMBOLS_V2, clean_chars, text_to_tokens, tokens_to_ids  # noqa: E402

NOTEBOOK = os.path.join(_root_dir, "notebooks", "02_train_matcha_colab.ipynb")


def test_tone_is_split_to_end_of_syllable():
    assert text_to_tokens("hồ") == ["h", "ô", "2"]
    assert text_to_tokens("nội") == ["n", "ô", "i", "5"]
    assert text_to_tokens("gươm") == ["g", "ư", "ơ", "m", "0"]
    assert text_to_tokens("quỹ ạ") == ["q", "u", "y", "4", " ", "a", "5"]


def test_tone_split_is_independent_of_unicode_composition():
    import unicodedata

    text = "Tiếng Việt chuẩn"
    assert text_to_tokens(unicodedata.normalize("NFD", text)) == text_to_tokens(unicodedata.normalize("NFC", text))


def test_punctuation_tokens():
    tokens = text_to_tokens("Hà Nội; đẹp không?")
    assert tokens[-2:] == [" ", "?"]
    assert "," in tokens  # dấu chấm phẩy quy về dấu phẩy
    assert "?" not in text_to_tokens("đẹp không?", keep_punctuation=False)
    assert text_to_tokens(", . xin chào")[0] == "x"


def test_acronyms_and_loanwords():
    assert clean_chars("Đáp án B: Matcha-TTS") == "đáp án bê matcha tê tê ét"
    assert clean_chars("Flow") == "phlou"
    assert all(t in SYMBOLS_V2 for t in text_to_tokens("Đáp án B: Zalo, Wifi, Jazz!"))


def test_tokens_to_ids_interleaves_blank():
    symbol2id = {s: i for i, s in enumerate(SYMBOLS_V2)}
    ids = tokens_to_ids(text_to_tokens("à"), symbol2id)
    assert ids == [0, symbol2id["a"], 0, symbol2id["2"], 0]


def test_notebook_embeds_identical_frontend():
    """Notebook train phải chứa bản sao nguyên văn src/vi_frontend.py để train & suy luận token hóa như nhau."""
    with open(NOTEBOOK, encoding="utf-8") as f:
        cells = json.load(f)["cells"]
    embedded = ["".join(c["source"]) for c in cells if "".join(c["source"]).startswith("%%writefile vi_frontend.py")]
    assert len(embedded) == 1, "Không tìm thấy cell %%writefile vi_frontend.py trong notebook train"
    with open(os.path.join(_src_dir, "vi_frontend.py"), encoding="utf-8") as f:
        assert embedded[0].split("\n", 1)[1] == f.read().rstrip("\n")
