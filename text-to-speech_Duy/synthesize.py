"""Entrypoint chính cho module Text-to-Speech (TTS).

Tuân thủ quy ước CONVENTIONS.md:
- Hàm thực thi chính: synthesize(text, ...) -> str (đường dẫn file âm thanh).
- Đầu vào: text thuần (str).
- Đầu ra: đường dẫn tuyệt đối tới file âm thanh (.mp3 / .wav).
"""

import argparse
import logging
import os
import sys
import tempfile
import time
from typing import Dict, Optional, Tuple

# Thiết lập mã hóa UTF-8 cho console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Cho phép import module từ cả thư mục gốc và thư mục src/
_current_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.join(_current_dir, "src")
for _p in (_current_dir, _src_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from src.normalizer import normalize_vietnamese_text
    from src.tts_engine import BaseTTSEngine, get_tts_engine
except ImportError:
    from normalizer import normalize_vietnamese_text
    from tts_engine import BaseTTSEngine, get_tts_engine

logger = logging.getLogger(__name__)

# Engine đã khởi tạo, dùng lại giữa các lần gọi để không phải nạp lại mô hình (vài giây mỗi lần)
_ENGINE_CACHE: Dict[Tuple[str, Optional[str]], BaseTTSEngine] = {}


def _get_engine(engine: str, checkpoint_path: Optional[str] = None) -> BaseTTSEngine:
    """Lấy engine từ bộ nhớ đệm, khởi tạo ở lần gọi đầu tiên."""
    key = (engine.strip().lower(), checkpoint_path)
    if key not in _ENGINE_CACHE:
        _ENGINE_CACHE[key] = get_tts_engine(engine, checkpoint_path=checkpoint_path)
    return _ENGINE_CACHE[key]


def synthesize(
    text: str,
    output_path: Optional[str] = None,
    voice: str = "vi-VN-HoaiMyNeural",
    engine: str = "matcha",
    checkpoint_path: Optional[str] = None,
    normalize: bool = True,
    rate: str = "+0%",
    pitch: str = "+0Hz",
    speaker_id: Optional[int] = None,
) -> str:
    """Chuyển đổi văn bản tiếng Việt thành giọng nói (audio file).

    Args:
        text: Chuỗi văn bản cần đọc (ví dụ câu trả lời từ mô hình MRC).
        output_path: Đường dẫn lưu file âm thanh. Nếu None, tự sinh file tại thư mục outputs/.
        voice: Giọng đọc ('vi-VN-HoaiMyNeural', 'vi-VN-NamMinhNeural', 'nu', 'nam').
        engine: Công cụ tổng hợp ('matcha', 'vits', 'edge', 'gtts'). Mặc định là 'matcha'.
        checkpoint_path: Đường dẫn đến file trọng số mô hình đã huấn luyện (.pt).
        normalize: Tự động chuẩn hóa số, ngày tháng, nhãn trắc nghiệm trước khi đọc.
        rate: Tốc độ đọc (ví dụ: '+0%', '+10%', '-10%').
        pitch: Cao độ giọng (ví dụ: '+0Hz', '+5Hz').
        speaker_id: Chỉ số người nói của checkpoint Matcha đa giọng (VIVOS: 0 - 64). None: chọn giọng
            mặc định theo giới tính suy ra từ `voice`. Các engine khác bỏ qua tham số này.

    Returns:
        Đường dẫn tuyệt đối (str) tới file âm thanh đã được tạo.
    """
    if not text or not text.strip():
        raise ValueError("Văn bản đầu vào không được để trống!")

    # 1. Tiền xử lý / Chuẩn hóa văn bản tiếng Việt
    processed_text = normalize_vietnamese_text(text) if normalize else text.strip()

    # 2. Xác định đường dẫn file đầu ra
    if output_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, "outputs")
        os.makedirs(output_dir, exist_ok=True)
        ext = ".wav" if engine in ("vits", "matcha") else ".mp3"
        filename = f"tts_{int(time.time() * 1000)}{ext}"
        output_path = os.path.join(output_dir, filename)
    else:
        output_dir = os.path.dirname(os.path.abspath(output_path))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

    # 3. Tổng hợp giọng nói qua Engine
    try:
        tts_service = _get_engine(engine, checkpoint_path)
        result_path = tts_service.synthesize(
            text=processed_text,
            output_path=output_path,
            voice=voice,
            rate=rate,
            pitch=pitch,
            speaker_id=speaker_id,
        )
        return result_path
    except Exception as e:
        logger.warning("Lỗi khi tổng hợp bằng engine '%s': %s. Thử fallback sang gTTS...", engine, e)
        if engine != "gtts":
            # gTTS luôn sinh dữ liệu MP3 -> đổi đuôi file để định dạng khớp nội dung
            fallback_path = os.path.splitext(output_path)[0] + ".mp3"
            fallback_service = _get_engine("gtts")
            return fallback_service.synthesize(text=processed_text, output_path=fallback_path)
        raise e


def main():
    """Giao diện dòng lệnh: đọc tham số, gọi synthesize() và in đường dẫn file audio."""
    parser = argparse.ArgumentParser(description="Vietnamese Text-to-Speech (TTS) synthesizer CLI")
    parser.add_argument("-t", "--text", required=True, help="Văn bản tiếng Việt cần đọc")
    parser.add_argument("-o", "--output", default=None, help="Đường dẫn file lưu audio đầu ra")
    parser.add_argument("-v", "--voice", default="vi-VN-HoaiMyNeural", help="Giọng đọc: 'nu' / 'nam' (Matcha chọn giọng VIVOS mặc định theo giới tính), "
                        "hoặc tên giọng Edge vi-VN-HoaiMyNeural / vi-VN-NamMinhNeural")
    parser.add_argument("-s", "--speaker-id", type=int, default=None, help="Chỉ số người nói Matcha (VIVOS: 0 - 64)")
    parser.add_argument("-e", "--engine", default="matcha", choices=["matcha", "vits", "edge", "gtts"], help="Engine sử dụng: 'matcha' (Flow Matching 2024), 'vits', 'edge', 'gtts'")
    parser.add_argument("-c", "--checkpoint", default=None, help="Đường dẫn file trọng số tự huấn luyện (.pt)")
    parser.add_argument("--no-norm", action="store_true", help="Tắt tính năng chuẩn hóa văn bản")
    parser.add_argument("--rate", default="+0%", help="Tốc độ nói (vd: +10%%, -5%%)")

    args = parser.parse_args()
    audio_path = synthesize(
        text=args.text,
        output_path=args.output,
        voice=args.voice,
        engine=args.engine,
        checkpoint_path=args.checkpoint,
        normalize=not args.no_norm,
        rate=args.rate,
        speaker_id=args.speaker_id,
    )
    print(f"[OK] File audio đã được lưu tại: {audio_path}")


if __name__ == "__main__":
    main()
