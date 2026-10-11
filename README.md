# ViMMRC Voice Q&A (Kiến trúc sơ bộ)

Dự án Hỏi–Đáp (Q&A) tiếng Việt dựa trên bộ dữ liệu [ViMMRC 2.0](https://huggingface.co/datasets/uitnlp/vimmrc2.0), mở rộng thêm khả năng **giao tiếp bằng giọng nói**: Speech-to-Text (STT) đầu vào và Text-to-Speech (TTS) đầu ra.

## Chạy hệ thống tích hợp

Backend FastAPI phục vụ STT, BM25 retrieval, MRC và TTS qua cùng cổng `8000`. Từ thư mục gốc:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-api.txt
python -m uvicorn scripts.api_server:app --host 127.0.0.1 --port 8000
```

Lần chạy đầu, `faster-whisper` tải mô hình Whisper. Có thể chọn kích thước khác bằng biến môi trường `WHISPER_MODEL` (mặc định `small`) và thiết bị bằng `WHISPER_DEVICE` (mặc định `auto`). TTS mặc định dùng Edge TTS tiếng Việt, cần kết nối mạng; đặt `TTS_ENGINE=gtts` để chọn dự phòng Google TTS.

Mặc định hệ thống chạy với kho hai đoạn văn mẫu và `LexicalBaselineClient` để minh họa kết nối. Đây không phải checkpoint MRC đã huấn luyện và chất lượng trả lời còn hạn chế. Để dùng dữ liệu/các mô hình đã chuẩn bị, đặt `QA_INDEX` tới index JSON đã tạo bởi `Retriever.save()` và `MRC_CHECKPOINT` tới checkpoint ViT5 đã fine-tune trước khi chạy backend. Dữ liệu ViMMRC, checkpoint, và âm thanh không được commit lên Git.

Trong terminal thứ hai:

```powershell
cd web-interface_Luong
npm ci
npm start
```

Mở URL Angular hiển thị trong terminal (mặc định `http://localhost:4200`). Proxy chuyển toàn bộ `/api/*` về backend ở cổng `8000`. Endpoint `/api/health` cho biết backend đang ở chế độ demo hay đã cấu hình index/checkpoint.

> Phần của Huy đã có Retrieval BM25, mã/notebook MRC và demo ghép nối độc lập. Xem [hướng dẫn bàn giao](docs/huy-handover.md). Huấn luyện ViT5 đầy đủ vẫn cần chạy để tạo checkpoint; demo hiện dùng baseline có ghi nhãn rõ ràng.

## Chạy phần của Huy

```powershell
python -X utf8 scripts/qa_pipeline.py --demo
```

- [Notebook Retrieval](retrieval-model_Huy/01_bm25_retrieval.ipynb)
- [Notebook MRC](mrc-model_Huy/01_vimmrc_training.ipynb)
- [Notebook tích hợp](notebooks/03_integration_demo.ipynb)
- [Quy trình và hợp đồng ghép nối](docs/huy-handover.md)

## 1. Mục tiêu

- Đọc hiểu văn bản tiếng Việt và trả lời câu hỏi trắc nghiệm/tự luận dựa trên ViMMRC 2.0.
- Cho phép người dùng **hỏi bằng giọng nói** thay vì gõ chữ.
- Trả lời lại bằng **giọng nói tổng hợp** (không chỉ hiển thị văn bản).

## 2. Dataset

- **Nguồn**: [uitnlp/vimmrc2.0](https://huggingface.co/datasets/uitnlp/vimmrc2.0)
- **Nội dung**: đoạn văn (passage) tiếng Việt + câu hỏi + các phương án trả lời (trắc nghiệm 4 đáp án) + đáp án đúng.
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
                         │    ViMMRC 2.0                │
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
4. **Mô hình MRC**: Đưa (passage, câu hỏi) vào mô hình đọc hiểu đã fine-tune trên ViMMRC 2.0 để sinh câu trả lời.
5. **TTS**: Chuyển câu trả lời text → audio (ví dụ: VAIS TTS, FPT.AI TTS, Google TTS, Coqui TTS).
6. **Phát lại**: Trả audio về cho người dùng nghe.

## 5. Các thành phần dự kiến

| Thành phần        | Vai trò                                   | Gợi ý công nghệ                          |
|--------------------|---------------------------------------------|--------------------------------------------|
| STT                | Audio → Text                               | Whisper, FPT.AI STT, Google STT           |
| Retrieval          | Chọn đoạn văn liên quan (nếu nhiều passage) | BM25, sentence-embedding + vector search  |
| MRC Model          | Trả lời câu hỏi dựa trên passage           | PhoBERT/ViBERT fine-tune trên ViMMRC 2.0  |
| TTS                | Text → Audio                                | FPT.AI TTS, Google TTS, Coqui TTS, VAIS   |
| Giao diện          | Ghi âm & phát audio                         | Web app (mic + speaker)                   |

## 6. Tiến độ

- [x] Tải và kiểm tra schema, số lượng, cách chia dữ liệu ViMMRC 2.0.
- [x] Chuẩn bị Retrieval BM25, notebook và đo baseline trên dev.
- [x] Chuẩn bị mã fine-tune ViT5 và API MRC độc lập.
- [ ] Hoàn tất huấn luyện GPU và đánh giá checkpoint ViT5.
- [ ] Chọn nhà cung cấp/thư viện STT & TTS tiếng Việt.
- [x] Thiết kế hợp đồng văn bản cho Retrieval → MRC và demo ghép nối.
- [ ] Ghép STT, TTS và giao diện với checkpoint cuối cùng.

## 7. Phân công

| Thành viên | Công việc | Thư mục |
|---|---|---|
| Huỳnh Công Lương | Speech-to-Text (STT) | `speech-to-text_Luong/` |
| Trương Hoàng Duy | Text-to-Speech (TTS) | `text-to-speech_Duy/` |
| Ngô Trí Huy | Retrieval model | `retrieval-model_Huy/` |
| Ngô Trí Huy | MRC model (fine-tune ViMMRC 2.0) | `mrc-model_Huy/` |
| Huỳnh Công Lương | Giao diện web (mic + speaker) | `web-interface_Luong/` |
