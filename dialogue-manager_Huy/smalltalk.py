"""Câu xã giao, câu hỏi về trợ lý, phép tính và ngày giờ: trả lời không cần truy xuất.

Mỗi ý định là một regex khớp TOÀN BỘ câu đã làm sạch (không khớp một phần), để câu
"Bạn có biết Hà Nội ở đâu không" không bị nhận nhầm là câu xã giao.
"""
from __future__ import annotations

import datetime as dt
import random
import re

from utterance import clean_utterance, fold, has_diacritics, nfc

BOT_NAME = "VietRead"

_P = r"(?:\s*(?:đi|nhé|nha|nhá|ạ|à|ha|nhỉ|đó|đấy|bạn|bot|nhiều|lắm|quá|vậy|thế|rồi|nữa|hen|nghen))*"

# (ý định, regex khớp toàn câu). Thứ tự quan trọng: cụ thể đứng trước.
INTENTS: list[tuple[str, str]] = [
    ("greeting", rf"(?:xin chào|chào|chào bạn|hello|hi|hey|alo|a lô|chào buổi (?:sáng|trưa|chiều|tối))(?:\s+(?:bạn|bot|cậu|anh|chị|em|mọi người|{BOT_NAME.casefold()}))?"),
    ("how_are_you", rf"(?:bạn|cậu|em)?\s*(?:có )?(?:khỏe|khoẻ) không|(?:bạn|cậu)?\s*(?:dạo này )?(?:thế nào|ra sao|sao rồi|ổn không)|hôm nay (?:bạn|cậu) (?:thế nào|ra sao|có vui không)"),
    ("goodbye", rf"(?:tạm biệt|bye|bai|bye bye|hẹn gặp lại|chào tạm biệt|thôi nhé|(?:mình|tôi|em) (?:đi|về|nghỉ|out) (?:đây|nhé|trước)|good ?bye|hẹn gặp (?:lại )?sau)"),
    ("thanks", rf"(?:cảm ơn|cám ơn|cảm ơn bạn|thank you|thanks|thank|cảm ơn nhiều|tuyệt vời cảm ơn)(?:\s+(?:bạn|cậu|nhé|nhiều|rất nhiều|nha))*"),
    ("bot_name", rf"(?:bạn|cậu|em)\s+(?:tên là gì|tên gì|là ai|tên là|là gì)|tên (?:của )?(?:bạn|cậu|em) là gì|(?:bạn|cậu|em) (?:là|có phải là) (?:người|robot|rô bốt|máy|máy móc|ai|chatbot|trợ lý(?: gì)?)(?:\s+(?:hay|hoặc)\s+[\w ]{{1,20}})?(?:\s+không)?|giới thiệu (?:về )?(?:bản thân|bạn)"),
    ("bot_creator", rf"ai (?:tạo|làm|phát triển|xây dựng|lập trình|viết) ra (?:bạn|cậu|em)|(?:bạn|cậu) (?:được|do) ai (?:tạo|làm|phát triển|xây dựng)(?: ra)?|(?:bạn|cậu) (?:được )?(?:làm|xây dựng) (?:bằng|từ) (?:gì|công nghệ gì|mô hình gì)"),
    ("bot_age", rf"(?:bạn|cậu|em) (?:bao nhiêu|mấy) tuổi|tuổi của (?:bạn|cậu)"),
    ("capabilities", rf"(?:bạn|cậu|em) (?:có thể |biết |giúp được |làm được )?(?:làm được |làm |giúp )?(?:gì|những gì|việc gì)(?: cho (?:tôi|mình))?|(?:bạn|cậu) giúp (?:được )?(?:gì|tôi được gì|mình được gì)|hướng dẫn(?: sử dụng)?|trợ giúp|help|tôi (?:nên|có thể) hỏi (?:gì|những gì)|(?:bạn|cậu) có (?:thể )?(?:nghe|hiểu|nói) (?:được )?tiếng việt không|sử dụng thế nào"),
    ("weather", rf"(?:thời tiết|trời)(?: hôm nay| ngày mai| bây giờ)?(?: ở [\w\s]+)?(?: (?:thế nào|ra sao|có mưa không|có nắng không|nóng không|lạnh không))?"),
    ("time_now", rf"(?:bây giờ|hiện tại|giờ)(?: là)? mấy giờ(?: rồi)?|mấy giờ rồi"),
    ("date_today", rf"hôm nay(?: là)? (?:ngày (?:mấy|bao nhiêu|nào)|thứ mấy|ngày gì|ngày tháng năm nào)|(?:hôm nay|bây giờ) là (?:tháng|năm) (?:mấy|bao nhiêu|nào)|năm nay là năm (?:mấy|bao nhiêu|nào)"),
    ("joke", rf"(?:kể|nói) (?:cho (?:tôi|mình|em) (?:nghe )?)?(?:một |1 )?(?:chuyện cười|truyện cười|câu chuyện vui|chuyện vui|câu đùa)|làm (?:tôi|mình) cười đi"),
    ("praise", rf"(?:bạn|cậu|em)?\s*(?:giỏi|hay|thông minh|tuyệt|xịn|đỉnh|tốt)(?: quá| thật| lắm| ghê| đấy)*|tuyệt vời|hay quá|giỏi quá|đúng rồi|chính xác|chuẩn rồi|ok|okay|được rồi|tốt lắm"),
    ("complaint", rf"(?:sai rồi|sai|không đúng|trả lời sai|bạn sai rồi|chưa đúng|dở quá|tệ quá|ngu quá|bạn dở quá|vô dụng|không hiểu gì cả|chán quá)"),
    ("apology", rf"(?:xin lỗi|sorry|mình xin lỗi|tôi xin lỗi)"),
    ("affirm", rf"(?:ừ|ừm|vâng|dạ|có|uh|ừ đúng|đúng vậy|phải)"),
    ("negate", rf"(?:không|không có gì|không cần|thôi|không sao|không có)"),
    ("repeat", rf"(?:nhắc lại|nói lại|lặp lại|đọc lại)(?: (?:đi|giúp|cho (?:tôi|mình)|câu trả lời|lần nữa|được không))*|(?:bạn )?vừa nói gì(?: thế| vậy)?|(?:tôi )?chưa nghe rõ|nghe không rõ"),
    ("source", rf"(?:bạn )?(?:lấy|tìm) (?:thông tin|câu trả lời|nó) (?:ở|từ) đâu|nguồn (?:ở đâu|nào|từ đâu|tin)|dựa vào đâu|căn cứ (?:vào )?đâu"),
    ("expand", rf"(?:giải thích|nói|trình bày|kể)(?: (?:rõ|cụ thể|chi tiết|kỹ)) hơn(?: (?:đi|được không|nữa))*|(?:cụ thể|chi tiết|rõ) hơn(?: (?:đi|được không|nữa))*|(?:còn )?gì nữa không|thêm (?:thông tin|chi tiết)(?: đi)?|nói thêm(?: đi| về nó)?|tại sao|vì sao|tại sao lại như (?:thế|vậy)|vì sao lại như (?:thế|vậy)|sao (?:lại )?vậy|ý (?:bạn|cậu) là (?:gì|sao)"),
    ("ask_name", rf"(?:tôi|mình|em|tớ) tên (?:là )?gì|(?:bạn|cậu) (?:có )?(?:nhớ|biết) tên (?:tôi|mình|em) (?:là gì|không)"),
    ("set_name", rf"(?:tôi|mình|em|tớ) tên (?:là )?(?P<name>[\w ]{{1,30}})|tên (?:tôi|mình|em|tớ) là (?P<name2>[\w ]{{1,30}})"),
    ("love", rf"(?:tôi|mình|em) (?:yêu|thích|quý) (?:bạn|cậu|em)(?: lắm| quá| nhiều)*|(?:bạn|cậu) có (?:yêu|thích) (?:tôi|mình) không"),
    ("feeling_sad", rf"(?:tôi|mình|em) (?:(?:đang|thấy|hơi|rất|cảm thấy|thật là)\s+)*(?:buồn|chán|mệt|cô đơn|stress|căng thẳng|lo lắng)(?: quá| lắm| thật| ghê)*"),
]
_COMPILED = [(name, re.compile(rf"^(?:{pat}){_P}$")) for name, pat in INTENTS]


def _fold_pattern(pattern: str) -> str:
    """Bỏ dấu trong regex mà không đổi hoa/thường (giữ cú pháp như (?P<name>...))."""
    import unicodedata
    out = unicodedata.normalize("NFD", pattern).replace("đ", "d").replace("Đ", "D")
    return "".join(ch for ch in out if unicodedata.category(ch) != "Mn").replace("A-y", "a-z")


_COMPILED_FOLD = [(name, re.compile(rf"^(?:{_fold_pattern(pat)}){_fold_pattern(_P)}$")) for name, pat in INTENTS]

RESPONSES: dict[str, list[str]] = {
    "greeting": [
        "Xin chào{name}! Mình là {bot}, trợ lý hỏi đáp tiếng Việt. Bạn muốn hỏi điều gì?",
        "Chào bạn{name}! Bạn cứ hỏi bằng giọng nói hoặc gõ chữ, mình sẽ tìm câu trả lời giúp bạn.",
    ],
    "how_are_you": [
        "Mình vẫn ổn và sẵn sàng trả lời câu hỏi của bạn. Còn bạn thì sao?",
        "Cảm ơn bạn đã hỏi thăm, mình rất ổn! Hôm nay bạn muốn tìm hiểu điều gì?",
    ],
    "goodbye": ["Tạm biệt{name}! Hẹn gặp lại bạn lần sau.", "Chào bạn{name}, chúc bạn một ngày tốt lành!"],
    "thanks": ["Không có gì đâu{name}! Bạn còn muốn hỏi thêm gì không?", "Rất vui vì đã giúp được bạn!"],
    "bot_name": [
        "Mình là {bot}, trợ lý hỏi đáp bằng giọng nói tiếng Việt. Mình nghe câu hỏi, tìm đoạn văn liên quan rồi đọc hiểu để trả lời.",
    ],
    "bot_creator": [
        "Mình được nhóm dự án ViMMRC Voice Q&A xây dựng, gồm nhận dạng giọng nói Whisper, truy xuất văn bản, mô hình đọc hiểu tiếng Việt và tổng hợp giọng nói tiếng Việt.",
    ],
    "bot_age": ["Mình là một chương trình máy tính nên không có tuổi, nhưng mình luôn học hỏi thêm mỗi ngày."],
    "capabilities": [
        "Mình có thể trả lời câu hỏi kiến thức bằng tiếng Việt, ví dụ: thủ đô của Nhật Bản là gì, sông Mê Kông dài bao nhiêu, vì sao có mùa. "
        "Bạn có thể hỏi nối tiếp như 'còn nước Pháp thì sao', hỏi so sánh, hỏi đúng sai, hoặc dán một đoạn văn để mình tóm tắt và đọc hiểu.",
    ],
    "weather": ["Mình chưa kết nối dữ liệu thời tiết trực tiếp nên không biết thời tiết lúc này. Bạn có thể xem ứng dụng dự báo thời tiết nhé."],
    "joke": [
        "Tại sao quyển sách toán lúc nào cũng buồn? Vì nó có quá nhiều vấn đề.",
        "Con gì càng to càng nhỏ? Con cua, vì càng nó to thì con cua nhỏ đi đấy!",
        "Tại sao máy tính không bao giờ đói? Vì nó luôn có sẵn rất nhiều bai.",
    ],
    "praise": ["Cảm ơn bạn nhiều! Bạn cứ hỏi tiếp nhé.", "Rất vui vì câu trả lời có ích với bạn!"],
    "complaint": [
        "Xin lỗi bạn, có thể mình đã tìm nhầm đoạn văn. Bạn thử hỏi lại cụ thể hơn, hoặc dán đoạn văn liên quan để mình đọc lại nhé.",
    ],
    "apology": ["Không sao đâu bạn! Mình sẵn sàng giúp tiếp."],
    "affirm": ["Vâng. Bạn muốn hỏi thêm điều gì nữa không?"],
    "negate": ["Được thôi. Khi nào cần bạn cứ hỏi mình nhé."],
    "love": ["Cảm ơn bạn! Mình cũng rất vui khi được trò chuyện với bạn."],
    "feeling_sad": [
        "Mình rất tiếc khi nghe vậy. Bạn hãy nghỉ ngơi một chút, hít thở sâu nhé. Nếu muốn, mình có thể kể một chuyện vui cho bạn.",
    ],
}

_WEEKDAYS = ["thứ Hai", "thứ Ba", "thứ Tư", "thứ Năm", "thứ Sáu", "thứ Bảy", "Chủ nhật"]


def _now() -> dt.datetime:
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    except Exception:  # không có tzdata: giờ UTC+7 cố định
        return dt.datetime.now(dt.timezone(dt.timedelta(hours=7)))


def detect_intent(text: str) -> tuple[str, dict] | None:
    """Trả (ý định, nhóm bắt được) nếu cả câu là câu xã giao; None nếu là câu hỏi kiến thức."""
    raw = nfc(text).strip().casefold()
    raw = re.sub(r"[?!.,…]+", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    cleaned = clean_utterance(text).casefold()
    found = _match_intent(raw, cleaned)
    if found:
        return found
    # "Mình đi đây, bye bye": mọi vế đều là câu xã giao -> trả lời vế cuối
    segments = [seg.strip() for seg in re.split(r"[,.!?;]+", nfc(text).casefold()) if seg.strip()]
    if len(segments) > 1:
        hits = [_match_intent(seg, clean_utterance(seg).casefold()) for seg in segments]
        if all(hits):
            return hits[-1]
    return None


def _match_intent(raw: str, cleaned: str) -> tuple[str, dict] | None:
    for candidate in dict.fromkeys([raw, cleaned]):
        if not candidate:
            continue
        table = _COMPILED if has_diacritics(candidate) else _COMPILED_FOLD
        probe = candidate if has_diacritics(candidate) else fold(candidate)
        for name, regex in table:
            m = regex.match(probe)
            if m:
                return name, {k: v for k, v in m.groupdict().items() if v}
    return None


def respond_intent(intent: str, groups: dict, *, user_name: str | None = None,
                   rng: random.Random | None = None) -> str:
    rng = rng or random
    name = f" {user_name}" if user_name else ""
    if intent == "time_now":
        now = _now()
        return f"Bây giờ là {now.hour} giờ {now.minute:02d} phút."
    if intent == "date_today":
        now = _now()
        return f"Hôm nay là {_WEEKDAYS[now.weekday()]}, ngày {now.day} tháng {now.month} năm {now.year}."
    if intent == "set_name":
        given = (groups.get("name") or groups.get("name2") or "").strip()
        given = " ".join(w.capitalize() for w in given.split()[:4])
        return f"Rất vui được làm quen với bạn {given}! Bạn muốn hỏi mình điều gì?"
    if intent == "ask_name":
        return f"Bạn tên là {user_name}." if user_name else "Bạn chưa cho mình biết tên. Bạn tên là gì vậy?"
    options = RESPONSES.get(intent)
    if not options:
        return "Mình chưa hiểu ý bạn lắm, bạn nói rõ hơn được không?"
    return rng.choice(options).format(name=name, bot=BOT_NAME)


# --- Phép tính đơn giản --------------------------------------------------------

_NUM_WORDS = {"không": 0, "một": 1, "mốt": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4, "năm": 5, "lăm": 5,
              "sáu": 6, "bảy": 7, "bẩy": 7, "tám": 8, "chín": 9, "mười": 10, "mươi": 10}
_OPS = {"cộng": "+", "thêm": "+", "+": "+", "trừ": "-", "bớt": "-", "-": "-", "nhân": "*", "nhân với": "*",
        "x": "*", "*": "*", "chia": "/", "chia cho": "/", "/": "/", ":": "/", "mũ": "**", "lũy thừa": "**"}


def _parse_vi_number(token: str) -> float | None:
    token = token.strip().replace(",", ".")
    if re.fullmatch(r"-?\d+(?:\.\d+)?", token):
        return float(token)
    parts = token.split()
    if not parts or any(p not in _NUM_WORDS and p not in {"trăm", "nghìn", "ngàn", "linh", "lẻ"} for p in parts):
        return None
    total, hundreds, current = 0, 0, 0
    for p in parts:
        if p in {"linh", "lẻ"}:
            continue
        if p == "trăm":
            hundreds, current = (current or 1) * 100, 0
        elif p in {"nghìn", "ngàn"}:
            total, hundreds, current = total + (hundreds + current or 1) * 1000, 0, 0
        elif p == "mươi":
            current *= 10
        elif p == "mười":
            current += 10
        else:
            current += _NUM_WORDS[p]
    total += hundreds
    return float(total + current)


_ARITH_RE = re.compile(
    r"^(?:tính(?: giúp| hộ)?(?: (?:tôi|mình))?\s+)?(?P<a>-?[\d.,]+|[a-zà-ỹ ]+?)\s+(?P<op>cộng|thêm|trừ|bớt|nhân(?: với)?|chia(?: cho)?|mũ|lũy thừa|\+|-|x|\*|/|:)\s+"
    r"(?P<b>-?[\d.,]+|[a-zà-ỹ ]+?)(?:\s+(?:bằng|là|được))?(?:\s+(?:mấy|bao nhiêu|gì|nhiêu))?$")


def try_arithmetic(text: str) -> str | None:
    q = clean_utterance(text).casefold()
    q = re.sub(r"\s*([+*/x:-])\s*", r" \1 ", q) if re.search(r"\d\s*[+*/x:-]\s*\d", q) else q
    q = re.sub(r"\s+", " ", q).strip()
    m = _ARITH_RE.match(q)
    if not m:
        return None
    a, b = _parse_vi_number(m.group("a")), _parse_vi_number(m.group("b"))
    if a is None or b is None:
        return None
    op = _OPS[m.group("op")]
    if op == "/" and b == 0:
        return "Không thể chia cho số không."
    if op == "**" and abs(b) > 100:
        return None
    value = {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b else 0, "**": a ** b}[op]
    words = {"+": "cộng", "-": "trừ", "*": "nhân", "/": "chia", "**": "mũ"}[op]
    return f"{_fmt(a)} {words} {_fmt(b)} bằng {_fmt(value)}."


def _fmt(x: float) -> str:
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{x:.4f}".rstrip("0").rstrip(".").replace(".", ",")
