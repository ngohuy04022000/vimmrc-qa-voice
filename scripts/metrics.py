"""Một nơi duy nhất định nghĩa token F1 của dự án (trước đây có 3 bản khác nhau).

- `token_f1_multiset`: chuẩn SQuAD, đếm lặp (Counter), NFC + hạ chữ + bỏ dấu câu, GIỮ dấu tiếng Việt.
  Đây là thước đo chính (reader trên đoạn đúng, tier, và từ nay cả đầu cuối).
- `token_f1_set_noaccent`: bản cũ của eval_hard_and_multiturn / eval_out_of_dataset (tập hợp, bỏ dấu, \\w+).
  Giữ để đối chiếu với các báo cáo cũ trong reports/; không dùng cho số mới.
- `best_f1`: lấy max trên các đáp án tham chiếu (như SQuAD).
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

_MRC = str(Path(__file__).resolve().parents[1] / "mrc-model_Huy")
if _MRC not in sys.path:
    sys.path.insert(0, _MRC)

from mrc_data import exact_match, normalize_text, token_f1 as token_f1_multiset  # noqa: E402,F401


def remove_accents(text: str) -> str:
    """Giống scripts/intent_router.remove_accents (giữ hành vi cũ để tái lập số cũ)."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.replace("đ", "d").replace("Đ", "D").lower()


def _tokens_noaccent(text: str) -> list[str]:
    return re.findall(r"\w+", remove_accents(text))


def token_f1_set_noaccent(pred: str, ref: str) -> float:
    """Bản cũ: giao của hai TẬP token chia cho độ dài DANH SÁCH token (không chuẩn)."""
    p, r = _tokens_noaccent(pred), _tokens_noaccent(ref)
    if not p or not r:
        return 0.0
    common = set(p) & set(r)
    if not common:
        return 0.0
    prec, rec = len(common) / len(p), len(common) / len(r)
    return 2 * prec * rec / (prec + rec)


def best_f1(pred: str, refs: list[str], f1=token_f1_multiset) -> float:
    return max(f1(pred, ref) for ref in refs)
