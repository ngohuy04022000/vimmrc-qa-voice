"""Gói mã nguồn lõi cho hệ thống Text-to-Speech (TTS)."""

from .normalizer import normalize_vietnamese_text
from .tts_engine import BaseTTSEngine, EdgeTTSEngine, GTTSEngine, VITSEngine, get_tts_engine
from .vits_decomposed import DecomposedVITSOutput, VITSDecomposedTTS, print_decomposition_report

__all__ = [
    "normalize_vietnamese_text",
    "BaseTTSEngine",
    "EdgeTTSEngine",
    "GTTSEngine",
    "VITSEngine",
    "get_tts_engine",
    "VITSDecomposedTTS",
    "DecomposedVITSOutput",
    "print_decomposition_report",
]
