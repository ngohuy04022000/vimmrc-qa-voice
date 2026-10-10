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
from .vits_decomposed import DecomposedVITSOutput, VITSDecomposedTTS, print_decomposition_report
from .vivos_preprocessor import AudioSample, VIVOSPreprocessor

__all__ = [
    "normalize_vietnamese_text",
    "BaseTTSEngine",
    "EdgeTTSEngine",
    "GTTSEngine",
    "VITSEngine",
    "MatchaTTSEngine",
    "get_tts_engine",
    "VITSDecomposedTTS",
    "DecomposedVITSOutput",
    "print_decomposition_report",
    "VIVOSPreprocessor",
    "AudioSample",
    "calculate_mcd",
    "calculate_cer",
    "calculate_f0_rmse",
    "calculate_rtf",
    "generate_benchmark_markdown_table",
]
