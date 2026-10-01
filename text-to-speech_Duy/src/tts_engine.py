"""Module các TTS Engine (Edge-TTS, gTTS).

Cung cấp lớp cơ sở BaseTTSEngine và các triển khai cụ thể:
- EdgeTTSEngine: Giọng đọc nơ-ron tự nhiên của Microsoft Edge (vi-VN-HoaiMyNeural, vi-VN-NamMinhNeural).
- GTTSEngine: Giọng đọc Google Translate TTS (dùng làm dự phòng).
"""

import asyncio
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseTTSEngine(ABC):
    """Lớp trừu tượng cho tất cả các TTS Engine."""

    @abstractmethod
    def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        """Tổng hợp giọng nói từ văn bản và lưu ra file âm thanh.

        Args:
            text: Văn bản cần đọc.
            output_path: Đường dẫn file âm thanh đầu ra (.mp3 hoặc .wav).
            **kwargs: Các tham số bổ sung tùy engine (voice, rate, pitch...).

        Returns:
            Đường dẫn tuyệt đối đến file âm thanh đã tạo.
        """
        pass


class EdgeTTSEngine(BaseTTSEngine):
    """TTS Engine sử dụng Microsoft Edge TTS (miễn phí, giọng đọc nơ-ron chất lượng cao)."""

    DEFAULT_VOICE = "vi-VN-HoaiMyNeural"  # Giọng nữ
    MALE_VOICE = "vi-VN-NamMinhNeural"   # Giọng nam

    SUPPORTED_VOICES = {
        "nu": "vi-VN-HoaiMyNeural",
        "nam": "vi-VN-NamMinhNeural",
        "female": "vi-VN-HoaiMyNeural",
        "male": "vi-VN-NamMinhNeural",
        "vi-VN-HoaiMyNeural": "vi-VN-HoaiMyNeural",
        "vi-VN-NamMinhNeural": "vi-VN-NamMinhNeural",
    }

    def __init__(self, default_voice: str = DEFAULT_VOICE):
        self.default_voice = self.SUPPORTED_VOICES.get(default_voice, self.DEFAULT_VOICE)

    async def _async_synthesize(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ) -> str:
        import edge_tts

        selected_voice = self.SUPPORTED_VOICES.get(voice, self.default_voice) if voice else self.default_voice
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        communicate = edge_tts.Communicate(
            text=text,
            voice=selected_voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )
        await communicate.save(output_path)
        return os.path.abspath(output_path)

    def synthesize(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
        **kwargs,
    ) -> str:
        """Chạy tổng hợp âm thanh đồng bộ (sync wrapper cho async edge_tts)."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Trong môi trường đã có event loop (như Jupyter Notebook)
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(
                self._async_synthesize(text, output_path, voice=voice, rate=rate, pitch=pitch, volume=volume)
            )
        else:
            return asyncio.run(
                self._async_synthesize(text, output_path, voice=voice, rate=rate, pitch=pitch, volume=volume)
            )

    @classmethod
    async def list_vietnamese_voices(cls) -> List[Dict[str, str]]:
        """Lấy danh sách các giọng tiếng Việt có sẵn từ Edge TTS."""
        import edge_tts
        voices = await edge_tts.list_voices()
        return [v for v in voices if v.get("Locale", "").startswith("vi-")]


class GTTSEngine(BaseTTSEngine):
    """TTS Engine dự phòng sử dụng Google Translate TTS."""

    def __init__(self, lang: str = "vi", slow: bool = False):
        self.lang = lang
        self.slow = slow

    def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        from gtts import gTTS

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        tts = gTTS(text=text, lang=self.lang, slow=self.slow)
        tts.save(output_path)
        return os.path.abspath(output_path)


class VITSEngine(BaseTTSEngine):
    """Mô hình End-to-End VITS chạy offline trên máy (facebook/mms-tts-vie)."""

    _instance = None

    def __init__(self, model_id: str = "facebook/mms-tts-vie"):
        try:
            from .vits_decomposed import VITSDecomposedTTS
        except ImportError:
            from vits_decomposed import VITSDecomposedTTS
        self.model_id = model_id
        self._vits = VITSDecomposedTTS(model_id=model_id)

    def synthesize(
        self,
        text: str,
        output_path: str,
        speaking_rate: float = 1.0,
        noise_scale: float = 0.667,
        **kwargs,
    ) -> str:
        return self._vits.synthesize(
            text=text,
            output_path=output_path,
            normalize=False,  # Chuẩn hóa đã được xử lý ở entrypoint synthesize
            speaking_rate=speaking_rate,
            noise_scale=noise_scale,
        )


class MatchaEngine(BaseTTSEngine):
    """Mô hình Optimal-Transport Conditional Flow Matching (Matcha-TTS, ICASSP 2024)."""

    def __init__(self, checkpoint_path: Optional[str] = None):
        try:
            from .matcha_engine import MatchaTTSEngine
        except ImportError:
            from matcha_engine import MatchaTTSEngine
        self._engine = MatchaTTSEngine(checkpoint_path=checkpoint_path)

    def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        path, _ = self._engine.synthesize(text=text, output_path=output_path, normalize=False)
        return path


def get_tts_engine(name: str = "edge") -> BaseTTSEngine:
    """Factory lấy TTS Engine tương ứng."""
    name_clean = name.strip().lower()
    if name_clean in ("matcha", "matcha-tts", "flowmatching"):
        return MatchaEngine()
    elif name_clean in ("vits", "mms", "local", "mms-tts"):
        return VITSEngine()
    elif name_clean in ("edge", "edge-tts", "edgetts"):
        return EdgeTTSEngine()
    elif name_clean in ("gtts", "google"):
        return GTTSEngine()
    else:
        raise ValueError(f"Không hỗ trợ engine: '{name}'. Các lựa chọn: 'matcha', 'vits', 'edge', 'gtts'")
