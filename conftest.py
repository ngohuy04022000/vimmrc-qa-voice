"""Test chạy không phụ thuộc Ollama: tắt LLM kiểm tra (bật lại bằng LLM_ASSIST=1 khi cần thử thật)."""
import os

os.environ.setdefault("LLM_ASSIST", "0")
