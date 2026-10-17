"""Module các TTS Engine dùng chung một giao diện `BaseTTSEngine.synthesize(text, output_path, **kwargs)`.

Các triển khai:
- MatchaEngine: Matcha-TTS (Optimal-Transport Conditional Flow Matching) tự huấn luyện, chạy cục bộ.
- VITSEngine: VITS end-to-end pretrained facebook/mms-tts-vie, chạy cục bộ (baseline).
- EdgeTTSEngine: giọng nơ-ron Microsoft Edge (vi-VN-HoaiMyNeural, vi-VN-NamMinhNeural), cần mạng.
- GTTSEngine: Google Translate TTS, dùng làm dự phòng khi engine khác lỗi.

Dùng `get_tts_engine(name)` để khởi tạo engine theo tên.
"""

import asyncio
import os
import time
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
    MAX_RETRIES = 3                      # số lần thử khi dịch vụ Edge lỗi tạm thời

    SUPPORTED_VOICES = {
        "nu": "vi-VN-HoaiMyNeural",
        "nam": "vi-VN-NamMinhNeural",
        "female": "vi-VN-HoaiMyNeural",
        "male": "vi-VN-NamMinhNeural",
        "vi-VN-HoaiMyNeural": "vi-VN-HoaiMyNeural",
        "vi-VN-NamMinhNeural": "vi-VN-NamMinhNeural",
    }

    def __init__(self, default_voice: str = DEFAULT_VOICE):
        """Khởi tạo engine với giọng mặc định (tên đầy đủ hoặc bí danh 'nu' / 'nam' / 'female' / 'male')."""
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
        """Gọi dịch vụ Edge-TTS (bất đồng bộ) và lưu kết quả MP3 ra `output_path`."""
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
        """Tổng hợp đồng bộ (bọc hàm async của edge_tts) và lưu MP3 ra `output_path`.

        Dịch vụ Edge thỉnh thoảng trả về lỗi tạm thời (ví dụ `NoAudioReceived`), nên mỗi yêu cầu được
        thử lại tối đa `MAX_RETRIES` lần, lần sau chờ lâu hơn lần trước.

        Args:
            text: Văn bản đã chuẩn hóa.
            output_path: Đường dẫn file .mp3 đầu ra.
            voice: Tên giọng hoặc bí danh ('nu', 'nam'); None dùng giọng mặc định.
            rate: Tốc độ đọc tương đối, ví dụ '+10%'.
            pitch: Cao độ tương đối, ví dụ '+5Hz'.
            volume: Âm lượng tương đối, ví dụ '+0%'.
            **kwargs: Tham số của engine khác, bị bỏ qua.

        Returns:
            Đường dẫn tuyệt đối tới file âm thanh.
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                return self._run(
                    self._async_synthesize(text, output_path, voice=voice, rate=rate, pitch=pitch, volume=volume)
                )
            except Exception:
                if attempt == self.MAX_RETRIES:
                    raise
                time.sleep(attempt)

    @staticmethod
    def _run(coro):
        """Chạy coroutine cả khi đã có event loop đang chạy (Jupyter Notebook) lẫn khi chưa có."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        return asyncio.run(coro)

    @classmethod
    async def list_vietnamese_voices(cls) -> List[Dict[str, str]]:
        """Lấy danh sách các giọng tiếng Việt có sẵn từ Edge TTS."""
        import edge_tts
        voices = await edge_tts.list_voices()
        return [v for v in voices if v.get("Locale", "").startswith("vi-")]


class GTTSEngine(BaseTTSEngine):
    """TTS Engine dự phòng sử dụng Google Translate TTS."""

    def __init__(self, lang: str = "vi", slow: bool = False):
        """Khởi tạo với mã ngôn ngữ của Google Translate TTS và tùy chọn đọc chậm."""
        self.lang = lang
        self.slow = slow

    def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        """Tổng hợp qua Google Translate TTS (cần mạng) và lưu dữ liệu MP3 ra `output_path`.

        Các tham số giọng/tốc độ trong `kwargs` bị bỏ qua vì gTTS chỉ có một giọng.
        """
        from gtts import gTTS

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        tts = gTTS(text=text, lang=self.lang, slow=self.slow)
        tts.save(output_path)
        return os.path.abspath(output_path)


class VITSEngine(BaseTTSEngine):
    """Mô hình End-to-End VITS chạy offline trên máy (facebook/mms-tts-vie)."""

    def __init__(self, model_id: str = "facebook/mms-tts-vie"):
        """Nạp mô hình VITS từ Hugging Face Hub (tải về bộ đệm ở lần chạy đầu)."""
        import torch
        from transformers import VitsModel, VitsTokenizer

        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = VitsTokenizer.from_pretrained(model_id)
        self.model = VitsModel.from_pretrained(model_id).to(self.device).eval()

    def synthesize(
        self,
        text: str,
        output_path: str,
        speaking_rate: float = 1.0,
        noise_scale: float = 0.667,
        **kwargs,
    ) -> str:
        """Tổng hợp bằng VITS và lưu WAV 16 kHz.

        Args:
            text: Văn bản đã chuẩn hóa.
            output_path: Đường dẫn file .wav đầu ra.
            speaking_rate: Hệ số tốc độ đọc (> 1.0 là nhanh hơn).
            noise_scale: Độ ngẫu nhiên của biến tiềm ẩn (ảnh hưởng ngữ điệu).
            **kwargs: Tham số của engine khác (voice, rate, ...), bị bỏ qua.

        Returns:
            Đường dẫn tuyệt đối tới file âm thanh.
        """
        import soundfile as sf
        import torch

        inputs = self.tokenizer(text.strip(), return_tensors="pt").to(self.device)
        self.model.speaking_rate = speaking_rate
        self.model.noise_scale = noise_scale
        with torch.no_grad():
            waveform = self.model(**inputs).waveform[0].cpu().float().numpy()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        sf.write(output_path, waveform, samplerate=self.model.config.sampling_rate)
        return os.path.abspath(output_path)


class MatchaEngine(BaseTTSEngine):
    """Mô hình Optimal-Transport Conditional Flow Matching (Matcha-TTS, ICASSP 2024)."""

    def __init__(self, checkpoint_path: Optional[str] = None):
        """Khởi tạo Matcha-TTS; None: dùng checkpoints/matcha_vi.pt."""
        try:
            from .matcha_engine import MatchaTTSEngine
        except ImportError:
            from matcha_engine import MatchaTTSEngine
        self._engine = MatchaTTSEngine(checkpoint_path=checkpoint_path)

    def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        """Tổng hợp bằng Matcha-TTS và lưu WAV 22.05 kHz.

        Args:
            text: Văn bản đã chuẩn hóa.
            output_path: Đường dẫn file .wav đầu ra.
            **kwargs: `rate` (dạng '+10%'); các tham số khác bị bỏ qua vì mô hình chỉ có một giọng.

        Returns:
            Đường dẫn tuyệt đối tới file âm thanh.
        """
        rate = str(kwargs.get("rate", "+0%")).strip().rstrip("%") or "0"
        path, _ = self._engine.synthesize(
            text=text,
            output_path=output_path,
            normalize=False,
            speaking_rate=1.0 + float(rate) / 100.0,
        )
        return path


def get_tts_engine(name: str = "edge", checkpoint_path: Optional[str] = None) -> BaseTTSEngine:
    """Khởi tạo TTS Engine theo tên.

    Args:
        name: 'matcha' (hoặc 'matcha-tts', 'flowmatching'), 'vits' ('mms', 'local'), 'edge', 'gtts' ('google').
        checkpoint_path: File trọng số cho Matcha-TTS; các engine khác bỏ qua.

    Returns:
        Đối tượng engine tương ứng.

    Raises:
        ValueError: Tên engine không được hỗ trợ.
    """
    name_clean = name.strip().lower()
    if name_clean in ("matcha", "matcha-tts", "flowmatching"):
        return MatchaEngine(checkpoint_path=checkpoint_path)
    elif name_clean in ("vits", "mms", "local", "mms-tts"):
        return VITSEngine()
    elif name_clean in ("edge", "edge-tts", "edgetts"):
        return EdgeTTSEngine()
    elif name_clean in ("gtts", "google"):
        return GTTSEngine()
    else:
        raise ValueError(f"Không hỗ trợ engine: '{name}'. Các lựa chọn: 'matcha', 'vits', 'edge', 'gtts'")
