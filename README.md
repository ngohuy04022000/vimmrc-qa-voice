# ViMMRC Voice Q&A (Kiến trúc sơ bộ)

Dự án Hỏi–Đáp (Q&A) tiếng Việt dựa trên bộ dữ liệu [ViMMRC 2.0](https://huggingface.co/datasets/uitnlp/vimmrc2.0), mở rộng thêm khả năng **giao tiếp bằng giọng nói**: Speech-to-Text (STT) đầu vào và Text-to-Speech (TTS) đầu ra.

> Lưu ý: đây chỉ là tài liệu thiết kế/sơ đồ kiến trúc, chưa triển khai code.

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

## 6. Bước tiếp theo (chưa triển khai)

- [ ] Tải và khảo sát dataset ViMMRC 2.0.
- [ ] Chọn base model tiếng Việt để fine-tune MRC.
- [ ] Chọn nhà cung cấp/thư viện STT & TTS tiếng Việt.
- [ ] Thiết kế API kết nối các module (STT → MRC → TTS).

## 7. Phân công

| Thành viên | Công việc | Thư mục |
|---|---|---|
| Huỳnh Công Lương | Speech-to-Text (STT) | `speech-to-text_Luong/` |
| Trương Hoàng Duy | Text-to-Speech (TTS) | `text-to-speech_Duy/` |
| Ngô Trí Huy | Retrieval model | `retrieval-model_Huy/` |
| Ngô Trí Huy | MRC model (fine-tune ViMMRC 2.0) | `mrc-model_Huy/` |
| Huỳnh Công Lương | Giao diện web (mic + speaker) | `web-interface_Luong/` |
