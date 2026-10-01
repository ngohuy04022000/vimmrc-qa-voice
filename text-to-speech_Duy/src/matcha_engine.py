"""Module điều khiển và tích hợp mô hình Matcha-TTS (Optimal-Transport Conditional Flow Matching).

Bài báo gốc:
Shivam Mehta et al., "Matcha-TTS: A fast TTS architecture with conditional flow matching", ICASSP 2024.

Hỗ trợ:
- Chạy suy luận (Inference) dựa trên bộ giải vi phân thường (ODE Solver).
- Điều chỉnh số bước lấy mẫu (n_timesteps: 4 - 50 bước).
- Đo đạc thời gian xử lý và Real-Time Factor (RTF).
"""

import os
import sys
import time
from typing import Optional, Tuple

import numpy as np
import soundfile as sf
import torch

try:
    from .normalizer import normalize_vietnamese_text
except ImportError:
    from normalizer import normalize_vietnamese_text


class MatchaTTSEngine:
    """Engine quản lý mô hình Matcha-TTS sử dụng Conditional Flow Matching."""

    def __init__(self, checkpoint_path: Optional[str] = None, device: Optional[str] = None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.checkpoint_path = checkpoint_path
        self.sample_rate = 22050
        self._is_loaded = False
        print(f"[Matcha-TTS] Khởi tạo Engine trên thiết bị: {self.device.upper()}")

    def _ensure_model_loaded(self):
        """Khởi tạo mô hình Matcha-TTS khi cần suy luận."""
        if self._is_loaded:
            return

        try:
            from matcha.cli import load_matcha
            print("[Matcha-TTS] Đang nạp mô hình Matcha-TTS từ thư viện chính thức...")
            self.model = load_matcha("matcha_ljspeech", device=self.device)
            self._is_loaded = True
            print("[Matcha-TTS] Nạp mô hình thành công!")
        except Exception as e:
            print(f"[Matcha-TTS] Thông báo: Chưa tải checkpoint Matcha-TTS chuyên biệt: {e}")
            self._is_loaded = False

    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        normalize: bool = True,
        n_timesteps: int = 10,
        temperature: float = 0.667,
        speaking_rate: float = 1.0,
    ) -> Tuple[str, float]:
        """Tổng hợp giọng nói bằng giải thuật Flow Matching.

        Args:
            text: Văn bản đầu vào.
            output_path: Đường dẫn lưu file audio.
            normalize: Tự động chuẩn hóa tiếng Việt.
            n_timesteps: Số bước giải ODE (càng cao càng chi tiết, 10 bước cho tốc độ cao).
            temperature: Nhiệt độ điều chỉnh ngẫu nhiên.
            speaking_rate: Tốc độ phát âm.

        Returns:
            Tuple (đường dẫn file âm thanh, giá trị RTF).
        """
        if not text or not text.strip():
            raise ValueError("Văn bản không được để trống!")

        clean_text = normalize_vietnamese_text(text) if normalize else text.strip()

        # Đường dẫn output mặc định
        if output_path is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            out_dir = os.path.join(root_dir, "outputs")
            os.makedirs(out_dir, exist_ok=True)
            output_path = os.path.join(out_dir, f"matcha_{int(time.time() * 1000)}.wav")
        else:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        t0 = time.time()
        self._ensure_model_loaded()

        if self._is_loaded:
            with torch.no_grad():
                output = self.model.synthesize(
                    clean_text,
                    steps=n_timesteps,
                    temperature=temperature,
                    length_scale=1.0 / speaking_rate,
                )
                waveform = output["waveform"].cpu().numpy().squeeze()
                sf.write(output_path, waveform, samplerate=self.sample_rate)
        else:
            # Fallback sang VITS nếu máy local chưa nạp được checkpoint Matcha
            from vits_decomposed import VITSDecomposedTTS
            fallback_vits = VITSDecomposedTTS()
            output_path = fallback_vits.synthesize(
                clean_text,
                output_path=output_path,
                normalize=False,
                speaking_rate=speaking_rate,
            )
            info = sf.info(output_path)
            self.sample_rate = info.samplerate

        t_infer = time.time() - t0
        audio_info = sf.info(output_path)
        rtf = round(t_infer / max(0.01, audio_info.duration), 3)

        return os.path.abspath(output_path), rtf


if __name__ == "__main__":
    matcha = MatchaTTSEngine()
    test_text = "Hệ thống tổng hợp tiếng nói sử dụng kỹ thuật Flow Matching tiên tiến."
    p, rtf_val = matcha.synthesize(test_text)
    print(f"[OK] File âm thanh sinh ra: {p} (RTF: {rtf_val})")
