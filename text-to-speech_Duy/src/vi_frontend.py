"""Frontend văn bản tiếng Việt cho Matcha-TTS, dùng chung cho notebook huấn luyện và engine suy luận.

Hai kiểu token hóa (lưu trong metadata checkpoint, khóa "frontend"):
- "char_v1": mỗi ký tự NFC là một token (nguyên âm mang dấu thanh là token riêng). Dùng cho checkpoint VIVOS cũ.
- "vi_tone_v2": tách dấu thanh khỏi nguyên âm và đặt thành token cuối mỗi âm tiết
  ("hồ" -> h, ô, 2). Năm thanh dùng chung cho mọi nguyên âm nên học thanh điệu nhanh và chuẩn hơn;
  dấu câu (, . ? !) được giữ làm token để mô hình học ngắt nghỉ, ngữ điệu (nếu dữ liệu có dấu câu).

Notebook notebooks/02_train_matcha_colab.ipynb chứa bản sao nguyên văn file này (kiểm tra bởi
tests/test_vi_frontend.py). Sau khi sửa file này, chạy `python scripts/sync_notebook_frontend.py`.
"""

import re
import unicodedata
from typing import Dict, List

# Tên chữ cái tiếng Việt, dùng để đánh vần nhãn đáp án (A/B/C/D) và chữ viết tắt
LETTER_NAMES = {
    "a": "a", "b": "bê", "c": "xê", "d": "dê", "đ": "đê", "e": "e", "f": "ép", "g": "giê",
    "h": "hát", "i": "i", "j": "gi", "k": "ca", "l": "e lờ", "m": "em mờ", "n": "en nờ",
    "o": "o", "p": "pê", "q": "quy", "r": "e rờ", "s": "ét", "t": "tê", "u": "u", "v": "vê",
    "w": "vê kép", "x": "ích", "y": "i dài", "z": "dét",
}
# Chữ cái ngoài bảng chữ tiếng Việt -> cách viết gần âm nhất
LOANWORD_LETTERS = (("f", "ph"), ("j", "gi"), ("w", "u"), ("z", "d"))

# Dấu thanh (dạng tổ hợp Unicode) -> token thanh điệu; "0" là thanh ngang
TONE_MARKS = {"́": "1", "̀": "2", "̉": "3", "̃": "4", "̣": "5"}
TONES = ["0", "1", "2", "3", "4", "5"]
BASE_LETTERS = list("abcdeghiklmnopqrstuvxy") + ["ă", "â", "đ", "ê", "ô", "ơ", "ư"]
PUNCTUATION = [",", ".", "?", "!"]
# Bộ token cố định của vi_tone_v2; id 0 = blank/pad (chèn giữa các token như add_blank của Matcha)
SYMBOLS_V2 = ["_", " "] + PUNCTUATION + BASE_LETTERS + TONES

_PUNCT_MAP = {";": ",", ":": ",", "…": ".", "\n": "."}
_ITEM_RE = re.compile(r"[a-zăâđêôơừ-ͯ]+|[,.?!]")


def spell_out(text: str) -> str:
    """Chuẩn hóa chính tả trước khi token hóa, giữ nguyên dấu câu.

    Các bước: chuẩn Unicode NFC; thay gạch nối bằng khoảng trắng; đánh vần chữ viết tắt in hoa tối đa
    5 ký tự theo tên chữ cái ("B" -> "bê", "TTS" -> "tê tê ét"); chuyển chữ thường; thay chữ cái ngoại lai
    f/j/w/z bằng âm tiếng Việt gần nhất.

    Args:
        text: Văn bản đã qua normalizer (số, ngày tháng đã viết thành chữ).

    Returns:
        Văn bản chữ thường chỉ gồm chữ cái tiếng Việt, khoảng trắng và dấu câu.
    """
    text = unicodedata.normalize("NFC", text).replace("-", " ")
    text = re.sub(
        r"\b[A-ZĐ]{1,5}\b",
        lambda m: " ".join(LETTER_NAMES[c] for c in m.group(0).lower()),
        text,
    )
    text = text.lower()
    for src, dst in LOANWORD_LETTERS:
        text = text.replace(src, dst)
    return text


def clean_chars(text: str) -> str:
    """Chuẩn hóa văn bản của frontend char_v1: chỉ giữ chữ cái và một khoảng trắng giữa các từ.

    Cũng được dùng để đưa văn bản gốc và kết quả ASR về cùng dạng khi tính CER.

    Args:
        text: Văn bản bất kỳ.

    Returns:
        Chuỗi chữ thường, không dấu câu, không chữ số.
    """
    text = re.sub(r"[\W\d_]+", " ", spell_out(text))
    return re.sub(r"\s+", " ", text).strip()


def syllable_tokens(syllable: str) -> List[str]:
    """Tách một âm tiết thành các chữ cái (đã bỏ dấu thanh) và một token thanh điệu ở cuối.

    Dấu phụ tạo nguyên âm (ă, â, ê, ô, ơ, ư) được giữ trong chữ cái; chỉ năm dấu thanh bị tách ra.
    Ví dụ: "hồ" -> ["h", "ô", "2"]; "gươm" -> ["g", "ư", "ơ", "m", "0"].

    Args:
        syllable: Một âm tiết chữ thường (NFC hoặc NFD).

    Returns:
        Danh sách token; phần tử cuối là thanh điệu "0" (ngang) đến "5" (nặng).
    """
    decomposed = unicodedata.normalize("NFD", syllable)
    tone = next((TONE_MARKS[c] for c in decomposed if c in TONE_MARKS), "0")
    letters = unicodedata.normalize("NFC", "".join(c for c in decomposed if c not in TONE_MARKS))
    return [c for c in letters if c in BASE_LETTERS] + [tone]


def text_to_tokens(text: str, frontend: str = "vi_tone_v2", keep_punctuation: bool = True) -> List[str]:
    """Chuyển văn bản thành danh sách token theo frontend của checkpoint.

    Args:
        text: Văn bản đã qua normalizer.
        frontend: "vi_tone_v2" (tách thanh điệu) hoặc "char_v1" (ký tự mang dấu, checkpoint VIVOS cũ).
        keep_punctuation: Giữ dấu câu (, . ? !) làm token; chỉ bật khi mô hình đã học dấu câu.
            Dấu ; : được quy về dấu phẩy, dấu … và xuống dòng quy về dấu chấm.

    Returns:
        Danh sách token; các âm tiết cách nhau bởi token khoảng trắng " ".
    """
    if frontend == "char_v1":
        return list(clean_chars(text))

    text = spell_out(text)
    for src, dst in _PUNCT_MAP.items():
        text = text.replace(src, dst)
    text = unicodedata.normalize("NFD", text)
    tokens: List[str] = []
    for item in _ITEM_RE.findall(text):
        if item in PUNCTUATION:
            if keep_punctuation and tokens and tokens[-1] not in PUNCTUATION:
                tokens += [" ", item]
            continue
        if tokens:
            tokens.append(" ")
        tokens += syllable_tokens(item)
    while tokens and tokens[0] in PUNCTUATION + [" "]:
        tokens.pop(0)
    return tokens


def tokens_to_ids(tokens: List[str], symbol2id: Dict[str, int]) -> List[int]:
    """Ánh xạ token sang id và chèn blank (id 0) xen giữa, như tùy chọn add_blank=True của Matcha-TTS.

    Token không có trong bộ từ vựng bị bỏ qua.

    Args:
        tokens: Kết quả của `text_to_tokens`.
        symbol2id: Bảng token -> id của checkpoint.

    Returns:
        Danh sách id độ dài 2·n + 1, dạng [0, t1, 0, t2, ..., 0].
    """
    ids = [symbol2id[t] for t in tokens if t in symbol2id]
    result = [0] * (2 * len(ids) + 1)
    result[1::2] = ids
    return result
