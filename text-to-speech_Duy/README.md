# Text-to-Speech tiếng Việt (Matcha-TTS)

Phân hệ tổng hợp tiếng nói của **ViMMRC Voice Q&A**: nhận câu trả lời dạng văn bản từ `mrc-model_Huy` và trả về đường dẫn file âm thanh cho `web-interface_Luong`.

Mô hình chính là **Matcha-TTS** (Conditional Flow Matching) tự huấn luyện trên InfoRe1. VITS MMS, Edge-TTS và gTTS dùng để so sánh và dự phòng. Kiến thức nền, quy trình huấn luyện và đánh giá: [docs/tts.md](docs/tts.md).

```python
from synthesize import synthesize

audio_path = synthesize("Đáp án B: Hồ Gươm nằm ở trung tâm thủ đô Hà Nội.")   # -> ".../outputs/tts_<ms>.wav"
```

## Cấu trúc

```text
text-to-speech_Duy/
├── synthesize.py                # Entrypoint: synthesize(text, ...) -> đường dẫn audio, kèm CLI
├── src/
│   ├── normalizer.py            # Chuẩn hóa văn bản tiếng Việt / nhãn đáp án ViMMRC
│   ├── vi_tokenizer.py          # Token hóa tách thanh điệu (dùng chung với notebook)
│   ├── matcha_engine.py         # Suy luận Matcha-TTS + HiFi-GAN, ngắt cụm theo dấu câu
│   ├── tts_engine.py            # Engine matcha / vits / edge / gtts cùng một giao diện
│   └── evaluator.py             # MCD, F0 RMSE, log-F0 RMSE, CER, RTF
├── scripts/
│   ├── setup_matcha.py          # Cài mã nguồn Matcha-TTS + MAS bản numba
│   ├── benchmark.py             # So sánh các engine với giọng người thật
│   └── sync_notebook_tokenizer.py
├── notebooks/train_matcha.ipynb # Huấn luyện trên Kaggle
├── docs/tts.md                  # Tài liệu
├── tests/
└── checkpoints/                 # matcha_vi.pt, matcha_vi_hifigan.pt (không commit)
```

## Cài đặt

```bash
cd text-to-speech_Duy
pip install -r requirements.txt
python scripts/setup_matcha.py
```

Chép hai file kết quả của notebook vào `checkpoints/`: `matcha_vi.pt` (mô hình, đã kèm bộ token) và `matcha_vi_hifigan.pt` (vocoder fine-tune). Thiếu vocoder fine-tune thì engine tự tải HiFi-GAN Universal. Engine `vits` tự tải `facebook/mms-tts-vie`; `edge` và `gtts` cần Internet.

## Hướng dẫn các câu lệnh chạy nhanh (Quick Start)

### 1. File chạy đa nền tảng (macOS, Windows, Linux) ⭐
Dự án đã tích hợp sẵn file thực thi chạy đồng nhất trên cả 3 hệ điều hành:

* **Chạy bằng Python (Khuyên dùng cho macOS & Windows):**
  ```bash
  cd text-to-speech_Duy

  # Mở Menu tương tác trực quan (tự động phát audio sau khi tạo):
  python run.py

  # Đọc câu mẫu từ file test_sentence.txt:
  python run.py -f test_sentence.txt

  # Đọc một câu văn bản bất kỳ:
  python run.py -t "Xin chào bạn, hệ thống ViMMRC đã sẵn sàng."

  # Chạy giọng nơ-ron Edge-TTS (cần internet):
  python run.py -f test_sentence.txt -e edge -v nu

  # Khởi động cả hệ thống Web UI (Backend FastAPI :8000 + Frontend Angular :4200):
  python run.py --app

  # Chạy đo đạc đánh giá benchmark (MCD, F0, CER, RTF):
  python run.py --benchmark
  ```

* **Chạy bằng Bash Script (dành riêng cho macOS / Linux):**
  ```bash
  cd text-to-speech_Duy
  chmod +x run.sh
  ./run.sh                  # Mở menu tương tác
  ./run.sh -f test_sentence.txt
  ./run.sh --app
  ```

* **Chạy bằng VS Code Task (Dùng phím tắt trong IDE):**
  Bấm tổ hợp phím **`Ctrl+Shift+P`** (trên Windows) hoặc **`Cmd+Shift+P`** (trên macOS) -> Chọn **`Tasks: Run Task`** -> Chọn một trong các tác vụ:
  - *`TTS: Chạy tổng hợp câu mẫu (Matcha-TTS)`*
  - *`TTS: Mở Menu tương tác (run.py)`*
  - *`TTS: Chạy với giọng nơ-ron Edge-TTS (Hoài My)`*
  - *`ViMMRC: Khởi động toàn bộ dự án (FE + BE)`*

### 2. Dùng script riêng trên Windows (Batch / PowerShell)
- **Batch script:** Nhấp đúp vào `run_tts.bat` (hoặc gõ `.\run_tts.bat` trong CMD/PowerShell).
- **PowerShell script:** `.\run_tts.ps1` hoặc `.\run_tts.ps1 -Text "Xin chào"` hoặc `.\run_tts.ps1 -LaunchApp`.

### 2. Các câu lệnh chạy trực tiếp bằng dòng lệnh (CLI)
```bash
# Di chuyển vào thư mục text-to-speech_Duy:
cd text-to-speech_Duy

# 1. Đọc văn bản từ file test_sentence.txt bằng Matcha-TTS (150k + 50k vocoder):
python synthesize.py -f test_sentence.txt

# 2. Đọc trực tiếp câu văn bản bất kỳ:
python synthesize.py -t "Đáp án đúng là câu C: Quá trình quang hợp diễn ra ở lục lạp."

# 3. Đọc và lưu ra file cụ thể kèm chỉnh tốc độ:
python synthesize.py -t "Xin chào các bạn." --rate -10% -o outputs/test_cham.wav

# 4. Đọc bằng Microsoft Edge-TTS (Hoài My - Nữ hoặc Nam Minh - Nam):
python synthesize.py -t "Xin chào các bạn." -e edge -v vi-VN-HoaiMyNeural
python synthesize.py -t "Xin chào các bạn." -e edge -v vi-VN-NamMinhNeural

# 5. Khởi động Web UI tích hợp cả dự án (từ thư mục gốc repository):
cd ..
python -m uvicorn scripts.api_server:app --host 127.0.0.1 --port 8000
# Trong một terminal khác:
cd web-interface_Luong && npm start
```

## Sử dụng trong mã nguồn Python

```python
path = synthesize("**Đáp án:** (B) Chiến thắng Điện Biên Phủ ngày 07/05/1954.")
path = synthesize("Xin chào.", output_path="outputs/a.wav", rate="-10%")
path = synthesize("Xin chào.", engine="edge", voice="vi-VN-NamMinhNeural")   # -> .mp3
```

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `text` | (bắt buộc) | Văn bản tiếng Việt |
| `output_path` | `outputs/tts_<ms>.wav` | `.wav` cho matcha/vits, `.mp3` cho edge/gtts |
| `engine` | `matcha` | `matcha`, `vits`, `edge`, `gtts` |
| `voice` | `vi-VN-HoaiMyNeural` | Giọng Edge-TTS (`nu` / `nam`); Matcha chỉ có một giọng |
| `checkpoint_path` | `checkpoints/matcha_vi.pt` | File `.pt` của Matcha-TTS |
| `normalize` | `True` | Chuẩn hóa số, ngày tháng, nhãn đáp án |
| `rate` | `+0%` | Tốc độ đọc (matcha, edge) |
| `pitch` | `+0Hz` | Cao độ (edge) |

Engine được khởi tạo một lần rồi dùng lại. Nếu engine được chọn lỗi, hàm tự chuyển sang gTTS và trả về `.mp3`.

```bash
# Từ thư mục gốc repository:
cd text-to-speech_Duy
python synthesize.py -t "Đáp án B: Hồ Gươm nằm ở Hà Nội."
python synthesize.py -t "Xin chào các bạn." --rate -10% -o outputs/cham.wav
python synthesize.py -t "Xin chào các bạn." -e edge -v vi-VN-NamMinhNeural
```

## Kiểm thử và đánh giá

```bash
# Từ thư mục gốc repository:
cd text-to-speech_Duy

# Chạy toàn bộ kiểm thử TTS:
python -m pytest tests/ -v       # edge, gtts cần Internet; vits tải mô hình ở lần đầu

# Hoặc chạy kiểm thử bộ tách token tiếng Việt:
python -m pytest tests/test_vi_tokenizer.py -q

# Chạy benchmark:
python scripts/benchmark.py      # báo cáo ở outputs/benchmark/benchmark_report.md
```

Hoặc chạy trực tiếp từ thư mục gốc repository (không cần `cd`):
```bash
python -m pytest text-to-speech_Duy/tests/test_vi_tokenizer.py -q
```
