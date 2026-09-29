# Module Text-to-Speech (TTS) - ViMMRC Voice Q&A

Người phụ trách: **Trương Hoàng Duy** (`text-to-speech_Duy/`)

Module nhận văn bản đầu ra từ mô hình đọc hiểu MRC (`mrc-model_Huy`), thực hiện tiền xử lý chuẩn hóa văn bản tiếng Việt và chuyển đổi thành giọng nói chất lượng cao để giao diện web (`web-interface_Luong`) phát lại cho người dùng.

---

## 1. Tính năng nổi bật

- **Chất lượng giọng đọc nơ-ron tự nhiên:** Tích hợp `Edge-TTS` với giọng nữ (`vi-VN-HoaiMyNeural`) và giọng nam (`vi-VN-NamMinhNeural`).
- **Cơ chế dự phòng (Fallback):** Tự động chuyển sang `gTTS` nếu gặp sự cố mạng.
- **Tiền xử lý & Chuẩn hóa tiếng Việt (Text Normalization):**
  - Xóa định dạng Markdown (`**in đậm**`, `*in nghiêng*`, liên kết...).
  - Chuẩn hóa các đáp án trắc nghiệm ViMMRC: `(A)`, `(B)`, `(C)`, `(D)`, `A.`, `B.` $\rightarrow$ *"Đáp án A: ..."*.
  - Đọc ngày tháng: `02/09/1945` $\rightarrow$ *"ngày 2 tháng 9 năm một nghìn chín trăm bốn mươi lăm"*.
  - Đọc số nguyên, số hàng nghìn (`500.000`), số thập phân (`99.5%` $\rightarrow$ *"chín mươi chín phẩy năm phần trăm"*).
  - Đọc đơn vị đo lường: `km/h`, `kg`, `km`, `m²`, `°C`, `VND`, `USD`...
- **Tuân thủ CONVENTIONS.md của nhóm:** Cung cấp hàm chuẩn `synthesize(text, ...)` trả về file âm thanh.

---

## 2. Cài đặt

Cài đặt các thư viện phụ thuộc:

```bash
pip install -r requirements.txt
```

Nội dung `requirements.txt`:
- `edge-tts`: Bộ tổng hợp giọng nói nơ-ron Microsoft Edge.
- `gTTS`: Google Translate TTS (fallback engine).
- `soundfile`: Xử lý định dạng audio.
- `pydub`: Hỗ trợ xử lý và chuyển đổi file âm thanh.

---

## 3. Hướng dẫn sử dụng cho các thành viên khác

### Dành cho Lương (`web-interface_Luong`) & Huy (`mrc-model_Huy`):

Chỉ cần import hàm `synthesize`:

```python
import sys
import os

# Thêm đường dẫn thư mục TTS nếu cần
sys.path.append(os.path.abspath("text-to-speech_Duy"))

from synthesize import synthesize

# Ví dụ 1: Tổng hợp câu trả lời từ MRC (tự động lưu vào outputs/)
audio_path = synthesize("Đáp án đúng là: (B) Thủ đô của Việt Nam là Hà Nội.")
print("File audio sẵn sàng phát:", audio_path)

# Ví dụ 2: Chỉ định đường dẫn lưu file cụ thể và chọn giọng nam
audio_path = synthesize(
    text="Chiến thắng diễn ra ngày 07/05/1954 tại Điện Biên Phủ.",
    output_path="static/audio/answer.mp3",
    voice="vi-VN-NamMinhNeural" # hoặc "nam", "female"
)
```

---

## 4. Chạy qua Command Line (CLI)

Bạn có thể chạy thử trực tiếp từ dòng lệnh:

```bash
# Đọc câu cơ bản
python synthesize.py -t "Xin chào bạn, tôi là trợ lý ảo ViMMRC." -o outputs/hello.mp3

# Chọn giọng nam Nam Minh
python synthesize.py -t "Đáp án C: Nhiệt độ hôm nay là 32°C." -v vi-VN-NamMinhNeural

# Điều chỉnh tốc độ nói (+10%)
python synthesize.py -t "Nội dung cần đọc nhanh hơn một chút." --rate "+10%"
```

---

## 5. Chạy kiểm thử (Testing)

Chạy script kiểm thử toàn diện:

```bash
python test_tts.py
```

Script sẽ tự động kiểm tra:
1. Độ chính xác của bộ chuẩn hóa tiếng Việt (Text Normalizer).
2. Hoạt động của Edge-TTS với 2 giọng Hoài My & Nam Minh.
3. Hoạt động của bộ fallback gTTS.
4. Giả lập luồng trả lời hoàn chỉnh từ văn bản ViMMRC ra âm thanh.

---

## 6. Cấu trúc thư mục

```text
text-to-speech_Duy/
├── README.md                  # Tài liệu hướng dẫn sử dụng module
├── requirements.txt           # Danh sách thư viện cần cài đặt
├── normalizer.py              # Xử lý số, ngày tháng, nhãn trắc nghiệm tiếng Việt
├── tts_engine.py              # Core engines: BaseTTSEngine, EdgeTTSEngine, GTTSEngine
├── synthesize.py              # Entrypoint chuẩn hàm synthesize(...)
├── test_tts.py                # Bộ test case & benchmark
└── 01_tts_exploration.ipynb   # Notebook nghiên cứu, so sánh mô hình
```
