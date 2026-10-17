"""Gói mã nguồn lõi của phân hệ Text-to-Speech tiếng Việt (Matcha-TTS, VITS, Edge-TTS, gTTS)."""

from .evaluator import (
    calculate_cer,
    calculate_f0_rmse,
    calculate_mcd,
    calculate_rtf,
    generate_benchmark_markdown_table,
)
from .matcha_engine import MatchaTTSEngine
from .normalizer import normalize_vietnamese_text
from .tts_engine import BaseTTSEngine, EdgeTTSEngine, GTTSEngine, VITSEngine, get_tts_engine

__all__ = [
    "normalize_vietnamese_text",
    "BaseTTSEngine",
    "EdgeTTSEngine",
    "GTTSEngine",
    "VITSEngine",
    "MatchaTTSEngine",
    "get_tts_engine",
    "calculate_mcd",
    "calculate_cer",
    "calculate_f0_rmse",
    "calculate_rtf",
    "generate_benchmark_markdown_table",
]
