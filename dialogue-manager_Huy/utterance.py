"""Làm sạch câu nói (từ STT hoặc gõ phím) và nhận dạng loại câu hỏi tiếng Việt.

Không phụ thuộc mô hình học máy: chỉ regex + từ điển nhỏ, để chạy được cả khi
chưa có checkpoint và để kiểm thử được trong CI.
"""
from __future__ import annotations

import re
import unicodedata

_VI_MARKS = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]")


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def fold(text: str) -> str:
    """Bỏ dấu tiếng Việt: 'Đà Nẵng' -> 'da nang' (dùng khi người dùng gõ không dấu)."""
    text = unicodedata.normalize("NFD", text.casefold()).replace("đ", "d")
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def has_diacritics(text: str) -> bool:
    return bool(_VI_MARKS.search(text.casefold()))


def words(text: str) -> list[str]:
    return re.findall(r"\w+", nfc(text).casefold())


def vi_search(pattern: str, text: str) -> re.Match | None:
    """Tìm pattern viết có dấu; nếu câu nhập không dấu thì so ở dạng không dấu.

    Không bỏ dấu với câu có dấu: 'máy bay' bỏ dấu thành 'may bay', trùng 'mấy'.
    """
    low = nfc(text).casefold()
    if has_diacritics(low):
        return re.search(pattern, low)
    return re.search(fold(pattern), fold(low))


# --- Làm sạch câu nói -------------------------------------------------------

# Từ đệm Whisper hay chép ra ở đầu/cuối câu nói tự nhiên.
_FILLERS = r"(?:ừm+|ừ+|ờ+|ơ+|à+|á+|um+|uhm+|hmm+|ừm ờ|dạ vâng|dạ|vâng|này|ê|alo|a lô)"
_WHO = r"(?:mình|tôi|em|tớ|con|cháu|anh|chị|tui)"
_YOU = r"(?:bạn|cậu|anh|chị|em|bot|trợ lý|ad)"
_POLITE_PREFIXES = [
    rf"{_YOU} ơi",
    rf"cho {_WHO} hỏi(?: (?:là|chút|một chút|xíu|một câu|câu này|nhé|nha))*",
    rf"{_WHO} (?:muốn|cần|đang muốn) (?:hỏi|biết)(?: (?:là|về|rằng))?",
    rf"{_WHO} (?:hỏi|thắc mắc)(?: (?:là|chút|xíu))?",
    rf"(?:{_YOU} )?(?:có thể |làm ơn |vui lòng |hãy )?(?:cho|nói cho) {_WHO} (?:biết|hỏi)(?: (?:là|về|rằng))?",
    rf"{_YOU} (?:có )?biết(?: (?:là|không|rằng))?",
    r"(?:làm ơn|vui lòng|xin|hãy)(?: cho biết| hỏi)?(?: là)?",
    r"xin hỏi(?: là)?",
    r"câu hỏi(?: là| của tôi là)?",
    r"(?:thế|vậy|thì|rồi|ok|okay|được rồi)",
]
_PREFIX_RE = re.compile(rf"^(?:{_FILLERS}|{'|'.join(_POLITE_PREFIXES)})[\s,.!:]+", re.IGNORECASE)
# Trợ từ cuối câu. "thế"/"vậy" sau "như" là một phần của "như thế"/"như vậy" nên giữ.
_SUFFIX_RE = re.compile(
    rf"[\s,]+(?:{_YOU}|ạ|nhé|nha|nhỉ|hả|hở|đấy|ấy|chứ|thế|vậy|đó|á|à|ha|hen|vậy ạ|thế ạ|nhé {_YOU})$",
    re.IGNORECASE)


def clean_utterance(text: str) -> str:
    """Bỏ từ đệm, lời mào đầu lịch sự và trợ từ cuối câu; giữ phần câu hỏi lõi.

    'Ừm cho mình hỏi là thủ đô của Pháp là gì vậy bạn?' -> 'thủ đô của Pháp là gì'
    (giữ nguyên hoa/thường để còn nhận ra tên riêng).
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    s = nfc(text).strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[?!.。…]+$", "", s).strip()
    for _ in range(6):
        new = _PREFIX_RE.sub("", s + " ").strip() if _PREFIX_RE.match(s + " ") else s
        new = _strip_suffix(new)
        if new == s:
            break
        s = new
    s = s.strip(" ,.;:")
    # "Bạn có biết Hà Nội ở đâu không" -> khung "có biết ... không" bao ngoài câu hỏi có từ để hỏi
    if vi_search(r"(?:\bgì\b|\bai\b|\bđâu\b|\bnào\b|bao nhiêu|\bmấy\b|tại sao|vì sao|thế nào|ra sao)\s+không$", s):
        s = s[: s.casefold().rfind(" kh")].rstrip()
    return s or nfc(text).strip().rstrip("?!. ")


def _strip_suffix(s: str) -> str:
    m = _SUFFIX_RE.search(s)
    if not m:
        return s
    head = s[:m.start()]
    tail = m.group(0).strip(" ,").casefold()
    if tail in {"thế", "vậy", "đó", "ấy"} and re.search(r"(?:như|lúc|khi|vì|do|nơi|người|điều|cái|chỗ|lên|đến|tới|vào|từ|về|ở|tại|của|với|trong|này|thời)$", head.casefold()):
        return s  # "như thế", "lúc đó", "người ấy": không phải trợ từ
    return head.rstrip(" ,")


# --- Loại câu hỏi -------------------------------------------------------------

QTYPE_PATTERNS: list[tuple[str, str]] = [
    ("summary", r"(?:nội dung chính|ý chính|tóm tắt|tóm lại|đại ý|chủ đề chính|chủ đề của|đoạn văn (?:này |trên )?(?:nói|viết|đề cập) (?:về )?(?:gì|điều gì|cái gì)|bài (?:này |viết )?nói về (?:gì|điều gì)|ý nghĩa của (?:đoạn văn|bài văn|bài viết|văn bản))"),
    ("why", r"(?:tại sao|vì sao|vì đâu|do đâu|lý do|nguyên nhân|vì lẽ gì|sao lại)"),
    ("how", r"(?:như thế nào|thế nào|ra sao|làm sao|làm thế nào|bằng cách nào|cách nào|ra làm sao|diễn ra|quá trình)"),
    ("describe", r"(?:^|\b)(?:giới thiệu|kể (?:cho \w+ )?(?:nghe )?về|nói về|trình bày|mô tả|giải thích|cho biết về|tìm hiểu về|thông tin về|đặc điểm của|kể về)"),
    ("yesno", r"(?:^có phải|(?:phải|đúng|có đúng|đúng là|có thật) (?:không|chứ)$|\bkhông$|\bchưa$|\bchăng$|\bhay không$)"),
    ("time", r"(?:khi nào|năm nào|năm bao nhiêu|lúc nào|bao giờ|thời gian nào|ngày nào|tháng nào|thế kỷ nào|thời điểm nào|giai đoạn nào|thời kỳ nào|vào năm|từ năm nào|ngày tháng năm nào)"),
    ("quantity", r"(?:bao nhiêu|mấy|bao xa|bao lâu|bao cao|độ cao|diện tích|dân số|chiều dài|số lượng)"),
    ("person", r"(?:(?:^|\s)ai(?:\s|$)|người nào|nhân vật nào|vị nào|do ai|bởi ai)"),
    ("location", r"(?:ở đâu|tại đâu|(?:^|\s)đâu(?:\s|$)|nơi nào|chỗ nào|nước nào|quốc gia nào|tỉnh nào|thành phố nào|vùng nào|khu vực nào|châu lục nào|châu nào|miền nào|địa điểm nào|nằm ở)"),
    ("list", r"(?:những .{1,30} nào|các .{1,30} nào|gồm những|bao gồm|kể tên|liệt kê|gồm (?:có )?gì)"),
    ("definition", r"(?:\blà gì$|\blà cái gì$|\blà ai$|nghĩa là gì|có nghĩa là|định nghĩa|khái niệm)"),
    ("choice", r"\bhay\b.*\?$|(?:\bhay là\b|\bhoặc\b)"),
]


def question_type(question: str) -> str:
    """Một nhãn trong: summary, why, how, describe, yesno, time, quantity, person, location,
    list, definition, factoid. Thứ tự ưu tiên theo QTYPE_PATTERNS."""
    q = clean_utterance(question)
    for label, pattern in QTYPE_PATTERNS:
        if label == "choice":
            continue
        if label == "yesno" and vi_search(r"(?:bao nhiêu|mấy|ai|gì|đâu|nào|khi nào|tại sao|vì sao)", q) \
                and not vi_search(r"^có phải|(?:phải|đúng) không$", q):
            continue
        if vi_search(pattern, q):
            return label
    return "factoid"


def is_question(text: str) -> bool:
    q = nfc(text).strip()
    return q.endswith("?") or question_type(q) != "factoid" or bool(
        vi_search(r"(?:\bgì\b|\bai\b|\bđâu\b|\bnào\b|bao nhiêu|\bmấy\b|không$)", q))
