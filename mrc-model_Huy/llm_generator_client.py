"""Generator thay ViT5: dùng LLM local (Ollama) sinh câu trả lời từ (passage, câu
hỏi) đã retrieve. Cùng hợp đồng answer_question(question, passage) -> str với
MRCClient/LexicalBaselineClient, nên QAPipeline dùng được không cần đổi code.

Thí nghiệm trong llm_eval.py (so sánh công bằng n=50) cho thấy LLM generate và
ViT5 fine-tune cho kết quả gần tương đương (judge acc 54% vs 50%) — class này
đưa hướng đó vào pipeline thật thay vì chỉ ở script đánh giá, để dùng được qua
demo/API nếu muốn so sánh trực tiếp hoặc dùng làm phương án dự phòng khi chưa
có checkpoint ViT5.
"""
from __future__ import annotations

import os
import time

import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ornith-1.5:9b")

PROMPT = """Đọc đoạn văn sau và trả lời câu hỏi bằng một câu ngắn gọn,
trích hoặc diễn giải trực tiếp từ đoạn văn. Không giải thích thêm, không lặp lại
câu hỏi, chỉ đưa ra câu trả lời.

Đoạn văn:
{passage}

Câu hỏi: {question}

Trả lời:"""


class LLMGeneratorClient:
    """Sinh câu trả lời tự luận bằng LLM local qua Ollama, không cần checkpoint."""

    def __init__(self, model: str | None = None, *, max_tokens: int = 400, timeout: int = 180):
        self.model = model or OLLAMA_MODEL
        self.max_tokens = max_tokens
        self.timeout = timeout

    def _generate(self, prompt: str, *, retries: int = 3) -> str:
        for attempt in range(retries):
            try:
                resp = requests.post(
                    OLLAMA_URL,
                    json={"model": self.model, "prompt": prompt, "stream": False,
                          "options": {"temperature": 0, "num_predict": self.max_tokens}},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                return resp.json()["response"].strip()
            except (requests.RequestException, KeyError) as exc:
                if attempt == retries - 1:
                    raise RuntimeError(f"Ollama request failed after {retries} tries: {exc}") from exc
                time.sleep(2 * (attempt + 1))
        raise AssertionError("unreachable")

    def answer_question(self, question: str, passage: str) -> str:
        reply = self._generate(PROMPT.format(passage=passage, question=question))
        # Model này luôn "nghĩ" (chain-of-thought) trước khi trả lời, đóng khung
        # bằng </think>; coi phần trước đó là rác, không phải câu trả lời.
        if "</think>" in reply:
            return reply.rsplit("</think>", 1)[1].strip()
        return reply
