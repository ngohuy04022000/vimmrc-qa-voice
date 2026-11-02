"""Conversational intent router and answer post-processor for ViMMRC Voice Q&A.

Handles greetings, assistant identity, capabilities, gratitude, farewell,
and formats raw MRC answers into natural, complete sentences for TTS.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional


def remove_accents(text: str) -> str:
    """Normalize and strip Vietnamese accents for robust intent matching."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "D")
    return text.lower()


class ConversationalIntentRouter:
    """Detect conversational intents and provide fluent Vietnamese assistant responses."""

    RESPONSES = {
        "greeting": (
            "Xin chào bạn! Tôi là trợ lý ảo hỏi đáp tiếng Việt ViMMRC. "
            "Tôi có thể giúp gì cho bạn hôm nay?"
        ),
        "identity": (
            "Tôi là trợ lý hỏi đáp thông minh tiếng Việt ViMMRC Voice Q&A, "
            "kết hợp mô hình nhận dạng giọng nói Whisper, hệ thống truy xuất tri thức RAG, "
            "mô hình đọc hiểu ViT5 và công nghệ giọng đọc tự nhiên Matcha-TTS."
        ),
        "capabilities": (
            "Tôi có thể lắng nghe câu hỏi qua micro bằng giọng nói, "
            "tự động tra cứu tài liệu trong kho tri thức tiếng Việt, "
            "suy luận câu trả lời chính xác bằng mô hình ViT5 "
            "và đọc câu trả lời trực tiếp cho bạn bằng âm thanh tự nhiên."
        ),
        "gratitude": (
            "Rất vui được hỗ trợ bạn! Nếu bạn có bất kỳ câu hỏi hoặc thắc mắc nào khác, "
            "hãy cứ hỏi tôi nhé."
        ),
        "farewell": (
            "Tạm biệt bạn! Chúc bạn một ngày tốt lành và nhiều niềm vui. "
            "Hẹn gặp lại bạn lần sau!"
        ),
        "how_are_you": (
            "Cảm ơn bạn đã quan tâm! Tôi là trợ lý AI nên luôn sẵn sàng 100% năng lượng "
            "để lắng nghe và giải đáp mọi câu hỏi của bạn."
        ),
    }

    @classmethod
    def match_intent(cls, question: str) -> Optional[tuple[str, str]]:
        """Return (intent_name, response_text) if matched, else None."""
        if not question or not question.strip():
            return None

        raw = question.strip().lower()
        norm = remove_accents(raw)
        # Pad with spaces to match whole words or phrases
        clean = " " + " ".join(re.sub(r"[^\w\s]", " ", norm).split()) + " "
        words = clean.strip().split()
        word_count = len(words)

        # 1. Identity intent
        identity_patterns = [
            r"\bban la ai\b",
            r"\bban ten (la )?gi\b",
            r"\bten (cua )?ban (la )?gi\b",
            r"\bgioi thieu (ban than|ve ban)\b",
            r"\bai (da )?(tao|sinh|phat trien|lam|viet) ra ban\b",
            r"\bnguon goc cua ban\b",
        ]
        if any(re.search(pat, clean) for pat in identity_patterns):
            return ("identity", cls.RESPONSES["identity"])

        # 2. Capabilities intent
        capability_patterns = [
            r"\bban (co the )?(lam|giup) (duoc )?(gi|nhung gi|nhung viec gi)\b",
            r"\bban giup (toi )?(duoc )?(gi|nhung gi)\b",
            r"\bban (co the )?giup (toi )?(duoc )?(gi|nhung gi)\b",
            r"\bchuc nang cua ban\b",
            r"\btinh nang cua ban\b",
            r"\bhuong dan su dung\b",
            r"\bcach (su )?dung ban\b",
            r"\bban biet lam (gi|nhung gi)\b",
        ]
        if any(re.search(pat, clean) for pat in capability_patterns):
            return ("capabilities", cls.RESPONSES["capabilities"])

        # 3. How are you
        how_are_you_patterns = [
            r"\bban (co )?khoe khong\b",
            r"\bhom nay the nao\b",
            r"\bdap ung the nao\b",
            r"\bsuc khoe the nao\b",
        ]
        if any(re.search(pat, clean) for pat in how_are_you_patterns):
            return ("how_are_you", cls.RESPONSES["how_are_you"])

        # 4. Gratitude
        gratitude_patterns = [
            r"\bcam on\b",
            r"\bthank(s| you)\b",
            r"\bban (tra loi |noi )?(gioi|thong minh|tuyet voi|hay) (qua|that day)\b",
            r"\brat (tot|tuyet)\b",
        ]
        if word_count <= 8 and any(re.search(pat, clean) for pat in gratitude_patterns):
            return ("gratitude", cls.RESPONSES["gratitude"])

        # 5. Farewell
        farewell_patterns = [
            r"\btam biet\b",
            r"\bhen gap lai\b",
            r"\bbye( bye)?\b",
            r"\bchuc (ban )?ngu ngon\b",
        ]
        if word_count <= 8 and any(re.search(pat, clean) for pat in farewell_patterns):
            return ("farewell", cls.RESPONSES["farewell"])

        # 6. Greeting intent
        greeting_patterns = [
            r"\bxin chao\b",
            r"\bchao (ban|em|anh|chi|bac|co|quy khach)\b",
            r"\bchao buoi (sang|chieu|toi)\b",
            r"^\s*chao\s*$",
            r"^\s*hello\b",
            r"^\s*hi\b",
            r"^\s*alo\b",
        ]
        if word_count <= 8 and any(re.search(pat, clean) for pat in greeting_patterns):
            return ("greeting", cls.RESPONSES["greeting"])

        return None

    @classmethod
    def get_conversational_response(cls, question: str) -> Optional[str]:
        """Return response string if question is conversational, else None."""
        match = cls.match_intent(question)
        return match[1] if match else None


def polish_answer(answer: str, question: str = "") -> str:
    """Post-process and clean raw MRC generated answer for natural TTS reading.

    Removes odd formatting, repairs trailing punctuation, capitalizes first character,
    and ensures a complete, polite Vietnamese answer.
    """
    if not answer or not answer.strip():
        return "Xin lỗi, tôi chưa tìm thấy thông tin phù hợp cho câu hỏi này trong kho tri thức."

    cleaned = answer.strip()

    # Remove enclosing quotation marks
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
        cleaned = cleaned[1:-1].strip()

    # Remove leading colons or hyphens
    cleaned = re.sub(r"^[:\-–—\s]+", "", cleaned).strip()

    # If answer ends without punctuation, add a period
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."

    # Capitalize first character
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned


def compute_phrase_overlap_score(question: str, passage: str) -> float:
    """Calculate continuous n-gram and phrase overlap bonus between question and passage."""
    if not question or not passage:
        return 0.0

    q_norm = remove_accents(question).lower()
    p_norm = remove_accents(passage).lower()

    # Extract cleaned word tokens
    q_words = [w for w in re.findall(r"\w+", q_norm) if len(w) > 1]
    if not q_words:
        return 0.0

    score = 0.0
    # 4-grams (high significance)
    if len(q_words) >= 4:
        for i in range(len(q_words) - 3):
            gram = " ".join(q_words[i:i + 4])
            if gram in p_norm:
                score += 5.0

    # 3-grams
    if len(q_words) >= 3:
        for i in range(len(q_words) - 2):
            gram = " ".join(q_words[i:i + 3])
            if gram in p_norm:
                score += 3.0

    # 2-grams
    if len(q_words) >= 2:
        for i in range(len(q_words) - 1):
            gram = " ".join(q_words[i:i + 2])
            if gram in p_norm:
                score += 1.0

    return score


def rerank_hits(question: str, hits: list[dict], top_k: int = 1) -> list[dict]:
    """Re-ranks retrieved passage hits by combining BM25 score with continuous phrase alignment.

    Supports both 'passage' and 'text' keys in hit dictionaries.
    """
    if not hits or len(hits) <= 1:
        return hits[:top_k]

    scored = []
    for hit in hits:
        text = hit.get("passage") or hit.get("text", "")
        base_score = float(hit.get("score", 0.0))
        phrase_bonus = compute_phrase_overlap_score(question, text)
        combined_score = base_score + phrase_bonus

        hit_copy = dict(hit)
        hit_copy["score"] = round(combined_score, 4)
        hit_copy["bm25_score"] = round(base_score, 4)
        hit_copy["phrase_bonus"] = round(phrase_bonus, 4)
        scored.append((combined_score, hit_copy))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_k]]

