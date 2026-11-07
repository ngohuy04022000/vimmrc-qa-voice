# ViMMRC Voice Q&A

Dự án Hỏi–Đáp (Q&A) tiếng Việt dựa trên bộ dữ liệu [ViMMRC 2.0](https://huggingface.co/datasets/uitnlp/vimmrc2.0), mở rộng thêm khả năng **giao tiếp bằng giọng nói**: Speech-to-Text (STT) đầu vào và Text-to-Speech (TTS) đầu ra.

> Trạng thái từng module, API contract thật và các bẫy đã biết: xem [STATUS.md](STATUS.md). Quy ước đặt tên/git: [CONVENTIONS.md](CONVENTIONS.md).

## Chạy hệ thống tích hợp

Backend FastAPI phục vụ STT (Whisper), retrieval lai BM25 + dense + reranker bge-reranker-v2-m3 (kho hai tầng: 5.879 đoạn ViMMRC + ViQuAD + thẻ tri thức và 1,48 triệu đoạn Wikipedia tiếng Việt), MRC (mặc định bộ đọc trích span `vi-mrc-large`, ViT5 sinh câu trả lời tự do là phương án thay thế), cổng từ chối theo điểm reranker (`DIALOGUE_MIN_RERANK`) và TTS (Matcha-TTS, VITS, Edge-TTS, gTTS) qua cổng `8000`.

Từ thư mục gốc:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-api.txt
python -m uvicorn scripts.api_server:app --host 127.0.0.1 --port 8000
```

- **Tầng hội thoại** (`dialogue-manager_Huy/`, route `POST /api/ask`; web UI gọi route này, giữ `session_id` giữa các lượt): hiểu câu xã giao, câu hỏi nối tiếp nhiều lượt
  ("còn Hàn Quốc thì sao?", "ông ấy sinh năm nào?"), câu so sánh, câu ghép nhiều vế, câu đúng/sai, tại sao/như thế nào,
  tóm tắt đoạn văn dán vào; trả lời thành câu trọn vẹn cho TTS và nói "chưa tìm thấy" thay vì đoán. Chi tiết và kết quả
  đánh giá trên hơn 200 câu hỏi/hội thoại ngoài dataset: [dialogue-manager_Huy/README.md](dialogue-manager_Huy/README.md).
- Hệ thống tự động nhận diện kho bài đọc ViMMRC tại `data/vimmrc_index.json` (hoặc biến `QA_INDEX`); chưa có thì dùng kho mẫu 75 đoạn.
- Mô hình đọc hiểu nạp qua biến môi trường `MRC_CHECKPOINT` (Docker mặc định dùng `mrc-model_Huy/checkpoints/vi-mrc-large`, mô hình trích span `nguyenvulebinh/vi-mrc-large`; ViT5 `vit5-combined-cont` vẫn dùng được bằng cách đặt biến này); không đặt thì dùng bộ trích câu khớp nhất làm dự phòng. Mô hình này có giấy phép CC-BY-NC-4.0 (chỉ phi thương mại); ViT5 là lựa chọn thay thế nếu cần dùng thương mại. Checkpoint không nằm trong git: tải bằng `hf download nguyenvulebinh/vi-mrc-large --local-dir mrc-model_Huy/checkpoints/vi-mrc-large` (cần `config.json`, `model.safetensors`, tokenizer).
- Phân hệ TTS tự động chuẩn hóa văn bản tiếng Việt (số, ngày tháng), hỗ trợ đa engine (`matcha`, `vits`, `edge`, `gtts`) với cơ chế tự động chuyển dự phòng thông minh (fallback).
- Giao diện web Angular đã được build sẵn tại `web-interface_Luong/dist/` và được phục vụ trực tiếp tại `http://127.0.0.1:8000/`.

## Chạy nhanh bằng Docker & Docker Compose

Dự án đã có cấu hình Multi-stage Dockerfile (tự động build frontend Angular và backend Python) cùng Docker Compose:

```powershell
# Khởi động container ở chế độ background
docker compose up -d --build

# Xem log hoạt động
docker logs -f vimmrc-qa-voice

# Dừng container
docker compose down
```

Truy cập ứng dụng tại `http://localhost:8090/` (Docker map cổng 8090 của máy chủ tới cổng 8000 trong container). Giao diện Angular và toàn bộ API backend đã sẵn sàng hoạt động.

Để chạy chế độ phát triển Frontend (với hot-reload qua proxy):

```powershell
cd web-interface_Luong
npm install
npm start
```

Mở trình duyệt tại `http://localhost:4200`.

## Kiểm thử toàn diện hệ thống

```powershell
python -m pytest -v
```

Hiện có **138 bài kiểm thử tự động, đạt cả 138** (chạy `pytest -q` ngày 2026-11-08, Python 3.11) phủ STT, Retrieval, Context Selection, MRC (ViT5), TTS (normalizer, VITS, Matcha, Edge, gTTS), tầng hội thoại (`dialogue-manager_Huy/tests`, gồm chốt chất lượng trên bộ đánh giá), Intent Router, bộ câu hỏi ngoài dataset, Web UI và FastAPI end-to-end (`/api/ask`).

### Môi trường cục bộ (không dùng Docker)

Dùng `.venv` của dự án (Python 3.11), không dùng Python hệ thống: `transformers` phải `<4.58` (ViT5), nếu không tokenizer không nạp được.

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-docker.txt   # nếu thiếu gói
.venv\Scripts\python.exe -m pip install "diffusers>=0.25,<0.36"      # khớp huggingface-hub<1.0 mà transformers<4.58 cần
.venv\Scripts\python.exe text-to-speech_Duy\scripts\setup_matcha.py   # clone mã Matcha-TTS vào text-to-speech_Duy/Matcha-TTS
$env:TRANSFORMERS_NO_TF = "1"; .venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m uvicorn scripts.api_server:app --port 8000
```

Chưa có `Matcha-TTS/` thì `synthesize()` im lặng chuyển sang gTTS (file `.mp3`, cần mạng); test `test_matcha_engine` và `test_vits_engine` kiểm tra đuôi `.wav` để phát hiện trường hợp này.

Web (`web-interface_Luong`): bấm micro rồi nói; hệ thống tự dừng thu âm sau khoảng 1,3 giây im lặng và tự gửi câu hỏi (bấm lại nút micro để dừng ngay). Không nghe thấy gì trong 8 giây thì huỷ và báo lỗi. Cần dựng lại web (`npm run build`) sau khi sửa mã.

## Chạy CLI Pipeline đầu-cuối

```powershell
# Hỏi đáp tự do với ViT5 đã fine-tune + tổng hợp giọng nói
python -X utf8 scripts/qa_pipeline.py --index data/vimmrc_index.json --model mrc-model_Huy/checkpoints/vit5-combined-cont --question "Thủ đô của Việt Nam là gì?" --tts

# Chạy demo offline
python -X utf8 scripts/qa_pipeline.py --demo --question "Cà phê trồng ở đâu?"

# Trò chuyện nhiều lượt trên terminal (không cần mô hình)
python -X utf8 dialogue-manager_Huy/chat_cli.py --debug
```

- [Notebook Retrieval](retrieval-model_Huy/01_bm25_retrieval.ipynb)
- [Notebook MRC](mrc-model_Huy/01_vimmrc_training.ipynb)
- [Notebook tích hợp](notebooks/03_integration_demo.ipynb)
- [Quy trình và hợp đồng ghép nối](docs/huy-handover.md)

## 1. Mục tiêu

- Đọc hiểu văn bản tiếng Việt và trả lời câu hỏi tự do dựa trên ViMMRC 2.0 (không cần phương án lựa chọn).
- Cho phép người dùng **hỏi bằng giọng nói** thay vì gõ chữ.
- Trả lời lại bằng **giọng nói tổng hợp** (không chỉ hiển thị văn bản).

## 2. Dataset

- **Nguồn**: [uitnlp/vimmrc2.0](https://huggingface.co/datasets/uitnlp/vimmrc2.0)
- **Nội dung**: ViMMRC gốc là dạng trắc nghiệm; dự án chuyển sang dạng hỏi - đáp tự do (đoạn văn + câu hỏi + câu trả lời dạng văn bản, lấy từ văn bản của đáp án đúng) và bổ sung thêm UIT-ViQuAD2.0.
- **Dữ liệu huấn luyện MRC**: ViMMRC 2.0 (5.273 câu) + UIT-ViQuAD2.0 (28.454 câu gốc → 21.891 câu sau khi loại câu không có đáp án) = 27.164 câu; chia theo bài đọc: train 21.733 / dev 2.715 / test 2.716.
- **Vai trò**: dùng để huấn luyện/đánh giá mô hình đọc hiểu (MRC) trả lời câu hỏi dựa trên ngữ cảnh.

## 3. Sơ đồ kiến trúc tổng thể

```
                         ┌────────────────────────────┐
                         │        Người dùng           │
                         └──────────────┬───────────────┘
                                         │ giọng nói (audio)
                                         ▼
                         ┌────────────────────────────┐
                         │   STT (Speech-to-Text)      │
                         │  audio → văn bản câu hỏi    │
                         └──────────────┬───────────────┘
                                         │ câu hỏi (text)
                                         ▼
                         ┌────────────────────────────┐
                         │      Module Q&A (MRC)        │
                         │  - Passage retrieval/chọn    │
                         │    đoạn văn liên quan        │
                         │  - Mô hình đọc hiểu (MRC)     │
                         │    được train/fine-tune trên │
                         │    ViMMRC 2.0 + ViQuAD2.0    │
                         └──────────────┬───────────────┘
                                         │ câu trả lời (text)
                                         ▼
                         ┌────────────────────────────┐
                         │   TTS (Text-to-Speech)      │
                         │  văn bản → audio            │
                         └──────────────┬───────────────┘
                                         │ giọng nói (audio)
                                         ▼
                         ┌────────────────────────────┐
                         │        Người dùng           │
                         └────────────────────────────┘
```

## 4. Luồng xử lý chi tiết (pipeline)

1. **Thu âm**: Người dùng nói câu hỏi qua micro (web/app).
2. **STT**: Chuyển audio → text (ví dụ: Whisper, Google Speech-to-Text, VAIS/FPT.AI cho tiếng Việt).
3. **Truy xuất ngữ cảnh (Retrieval)**: Nếu có nhiều đoạn văn, chọn passage liên quan nhất tới câu hỏi (BM25/embedding search).
4. **Mô hình MRC**: Đưa (passage, câu hỏi) vào mô hình đọc hiểu đã fine-tune trên ViMMRC 2.0 + UIT-ViQuAD2.0 để sinh câu trả lời.
5. **TTS**: Chuyển câu trả lời text → audio (ví dụ: VAIS TTS, FPT.AI TTS, Google TTS, Coqui TTS).
6. **Phát lại**: Trả audio về cho người dùng nghe.

## 5. Các thành phần dự kiến

| Thành phần        | Vai trò                                   | Gợi ý công nghệ                          |
|--------------------|---------------------------------------------|--------------------------------------------|
| STT                | Audio → Text                               | Whisper, FPT.AI STT, Google STT           |
| Retrieval          | Chọn đoạn văn liên quan (nếu nhiều passage) | BM25 + dense (multilingual-e5-small) + reranker bge-reranker-v2-m3 |
| MRC Model          | Trả lời câu hỏi dựa trên passage           | `vi-mrc-large` (trích span, mặc định) · ViT5-base fine-tune trên ViMMRC 2.0 + UIT-ViQuAD2.0 (thay thế) |
| TTS                | Text → Audio                                | FPT.AI TTS, Google TTS, Coqui TTS, VAIS   |
| Giao diện          | Ghi âm & phát audio                         | Web app (mic + speaker)                   |

## 6. Tiến độ

- [x] Tải và kiểm tra schema dữ liệu ViMMRC 2.0 (5.273 câu) và gộp với UIT-ViQuAD2.0 (21.891 câu) thành 27.164 câu, chia theo bài đọc: train 21.733 / dev 2.715 / test 2.716.
- [x] Chuẩn bị Retrieval BM25, lập chỉ mục toàn bộ bài đọc (`data/vimmrc_index.json`).
- [x] Chuẩn bị mã fine-tune ViT5 và API MRC độc lập.
- [x] Fine-tune ViT5 sinh câu trả lời tự do (test: EM 41,05%, token F1 66,55% (bộ gộp, test 2.716 câu)).
- [x] Tích hợp STT tiếng Việt (Whisper-small fine-tune LoRA 50h VietSpeech → CTranslate2 int8, WER 13,77% / CER 6,67% trên 1.802 mẫu test; bộ đệm lazy-load).
- [x] Triển khai hệ thống TTS đa engine tiếng Việt (Matcha-TTS, VITS MMS, Edge-TTS, gTTS) có tự động fallback và chuẩn hóa văn bản.
- [x] Thiết kế hợp đồng văn bản cho Retrieval → MRC và pipeline đầu-cuối CLI.
- [x] Ghép toàn diện STT, Retrieval, MRC, TTS và giao diện web Angular vào API Server FastAPI thống nhất.
- [x] Tự động hóa bộ kiểm thử tích hợp (138 test cases kiểm thử tự động toàn diện, gồm tầng hội thoại).
- [x] Đối sánh 8 bộ đọc trên cùng đoạn văn (`scripts/eval_readers.py`) và chuyển bộ đọc mặc định sang `vi-mrc-large`; cộng điểm KB trên logit, cổng từ chối, reranker INT8.

## 7. Phân công

| Thành viên | Công việc | Thư mục |
|---|---|---|
| Huỳnh Công Lương | Speech-to-Text (STT) | `speech-to-text_Luong/` |
| Trương Hoàng Duy | Text-to-Speech (TTS) | `text-to-speech_Duy/` |
| Ngô Trí Huy | Retrieval model (+ tích hợp backend, kho tri thức) | `retrieval-model_Huy/` |
| Ngô Trí Huy | MRC model (ViT5 fine-tune trên ViMMRC 2.0 + UIT-ViQuAD2.0) | `mrc-model_Huy/` |
| Huỳnh Công Lương | Giao diện web (mic + speaker) và Docker | `web-interface_Luong/` |
