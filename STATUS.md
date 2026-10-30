# STATUS.md

Trạng thái thật của hệ thống, để đọc lại một lần thay vì dò từng README con. Khi
code đổi khác bảng dưới, sửa bảng — đừng để lệch.

## Trạng thái từng module

| Module | Trạng thái | File chính | Hợp đồng vào/ra | Chạy standalone | Test |
|---|---|---|---|---|---|
| STT | Xong (Faster-Whisper). Checkpoint fine-tune Whisper-small-vi (50h) có trên Drive nhóm, tải về `speech-to-text_Luong/checkpoints/whisper-small-vi-50h-ct2/` (không commit vào git) | `speech-to-text_Luong/stt_server.py` | `POST /api/stt` (multipart audio) → `{text}` | `WHISPER_MODEL=<path checkpoint> uvicorn stt_server:app --port 8001` (bỏ `WHISPER_MODEL` → model "small" gốc chưa fine-tune) | chưa có test riêng |
| Retrieval (RAG) | Xong. KB 2 tầng: `data/kb_index.json` (552 ViMMRC + 5.317 ViQuAD) + `data/kb_wiki_full` (1,48 triệu đoạn Wikipedia tiếng Việt, bm25s shard, dùng khi điểm wiki > 0,5 × điểm KB). Dựng bằng `build_kb.py`; data không commit. Dev R@1 70,7% / R@5 85,1%, ~30 ms/câu | `retrieval-model_Huy/kb_retriever.py` (`load_any`), `retrieval_client.py` | `Retriever.search(q, top_k) -> list[{id,passage,score}]`; `Retriever.retrieve(q) -> str` (API phụ, chỉ `test_retrieval.py` dùng) | `retrieval_cli.py` | `retrieval-model_Huy/test_retrieval.py` |
| MRC (ViT5) | Đã fine-tune trên bộ dữ liệu mở rộng (xem dưới): **Exact Match 41,05%, token F1 66,55%** trên test (27.164 câu, không so được với số liệu ViMMRC thuần cũ). Checkpoint dùng trong Docker: `mrc-model_Huy/checkpoints/vit5-combined-cont/` (train tiếp 2 epoch từ `vit5-combined`, F1 66,02%), không commit (quá lớn) | `mrc-model_Huy/mrc_client.py` | `answer_question(question, passage) -> str` | `MRC_CHECKPOINT=<path> uvicorn scripts.api_server:app`, hoặc `MRCClient(checkpoint_dir)` trực tiếp | `mrc-model_Huy/tests/` |
| Lexical baseline (MRC) | Xong, dùng khi chưa có checkpoint ViT5 | `mrc_client.LexicalBaselineClient` | `answer_question(question, passage) -> str` | không cần setup | cùng `mrc-model_Huy/tests/` |
| TTS | Xong: Matcha-TTS mặc định (cần `checkpoints/matcha_vi.pt` + `scripts/setup_matcha.py`), VITS/Edge/gTTS, lỗi thì fallback gTTS | `text-to-speech_Duy/synthesize.py` | `synthesize(text, engine?, voice?) -> đường dẫn audio` | `python synthesize.py --text "..."` | `text-to-speech_Duy/tests/` |
| Tích hợp API | Xong | `scripts/api_server.py` (mount `stt_server.app`) | xem bảng route dưới | `uvicorn scripts.api_server:app` | `tests/test_api_server.py`, `tests/test_pipeline.py` |
| Web UI | Xong (Angular), build sẵn được server phục vụ nếu có `dist/` | `web-interface_Luong/src/app/` | gọi các route `/api/*` qua `pipeline.service.ts` | `npm start` trong `web-interface_Luong/` | chưa có test riêng |

## API contract thật (khớp code, không phải thiết kế dự kiến)

- `GET  /api/health` → `{status, retrieval, retrieval_passages, reader, tts_engine, frontend_served}`
- `POST /api/stt` (multipart file audio) → `{text}`
- `POST /api/retrieve` `{question, top_k?}` → `{passages: [{id, text, score}]}`
- `POST /api/answer` `{question, passage}` → `{answer}` (text tự do, từ `MRCClient`/`LexicalBaselineClient`).
  Hệ thống chỉ hỏi đáp tự do; phần trắc nghiệm (ChoiceRanker, `options`) đã bị gỡ bỏ.
- `POST /api/tts` `{text, engine?, voice?, rate?}` → file audio

## Biết rồi, không cần đọc lại

- `requirements-api.txt` (dùng khi chạy `uvicorn` trực tiếp, không qua Docker) đã bổ sung
  `torch`/`transformers` — cần nếu bật `MRC_CHECKPOINT`; không cần nếu chỉ dùng lexical baseline.
- transformers ≥5 không đọc được tokenizer ViT5 đã lưu (`TypeError ... 'vocab'`); giữ `<4.58`. Khi train,
  đặt `TRANSFORMERS_NO_TF=1` để tránh treo lúc import TensorFlow.
- `Retriever.load()` và `Retriever(passages)` (khởi tạo mới) dùng **cùng** `OPTIMIZED_CONFIG` làm mặc định
  cho field BM25 thiếu trong JSON — đã đồng bộ, trước đây `load()` lặng lẽ rơi về baseline cũ.
- `transformers` được nới về `>=4.40.0,<4.58` ở cả `mrc-model_Huy/requirements.txt` và
  `requirements-api.txt`/`text-to-speech_Duy/requirements.txt`, tránh pin cứng gây resolver conflict
  khi cài chung một venv.

## Đánh giá toàn chuỗi (retrieval → ViT5), `scripts/eval_e2e.py`

Dev 2.570 câu (404 ViMMRC + 2.166 ViQuAD có đoạn văn trong KB), báo cáo `reports/e2e_dev_kb_*.json`:

| Reader | Toàn chuỗi EM / F1 | ViMMRC F1 | ViQuAD F1 | Đoạn đúng F1 |
|---|---|---|---|---|
| **vit5-combined-cont** (đang dùng) | 33,4 / 54,6 | 22,5 | 60,6 | 68,7 |
| vit5-vimmrc-ft (fine-tune riêng ViMMRC, dừng sớm khi dev phẳng) | 32,4 / 54,4 | 23,9 | 60,1 | 68,1 |

**Test** (2.545 câu, `vit5-combined-cont`, `reports/e2e_test_kb_vit5-combined-cont.json`): R@1 71,1% / R@5 85,9%;
toàn chuỗi EM 32,3 / F1 53,9 (ViMMRC F1 22,4, ViQuAD F1 59,6); đoạn đúng F1 68,6.

**Chọn tầng KB/Wikipedia** (`scripts/eval_routing.py`, `reports/routing_e2e.json`, 500 câu/bộ, answer F1): A = câu có
đoạn trong KB, B = câu ViQuAD test đã gỡ đoạn khỏi KB (kiến thức mở). Ngưỡng BM25 0,5 → A 53,7 / B 14,1; **0,4 → A 52,9 /
B 16,0 (đang dùng)**; chọn theo độ tự tin ViT5 (margin 0) → A 44,7 / B 19,4. Câu kiến thức mở vẫn yếu (F1 ~16).
**Dense Wikipedia** (`build_dense.py`, e5-small, `shard_*/embeddings.npy` float16 1,1 GB; `scripts/eval_dense.py`,
`reports/dense_routing_e2e.json`, 200 câu/bộ, CPU): ngưỡng BM25 0,4 chọn tầng, đoạn wiki lấy từ dense → A 57,9 / B 16,9
(BM25 thuần: 58,0 / 15,4) — **đang dùng**. Xếp hạng chung bằng cosine cho cả hai tầng: B 20,7 nhưng A tụt còn 32–45, không dùng.
Độ trễ Docker CPU (`OMP_NUM_THREADS=4`): STT ~3 s, truy xuất ~0,1 s, ViT5 1,4–4 s, Matcha 1–4 s.

Đã thử, không áp dụng: reranker bge-v2-m3 (+1,5 R@1, chậm ~1 s/câu), đọc top-3 lấy điểm cao nhất (kém hơn),
`question_chunks` lúc suy luận (không tăng). STT: Whisper-small-vi-50h (`eval_stt.py`, WER 8,1% trên gTTS).

## Dữ liệu huấn luyện MRC đã mở rộng

`mrc-model_Huy/build_combined_dataset.py` gộp ViMMRC 2.0 (5.273 câu hỏi, trắc nghiệm) với
[UIT-ViQuAD2.0](https://huggingface.co/datasets/taidng/UIT-ViQuAD2.0) (21.891 câu hỏi tự luận,
Wikipedia, công khai) thành pool chung, rồi chia lại 80/10/10 theo **đơn vị passage** (không rò rỉ
article giữa split) → ghi ra `data/combined/{train,dev,test}_vimmrc.json` (27.164 câu hỏi tổng, không
commit — tự chạy script để tái tạo, seed cố định 42). `mrc_data.flatten_articles` đọc được cả hai dạng
article (ViMMRC có `options`/`answers` → lấy văn bản phương án đúng làm đáp án; ViQuAD có `answer_texts`).
Chi tiết: `mrc-model_Huy/README.md`.

- `train.py`'s `compute_metrics`/predict test từng crash `OverflowError: can't convert negative int to unsigned`
  khi eval cuối epoch 1 trên bộ dữ liệu mở rộng — `predictions` sinh ra từ `generate()` có thể chứa `-100`
  giống `labels`, nhưng chỉ `labels` được lọc trước `batch_decode`. Đã sửa: lọc `-100` → `pad_token_id`
  cho cả `predictions` ở `compute_metrics` và ở phần predict test cuối.

## Đã thử: nâng độ chính xác MRC lên 80-90% bằng LLM (kết luận: không khả thi với cách đo hiện có)

Mục tiêu ban đầu là đạt 80-90% Exact Match. Đã thử 2 hướng dùng LLM local (Ollama,
`mrc-model_Huy/llm_eval.py`):

| Hướng | n | LLM-judge acc | EM ký tự | Token F1 |
|---|---|---|---|---|
| ViT5 fine-tune + LLM chấm theo ý nghĩa | 200 | 61,0% | 43,5% | 65,6% |
| ViT5 fine-tune + LLM chấm theo ý nghĩa | 50 (cùng seed với dòng dưới) | 50,0% | 44,0% | 63,0% |
| LLM (`ornith-1.5:9b`) sinh trực tiếp, không dùng ViT5 | 50 (cùng seed) | 54,0% | 32,0% | 61,7% |

**Kết luận:** không hướng nào tới gần 80-90% ở bất kỳ thước đo nào. So sánh công bằng (cùng 50
câu, cùng seed) cho thấy ViT5 fine-tune và LLM 9B sinh trực tiếp **gần như tương đương**
(chênh vài điểm, trong biên độ sai số của mẫu 50 câu) — không có hướng nào nổi trội rõ ràng.
32% câu hỏi (16/50) cả hai hướng đều trả lời sai giống nhau — đây là giới hạn thật của bài toán
(câu hỏi cần suy luận/ngữ cảnh phức tạp), không phải điểm yếu riêng của một model. Chấm theo ý
nghĩa (LLM judge) luôn cao hơn EM ký tự ~10-20 điểm vì câu trả lời dài diễn giải khác cách nhưng
đúng ý — đây là hướng cải thiện thước đo thật, không phải cải thiện model.

Để tiến xa hơn mức ~50-61% thật sự cần: model LLM lớn hơn hẳn (70B+, hoặc API thương mại như
GPT-4/Claude thay Ollama local 9B), hoặc re-rank nhiều candidate answer, hoặc chấp nhận F1/judge
accuracy làm thước đo chính thay EM ký tự (EM ký tự về cấu trúc không thể cao với câu trả lời
dài có trong dữ liệu này, bất kể model tốt đến đâu).

## Nợ kỹ thuật còn lại (không gấp)

- STT, web UI chưa có test riêng.
- Pipeline mặc định (không set `MRC_CHECKPOINT`) vẫn chạy lexical baseline — checkpoint ViT5 đã có nhưng
  không commit vào git (quá lớn), mỗi máy cần tự chạy `train.py` để có checkpoint cục bộ.
- Exact Match 41% còn khiêm tốn — ViT5-base, 3 epoch, chưa hyperparameter search. Đã thử LLM judge/generate
  để cải thiện (xem mục trên) — không có hướng nào vượt trội rõ ràng ở quy mô đã thử.
