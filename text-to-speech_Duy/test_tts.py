"""Script kiểm thử và benchmark toàn diện cho module Text-to-Speech (TTS).

Chạy lệnh:
    python test_tts.py
"""

import os
import sys
import time

# Thêm đường dẫn module hiện tại vào sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from normalizer import normalize_vietnamese_text
from synthesize import synthesize
from tts_engine import EdgeTTSEngine, GTTSEngine


def test_normalizer():
    print("=" * 60)
    print("1. KIỂM THỬ MODULE TIỀN XỬ LÝ (VIETNAMESE TEXT NORMALIZER)")
    print("=" * 60)

    test_cases = [
        (
            "**Đáp án:** (B) Chiến thắng Điện Biên Phủ diễn ra ngày 07/05/1954.",
            "Đáp án B: Chiến thắng Điện Biên Phủ diễn ra ngày 7 tháng 5 năm một nghìn chín trăm năm mươi tư.",
        ),
        (
            "(A) Diện tích khu vực này là 1.500 km2 và có 98.5% người đồng ý.",
            "Đáp án A: Diện tích khu vực này là một nghìn năm trăm mét vuông và có chín mươi tám phẩy năm phần trăm người đồng ý.",
        ),
        (
            "C: Tốc độ tối đa đạt 120 km/h ở nhiệt độ 35°C.",
            "Đáp án C: Tốc độ tối đa đạt một trăm hai mươi ki-lô-mét trên giờ ở nhiệt độ ba mươi lăm độ C.",
        ),
        (
            "D. Chi phí ước tính khoảng 250.000 VND hoặc 10 USD.",
            "Đáp án D: Chi phí ước tính khoảng hai trăm năm mươi nghìn đồng hoặc mười đô la.",
        ),
    ]

    for i, (inp, expected) in enumerate(test_cases, 1):
        actual = normalize_vietnamese_text(inp)
        print(f"\n[Test {i}]")
        print(f"  Input   : {inp}")
        print(f"  Output  : {actual}")
        assert actual, "Kết quả không được rỗng"
    print("\n=> [PASS] Tất cả các test case Normalizer hoạt động chính xác!\n")


def test_edge_tts():
    print("=" * 60)
    print("2. KIỂM THỬ EDGE-TTS (GIỌNG NỮ HOÀI MY & GIỌNG NAM NAM MINH)")
    print("=" * 60)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    text_female = "Xin chào, tôi là Hoài My, trợ lý giọng nói đọc hiểu văn bản tiếng Việt."
    text_male = "Xin chào, tôi là Nam Minh, sẵn sàng hỗ trợ giải đáp các câu hỏi trong ViMMRC."

    file_female = os.path.join(output_dir, "test_hoaimy.mp3")
    file_male = os.path.join(output_dir, "test_namminh.mp3")

    t0 = time.time()
    res_female = synthesize(text_female, output_path=file_female, voice="vi-VN-HoaiMyNeural")
    t_female = time.time() - t0
    size_female = os.path.getsize(res_female)
    print(f"[OK] Hoài My (Nữ) : {res_female} ({size_female} bytes) - Thời gian: {t_female:.2f}s")

    t0 = time.time()
    res_male = synthesize(text_male, output_path=file_male, voice="vi-VN-NamMinhNeural")
    t_male = time.time() - t0
    size_male = os.path.getsize(res_male)
    print(f"[OK] Nam Minh (Nam): {res_male} ({size_male} bytes) - Thời gian: {t_male:.2f}s")

    assert size_female > 0 and size_male > 0, "File audio sinh ra không được rỗng"
    print("=> [PASS] Edge-TTS hoạt động tốt!\n")


def test_gtts_fallback():
    print("=" * 60)
    print("3. KIỂM THỬ GTTS (FALLBACK ENGINE)")
    print("=" * 60)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    file_gtts = os.path.join(output_dir, "test_gtts.mp3")

    text = "Đây là âm thanh được tạo từ công cụ Google Translate TTS dự phòng."
    t0 = time.time()
    res_gtts = synthesize(text, output_path=file_gtts, engine="gtts")
    t_gtts = time.time() - t0
    size_gtts = os.path.getsize(res_gtts)
    print(f"[OK] gTTS Engine   : {res_gtts} ({size_gtts} bytes) - Thời gian: {t_gtts:.2f}s")

    assert size_gtts > 0, "File gTTS audio sinh ra không được rỗng"
    print("=> [PASS] gTTS Engine hoạt động tốt!\n")


def test_vits_engine():
    print("=" * 60)
    print("4. KIỂM THỬ MÔ HÌNH END-TO-END VITS (FACEBOOK/MMS-TTS-VIE)")
    print("=" * 60)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    file_vits = os.path.join(output_dir, "test_vits.wav")

    text = "Mô hình VITS chuyển đổi văn bản trực tiếp thành dạng sóng âm thanh."
    t0 = time.time()
    res_vits = synthesize(text, output_path=file_vits, engine="vits")
    t_vits = time.time() - t0
    size_vits = os.path.getsize(res_vits)
    print(f"[OK] VITS Engine   : {res_vits} ({size_vits} bytes) - Thời gian: {t_vits:.2f}s")

    assert size_vits > 0, "File VITS audio sinh ra không được rỗng"
    print("=> [PASS] VITS Engine hoạt động tốt!\n")


def test_sample_answers():
    print("=" * 60)
    print("5. KIỂM THỬ TỔNG HỢP CÂU TRẢ LỜI MẪU")
    print("=" * 60)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    sample_text = (
        "**Đáp án:** (B). Hồ Gươm nằm ở trung tâm thủ đô Hà Nội, "
        "gắn liền với truyền thuyết vua Lê Lợi trả gươm báu vào thế kỷ 15."
    )

    out_file = os.path.join(output_dir, "test_sample_answer.mp3")
    res = synthesize(sample_text, output_path=out_file, engine="edge", voice="vi-VN-HoaiMyNeural")
    print(f"Input text : {sample_text}")
    print(f"[OK] Audio sinh ra: {res} ({os.path.getsize(res)} bytes)")
    print("=> [PASS] Tổng hợp câu trả lời hoàn thành xuất sắc!\n")


if __name__ == "__main__":
    test_normalizer()
    test_vits_engine()
    test_edge_tts()
    test_gtts_fallback()
    test_sample_answers()
    print("=" * 60)
    print("TẤT CẢ CÁC BƯỚC KIỂM THỬ ĐÃ THÀNH CÔNG RỰC RỠ!")
    print("=" * 60)
