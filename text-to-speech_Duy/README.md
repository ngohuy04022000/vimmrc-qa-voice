# Hệ Thống Text-to-Speech (TTS) Tiếng Việt

Tài liệu hướng dẫn và mã nguồn triển khai hệ thống chuyển đổi văn bản thành giọng nói (Text-to-Speech) tiếng Việt, tập trung nghiên cứu chuyên sâu kiến trúc học sâu State-of-the-Art **VITS (Variational Inference for End-to-End Text-to-Speech)** cùng các giải pháp phụ trợ.

---

## 1. Tổng Quan Kiến Trúc VITS

Khác với các hệ thống TTS truyền thống chia làm 2 giai đoạn độc lập (Acoustic Model sinh Mel-spectrogram + Vocoder sinh sóng âm), **VITS** là kiến trúc **Fully End-to-End** thực sự:
- Ánh xạ trực tiếp từ chuỗi ký tự / âm vị (Phonemes) sang sóng âm thời gian thực (Raw Waveform).
- Loại bỏ hoàn toàn lỗi tích lũy miền (Acoustic-Vocoder Domain Mismatch).
- Tích hợp 4 kỹ thuật học sâu cốt lõi: **Variational Autoencoder (VAE)**, **Normalizing Flows**, **Monotonic Alignment Search (MAS)** và **Huấn luyện đối nghịch (GAN)**.

### Sơ đồ luồng xử lý bên trong mô hình:

```
[Văn bản tiếng Việt]
        │
        ▼
[1. Text Normalizer] ──> Chuẩn hóa số, ngày tháng, ký hiệu, viết tắt
        │
        ▼
[2. Tokenizer / Phonemizer] ──> Chuỗi Token IDs
        │
        ▼
[3. Text Encoder] ──> Trích xuất h_text & Phân phối tiên nghiệm N(μ_0, σ_0)
        │
        ├─────────────────────────────┐
        ▼                             ▼
[4. Duration Predictor (SDP)]    [5. Length Regulator]
(Dự đoán thời lượng âm vị)    (Mở rộng μ, σ theo thời gian)
        │                             │
        └─────────────────────────────┤
                                      ▼
                        [6. Normalizing Flows]
                        (Biến đổi không gian tiềm ẩn z)
                                      │
                                      ▼
                        [7. HiFi-GAN Waveform Generator]
                        (Upsampling 256x + Multi-Receptive Field Fusion)
                                      │
                                      ▼
                        [Sóng âm Raw Waveform y(t) (16 kHz)]
```

> Chi tiết phân rã toán học và các hàm mất mát của từng khối được trình bày đầy đủ tại: **[`docs/vits-architecture.md`](docs/vits-architecture.md)**.

---

## 2. Cấu Trúc Thư Mục & Các Thành Phần

```text
text-to-speech_Duy/
├── docs/                        # Tài liệu nghiên cứu chuyên sâu
│   └── vits-architecture.md     # Phân rã lý thuyết toán học & kiến trúc VITS
├── notebooks/                   # Notebook thực nghiệm & trực quan hóa
│   └── 01_tts_exploration.ipynb
├── src/                         # Gói mã nguồn cốt lõi
│   ├── __init__.py
│   ├── normalizer.py            # Tiền xử lý & chuẩn hóa tiếng Việt
│   ├── tts_engine.py            # Các Engine (VITS, Edge-TTS, gTTS)
│   └── vits_decomposed.py       # Phân rã mô hình VITS (tensor extraction)
├── tests/                       # Bộ kiểm thử toàn diện
│   ├── __init__.py
│   └── test_tts.py
├── outputs/                     # File âm thanh sinh ra (đã được .gitignore)
├── requirements.txt             # Thư viện phụ thuộc
├── synthesize.py                # Entrypoint chính (CLI & API gọi nhanh)
└── README.md                    # Tài liệu tổng quan
```

| Thành phần | Đường dẫn | Vai trò |
|---|---|---|
| **VITS Decomposed** | [`src/vits_decomposed.py`](src/vits_decomposed.py) | Bóc tách và trích xuất từng tensor trung gian ($h_{text}$, $\mu_0$, duration, vector $z$, waveform). |
| **Lý thuyết VITS** | [`docs/vits-architecture.md`](docs/vits-architecture.md) | Tài liệu học thuật chuyên sâu: VAE, Flows, MAS, HiFi-GAN và các hàm Loss. |
| **Text Normalizer** | [`src/normalizer.py`](src/normalizer.py) | Xử lý số, ngày tháng, phần trăm, tiền tệ, các ký hiệu viết tắt tiếng Việt. |
| **TTS Engines** | [`src/tts_engine.py`](src/tts_engine.py) | Quản lý đa Engine: `vits` (Local Deep Learning), `edge` (Cloud Neural), `gtts` (dự phòng). |
| **Entrypoint** | [`synthesize.py`](synthesize.py) | Cung cấp hàm `synthesize(...)` và giao diện dòng lệnh CLI. |
| **Testing** | [`tests/test_tts.py`](tests/test_tts.py) | Bộ kiểm thử toàn diện cho Normalizer và các engine tổng hợp. |
| **Notebook** | [`notebooks/01_tts_exploration.ipynb`](notebooks/01_tts_exploration.ipynb) | Trực quan hóa tensor, vẽ phổ sóng âm, đo đạc benchmark (RTF). |

---

## 3. Cài Đặt Môi Trường

Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

Nội dung `requirements.txt`:
```text
transformers>=4.40.0
torch>=2.0.0
soundfile>=0.12.0
edge-tts>=7.0.0
gTTS>=2.5.0
pydub>=0.25.1
```

---

## 4. Hướng Dẫn Sử Dụng

### 4.1. Sử dụng hàm tổng hợp nhanh (`synthesize`)

```python
from synthesize import synthesize

# 1. Chạy với mô hình End-to-End VITS chạy offline trên máy (mặc định)
audio_file = synthesize(
    text="Thủ đô của Việt Nam là Hà Nội.",
    output_path="outputs/vits_output.wav",
    engine="vits"
)
print("File âm thanh đã tạo:", audio_file)

# 2. Chạy với Edge-TTS (khi cần giọng đọc nơ-ron qua đám mây)
audio_file_edge = synthesize(
    text="Nhiệt độ hôm nay là 28°C.",
    output_path="outputs/edge_output.mp3",
    engine="edge",
    voice="vi-VN-HoaiMyNeural"
)
```

### 4.2. Phân rã và bóc tách từng tensor bên trong VITS

Để quan sát từng bước tính toán bên trong mô hình VITS:

```python
from src.vits_decomposed import VITSDecomposedTTS, print_decomposition_report

# Khởi tạo mô hình
vits = VITSDecomposedTTS(model_id="facebook/mms-tts-vie")

# Chạy phân rã suy luận
report = vits.decompose_inference(
    text="Chiến thắng Điện Biên Phủ ngày 07/05/1954.",
    output_path="outputs/decomposed.wav",
    speaking_rate=1.0  # Điều chỉnh tốc độ nói: > 1.0 (nhanh), < 1.0 (chậm)
)

# In báo cáo các tensor trung gian
print_decomposition_report(report)

# Truy xuất các tensor phục vụ nghiên cứu
print("Kích thước Text Encoder:", report.encoder_hidden_shape)
print("Số khung hình (Frames)  :", report.total_frames)
print("Thời lượng từng ký tự   :", report.durations_ms[:5])
```

### 4.3. Chạy từ dòng lệnh (CLI)

```bash
# Tổng hợp bằng VITS offline
python synthesize.py -t "Học máy và xử lý ngôn ngữ tự nhiên tiếng Việt." -e vits -o output.wav

# Chạy báo cáo phân rã VITS
python src/vits_decomposed.py
```

---

## 5. Kết Quả Kiểm Thử (Testing)

Chạy bộ kiểm thử để xác thực toàn bộ pipeline:

```bash
python tests/test_tts.py
```

Bộ kiểm thử thực hiện xác minh:
1. Độ chính xác của bộ chuyển đổi số thành chữ và các quy tắc ngày tháng tiếng Việt.
2. Quá trình tổng hợp âm thanh không bị rỗng và đúng định dạng tần số lấy mẫu.
3. Cơ chế chuyển đổi linh hoạt giữa mô hình Local (VITS) và Cloud (Edge-TTS, gTTS).
