"""Tầng hội thoại giữa STT và retrieval/MRC.

Một lượt nói đi qua các bước:
1. Câu xã giao / hỏi về trợ lý / ngày giờ / phép tính -> trả lời ngay (smalltalk.py).
2. Câu nối tiếp ("còn Nhật Bản thì sao?", "ông ấy mất năm nào?", "tại sao?") -> viết lại thành
   câu hỏi đầy đủ nhờ chủ đề của lượt trước trong cùng phiên.
3. Câu hỏi phức tạp -> tách: so sánh hai thực thể, câu hỏi ghép nhiều vế, câu hỏi đúng/sai.
4. Mỗi câu hỏi đơn: retriever.search -> reader.answer_question -> soạn câu trả lời trọn câu
   (answer_composer.py); đoạn văn không đủ liên quan thì nói không biết thay vì đoán.

Retriever/reader là hai hợp đồng có sẵn của dự án (search(q, top_k), answer_question(q, p)),
nên dùng được với BM25 + ViT5 thật lẫn bản dự phòng không cần mô hình.
"""
from __future__ import annotations

import random
import re
import threading
import time
import uuid
from collections import OrderedDict, deque
from dataclasses import dataclass, field

from answer_composer import (
    UPPER, HeuristicReader, looks_foreign, compose_answer, content_terms, evidence_sentences, extract_span,
    parse_quantity, split_sentences, summarize, support, _cap, _end, _CAP_SPAN, _NOT_NAME_SET,
)
from smalltalk import detect_intent, respond_intent, try_arithmetic
from utterance import clean_utterance, nfc, question_type, vi_search, words

UNKNOWN_ANSWER = "Xin lỗi, mình chưa tìm thấy thông tin đủ tin cậy để trả lời câu hỏi này."
_WH = r"(?:\bgì\b|\bai\b|\bđâu\b|\bnào\b|bao nhiêu|\bmấy\b|khi nào|tại sao|vì sao|thế nào|ra sao|bao giờ|bao lâu|bao xa|có phải|không$)"
_CLASSIFIERS = (r"(?:thành phố|tỉnh|nước|quốc gia|sông|núi|hồ|vịnh|đảo|biển|chùa|đền|lăng|cầu|tháp|hang|động|"
                r"vườn quốc gia|cao nguyên|đồng bằng|dãy núi|bán đảo|châu|vua|ông|bà|nhà thơ|nhà văn|"
                r"chủ tịch|đại tướng|tổng thống|hành tinh|ngôi sao|loài|con|cây|món|thủ đô|chiến dịch|trận|khởi nghĩa|"
                r"đỉnh|phố cổ|tháp|vườn quốc gia|quần đảo|bán đảo|sa mạc|đại dương)")
_PREDICATE_START = (r"(?:là|có|ở|nằm|sinh|mất|được|thuộc|dài|cao|rộng|sâu|chảy|ra đời|thành lập|xây dựng|"
                    r"bắt nguồn|đổ|gồm|bao gồm|qua đời|viết|sáng tác|phát minh|tìm ra|diễn ra|xảy ra|kéo dài|"
                    r"giáp|cách|nổi tiếng|thường|đã|bị|lớn|nhỏ|nặng|nhiều|ít|tên|của)\b")
_PERSON_NOUNS = r"ông|bà|anh|chị|cô|cậu|người|vị|vị tướng|vị vua|nhà vua|nhà khoa học|nhà phát minh|nhà thơ|nhà văn|nhân vật|tác giả|danh tướng"
_THING_NOUNS = (r"nơi|chỗ|vùng|khu vực|thành phố|tỉnh|đất nước|nước|quốc gia|con sông|dòng sông|sông|ngọn núi|núi|đỉnh núi|"
                r"đỉnh|hồ|tác phẩm|cuốn sách|bài thơ|sự kiện|công trình|loài|con vật|hành tinh|ngôi sao|món ăn|món|"
                r"cái|thứ|chiến dịch|trận đánh|trận|cuộc khởi nghĩa|khởi nghĩa|hòn đảo|đảo|hang động|hang|vịnh|tháp|"
                r"chùa|đền|lễ hội|giải đấu|phố cổ|di tích|thiết bị|phát minh|con|cây")
_PRONOUNS = [
    # (cụm đại từ, cách thay: {t} = chủ đề, {p} = người vừa được nhắc tới trong câu trả lời)
    (rf"(?:{_PERSON_NOUNS})\s+(?:ấy|ta|đó|này|kia)", "{p}"),
    (r"ở đó|ở đấy|ở đây|tại đó|tại đây", "ở {t}"),
    (r"(lên|đến|tới|vào|từ|về) (?:đó|đấy|đây)(?=\s|$)", r"\1 {t}"),
    (rf"(?:{_THING_NOUNS})\s+(?:này|đó|ấy|kia)", "{t}"),
    (r"^(?:ông|bà|hắn)(?=\s)", "{p}"),
    (r"^(?:nó|họ)(?=\s)", "{t}"),
    (r"(?<=\s)(?:nó|họ)(?=\s|$)", "{t}"),
    (r"(?<=\s)(?:ông|bà)$", "{p}"),
]
_ATTRIBUTE_WORDS = ("dân số|diện tích|chiều dài|độ cao|chiều cao|độ sâu|thủ đô|ngôn ngữ|tiền tệ|đơn vị tiền|"
                    "quốc hoa|quốc kỳ|khí hậu|vị trí|lịch sử|nguồn gốc|tên gọi|năm sinh|ngày sinh|năm mất|quê|"
                    "quê quán|tác giả|đặc điểm|ý nghĩa|nhiệt độ|tốc độ|khối lượng|cân nặng|tuổi thọ|màu sắc|"
                    "thức ăn|món ăn|đặc sản|dân tộc|tôn giáo|người sáng lập|người phát minh")

# tính từ so sánh -> (mẫu câu hỏi thuộc tính, chiều thắng: +1 lớn hơn thắng, -1 nhỏ hơn thắng)
_COMPARE_ATTRS = [
    (r"dài|ngắn", "{e} dài bao nhiêu", {"dài": 1, "ngắn": -1}),
    (r"cao|thấp", "{e} cao bao nhiêu", {"cao": 1, "thấp": -1}),
    (r"sâu|nông", "{e} sâu bao nhiêu", {"sâu": 1, "nông": -1}),
    (r"đông dân|đông|nhiều dân|ít dân|thưa dân", "dân số của {e} là bao nhiêu",
     {"đông dân": 1, "đông": 1, "nhiều dân": 1, "ít dân": -1, "thưa dân": -1}),
    (r"lớn|rộng|to|nhỏ|hẹp|bé", "diện tích của {e} là bao nhiêu",
     {"lớn": 1, "rộng": 1, "to": 1, "nhỏ": -1, "hẹp": -1, "bé": -1}),
    (r"nặng|nhẹ", "{e} nặng bao nhiêu", {"nặng": 1, "nhẹ": -1}),
    (r"nóng|lạnh", "nhiệt độ của {e} là bao nhiêu", {"nóng": 1, "lạnh": -1}),
    (r"nhanh|chậm", "tốc độ của {e} là bao nhiêu", {"nhanh": 1, "chậm": -1}),
    (r"lâu đời|cổ|già|sớm|có trước|ra đời trước|xuất hiện trước|trước|trẻ|muộn|sau|ra đời sau|mới",
     "{e} ra đời vào năm nào",
     {"lâu đời": -1, "cổ": -1, "già": -1, "sớm": -1, "có trước": -1, "ra đời trước": -1, "xuất hiện trước": -1,
      "trước": -1, "trẻ": 1, "muộn": 1, "sau": 1, "ra đời sau": 1, "mới": 1}),
]


@dataclass
class Turn:
    user: str
    resolved: str
    answer: str
    kind: str
    raw_answer: str = ""
    passage: dict | None = None


@dataclass
class Session:
    turns: deque = field(default_factory=lambda: deque(maxlen=10))
    user_name: str | None = None
    topic: str | None = None
    person: str | None = None      # người vừa là câu trả lời ("Ai phát minh ...?" -> "Thomas Edison")
    person_age: int = 99           # số lượt kiến thức từ khi nhắc tới person
    updated: float = field(default_factory=time.time)

    def last_knowledge_turn(self) -> Turn | None:
        for turn in reversed(self.turns):
            if turn.passage is not None:
                return turn
        return None


# --- Thực thể, chủ đề ----------------------------------------------------------------

def entity_spans(text: str) -> list[str]:
    """Tên riêng trong câu, kèm danh từ loại đứng ngay trước ('sông Mê Kông')."""
    text = nfc(text)
    spans = []
    for m in re.finditer(_CAP_SPAN, text):
        span = m.group(0)
        span_words = span.split()
        if span_words[0].casefold() in _NOT_NAME_SET:
            span_words = span_words[1:]
            if not span_words:
                continue
            span = " ".join(span_words)
        elif m.start() == 0 and len(span_words) == 1 and not re.search(rf"^\S+\s+[{UPPER}]", text):
            # Từ đầu câu viết hoa do quy tắc câu ('Thủ đô của ...'), không phải tên riêng,
            # trừ khi không còn từ viết hoa nào khác ('Fansipan cao bao nhiêu').
            if re.search(rf"\s[{UPPER}]", text[m.end():]) and not looks_foreign(span):
                continue
            if span.casefold() in {"ai", "khi", "tại", "vì", "có", "bao", "những", "các", "hãy", "cho", "thế", "vậy", "còn"}:
                continue
        before = text[:text.find(span)]
        cls = re.search(rf"\b({_CLASSIFIERS})\s*$", before, flags=re.IGNORECASE)
        spans.append(f"{cls.group(1)} {span}" if cls and cls.group(1).casefold() not in {"ông", "bà"} else span)
    return spans


def main_entity(question: str) -> str | None:
    q = clean_utterance(question)
    spans = entity_spans(q)
    if spans:
        return spans[0]
    # Câu viết thường hết (STT không viết hoa): lấy chủ ngữ trước vị ngữ, ưu tiên phần sau "của"
    m = re.match(rf"^(.{{2,60}}?)\s+{_PREDICATE_START}", q, flags=re.IGNORECASE)
    if not m or vi_search(_WH, m.group(1)):
        return None
    subj = m.group(1).strip()
    if " của " in subj.casefold():
        subj = subj[subj.casefold().rfind(" của ") + 5:]
    if len(subj.split()) > 6 or not content_terms(subj):
        return None
    return subj


def _strip_classifier(entity: str) -> str:
    return re.sub(rf"^{_CLASSIFIERS}\s+", "", entity, flags=re.IGNORECASE)


# --- Viết lại câu nối tiếp ------------------------------------------------------------

_FOLLOW_ELLIPSIS = re.compile(
    r"^(?:(?:thế|vậy|còn|thế còn|vậy còn|còn về|còn với|thế với|thế thì|vậy thì|với)\s+)+(?P<x>.+?)"
    r"(?:\s+(?:thì sao|thì thế nào|thì như thế nào|thì ra sao|thì sao nhỉ|thì|nữa|thì có không))?$",
    re.IGNORECASE)
_FOLLOW_SUFFIX = re.compile(r"^(?P<x>.+?)\s+(?:thì sao|thì thế nào|thì như thế nào|thì ra sao)$", re.IGNORECASE)


def resolve_followup(question: str, session: Session) -> tuple[str, bool]:
    """Câu hỏi đầy đủ + cờ có viết lại hay không."""
    q = clean_utterance(question)
    prev = session.last_knowledge_turn()
    topic = session.topic
    person = session.person if session.person_age <= 1 else None
    if prev is None or not (topic or person):
        return q, False
    topic = topic or person

    m = _FOLLOW_ELLIPSIS.match(q) or _FOLLOW_SUFFIX.match(q)
    if m and not vi_search(r"(?:\bgì\b|\bai\b|\bđâu\b|\bnào\b|bao nhiêu|\bmấy\b|khi nào|tại sao|vì sao)", m.group("x")):
        x = m.group("x").strip(" ,")
        prev_q = prev.resolved
        if vi_search(rf"^(?:{_ATTRIBUTE_WORDS})$", x):
            qword = "là bao nhiêu" if vi_search(r"dân số|diện tích|chiều dài|độ cao|chiều cao|độ sâu|nhiệt độ|tốc độ|khối lượng|cân nặng|tuổi thọ|năm", x) else "là gì"
            return f"{x} của {topic} {qword}", True
        old = topic if topic.casefold() in prev_q.casefold() else _strip_classifier(topic)
        idx = prev_q.casefold().find(old.casefold())
        if idx >= 0:
            new_q = prev_q[:idx] + x + prev_q[idx + len(old):]
            return new_q, True
        return f"{x} {prev_q}", True

    # Đại từ thay cho chủ đề
    low = q.casefold()
    for pattern, repl in _PRONOUNS:
        mm = re.search(pattern, low)
        if mm:
            filled = mm.expand(repl.replace("{t}", topic.replace("\\", "")).replace("{p}", (person or topic)))
            new_q = q[:mm.start()] + filled + q[mm.end():]
            return re.sub(r"\s+", " ", new_q).strip(), True

    # Câu chỉ còn từ để hỏi: "Vào năm nào?", "Ở đâu?" -> ghép vào câu hỏi trước (bỏ từ để hỏi cũ)
    if not content_terms(q) or (len(q.split()) <= 3 and not entity_spans(q) and vi_search(_WH, q)
                                and not vi_search(r"^(?:có|là)\b", q)):
        base = strip_wh(prev.resolved) or topic
        return f"{base} {q[:1].lower() + q[1:]}", True
    return q, False


_WH_STRIP = re.compile(r"(?:^|\s)(?:ai là|là ai|là gì|là cái gì|cái gì|điều gì|vào năm nào|năm nào|vào lúc nào|khi nào|"
                       r"lúc nào|bao giờ|ở đâu|tại đâu|đâu|bao nhiêu|mấy|ai|gì|nào)(?=\s|$)", re.IGNORECASE)


def strip_wh(question: str) -> str:
    """'Ai là người đầu tiên lên Mặt Trăng' -> 'người đầu tiên lên Mặt Trăng'."""
    out = _WH_STRIP.sub(" ", clean_utterance(question))
    out = re.sub(r"\s+", " ", out).strip(" ,")
    return out[:1].upper() + out[1:] if out else out


# --- Tách câu hỏi phức tạp -----------------------------------------------------------

def split_multi_question(question: str) -> list[str]:
    """'Hà Nội là thủ đô nước nào và có bao nhiêu quận?' -> 2 câu hỏi đơn có đủ chủ ngữ."""
    text = nfc(question).strip()
    pieces = [p.strip(" ,") for p in re.split(r"\?\s*", text) if p.strip(" ,")]
    parts: list[str] = []
    for piece in pieces:
        sub = re.split(r"\s*(?:,\s*|\s)(?:và|còn|rồi|với lại|đồng thời|ngoài ra|thêm nữa là)\s+|\s*;\s*|,\s+", piece)
        merged: list[str] = []
        for s in sub:
            if merged and not vi_search(_WH, s):
                merged[-1] = f"{merged[-1]} và {s}"  # vế không phải câu hỏi: nối lại ("A và B là gì")
            elif merged and not vi_search(_WH, merged[-1]):
                merged[-1] = f"{merged[-1]} và {s}"
            else:
                merged.append(s)
        parts.extend(merged)
    parts = [clean_utterance(p) for p in parts if p.strip()]
    if len(parts) <= 1:
        return [clean_utterance(text)]
    # "Ai chỉ huy ... quân Thanh và ông lên ngôi ở đâu": 'ông' là người trong câu trả lời, không phải
    # 'Thanh'; để nguyên đại từ, ngữ cảnh phiên sẽ thay bằng người vừa trả lời
    asks_who = re.match(r"^(?:ai\b|người nào\b|vị \w+ nào\b)", parts[0], flags=re.IGNORECASE)
    subject = None if asks_who else main_entity(parts[0])
    out = [parts[0]]
    for p in parts[1:4]:
        if subject:
            for pattern, repl in _PRONOUNS:
                mm = re.search(pattern, p.casefold())
                if mm:
                    p = p[:mm.start()] + mm.expand(repl.replace("{t}", subject).replace("{p}", subject)) + p[mm.end():]
                    break
        attr = re.match(rf"^({_ATTRIBUTE_WORDS})\s+(?!của)(.+)$", p, flags=re.IGNORECASE)
        if subject and not entity_spans(p) and attr:
            p = f"{attr.group(1)} của {subject} {attr.group(2)}"
        elif subject and not entity_spans(p) and not re.match(r"^(?:ai|cái gì|điều gì)\b", p, flags=re.IGNORECASE):
            p = subject + " " + re.sub(r"^để\s+", "", p)
        out.append(p)
    return out


_ADJ = (r"đông dân|nhiều dân|ít dân|thưa dân|lâu đời|có trước|ra đời trước|ra đời sau|xuất hiện trước|"
        r"nổi tiếng|phổ biến|\w+")
_CMP_RE = [
    # "Sông Hồng hay sông Mê Kông dài hơn", "Giữa Hà Nội và Huế, thành phố nào lớn hơn"
    re.compile(r"^(?:giữa\s+)?(?P<a>.+?)\s+(?:hay là|hay|hoặc|với|và|so với)\s+(?P<b>.+?)\s*,?\s*"
               r"(?:(?:thì\s+)?(?:\w+\s+){0,2}nào\s+|(?:thì\s+)?(?:ai|cái gì)\s+)?(?:thì\s+)?(?:là\s+)?(?:có\s+)?"
               rf"(?P<adj>{_ADJ})\s+hơn(?:\s+\w+)?$", re.IGNORECASE),
    # "Sông Hồng dài hơn hay ngắn hơn sông Mê Kông" -> bỏ qua; "A có dài hơn B không"
    re.compile(rf"^(?P<a>.+?)\s+(?:có\s+)?(?P<adj>{_ADJ})\s+hơn\s+(?P<b>.+?)\s+(?:không|phải không|đúng không|chứ)$",
               re.IGNORECASE),
]
_CMP_ATTR_RE = re.compile(r"^so sánh\s+(?P<attr>.+?)\s+(?:của|giữa)\s+(?P<a>.+?)\s+(?:và|với)\s+(?P<b>.+)$", re.IGNORECASE)
_CMP_DIFF_RE = re.compile(r"^(?:so sánh\s+)?(?:giữa\s+)?(?P<a>.+?)\s+(?:và|với)\s+(?P<b>.+?)\s*(?:có\s+)?(?:khác nhau|giống nhau|khác|giống)?"
                          r"(?:\s+(?:như thế nào|thế nào|ra sao|ở điểm nào|ở chỗ nào|gì|điểm gì|chỗ nào))?$", re.IGNORECASE)


_CMP_ORDER_RE = re.compile(r"^(?:giữa\s+)?(?P<a>.+?)\s+(?:và|với|hay)\s+(?P<b>.+?)\s*,?\s*(?:thì\s+)?(?:ai|cái nào|bên nào|\w+\s+nào)\s+"
                           r"(?:được\s+)?(?P<verb>sinh|ra đời|xuất hiện|xây dựng|xây|thành lập|có)\s+(?:ra\s+)?(?P<when>trước|sau|sớm hơn|muộn hơn)$",
                           re.IGNORECASE)


def parse_comparison(question: str) -> dict | None:
    q = clean_utterance(question)
    m = _CMP_ORDER_RE.match(q)
    if m:
        verb = m.group("verb").casefold()
        tmpl = "{e} sinh năm nào" if verb == "sinh" else ("{e} được xây dựng năm nào" if verb.startswith("xây") else "{e} ra đời vào năm nào")
        when = m.group("when").casefold()
        return {"a": m.group("a").strip(" ,"), "b": m.group("b").strip(" ,"), "attr": None,
                "adj": f"{verb} {when.replace(' hơn', '')}", "yesno": False, "template": tmpl,
                "direction": -1 if when in {"trước", "sớm hơn"} else 1, "no_hon": True}
    m = _CMP_ATTR_RE.match(q)
    if m:
        return {"a": m.group("a"), "b": m.group("b"), "attr": m.group("attr"), "adj": None, "yesno": False}
    for i, regex in enumerate(_CMP_RE):
        m = regex.match(q)
        if m:
            adj = m.group("adj").casefold()
            adj = re.sub(r"^(?:thì|là|có|nào)\s+", "", adj)
            if not any(re.fullmatch(rf"(?:{alts})", adj) for alts, _, _ in _COMPARE_ATTRS) and len(adj.split()) > 1:
                adj = adj.split()[-1]
            a = re.sub(r"^(?:giữa)\s+", "", m.group("a")).strip(" ,")
            b = re.sub(r"\s*,?\s*(?:\w+\s+){0,2}nào$", "", m.group("b")).strip(" ,")
            if not a or not b or vi_search(_WH, a):
                continue
            return {"a": a, "b": b, "attr": None, "adj": adj, "yesno": i == 1}
    if vi_search(r"(?:khác nhau|giống nhau|so sánh)", q):
        m = _CMP_DIFF_RE.match(q)
        if m:
            return {"a": m.group("a").strip(" ,"), "b": m.group("b").strip(" ,"), "attr": None, "adj": None,
                    "yesno": False, "describe": True}
    return None


# --- Câu hỏi đúng/sai ----------------------------------------------------------------

def yesno_claims(question: str) -> list[str]:
    q = clean_utterance(question)
    q = re.sub(r"\s+(?:hay không|phải không|đúng không|có đúng không|không|chưa|chăng|chứ)$", "", q, flags=re.IGNORECASE)
    m = re.match(r"^(?:có phải|phải chăng|có đúng là|đúng là|liệu)\s+(?:là\s+)?(.+)$", q, flags=re.IGNORECASE)
    if m:
        return [m.group(1)]
    m = re.match(r"^(.+?)\s+có phải (?:là\s+)?(.+)$", q, flags=re.IGNORECASE)
    if m:
        return [f"{m.group(1)} là {m.group(2)}"]
    m = re.match(r"^(.+?)\s+(?:có|đã|đang|sẽ|có từng|từng)\s+(.+)$", q, flags=re.IGNORECASE)
    if m:
        return [f"{m.group(1)} {m.group(2)}", q]
    return [q]


_NEGATION = r"\b(?:không|chưa|chẳng|chả|không phải|không hề|chưa từng|không còn)\b"


def judge_claim(claim: str, sentence: str) -> tuple[str, float]:
    """('yes'|'no'|'unsure', độ phủ) theo từ khóa, tên riêng, con số và phủ định."""
    terms = set(content_terms(claim))
    if not terms:
        return "unsure", 0.0
    s_tokens = set(words(sentence))
    coverage = sum(t in s_tokens for t in terms) / len(terms)
    claim_ents = {t for span in entity_spans(claim) for t in words(_strip_classifier(span))}
    claim_nums = set(re.findall(r"\d[\d.,]*", claim))
    sent_nums = set(re.findall(r"\d[\d.,]*", sentence))
    missing_ent = claim_ents - s_tokens
    neg_claim = bool(re.search(_NEGATION, claim.casefold()))
    neg_sent = bool(re.search(_NEGATION, sentence.casefold()))
    if coverage < 0.4:
        return "unsure", coverage
    if claim_nums and sent_nums and not claim_nums & sent_nums:
        return "no", coverage
    if missing_ent and coverage < 0.95:
        return "no", coverage
    for head in ("miền", "phía", "bán cầu", "cực", "hướng", "bờ"):
        for a, b in (("bắc", "nam"), ("nam", "bắc"), ("đông", "tây"), ("tây", "đông")):
            if f"{head} {a}" in claim.casefold() and f"{head} {b}" in sentence.casefold() \
                    and f"{head} {a}" not in sentence.casefold():
                return "no", coverage
    if coverage >= 0.65:
        return ("no" if neg_claim != neg_sent else "yes"), coverage
    return "unsure", coverage


# --- Quản lý hội thoại ---------------------------------------------------------------

REALTIME = re.compile(r"\b(?:hôm nay|ngày mai|tối nay|sáng nay|hiện nay|hiện tại|bây giờ|mới nhất|năm nay|tuần này|đang giao dịch)\b",
                      re.IGNORECASE)


class DialogueManager:
    def __init__(self, retriever, reader=None, *, top_k: int = 3, min_support: float = 0.34,
                 max_sessions: int = 1000, session_ttl: float = 6 * 3600, seed: int | None = None,
                 assist=None, assist_gate: bool = True, assist_verify: bool = True):
        self.assist = assist  # LLMAssist hoặc None; None/không sẵn sàng = chạy như trước
        self.assist_gate = assist_gate
        self.assist_verify = assist_verify
        self.retriever = retriever
        self.reader = reader or HeuristicReader()
        self.fallback_reader = HeuristicReader()
        self.top_k = top_k
        self.min_support = min_support
        self.max_sessions = max_sessions
        self.session_ttl = session_ttl
        self.rng = random.Random(seed)
        self._sessions: OrderedDict[str, Session] = OrderedDict()
        self._lock = threading.Lock()

    # ---- phiên ----
    def session(self, session_id: str | None) -> tuple[str, Session]:
        sid = session_id or uuid.uuid4().hex
        now = time.time()
        with self._lock:
            for key in [k for k, s in self._sessions.items() if now - s.updated > self.session_ttl]:
                del self._sessions[key]
            sess = self._sessions.pop(sid, None) or Session()
            sess.updated = now
            self._sessions[sid] = sess
            while len(self._sessions) > self.max_sessions:
                self._sessions.popitem(last=False)
        return sid, sess

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    # ---- lượt nói ----
    def respond(self, text: str, session_id: str | None = None, passage: str | None = None) -> dict:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be non-empty")
        sid, sess = self.session(session_id)
        text = nfc(text).strip()
        result = self._respond(text, sess, (passage or "").strip() or None)
        result.update(session_id=sid, question=text)
        sess.turns.append(Turn(user=text, resolved=result.get("resolved_question", text), answer=result["answer"],
                               kind=result["kind"], raw_answer=result.get("raw_answer", ""),
                               passage=result.get("passage")))
        if result.get("passage") is not None:
            tq = result.get("topic_question") or result.get("resolved_question", "")
            spans = entity_spans(clean_utterance(tq))
            topic = spans[0] if spans else (main_entity(tq) if not re.search(f"[{UPPER}]", tq) else None)
            if topic:
                sess.topic = topic
            sess.person_age += 1
            if result.get("qtype") == "person":
                name = entity_spans(result.get("raw_answer", "")) or entity_spans(result.get("answer", ""))
                q_toks = set(words(tq))
                name = [n for n in name if not set(words(n)) <= q_toks]
                if name:
                    sess.person, sess.person_age = name[0], 0
        return result

    def _respond(self, text: str, sess: Session, passage: str | None) -> dict:
        intent = detect_intent(text)
        # "Tại sao?" khi chưa có gì để giải thích -> coi như câu hỏi bình thường
        if intent and not (intent[0] == "expand" and sess.last_knowledge_turn() is None and passage is None):
            return self._smalltalk(intent[0], intent[1], sess, text)
        math_answer = try_arithmetic(text)
        if math_answer:
            return {"answer": math_answer, "kind": "math", "resolved_question": clean_utterance(text)}

        resolved, rewritten = resolve_followup(text, sess) if passage is None else (clean_utterance(text), False)

        cmp = parse_comparison(resolved)
        if cmp:
            return self._compare(cmp, resolved, passage)
        parts = split_multi_question(resolved)
        if len(parts) > 1:
            results = [self._answer_single(p, passage, sess if rewritten else None) for p in parts]
            known = [r for r in results if r["kind"] != "unknown"]
            if not known:
                return dict(results[0], resolved_question=resolved)
            answer = " ".join(r["answer"] for r in results)
            return {"answer": answer, "kind": "multi", "resolved_question": resolved, "parts": results,
                    "passage": known[0].get("passage"), "raw_answer": known[0].get("raw_answer", ""),
                    "topic_question": parts[0], "rewritten": rewritten}
        out = self._answer_single(resolved, passage, sess if rewritten else None)
        out["rewritten"] = rewritten
        return out

    def _smalltalk(self, intent: str, groups: dict, sess: Session, text: str) -> dict:
        base = {"kind": "smalltalk", "intent": intent, "resolved_question": clean_utterance(text)}
        last = sess.last_knowledge_turn()
        if intent == "set_name":
            given = (groups.get("name") or groups.get("name2") or "").strip()
            sess.user_name = " ".join(w.capitalize() for w in given.split()[:4]) or None
        if intent == "repeat":
            prev = sess.turns[-1].answer if sess.turns else "Mình chưa nói gì cả. Bạn muốn hỏi gì?"
            return dict(base, answer=prev)
        if intent == "source":
            if last and last.passage:
                first = split_sentences(last.passage["text"])[:1]
                return dict(base, answer=f"Mình lấy thông tin từ đoạn văn {last.passage.get('id') or 'bạn cung cấp'}: "
                                         f"{first[0] if first else ''}", passage=None)
            return dict(base, answer="Mình chưa trả lời câu hỏi kiến thức nào nên chưa có nguồn.")
        if intent == "expand":
            if not last or not last.passage:
                return dict(base, answer="Bạn muốn mình giải thích thêm về điều gì?")
            said = set(split_sentences(last.answer))
            ev = [s for s in evidence_sentences(last.resolved, last.passage["text"], last.raw_answer, limit=4)
                  if s not in said and _end(s) not in said]
            if not ev:
                ev = [s for s in split_sentences(last.passage["text"]) if s not in said and _end(s) not in said][:3]
            answer = " ".join(_end(s) for s in ev) or "Mình không có thêm thông tin nào khác trong đoạn văn này."
            return dict(base, kind="expand", answer=answer, resolved_question=last.resolved)
        return dict(base, answer=respond_intent(intent, groups, user_name=sess.user_name, rng=self.rng))

    # ---- câu hỏi đơn ----
    def _candidates(self, question: str, passage: str | None, sess: Session | None) -> list[dict]:
        if passage:
            return [{"id": "user_passage", "passage": passage, "score": 1.0}]
        hits = list(self.retriever.search(question, top_k=self.top_k) or [])
        last = sess.last_knowledge_turn() if sess else None
        if last and last.passage and last.passage.get("id") not in {h.get("id") for h in hits}:
            hits.append({"id": last.passage.get("id"), "passage": last.passage["text"], "score": 0.0,
                         "carried_over": True})
        return hits

    def _pick(self, question: str, hits: list[dict], qtype: str = "factoid") -> tuple[dict | None, float]:
        """Giữ thứ hạng retriever (reranker đã chấm) trừ khi đoạn khác khớp rõ hơn hẳn: chứa đủ
        tên riêng của câu hỏi mà đoạn đầu thiếu, hoặc phủ từ khóa (cả đoạn và trong cùng một câu)
        hơn hẳn. Câu hỏi tại sao ưu tiên đoạn có câu chứa từ chỉ nguyên nhân."""
        if not hits:
            return None, 0.0
        ents = {t for span in entity_spans(question) for t in words(_strip_classifier(span))}
        terms = set(content_terms(question))

        def features(h):
            toks = set(words(h["passage"]))
            sent_sup = 0.0
            causal = False
            for sent in split_sentences(h["passage"]):
                st = set(words(sent))
                cov = len(terms & st) / len(terms) if terms else 1.0
                if cov > sent_sup:
                    sent_sup = cov
                    causal = bool(re.search(r"\b(?:vì|do|bởi|nên|nguyên nhân|gây ra|nhờ|khiến)\b", sent.casefold()))
            sup = support(question, h["passage"])
            score = 0.5 * sup + 0.5 * sent_sup + (0.15 if qtype == "why" and causal else 0.0)
            return sup, (not ents or ents <= toks), score

        scored = [(*features(h), i, h) for i, h in enumerate(hits)]
        best = scored[0]
        for cand in scored[1:]:
            sup, ent_ok, score, _, h = cand
            if (ent_ok and not best[1] and sup >= self.min_support) or \
                    (ent_ok >= best[1] and score >= best[2] + 0.15) or \
                    (h.get("carried_over") and ent_ok >= best[1] and score > best[2]):
                best = cand
        return best[4], best[0]

    def _gate(self, question: str, hit: dict, hits: list[dict]) -> tuple[dict | None, bool]:
        """LLM chọn đoạn đầu tiên (hit trước) thực sự trả lời được câu hỏi. (None, True) = không đoạn nào;
        (hit, False) = LLM không dùng được, giữ nguyên lựa chọn cũ."""
        for cand in [hit] + [h for h in hits if h is not hit]:
            ok = self.assist.supports(question, cand["passage"])
            if ok is None:
                return hit, False
            if ok:
                return cand, True
        return None, True

    def _answer_single(self, question: str, passage: str | None, sess: Session | None) -> dict:
        qtype = question_type(question)
        if qtype == "yesno":
            return self._yesno(question, passage, sess)
        hits = self._candidates(question, passage, sess)
        hit, sup = self._pick(question, hits, qtype)
        base = {"resolved_question": question, "qtype": qtype}
        if hit is None or (sup < self.min_support and len(set(content_terms(question))) >= 2 and not passage):
            return dict(base, answer=UNKNOWN_ANSWER, kind="unknown", passage=None, support=round(sup, 3))
        q_ents = {t for span in entity_spans(question) for t in words(_strip_classifier(span))}
        if q_ents and not passage:
            p_toks = set(words(hit["passage"]))
            if sum(t in p_toks for t in q_ents) / len(q_ents) < 0.5:
                # tên riêng chính của câu hỏi không có trong đoạn: đoạn nói về chuyện khác
                return dict(base, answer=UNKNOWN_ANSWER, kind="unknown", passage=None, support=round(sup, 3))
        llm = {}
        if self.assist and self.assist_gate and not passage and REALTIME.search(question):
            # giá, thời tiết, tin mới: kho tĩnh không có, đoạn trùng từ khóa chỉ dẫn tới câu trả lời bịa
            return dict(base, answer=UNKNOWN_ANSWER, kind="unknown", passage=None, support=round(sup, 3),
                        llm={"realtime": True})
        if self.assist and self.assist_gate and not passage and qtype != "summary" and self.assist.available():
            hit, used = self._gate(question, hit, hits)
            llm["gate"] = used
            if hit is None:
                return dict(base, answer=UNKNOWN_ANSWER, kind="unknown", passage=None, support=round(sup, 3), llm=llm)
        text = hit["passage"]
        if qtype == "summary":
            raw = summarize(text)
        else:
            raw = self.reader.answer_question(question, text) or ""
            # ViT5 học từ đáp án trắc nghiệm ViMMRC nên đôi khi sinh "Cả A, B, C đều đúng"
            raw = re.sub(r"^\s*(?:Chi\s+)?Cả\s+[A-D](?:\s*(?:,|và)\s*[A-D])*\s+đều\s+(?:đúng|sai)\.?\s*", "", raw)
            if not raw.strip():
                raw = self.fallback_reader.answer_question(question, text)
            elif qtype in {"time", "quantity", "person", "location"} and len(raw.split()) > 12:
                # reader trả cả câu dài: cố trích cụm đúng loại để câu trả lời gọn khi đọc
                raw = extract_span(question, raw, qtype) or raw
        if self.assist and self.assist_verify and not passage and qtype != "summary" and self.assist.available():
            ok = self.assist.verify(question, text, raw)
            llm["verify"] = ok
            if ok is False:
                alt = self.assist.answer(question, text)
                if alt:
                    llm["replaced"] = raw
                    raw = alt
        answer = compose_answer(question, raw, text, qtype)
        if not answer.strip():
            return dict(base, answer=UNKNOWN_ANSWER, kind="unknown", passage=None, support=round(sup, 3), llm=llm)
        return dict(base, llm=llm, answer=answer, raw_answer=raw, kind="summary" if qtype == "summary" else "qa",
                    passage={"id": hit.get("id"), "text": text, "score": hit.get("score")}, support=round(sup, 3))

    def _yesno(self, question: str, passage: str | None, sess: Session | None) -> dict:
        claims = yesno_claims(question)
        best = None
        for claim in claims:
            hits = self._candidates(claim, passage, sess)
            for hit in hits[: self.top_k + 1]:
                for sentence in split_sentences(hit["passage"]):
                    verdict, cov = judge_claim(claim, sentence)
                    c_bi = set(zip(words(claim), words(claim)[1:]))
                    s_toks = words(sentence)
                    bi = len(c_bi & set(zip(s_toks, s_toks[1:]))) / max(1, len(c_bi))
                    rank = (round(cov + 0.3 * bi, 4), verdict != "unsure")
                    if best is None or rank > best[0]:
                        best = (rank, verdict, sentence, hit, claim)
        base = {"resolved_question": question, "qtype": "yesno"}
        if best is None or best[0][0] < 0.45:
            return dict(base, answer=UNKNOWN_ANSWER, kind="unknown", passage=None)
        _, verdict, sentence, hit, claim = best
        lead = {"yes": "Đúng vậy.", "no": "Không phải.", "unsure": "Mình chưa chắc chắn, nhưng thông tin tìm được cho biết:"}[verdict]
        return dict(base, answer=f"{lead} {_end(sentence)}", kind="yesno", verdict=verdict, raw_answer=sentence,
                    passage={"id": hit.get("id"), "text": hit["passage"], "score": hit.get("score")})

    # ---- so sánh ----
    def _superlative(self, a: str, b: str, adj: str, passage: str | None):
        """Không có số liệu: tìm câu 'A là ... <adj> nhất' (vd. 'Sao Mộc là hành tinh lớn nhất')."""
        for e, other in ((a, b), (b, a)):
            e_toks = set(words(_strip_classifier(e)))
            hits = [{"passage": passage}] if passage else list(self.retriever.search(f"{e} {adj} nhất", top_k=self.top_k) or [])
            for h in hits:
                for sent in split_sentences(h["passage"]):
                    low = sent.casefold()
                    if e_toks <= set(words(sent)) and re.search(rf"\b{re.escape(adj)}\s+nhất\b", low) \
                            and not set(words(_strip_classifier(other))) <= set(words(sent)):
                        return e, other, sent
        return None

    def _compare(self, cmp: dict, question: str, passage: str | None) -> dict:
        a, b = cmp["a"], cmp["b"]
        base = {"kind": "compare", "resolved_question": question, "qtype": "compare", "topic_question": a}
        if cmp.get("describe"):
            facts = [self._answer_single(f"Giới thiệu về {e}", passage, None) for e in (a, b)]
            known = [f for f in facts if f["kind"] != "unknown"]
            if not known:
                return dict(base, answer=UNKNOWN_ANSWER, kind="unknown", passage=None)
            body = " ".join(f"Về {e}: {f['answer']}" for e, f in zip((a, b), facts) if f["kind"] != "unknown")
            return dict(base, answer=body, parts=facts, passage=known[0].get("passage"))
        if cmp.get("template"):
            template, direction, adj = cmp["template"], cmp["direction"], cmp["adj"]
        elif cmp["attr"]:
            template, direction, adj = f"{cmp['attr']} của {{e}} là bao nhiêu", 1, None
        else:
            adj = cmp["adj"]
            template, direction = f"{{e}} {adj} bao nhiêu", 1
            for alts, tmpl, dirs in _COMPARE_ATTRS:
                if re.fullmatch(rf"(?:{alts})", adj):
                    template, direction = tmpl, dirs.get(adj, 1)
                    break
        facts, values = [], []
        for e in (a, b):
            sub = template.format(e=e)
            fact = self._answer_single(sub, passage, None)
            facts.append(fact)
            value = None
            if fact["kind"] != "unknown":
                raw = fact.get("raw_answer", "")
                if "năm nào" in sub or "năm nào" in template:
                    years = re.findall(r"\b(\d{3,4})\b", raw) or re.findall(r"\b(\d{3,4})\b", fact["answer"])
                    value = float(years[0]) if years else None
                else:
                    value = parse_quantity(raw)
                    if value is None:
                        span = extract_span(sub, fact["passage"]["text"], "quantity")
                        value = parse_quantity(span or "")
            values.append(value)
        # danh từ loại đầu câu hỏi viết hoa ("Sông Hồng hay ..."): giữa câu trả lời thì viết thường
        b = re.sub(rf"^({_CLASSIFIERS})\b", lambda m: m.group(1).lower(), b, flags=re.IGNORECASE)
        a_mid = re.sub(rf"^({_CLASSIFIERS})\b", lambda m: m.group(1).lower(), a, flags=re.IGNORECASE)
        known = [f for f in facts if f["kind"] != "unknown"]
        if not known and not (adj and self._superlative(a, b, adj, passage)):
            return dict(base, answer=UNKNOWN_ANSWER, kind="unknown", passage=None)
        details = " ".join(f["answer"] for f in facts if f["kind"] != "unknown")
        if None not in values and values[0] != values[1]:
            first_wins = (values[0] > values[1]) == (direction > 0)
            winner, loser = (a, b) if first_wins else (b, a_mid)
            label = adj or f"có {cmp['attr']} lớn"
            than = " " if cmp.get("no_hon") else " hơn "
            if cmp.get("yesno"):
                lead = "Đúng vậy." if first_wins else "Không phải."
                answer = f"{lead} {_cap(winner)} {label}{than}{loser}. {details}"
            else:
                answer = f"{_cap(winner)} {label}{than}{loser}. {details}"
        else:
            sup = self._superlative(a, b, adj, passage) if adj else None
            if sup:
                winner, loser, sentence = sup
                label = adj
                lead = ("Đúng vậy. " if winner == a else "Không phải. ") if cmp.get("yesno") else ""
                return dict(base, answer=f"{lead}{_cap(winner)} {label} hơn {loser}. {_end(sentence)}", parts=facts,
                            passage=known[0].get("passage") if known else None, values=values)
            answer = f"Mình chưa đủ số liệu để so sánh chắc chắn. {details}"
        return dict(base, answer=answer, parts=facts, passage=known[0].get("passage"),
                    raw_answer=known[0].get("raw_answer", ""), values=values)


def build_default_manager(retriever=None, reader=None, **kwargs) -> DialogueManager:
    """Tiện cho demo/test: không có retriever thì dùng kho kiến thức mẫu đi kèm."""
    if retriever is None:
        import json
        import sys
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / "retrieval-model_Huy"))
        from retrieval_client import Retriever
        seed = json.loads((Path(__file__).parent / "eval" / "seed_kb.json").read_text(encoding="utf-8"))
        retriever = Retriever(seed)
    return DialogueManager(retriever, reader, **kwargs)
