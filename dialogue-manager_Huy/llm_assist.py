"""LLM cục bộ (Ollama) làm "người kiểm tra" bù cho ViT5 + BM25.

ViT5 trích đáp án tốt nhưng không biết từ chối: đoạn sai thì vẫn trả lời. LLM đọc hiểu
tốt hơn ở việc "đoạn này có trả lời được câu hỏi không" và "đáp án này có đúng theo đoạn
không", nhưng sinh đáp án dài, dễ lệch. Nên chia việc: ViT5 trả lời, LLM kiểm tra.

Mọi hàm trả None khi Ollama không dùng được (chưa chạy, thiếu model, quá hạn); khi đó
DialogueManager chạy như trước, không phụ thuộc LLM.
"""
from __future__ import annotations

import os
import re
import threading
import time

import requests

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_ASSIST_MODEL = os.getenv("OLLAMA_ASSIST_MODEL", "nemotron-3.5-bolt:e4b-q4_K_M")
MAX_PASSAGE_CHARS = 2400

SUPPORT_PROMPT = """Đoạn văn:
{passage}

Câu hỏi: {question}

Đoạn văn có nói về đúng chủ đề, nhân vật hoặc sự kiện mà câu hỏi nhắc tới, và có thông tin liên quan để trả lời
(kể cả phải suy ra hoặc giải thích từ các ý trong đoạn) không? Chỉ trả lời KHÔNG khi đoạn nói về chuyện hoàn toàn
khác, hoặc câu hỏi cần thông tin thời sự/cá nhân mà đoạn không hề có. Chỉ trả lời CÓ hoặc KHÔNG."""

VERIFY_PROMPT = """Đoạn văn:
{passage}

Câu hỏi: {question}
Đáp án đề xuất: {answer}

Theo đoạn văn, đáp án đề xuất có đúng và trả lời đúng ý câu hỏi không? Chỉ trả lời ĐÚNG hoặc SAI."""

ANSWER_PROMPT = """Đọc đoạn văn rồi trả lời câu hỏi bằng một câu ngắn, lấy thông tin trực tiếp từ đoạn văn.
Không giải thích thêm, không lặp lại câu hỏi.

Đoạn văn:
{passage}

Câu hỏi: {question}

Trả lời:"""

FIX_PROMPT = """Câu sau do máy nhận dạng giọng nói tiếng Việt ghi lại nên có thể sai chính tả hoặc nghe nhầm từ
(ví dụ "chuyện kiều" thật ra là "Truyện Kiều"). Hãy sửa lại cho đúng, giữ nguyên ý và độ dài, không thêm bớt
ý mới. Chỉ in ra câu đã sửa, không giải thích.

Câu: {text}
Câu đã sửa:"""


def _clip(passage: str) -> str:
    return passage if len(passage) <= MAX_PASSAGE_CHARS else passage[:MAX_PASSAGE_CHARS]


def _first_word(reply: str) -> str:
    return re.sub(r"[^\wÀ-ỹ]", "", reply.strip().split()[0].upper()) if reply.strip() else ""


class LLMAssist:
    def __init__(self, base: str | None = None, model: str | None = None, *, timeout: float = 25.0,
                 enabled: bool = True):
        self.base = (base or OLLAMA_BASE).rstrip("/")
        self.model = model or OLLAMA_ASSIST_MODEL
        self.timeout = timeout
        self.enabled = enabled
        self._ok_until = 0.0     # còn tin Ollama đang sống đến lúc này
        self._down_until = 0.0   # đã thấy chết: đừng thử lại ngay
        self._lock = threading.Lock()
        self.calls = 0

    def available(self) -> bool:
        if not self.enabled:
            return False
        now = time.time()
        if now < self._ok_until:
            return True
        if now < self._down_until:
            return False
        with self._lock:
            try:
                tags = requests.get(f"{self.base}/api/tags", timeout=2).json().get("models", [])
                ok = any(m.get("name") == self.model or m.get("model") == self.model for m in tags)
            except (requests.RequestException, ValueError):
                ok = False
            if ok:
                self._ok_until = now + 60
            else:
                self._down_until = now + 30
            return ok

    def _gen(self, prompt: str, max_tokens: int = 64) -> str | None:
        if not self.available():
            return None
        try:
            resp = requests.post(
                f"{self.base}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "think": False,
                      "options": {"temperature": 0, "num_predict": max_tokens}},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            self.calls += 1
            return resp.json()["response"].strip()
        except (requests.RequestException, KeyError, ValueError):
            self._down_until = time.time() + 30
            self._ok_until = 0.0
            return None

    def supports(self, question: str, passage: str) -> bool | None:
        reply = self._gen(SUPPORT_PROMPT.format(passage=_clip(passage), question=question), 4)
        if reply is None:
            return None
        word = _first_word(reply)
        return True if word.startswith("C") else False if word.startswith("KH") else None

    def verify(self, question: str, passage: str, answer: str) -> bool | None:
        reply = self._gen(VERIFY_PROMPT.format(passage=_clip(passage), question=question, answer=answer), 4)
        if reply is None:
            return None
        word = _first_word(reply)
        return True if word.startswith("ĐÚNG") or word.startswith("DUNG") else False if word.startswith("SAI") else None

    def answer(self, question: str, passage: str) -> str | None:
        reply = self._gen(ANSWER_PROMPT.format(passage=_clip(passage), question=question), 120)
        return reply or None

    def fix_transcript(self, text: str) -> str:
        """Sửa lỗi chính tả của STT; chỉ nhận bản sửa nếu còn gần bản gốc (chống LLM viết lại câu)."""
        reply = self._gen(FIX_PROMPT.format(text=text), max(32, len(text)))
        if not reply:
            return text
        fixed = reply.splitlines()[0].strip().strip('"“”')
        a, b = text.casefold(), fixed.casefold()
        if not fixed or abs(len(a) - len(b)) > max(6, len(a) // 4):
            return text
        shared = len(set(a.split()) & set(b.split()))
        return fixed if shared >= max(1, len(a.split()) // 2) else text
