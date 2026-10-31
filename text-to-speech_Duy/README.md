# Text-to-Speech tiếng Việt (Matcha-TTS)

Phân hệ tổng hợp tiếng nói của **ViMMRC Voice Q&A**: nhận câu trả lời dạng văn bản từ `mrc-model_Huy` và trả về đường dẫn file âm thanh cho `web-interface_Luong`.

Mô hình chính là **Matcha-TTS** (Conditional Flow Matching) tự huấn luyện trên InfoRe1. VITS MMS, Edge-TTS và gTTS dùng để so sánh và dự phòng. Kiến thức nền, quy trình huấn luyện và đánh giá: [docs/tts.md](docs/tts.md).

```python
from synthesize import synthesize

audio_path = synthesize("Tác giả Truyện Kiều là Nguyễn Du.")   # -> ".../outputs/tts_<ms>.wav"
```

## Cấu trúc

```text
text-to-speech_Duy/
├── synthesize.py                # Entrypoint: synthesize(text, ...) -> đường dẫn audio, kèm CLI
├── src/
│   ├── normalizer.py            # Chuẩn hóa văn bản tiếng Việt (số liệu, ngày tháng, tiền tệ, viết tắt, nhãn liệt kê)
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

## Sử dụng

```python
path = synthesize("Chiến thắng Điện Biên Phủ diễn ra ngày 07/05/1954.")
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
| `normalize` | `True` | Chuẩn hóa số, ngày tháng, nhãn liệt kê |
| `rate` | `+0%` | Tốc độ đọc (matcha, edge) |
| `pitch` | `+0Hz` | Cao độ (edge) |

Engine được khởi tạo một lần rồi dùng lại. Nếu engine được chọn lỗi, hàm tự chuyển sang gTTS và trả về `.mp3`.

```bash
# Từ thư mục gốc repository:
cd text-to-speech_Duy
python synthesize.py -t "Tác giả Truyện Kiều là Nguyễn Du."
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
