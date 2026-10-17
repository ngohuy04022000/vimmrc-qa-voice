# STATUS.md

Trạng thái thật của hệ thống, để đọc lại một lần thay vì dò từng README con. Khi
code đổi khác bảng dưới, sửa bảng — đừng để lệch.

## Trạng thái từng module

| Module | Trạng thái | File chính | Hợp đồng vào/ra | Chạy standalone | Test |
|---|---|---|---|---|---|
| STT | Xong (Faster-Whisper) | `speech-to-text_Luong/stt_server.py` | `POST /api/stt` (multipart audio) → `{text}` | `uvicorn stt_server:app --port 8001` | chưa có test riêng |
| Retrieval | Xong, đã benchmark | `retrieval-model_Huy/retrieval_client.py` | `Retriever.search(q, top_k) -> list[{id,passage,score}]`; `Retriever.retrieve(q) -> str` (API phụ, chỉ `test_retrieval.py` dùng) | `retrieval_cli.py` | `retrieval-model_Huy/test_retrieval.py` |
| MRC (ViT5) | Chỉ hoạt động sau khi fine-tune; chưa có checkpoint sẵn trong repo | `mrc-model_Huy/mrc_client.py` | `answer_question(question, passage) -> str` | `train.py` → checkpoint, rồi `MRCClient(checkpoint_dir)` | `mrc-model_Huy/tests/` |
| Lexical baseline (MRC) | Xong, dùng khi chưa có checkpoint ViT5 | `mrc_client.LexicalBaselineClient` | `answer_question(question, passage) -> str` | không cần setup | cùng `mrc-model_Huy/tests/` |
| ChoiceRanker (trắc nghiệm) | Đã train: **51,95%** acc dev (vs lexical baseline 43,62%, random 25,18%) | `mrc-model_Huy/choice_ranker.py` | `predict(question, passage, options[4]) -> {label, scores, answer}` | `train_choice_ranker.py` | `test_choice_ranker.py` |
| TTS | Xong: Matcha-TTS mặc định (cần `checkpoints/matcha_vi.pt` + `scripts/setup_matcha.py`), VITS/Edge/gTTS, lỗi thì fallback gTTS | `text-to-speech_Duy/synthesize.py` | `synthesize(text, engine?, voice?) -> đường dẫn audio` | `python synthesize.py --text "..."` | `text-to-speech_Duy/tests/` |
| Tích hợp API | Xong | `scripts/api_server.py` (mount `stt_server.app`) | xem bảng route dưới | `uvicorn scripts.api_server:app` | `tests/test_api_server.py`, `tests/test_pipeline.py` |
| Web UI | Xong (Angular), build sẵn được server phục vụ nếu có `dist/` | `web-interface_Luong/src/app/` | gọi các route `/api/*` qua `pipeline.service.ts` | `npm start` trong `web-interface_Luong/` | chưa có test riêng |

## API contract thật (khớp code, không phải thiết kế dự kiến)

- `GET  /api/health` → `{status, retrieval, retrieval_passages, reader, choice_ranker, tts_engine, frontend_served}`
- `POST /api/stt` (multipart file audio) → `{text}`
- `POST /api/retrieve` `{question, top_k?}` → `{passages: [{id, text, score}]}`
- `POST /api/answer` `{question, passage, options?: [4 string]}` →
  - không có `options`: `{answer}` (text tự do, từ `MRCClient`/`LexicalBaselineClient`)
  - có `options`: `{answer, choice_label, choice_scores}` (từ `ChoiceRanker`) — **web UI hiện không gửi `options`**, chỉ CLI/test dùng nhánh này.
- `POST /api/tts` `{text, engine?, voice?, rate?}` → file audio

## Biết rồi, không cần đọc lại

- `QAPipeline.predict(..., options=[...])` chỉ an toàn khi `reader` là `ChoiceRanker` (có `.predict()`).
  Dùng với `MRCClient`/`LexicalBaselineClient` (chỉ có `.answer_question()`) sẽ raise `TypeError` rõ nghĩa
  (đã thêm guard ở `scripts/qa_pipeline.py`, không còn `AttributeError` mơ hồ).
- `requirements-api.txt` (dùng khi chạy `uvicorn` trực tiếp, không qua Docker) đã bổ sung
  `torch`/`transformers`/`scikit-learn`/`joblib` — cần nếu bật `MRC_CHECKPOINT` hoặc checkpoint ChoiceRanker;
  không cần nếu chỉ dùng lexical baseline.
- `Retriever.load()` và `Retriever(passages)` (khởi tạo mới) dùng **cùng** `OPTIMIZED_CONFIG` làm mặc định
  cho field BM25 thiếu trong JSON — đã đồng bộ, trước đây `load()` lặng lẽ rơi về baseline cũ.
- `transformers` được nới về `>=4.40.0,<4.58` ở cả `mrc-model_Huy/requirements.txt` và
  `requirements-api.txt`/`text-to-speech_Duy/requirements.txt`, tránh pin cứng gây resolver conflict
  khi cài chung một venv.
- `choice_accuracy` trong `mrc-model_Huy/README.md` là phép ghép **heuristic** (so khớp F1 câu sinh với 4
  lựa chọn), không phải điểm xác suất thật của mô hình cho từng lựa chọn — khác với `ChoiceRanker.predict`.

## Nợ kỹ thuật còn lại (không gấp)

- STT, web UI chưa có test riêng.
- MRC (ViT5 fine-tune) chưa có checkpoint kèm repo — pipeline mặc định chạy lexical baseline cho đến khi ai train.
- Tính năng trắc nghiệm của `/api/answer` (`options` → `choice_label`) chưa được web UI dùng; chỉ tồn tại qua CLI/test.
