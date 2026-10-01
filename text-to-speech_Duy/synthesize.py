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
from typing import Optional

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


def synthesize(
    text: str,
    output_path: Optional[str] = None,
    voice: str = "vi-VN-HoaiMyNeural",
    engine: str = "matcha",
    checkpoint_path: Optional[str] = None,
    normalize: bool = True,
    rate: str = "+0%",
    pitch: str = "+0Hz",
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
        tts_service: BaseTTSEngine = get_tts_engine(engine, checkpoint_path=checkpoint_path)
        result_path = tts_service.synthesize(
            text=processed_text,
            output_path=output_path,
            voice=voice,
            rate=rate,
            pitch=pitch,
        )
        return result_path
    except Exception as e:
        logger.warning("Lỗi khi tổng hợp bằng engine '%s': %s. Thử fallback sang gTTS...", engine, e)
        if engine != "gtts":
            fallback_service = get_tts_engine("gtts")
            return fallback_service.synthesize(text=processed_text, output_path=output_path)
        raise e


def main():
    parser = argparse.ArgumentParser(description="Vietnamese Text-to-Speech (TTS) synthesizer CLI")
    parser.add_argument("-t", "--text", required=True, help="Văn bản tiếng Việt cần đọc")
    parser.add_argument("-o", "--output", default=None, help="Đường dẫn file lưu audio đầu ra")
    parser.add_argument("-v", "--voice", default="vi-VN-HoaiMyNeural", help="Giọng đọc Edge: vi-VN-HoaiMyNeural (nữ) hoặc vi-VN-NamMinhNeural (nam)")
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
    )
    print(f"[OK] File audio đã được lưu tại: {audio_path}")


if __name__ == "__main__":
    main()
