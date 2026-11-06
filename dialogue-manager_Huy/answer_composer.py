"""Chọn câu bằng chứng, trích câu trả lời ngắn và soạn câu trả lời hoàn chỉnh để đọc (TTS).

- `HeuristicReader`: reader dự phòng khi chưa có checkpoint ViT5, trích cụm theo loại câu
  hỏi (số + đơn vị, năm/ngày, tên riêng, nơi chốn, vế sau "là") từ câu khớp nhất.
- `compose_answer`: biến cụm ngắn của reader ("Hà Nội") thành câu trọn vẹn
  ("Thủ đô của Việt Nam là Hà Nội."), và với câu hỏi tại sao/như thế nào/giới thiệu thì
  thêm câu bằng chứng từ đoạn văn, vì ViT5 được huấn luyện để trả lời cụm ngắn.
"""
from __future__ import annotations

import math
import re
from collections import Counter

from utterance import clean_utterance, nfc, question_type, vi_search, words

STOP = frozenset(
    "là gì ai ở đâu nào có của và được theo trong một những các với cho đã thì mà về hãy bao nhiêu mấy "
    "khi lúc nào năm sao tại vì như thế không phải đúng hay hoặc này kia đó ấy rằng thì bị do bởi "
    "người nơi cái điều nó họ ông bà anh chị em tôi bạn mình lại ra vào lên xuống đến từ trên dưới "
    "hơn nhất rất cũng đang sẽ vẫn còn chỉ hãy cho biết hỏi khoảng chừng tầm xấp xỉ tất cả".split())

UPPER = "A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"
_ABBREV = r"(?:TP|Tp|tp|TS|GS|PGS|ThS|St|Mr|Mrs|Dr|v\.v|tr|Th|CN|TCN|SCN)"


def split_sentences(passage: str) -> list[str]:
    text = re.sub(r"\s+", " ", nfc(passage)).strip()
    if not text:
        return []
    protected = re.sub(rf"\b({_ABBREV})\.", r"\1<DOT>", text)
    protected = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", protected)
    parts = re.split(r"(?<=[.!?…;])\s+(?=[\"“(]?[" + UPPER + "0-9])|\n+", protected)
    return [p.replace("<DOT>", ".").strip() for p in parts if p.strip()]


def content_terms(text: str) -> list[str]:
    return [w for w in words(text) if w not in STOP and len(w) > 1 or w.isdigit()]


def _bigrams(tokens: list[str]) -> set[tuple[str, str]]:
    return set(zip(tokens, tokens[1:]))


_VI_SYLLABLE = re.compile(r"^(?:ngh|ng|nh|ch|gh|gi|kh|ph|qu|th|tr|[bcdghklmnpqrstvx])?[aeiouy]{1,3}(?:ng|nh|ch|[cmnpt])?$")


def looks_foreign(word: str) -> bool:
    """'Tokyo', 'Fansipan', 'Bitcoin' không phải âm tiết tiếng Việt -> chắc là tên riêng."""
    from utterance import fold
    w = fold(word)
    return bool(w) and w.isalpha() and not _VI_SYLLABLE.match(w)


def entity_tokens(text: str) -> set[str]:
    """Từ thuộc tên riêng (viết hoa, trừ từ đầu câu đứng một mình), kèm chức danh đứng trước."""
    text = nfc(text)
    toks: set[str] = set()
    for m in re.finditer(_CAP_SPAN, text):
        span_words = m.group(0).split()
        if m.start() == 0 and len(span_words) == 1 and not looks_foreign(span_words[0]):
            continue
        toks.update(words(m.group(0)))
    for m in re.finditer(rf"\b(?i:{_TITLES})\s+(?={_CAP_WORD})", text):
        toks.update(words(m.group(0)))
    return toks


# Cặp từ gần nghĩa hay gặp giữa câu hỏi nói và văn viết (một chiều: từ hỏi -> từ trong văn bản)
SYNONYMS = {
    "hình": ["xuất", "tạo"], "thành": ["hiện"], "chế": ["phát", "minh"], "tạo": ["phát", "chế", "sáng"],
    "xây": ["dựng", "lập"], "lập": ["xây", "thành"], "viết": ["tác", "giả", "sáng"], "tiếng": ["giờ"],
    "giờ": ["tiếng"], "nước": ["quốc", "gia"], "quốc": ["nước"], "tìm": ["phát", "hiện"],
    "chinh": ["lên", "đỉnh"], "phục": ["lên", "đỉnh"], "mất": ["qua", "đời"], "chết": ["mất"],
    "trồng": ["canh", "tác"], "nằm": ["ở", "thuộc"], "lâu": ["mất", "kéo"], "đông": ["dân"],
}


def _expand(terms: set[str]) -> set[str]:
    return terms | {syn for t in terms for syn in SYNONYMS.get(t, [])}


def score_sentences(question: str, sentences: list[str]) -> list[float]:
    q_terms = set(content_terms(question))
    syn_terms = _expand(q_terms) - q_terms - STOP
    # Tên riêng là chủ đề, hay được thay bằng đại từ ("Người", "ông") ở câu sau; vị ngữ
    # ("mất", "sinh") mới phân biệt câu nào trả lời.
    ents = entity_tokens(question)
    q_bi = _bigrams(words(question))
    if not sentences:
        return []
    df = Counter(t for s in sentences for t in set(words(s)))
    n = len(sentences)
    scores = []
    for s in sentences:
        toks = words(s)
        tset = set(toks)
        overlap = sum((math.log1p(n / df[t]) + 1.0) * (0.35 if t in ents else 1.6) for t in q_terms if t in tset)
        overlap += sum(0.6 for t in syn_terms if t in tset)
        bi = sum(1.5 for b in q_bi & _bigrams(toks) if not (b[0] in ents and b[1] in ents))
        scores.append((overlap + bi) / (1 + 0.02 * len(toks)))
    return scores


def best_sentence(question: str, passage: str) -> tuple[int, list[str]]:
    sentences = split_sentences(passage)
    if not sentences:
        return -1, []
    scores = score_sentences(question, sentences)
    return max(range(len(sentences)), key=lambda i: (scores[i], -i)), sentences


def support(question: str, passage: str) -> float:
    """Tỉ lệ từ nội dung của câu hỏi xuất hiện trong đoạn văn (0..1), để từ chối khi lạc đề."""
    terms = set(content_terms(question))
    if not terms:
        return 1.0
    ptoks = set(words(passage))
    return sum(t in ptoks for t in terms) / len(terms)


# --- Reader dự phòng -------------------------------------------------------------

_NUM = (r"(?:khoảng |gần |hơn |trên |dưới |chừng |xấp xỉ |chỉ |tới |đến )?(?<![\d.,])\d[\d.,]*"
        r"(?:\s?(?:đến|tới|-|–)\s?\d[\d.,]*)?(?:\s?(?:triệu|tỷ|tỉ|nghìn|ngàn|vạn|trăm))?")
_UNITS = (r"(?:km²|km2|m²|m2|m³|km/h|km|m|cm|mm|kg|tấn|g|°C|độ C|độ|%|phần trăm|năm|tuổi|người|dân tộc|tỉnh|thành phố|"
          r"quốc gia|nước|đảo|quận|huyện|xã|ngày|tháng|giờ|phút|giây|lần|loại|loài|chiếc|con|cây|ki-lô-mét|mét|"
          r"ki-lô-gam|héc-ta|ha|đồng|USD|đô la|bài|chương|tập|thành viên|nguyên tố|hành tinh|vệ tinh|ngôn ngữ|"
          r"ca sĩ|học sinh|sinh viên|giải|huy chương|bàn thắng|cầu thủ|tầng|ngọn|dòng|tiếng)")
_DIMENSIONS = [  # gợi ý trong câu hỏi -> đơn vị mong đợi trong câu trả lời
    (r"nặng|khối lượng|cân nặng", r"tấn|kg|ki-lô-gam|gam|g"),
    (r"diện tích|rộng bao nhiêu|rộng khoảng", r"km²|km2|m²|m2|ha|héc-ta"),
    (r"dân số|bao nhiêu người|đông dân", r"triệu người|nghìn người|người|triệu|tỷ người|tỷ"),
    (r"nhiệt độ|bao nhiêu độ|nóng bao nhiêu|lạnh bao nhiêu", r"°C|độ C|độ"),
    (r"dài|cao|sâu|xa|cách|chiều|độ cao|bao nhiêu mét|bao nhiêu km", r"km|m|cm|mm|mét|ki-lô-mét"),
    (r"bao nhiêu tuổi|thọ", r"tuổi"),
    (r"bao lâu|mất bao nhiêu thời gian|kéo dài", r"năm|tháng|ngày|giờ|phút|giây|ngày đêm"),
]
_DATE = (r"(?:ngày \d{1,2} tháng \d{1,2} năm \d{3,4}|ngày \d{1,2}/\d{1,2}/\d{3,4}|tháng \d{1,2} năm \d{3,4}|"
         r"(?:năm )?(?<![\d.,])\d{3,4}(?![\d]|[.,]\d)(?:\s?(?:TCN|SCN))?|thế kỷ (?:thứ )?[IVXLC\d]+(?:\s?(?:TCN|SCN))?)")
_CAP_WORD = rf"(?<!\w)[{UPPER}][\w'-]*"
_CAP_SPAN = rf"{_CAP_WORD}(?:\s+{_CAP_WORD})*"
_NOT_NAME = r"Người|Ông|Bà|Ngày|Năm|Tháng|Theo|Trong|Sau|Trước|Khi|Vào|Từ|Đến|Tại|Ở|Với|Các|Những|Một|Đây|Đó|Nhà|Vua|Chủ tịch|Tổng thống|Thủ tướng|Đại tướng|Nhà thơ|Nhà văn|Nhạc sĩ"
_NOT_NAME_SET = {w.casefold() for w in re.findall(r"\w+", _NOT_NAME)}
_TITLES = r"chủ tịch|đại tướng|tổng thống|thủ tướng|vua|nhà thơ|nhà văn|nhà khoa học|nhà phát minh|nhạc sĩ|danh tướng|bác sĩ|giáo sư|xạ thủ|phi hành gia"
_TWO_WORD_VERBS = {"phát minh", "phát hiện", "chế tạo", "sáng tác", "sáng lập", "đưa ra", "tìm ra", "xây dựng",
                   "lãnh đạo", "chỉ huy", "đặt chân", "lên tới", "lên ngôi", "đánh thắng", "đánh tan", "tìm thấy",
                   "khám phá", "viết ra", "tạo ra", "đặt tên", "thành lập", "giành được", "vô địch"}
_LOC_PREP = r"(?:nằm ở|nằm tại|tọa lạc tại|tọa lạc ở|ở|tại|thuộc|đặt tại|đặt ở|bắt nguồn từ|chảy qua|chảy vào|đổ ra)"


_NUM_WORDS = r"một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|mười một|mười hai|trăm|nghìn"


def _in_date(sentence: str, pos: int) -> bool:
    """Số ở vị trí pos thuộc một ngày tháng ('ngày 1 tháng 7 năm 2025')."""
    before = sentence[max(0, pos - 8):pos].casefold()
    after = sentence[pos:pos + 16].casefold()
    return bool(re.search(r"(?:ngày|tháng|năm)\s*$", before)) or bool(re.match(r"\d+\s*(?:tháng\s*\d|/\d)", after))


def _words_after(question: str, cue: str, n: int = 2) -> list[str]:
    m = vi_search(cue + r"\s+((?:\w+\s*){1,%d})" % n, question)
    return m.group(1).split() if m else []


def copula_span(question: str, sentence: str) -> str | None:
    """Câu hỏi dạng 'X nào là Y' / 'Y là X nào' / 'X nào <vị ngữ>':
    tìm 'Y là Z', 'Z là Y' hoặc 'Z là X' trong câu bằng chứng."""
    q = clean_utterance(question)
    m = re.match(r"^(?P<noun>.+?)\s+nào\s+(?:là\s+)?(?P<rest>.+)$", q, flags=re.IGNORECASE) or \
        re.match(r"^(?P<rest>.+?)\s+là\s+(?P<noun>[\w ]+?)\s+nào$", q, flags=re.IGNORECASE)
    if not m:
        return None
    noun, rest = m.group("noun").strip(), m.group("rest").strip()
    if len(noun.split()) > 3:
        return None
    heads = [rest]
    if " của " in rest.casefold():
        heads.append(rest[: rest.casefold().find(" của ")])
    for head in heads:
        if not content_terms(head):
            continue
        mm = re.search(rf"\b(?i:{re.escape(head)})\s+(?:chính\s+)?là\s+({_CAP_SPAN})", sentence)
        if mm:
            return mm.group(1)
    # "Sa mạc Sahara ở Bắc Phi là sa mạc ..." khi hỏi "... là sa mạc nào"
    mm = re.search(rf"(?i:{re.escape(noun)})\s+({_CAP_SPAN})[^.;]{{0,50}}?\s+(?:là|được xem là|được coi là)\s+(?:một\s+)?(?i:{re.escape(noun)})", sentence)
    if mm and mm.group(1).casefold() not in q.casefold():
        return mm.group(1)
    # "Lào là quốc gia duy nhất ..." khi hỏi "Quốc gia nào ..."; "hang Sơn Đoòng, được xem là hang động ..."
    mm = re.search(rf"({_CAP_SPAN})\s*,?\s+(?:là|chính là|được xem là|được coi là|được gọi là|được mệnh danh là)\s+"
                   rf"(?:một\s+)?(?:trong\s+những\s+)?(?i:{re.escape(noun)})", sentence)
    if mm and mm.group(1).casefold() not in q.casefold():
        return mm.group(1)
    return None


def gap_span(question: str, sentence: str) -> str | None:
    """Lấp chỗ trống: 'Trần Hưng Đạo là tác giả của tác phẩm nào' -> tìm 'tác giả của' trong câu
    bằng chứng rồi lấy cụm theo sau ('Hịch tướng sĩ'). Neo = 1-3 từ ngay trước từ để hỏi."""
    q = clean_utterance(question)
    m = re.search(r"^(?P<pre>.*?)(?:\s+(?:\w+\s+)?nào|\s+gì|\s+ai)$", q, flags=re.I)
    if not m or not m.group("pre"):
        return None
    pre_words = m.group("pre").split()
    low = sentence.casefold()
    for k in (3, 2):
        if len(pre_words) < k:
            continue
        anchor = " ".join(pre_words[-k:]).casefold()
        if not content_terms(anchor):
            continue
        idx = low.find(anchor)
        if idx < 0:
            continue
        tail = sentence[idx + len(anchor):].strip()
        tail = re.split(r"[,.;:()]|\s(?:và|nhưng|vì|để|khi|sau khi|trong khi)\s", tail)[0].strip()
        tail = re.sub(r"^(?:là|chính là)\s+", "", tail)
        if tail and len(tail.split()) <= 8 and not set(words(tail)) <= set(words(q)):
            return tail
    return None


def extract_span(question: str, sentence: str, qtype: str | None = None) -> str | None:
    """Cụm trả lời ngắn từ câu bằng chứng theo loại câu hỏi; None nếu không chắc."""
    qtype = qtype or question_type(question)
    span = _extract_span(question, sentence, qtype)
    if span and qtype == "person":
        # "Edmund Hillary và Tenzing Norgay": giữ đủ cả nhóm người
        m = re.search(rf"{re.escape(span)}((?:\s*,\s*{_CAP_SPAN})*\s+và\s+{_CAP_SPAN})", sentence)
        if m:
            span += m.group(1)
    return span


def _extract_span(question: str, sentence: str, qtype: str) -> str | None:
    q_low = nfc(question).casefold()
    if qtype not in {"time", "quantity"}:
        span = copula_span(question, sentence)
        if span:
            return span
    if qtype == "time":
        dates = [m for m in re.finditer(_DATE, sentence, flags=re.IGNORECASE) if m.group(0).casefold() not in q_low]
        if not dates:
            return None
        # "sinh năm 1765 và mất năm 1820" + hỏi "mất": lấy mốc đứng sau vị ngữ gần nhất
        ents = entity_tokens(question)
        preds = [t for t in content_terms(question) if t not in ents]
        low = sentence.casefold()
        anchors = [mm.end() for t in preds for mm in re.finditer(rf"(?<!\w){re.escape(t)}(?!\w)", low)]
        if anchors and len(dates) > 1:
            def dist(m):
                return min((m.start() - a) if m.start() >= a else 1000 + (a - m.start()) for a in anchors)
            return min(dates, key=dist).group(0)
        return dates[0].group(0)
    if qtype == "quantity":
        head = _words_after(question, r"(?:bao nhiêu|mấy)", 2)
        # 1) số đứng ngay trước danh từ được hỏi: "bao nhiêu ngày đêm" -> "56 ngày đêm"
        for k in (2, 1):
            if len(head) >= k and head[k - 1].casefold() not in STOP | {"mỗi"}:
                noun = " ".join(head[:k])
                m = re.search(rf"({_NUM})\s+({re.escape(noun)})(?!\w)", sentence, flags=re.IGNORECASE)
                if m and not _in_date(sentence, m.start(1)):
                    return f"{m.group(1).strip()} {m.group(2)}"
        # 2) số có đơn vị đúng chiều đo: "nặng" -> tấn/kg
        want = next((units for cue, units in _DIMENSIONS if vi_search(cue, question)), None)
        if want:
            for m in re.finditer(rf"({_NUM})\s?({want})(?![\w²³])", sentence):
                if m.group(1).strip().casefold() not in q_low and not _in_date(sentence, m.start(1)):
                    unit = m.group(2)
                    return f"{m.group(1).strip()}{'' if unit.startswith(('%', '°')) else ' '}{unit}"
        # 3) số bất kỳ (bỏ số trong ngày tháng), ưu tiên số có đơn vị
        best = None
        for m in re.finditer(rf"({_NUM})(?:\s?({_UNITS})(?![\w²³]))?", sentence):
            num = m.group(1).strip()
            if (num.casefold() in q_low and not m.group(2)) or _in_date(sentence, m.start(1)):
                continue
            unit = m.group(2) or ""
            if unit in {"tháng", "năm"} and re.match(r"\s?\d", sentence[m.end():]):
                continue
            span = f"{num} {unit}".strip() if unit and not unit.startswith(("%", "°", "²")) else f"{num}{unit}"
            if re.fullmatch(r"\d{4}", num) and not unit and best is not None:
                continue
            if unit or best is None:
                best = span
                if unit:
                    break
        if best is None:  # số viết bằng chữ: "hai vệ tinh", "sáu thanh điệu"
            if head:
                m = re.search(rf"\b({_NUM_WORDS})\s+({re.escape(head[0])})", sentence, flags=re.IGNORECASE)
                if m:
                    return f"{m.group(1)} {m.group(2)}"
            m = re.search(rf"\b(?:thứ\s+)?({_NUM_WORDS})\b", sentence, flags=re.IGNORECASE)
            if m and vi_search(r"thứ mấy|thứ bao nhiêu", question):
                return m.group(0)
        return best
    if qtype == "person":
        q_tokens = set(words(question))
        cq = clean_utterance(question)
        obj = re.search(r"(\w+(?:\s+\w+)?)\s+ai$", cq, flags=re.IGNORECASE)      # "... để thờ ai"
        subj = re.match(r"^(?:ai|người nào)\s+(?:đã\s+|là người\s+)?(\w+(?:\s+\w+)?)", cq, flags=re.IGNORECASE)
        for verb in ([obj.group(1), obj.group(1).split()[-1]] if obj else []):
            mm = re.search(rf"\b(?i:{re.escape(verb)})\s+(?:(?i:{_TITLES})\s+)?({_CAP_SPAN})", sentence)
            if mm and not set(words(mm.group(1))) <= q_tokens:
                return mm.group(1)
        if subj and subj.group(1).split()[0].casefold() not in {"là", "được"}:
            two = subj.group(1)
            verb = two if two.casefold() in _TWO_WORD_VERBS else two.split()[0]
            mm = re.search(rf"({_CAP_SPAN})(?:\s+\w+){{0,4}}?\s+(?i:{re.escape(verb)})", sentence)
            if mm:
                span = re.sub(rf"^(?:{_NOT_NAME})\s+", "", mm.group(1))
                if len(words(span)) >= 2 and not set(words(span)) <= q_tokens:
                    return span
        for m in re.finditer(_CAP_SPAN, sentence):
            span = re.sub(rf"^(?:{_NOT_NAME})\s+", "", m.group(0))
            toks = words(span)
            if words(m.group(0))[0] in _NOT_NAME_SET and len(toks) < 2:
                continue
            if re.search(r"(?:tại|ở|thuộc|từ|đến|tới|của)\s*$", sentence[:m.start()]):
                continue  # đứng sau giới từ nơi chốn/sở hữu: không phải chủ thể hành động
            if len(toks) >= 2 and not set(toks) <= q_tokens:
                return span
        return None
    if qtype == "location":
        noun = vi_search(r"(tỉnh|thành phố|nước|quốc gia|châu lục|châu|vùng|miền|huyện|quận|biển|đại dương|sông|dãy núi) nào", question)
        if noun:
            m = re.search(rf"\b(?i:{noun.group(1)})\s+({_CAP_SPAN})", sentence)
            if m and m.group(1).casefold() not in q_low:
                return m.group(1)
        for m in re.finditer(rf"\b{_LOC_PREP}\s+([^,.;()]+)(?:,\s*({_CAP_SPAN}))?", sentence):
            span = m.group(1).strip()
            if len(span.split()) > 9 or span.casefold() in q_low or not re.match(rf"[{UPPER}]|(?:tỉnh|thành phố|làng|xã|huyện|quận|vùng|miền|khu vực|châu|nước|biển|vịnh|sông|đảo|bán đảo|đồng bằng|cao nguyên|dãy|núi|phía|trung tâm|thủ đô|bờ)\b", span):
                continue
            return f"{span}, {m.group(2)}" if m.group(2) else span
        return gap_span(question, sentence) if noun else None
    if qtype in {"definition", "factoid"}:
        subj = re.sub(r"\s+(?:tên\s+)?là\s+(?:gì|ai|cái gì)$", "", clean_utterance(question), flags=re.I)
        if subj == clean_utterance(question):
            return gap_span(question, sentence)
        low = sentence.casefold()
        candidates = [subj]
        if " của " in subj.casefold():  # "thủ đô của Pháp" -> câu viết "Pháp ..., thủ đô là Paris"
            candidates.append(subj[: subj.casefold().find(" của ")])
        ent_tail = re.match(rf"^(.+?)\s+(?:{_CAP_SPAN})$", subj)  # "thành phố lớn nhất Úc" -> "thành phố lớn nhất"
        if ent_tail and content_terms(ent_tail.group(1)):
            candidates.append(ent_tail.group(1))
        m_head = re.match(r"^(\w+\s+\w+)\s+(?:nước|thành phố|tỉnh)\s", subj, flags=re.I)  # "thủ đô nước Pháp"
        if m_head:
            candidates.append(m_head.group(1))
        for cand in candidates:
            idx = low.find(cand.casefold())
            if idx < 0:
                continue
            m = re.match(r"\s*(?:,\s*)?(?:chính\s+)?là\s+(.+?)(?:[.;]|$)", sentence[idx + len(cand):])
            if m:
                span = re.split(r",\s*(?:còn|nhưng|trong khi|song|tuy nhiên)\b", m.group(1))[0]
                first = span.split(",")[0].strip()
                if "," in span and re.fullmatch(_CAP_SPAN, first):
                    span = first  # "Nguyễn Sinh Cung, sinh ngày ..." -> tên là đủ
                return span.rstrip(" .,")
        return gap_span(question, sentence)
    return None


_PRONOUN_SUBJ = re.compile(r"(?:(?:^|,\s*|\.\s*)(?:[Ôô]ng|[Bb]à|Người|[Hh]ọ)\b|\b(?:của|cho|với) (?:ông|bà|Người|họ)\b)")


def passage_main_name(passage: str, question: str = "") -> str | None:
    """Tên người/vật chính của đoạn: cụm viết hoa nhiều từ đầu tiên của câu đầu, khác tên trong câu hỏi."""
    q_tokens = set(words(question))
    first = split_sentences(passage)[:1]
    for m in re.finditer(_CAP_SPAN, first[0] if first else ""):
        span = re.sub(rf"^(?:{_NOT_NAME})\s+", "", m.group(0))
        toks = words(span)
        if len(toks) >= 2 and not set(toks) <= q_tokens:
            return span
    return None


class HeuristicReader:
    """Reader không cần mô hình: câu khớp nhất có chứa cụm đúng loại câu hỏi, không có thì cả câu."""

    def answer_question(self, question: str, passage: str) -> str:
        sentences = split_sentences(passage)
        if not sentences:
            return ""
        scores = score_sentences(question, sentences)
        order = sorted(range(len(sentences)), key=lambda i: (-scores[i], i))
        qtype = question_type(question)
        top = scores[order[0]]
        noun = vi_search(r"(nước|quốc gia|thành phố|tỉnh) nào", question) if qtype == "location" else None
        if noun:
            # "Đền Angkor Wat nằm ở nước nào" -> đoạn mở đầu "Campuchia là quốc gia ..."
            m = re.match(rf"^({_CAP_SPAN})\s*(?:,[^,]*,\s*)?\s+là\s+(?:một\s+)?(?i:{noun.group(1)}|quốc gia|nước)\b",
                         sentences[0])
            if m and m.group(1).casefold() not in nfc(question).casefold():
                in_best = extract_span(question, sentences[order[0]], qtype)
                if not in_best or not re.search(rf"\b{noun.group(1)}\s+{re.escape(in_best)}", sentences[order[0]], re.I):
                    return m.group(1)
        for i in order[:4]:
            if scores[i] <= 0 or scores[i] < 0.3 * top:
                break
            span = extract_span(question, sentences[i], qtype)
            if span:
                return span
            if qtype == "person" and _PRONOUN_SUBJ.search(sentences[i]):
                # "Năm 1879, ông chế tạo ..." -> "ông" là nhân vật chính của đoạn
                name = passage_main_name(passage, question)
                if name:
                    return name
        return sentences[order[0]]


# --- Soạn câu trả lời -----------------------------------------------------------

_WH = [
    (r"vào năm nào|vào năm bao nhiêu|năm nào|năm bao nhiêu", "year"),
    (r"vào thời gian nào|vào lúc nào|vào khi nào|khi nào|lúc nào|bao giờ|thời điểm nào|ngày nào|tháng nào|thế kỷ nào", "time"),
    (r"bao nhiêu|mấy|bao lâu|bao xa", "qty"),
    (r"ở đâu|tại đâu|đâu|ở nơi nào|nơi nào|chỗ nào", "loc"),
    (r"(?:nước|quốc gia|tỉnh|thành phố|vùng|châu lục|châu|miền|công trình|tác phẩm|nhân vật|sự kiện|loài vật|"
     r"con vật|hành tinh|môn thể thao|ngọn núi|con sông|dòng sông|triều đại|đội bóng|đội tuyển|món ăn|ngôn ngữ|"
     r"tôn giáo|dân tộc|ngày lễ|lễ hội|nhà thơ|nhà văn|nhà khoa học|di sản|loài|màu|giải|môn|bộ phận|cơ quan|"
     r"sa mạc|đại dương|hang động|hòn đảo|biển|hồ|vịnh|đền|chùa|cuộc khởi nghĩa|trận đánh|vị vua|hang|đảo|núi|sông) nào", "which"),
    (r"\w+ nào", "which"),
    (r"là ai|ai", "who"),
    (r"là gì|là cái gì|cái gì|điều gì|gì", "what"),
]
_UNIT_WORDS = {"mét", "m", "km", "ki-lô-mét", "cây", "số", "kg", "ki-lô-gam", "tấn", "độ", "năm", "tuổi",
               "phần", "trăm", "giờ", "phút", "giây", "ngày", "tháng", "lần", "km²", "người"}


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def _end(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text if text[-1] in ".!?…" else text + "."


def answer_covers_question(question: str, answer: str) -> bool:
    q = set(content_terms(question))
    if not q:
        return False
    a = set(words(answer))
    return len(q & a) / len(q) >= 0.6


def fill_template(question: str, answer: str) -> str | None:
    """Thế cụm trả lời vào vị trí từ để hỏi: 'Thủ đô của Nhật là gì' + 'Tokyo' -> 'Thủ đô của Nhật là Tokyo.'"""
    q = clean_utterance(question)
    a = answer.strip().rstrip(".")
    if re.match(r"(?:Ngày|Tháng|Năm|Thế kỷ|Vào|Khoảng|Hơn|Gần|Trên|Dưới)\b", a):
        a = a[:1].lower() + a[1:]
    if not a or len(a.split()) > 25:
        return None
    low = q.casefold()
    for pattern, kind in _WH:
        m = re.search(rf"(?:^|\s)({pattern})(?=\s|$)", low)
        if not m:
            continue
        start, end = m.start(1), m.end(1)
        before, after = q[:start].rstrip(), q[end:].lstrip()
        a_low = a.casefold()
        if kind == "year":
            filler = a if re.match(r"(?:năm|ngày|tháng|thế kỷ|vào)\b", a_low) else f"năm {a}"
            if re.match(r"(?:ngày|tháng)\b", a_low) and not re.search(r"(?:sinh|mất|vào|từ|đến|tới)$", before.casefold()):
                filler = f"vào {filler}"
        elif kind == "time":
            filler = a if re.match(r"(?:vào|từ|trong|khi|lúc|sau|trước|đầu|cuối|giữa)\b", a_low) else f"vào {a}"
            if re.search(r"(?:sinh|mất|vào|từ|đến|tới)$", before.casefold()):
                filler = re.sub(r"^vào\s+", "", filler)
            if not before:  # "Khi nào X?" đứng đầu: "X vào A"
                return _end(_cap(f"{after} {filler}"))
        elif kind == "qty":
            filler = a
            if re.search(r"(?:khoảng|chừng|độ|tầm)$", before.casefold()) and \
                    re.match(r"(?:khoảng|gần|hơn|trên|dưới|chừng|xấp xỉ)\b", a_low):
                before = before.rsplit(" ", 1)[0] if " " in before else ""
            nxt = after.split()
            if nxt:
                head = nxt[0].casefold()
                two = " ".join(nxt[:2]).casefold()
                if two in a_low:
                    after = " ".join(nxt[2:])
                elif head in a_low.split() or (head in _UNIT_WORDS and re.search(r"\d\s*[^\d\s.,]", a)):
                    after = " ".join(nxt[1:])
        elif kind == "loc":
            filler = a
            if m.group(1) in {"ở đâu", "tại đâu", "ở nơi nào"} and not re.match(r"(?:ở|tại|trong|thuộc|gần)\b", a_low):
                filler = f"{m.group(1).split()[0]} {a}"
            if m.group(1) == "đâu" and not before.casefold().endswith((" ở", " tại", " từ", " đến", " về")) \
                    and not re.match(r"(?:ở|tại|trong|thuộc|gần)\b", a_low):
                filler = f"ở {a}"
            if re.match(r"(?:ở|tại)\b", a_low) and before.casefold().endswith((" ở", " tại")):
                before = before[: before.casefold().rfind(" ")]
        elif kind == "which":
            filler = a
            noun = m.group(1)[: -len(" nào")]
            if not before and not re.match(r"(?:là|chính là)\b", after.casefold()) \
                    and not a_low.startswith(noun.casefold()) and len(a.split()) <= 6:
                filler = f"{a} là {noun.casefold()}"  # "Quốc gia nào ..." -> "Lào là quốc gia ..."
        elif kind == "who":
            filler = a if m.group(1) == "ai" else f"là {a}"
        else:  # what
            filler = a if m.group(1) in {"gì", "cái gì", "điều gì"} else f"là {a}"
        if a_low in before.casefold() and len(a_low) > 3:
            return None  # câu trả lời lặp lại chủ ngữ: không ghép được
        tail = before.rsplit(" ", 1)
        if before and filler.split()[0].casefold() == tail[-1].casefold():
            # "... sau sự kiện nào" + "Sau khi bán ..." -> "... sau khi bán ...", không "sau Sau khi"
            before = tail[0] if len(tail) > 1 else ""
            filler = tail[-1] + filler[len(tail[-1]):]
        sentence = " ".join(part for part in (before, filler, after) if part)
        sentence = re.sub(r"\b(đã|là|được|có|của|ở|vào|năm|ngày|đầu tiên|nhất)(\s+\1\b)+", r"\1", sentence, flags=re.I)
        sentence = re.sub(r"\b(đầu tiên|nhất)\b(.*)\s\1$", r"\1\2", sentence)
        return _end(_cap(sentence))
    return None


def evidence_sentences(question: str, passage: str, answer: str = "", limit: int = 2) -> list[str]:
    """Câu chứa câu trả lời (nếu có) rồi các câu khớp câu hỏi nhất, giữ thứ tự trong đoạn."""
    sentences = split_sentences(passage)
    if not sentences:
        return []
    scores = score_sentences(question, sentences)
    chosen: list[int] = []
    a = answer.strip().rstrip(".").casefold()
    if a:
        for i, s in enumerate(sentences):
            if a in s.casefold():
                chosen.append(i)
                break
    top = max(scores) if scores else 0
    for i in sorted(range(len(sentences)), key=lambda i: (-scores[i], i)):
        if len(chosen) >= limit:
            break
        # câu thêm phải khớp ít nhất một nửa câu tốt nhất, tránh kéo theo câu lạc ý
        if i not in chosen and scores[i] > 0 and (not chosen or scores[i] >= 0.5 * top):
            chosen.append(i)
    if not chosen:
        chosen = [0]
    return [sentences[i] for i in sorted(chosen)]


def summarize(passage: str, limit: int = 3) -> str:
    """Tóm tắt trích rút: câu đầu + các câu có nhiều từ khóa chung với cả đoạn."""
    sentences = split_sentences(passage)
    if len(sentences) <= limit:
        return " ".join(sentences)
    freq = Counter(t for s in sentences for t in set(content_terms(s)))
    scores = [sum(freq[t] for t in set(content_terms(s))) / (1 + len(words(s))) ** 0.5 for s in sentences]
    scores[0] += max(scores) * 0.6  # câu chủ đề thường đứng đầu
    keep = sorted(sorted(range(len(sentences)), key=lambda i: -scores[i])[:limit])
    return " ".join(sentences[i] for i in keep)


def restore_case(text: str, passage: str) -> str:
    """Câu hỏi từ STT/gõ thường ('vịnh hạ long') -> viết hoa tên riêng theo đoạn văn ('vịnh Hạ Long')."""
    names = {}
    for m in re.finditer(_CAP_SPAN, passage):
        span = m.group(0)
        if m.start() > 0 and passage[m.start() - 2:m.start()].strip() not in {".", "!", "?"} or len(span.split()) > 1:
            names.setdefault(span.casefold(), span)
    for low, proper in sorted(names.items(), key=lambda kv: -len(kv[0])):
        if len(low) > 2:
            text = re.sub(rf"(?<!\w){re.escape(low)}(?!\w)", proper, text)
    return text


def compose_answer(question: str, answer: str, passage: str, qtype: str | None = None) -> str:
    """Câu trả lời hoàn chỉnh, tự nhiên khi đọc to."""
    return _cap(restore_case(_compose(question, answer, passage, qtype), passage))


def _compose(question: str, answer: str, passage: str, qtype: str | None = None) -> str:
    qtype = qtype or question_type(question)
    answer = (answer or "").strip()
    if qtype == "summary":
        return _end(summarize(passage))
    if qtype in {"why", "how", "describe", "list"}:
        short = len(answer.split()) < 9
        if qtype == "describe":
            ev = evidence_sentences(question, passage, answer, limit=3)
            return " ".join(_end(s) for s in ev)
        whole = answer.rstrip(".") in {x.rstrip(".") for x in split_sentences(passage)}
        if short or not answer or whole:
            ev = evidence_sentences(question, passage, answer, limit=2)
            body = " ".join(_end(s) for s in ev)
            if answer and answer.casefold().rstrip(".") not in body.casefold():
                lead = answer if qtype != "why" or re.match(r"(?:vì|do|bởi|tại|nhờ)\b", answer.casefold()) \
                    else f"Vì {answer[:1].lower() + answer[1:]}"
                body = f"{_end(_cap(lead))} {body}"
            return body
        return _end(_cap(answer))
    if not answer:
        return ""
    whole_sentence = answer.rstrip(".") in {x.rstrip(".") for x in split_sentences(passage)}
    if whole_sentence or len(answer.split()) >= 12 or answer_covers_question(question, answer):
        return _end(_cap(answer))
    filled = fill_template(question, answer)
    return filled or _end(_cap(answer))


# --- Số liệu để so sánh -----------------------------------------------------------

_MULT = {"nghìn": 1e3, "ngàn": 1e3, "vạn": 1e4, "triệu": 1e6, "tỷ": 1e9, "tỉ": 1e9, "trăm": 1e2}


def parse_quantity(text: str) -> float | None:
    """Số đầu tiên trong cụm, hiểu dấu chấm hàng nghìn kiểu Việt và hệ số 'triệu', 'tỷ'."""
    m = re.search(r"(\d[\d.,]*)\s*(triệu|tỷ|tỉ|nghìn|ngàn|vạn|trăm)?", text or "")
    if not m:
        return None
    raw = m.group(1).rstrip(".,")
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", raw):
        value = float(raw.replace(".", ""))
    elif re.fullmatch(r"\d{1,3}(?:,\d{3})+", raw) and not m.group(2):
        value = float(raw.replace(",", ""))
    else:
        try:
            value = float(raw.replace(",", "."))
        except ValueError:
            return None
    return value * _MULT.get(m.group(2) or "", 1.0)
