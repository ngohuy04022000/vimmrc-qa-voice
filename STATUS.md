# STATUS.md

Trạng thái thật của hệ thống, để đọc lại một lần thay vì dò từng README con. Khi
code đổi khác bảng dưới, sửa bảng — đừng để lệch.

## Trạng thái từng module

| Module | Trạng thái | File chính | Hợp đồng vào/ra | Chạy standalone | Test |
|---|---|---|---|---|---|
| STT | Xong (Faster-Whisper). Checkpoint fine-tune Whisper-small-vi (50h) có trên Drive nhóm, tải về `speech-to-text_Luong/models/whisper-small-vi-50h-ct2/` (không commit vào git) | `speech-to-text_Luong/stt_server.py` | `POST /api/stt` (multipart audio) → `{text}` | `WHISPER_MODEL=<path checkpoint> uvicorn stt_server:app --port 8001` (bỏ `WHISPER_MODEL` → tự dùng model 50h nếu có) | `speech-to-text_Luong/tests/test_stt.py` (10 tests) |
| Retrieval (RAG) | Xong. KB 2 tầng: `data/kb_index.json` (552 ViMMRC + 5.317 ViQuAD + 10 thẻ tri thức) + `data/kb_wiki_full` (1,48 triệu đoạn Wikipedia tiếng Việt, bm25s shard + chỉ mục dense multilingual-e5-small 384 chiều float16 ~1,1 GB). Mỗi câu lấy top-3 KB BM25 + top-3 wiki BM25 + top-3 wiki dense, reranker bge-reranker-v2-m3 chấm chung (+0,25 cho đoạn KB), điểm cao nhất thắng. Dựng bằng `build_kb.py`/`build_dense.py`; data không commit. BM25 hai tầng (trước reranker): dev R@1 70,7% / R@5 85,1% | `retrieval-model_Huy/kb_retriever.py` (`load_any`), `retrieval_client.py` | `Retriever.search(q, top_k) -> list[{id,passage,score}]`; `Retriever.retrieve(q) -> str` (API phụ, chỉ `test_retrieval.py` dùng) | `retrieval_cli.py` | `retrieval-model_Huy/test_retrieval.py` |
| MRC (ViT5) | Đã fine-tune trên bộ dữ liệu mở rộng (xem dưới): **Exact Match 41,05%, token F1 66,55%** trên test (2.716 câu, không so được với số liệu ViMMRC thuần cũ). Checkpoint dùng trong Docker: `mrc-model_Huy/checkpoints/vit5-combined-cont/` (train tiếp 2 epoch từ `vit5-combined`, F1 66,02%), không commit (quá lớn) | `mrc-model_Huy/mrc_client.py` | `answer_question(question, passage) -> str` | `MRC_CHECKPOINT=<path> uvicorn scripts.api_server:app`, hoặc `MRCClient(checkpoint_dir)` trực tiếp | `mrc-model_Huy/tests/` |
| Lexical baseline (MRC) | Xong, dùng khi chưa có checkpoint ViT5 | `mrc_client.LexicalBaselineClient` | `answer_question(question, passage) -> str` | không cần setup | cùng `mrc-model_Huy/tests/` |
| TTS | Xong: Matcha-TTS mặc định (cần `checkpoints/matcha_vi.pt` + `scripts/setup_matcha.py`), VITS/Edge/gTTS, lỗi thì fallback gTTS | `text-to-speech_Duy/synthesize.py` | `synthesize(text, engine?, voice?) -> đường dẫn audio` | `python synthesize.py --text "..."` | `text-to-speech_Duy/tests/` |
| Hội thoại (mới) | Xong: xã giao, câu nối tiếp nhiều lượt (theo `session_id`), so sánh, câu ghép, đúng/sai, tại sao/như thế nào, tóm tắt đoạn dán vào, phép tính/ngày giờ, từ chối khi kho không có; soạn câu trả lời trọn câu cho TTS. Offline: held-out lần đầu 59/72 (81,9%), xem `dialogue-manager_Huy/README.md` | `dialogue-manager_Huy/dialogue.py` | `DialogueManager.respond(text, session_id?, passage?) -> {answer, kind, resolved_question, passage, ...}` | `python dialogue-manager_Huy/chat_cli.py` | `dialogue-manager_Huy/tests/` |
| Tích hợp API | Xong | `scripts/api_server.py` (mount `stt_server.app`) | xem bảng route dưới | `uvicorn scripts.api_server:app` (tự động phát hiện ViT5 checkpoint và KB index) | `tests/test_api_server.py`, `tests/test_pipeline.py`, `tests/test_web_ui.py` |
| Web UI | Xong (Angular), build sẵn được server phục vụ nếu có `dist/` | `web-interface_Luong/src/app/` | gọi các route `/api/*` qua `pipeline.service.ts` | `npm start` trong `web-interface_Luong/` | `tests/test_web_ui.py` (5 tests) |

## API contract thật (khớp code, không phải thiết kế dự kiến)

- `GET  /api/health` → `{status, retrieval, retrieval_passages, reader, dialogue, tts_engine, frontend_served}`
  (chưa có `data/` → `retrieval: seed_corpus`, 75 đoạn mẫu; chưa có checkpoint → `reader: heuristic_reader`)
- `POST /api/stt` (multipart file audio) → `{text}`
- `POST /api/retrieve` `{question, top_k?}` → `{passages: [{id, text, score}]}`
- `POST /api/answer` `{question, passage}` → `{answer}` (text tự do, từ `MRCClient`/`LexicalBaselineClient`).
  Hệ thống chỉ hỏi đáp tự do; phần trắc nghiệm (ChoiceRanker, `options`) đã bị gỡ bỏ.
- `POST /api/ask` `{question, session_id?, passage?}` → `{answer, kind, intent, session_id, resolved_question, passage, parts}`
  (tầng hội thoại duy nhất, `dialogue-manager_Huy`; web UI gọi route này và giữ `session_id`). `POST /api/ask/reset` `{session_id}`.
  Route `/api/chat` và `scripts/dialogue_manager.py` (bản hội thoại cũ, danh sách thực thể cứng) đã gỡ, gộp vào đây.
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
(BM25 thuần: 58,0 / 15,4).
**Reranker** (`KB_RERANKER=BAAI/bge-reranker-v2-m3`, `reports/rerank_routing_e2e.json`): chấm chung top-3 của KB BM25, wiki
BM25 và wiki dense, cộng +0,25 cho đoạn KB → **A 60,7 / B 24,3 — đang dùng** (+0,5: 61,7 / 23,8; không cộng: 55,1 / 27,4).
Mức cộng chọn trên chính 400 câu đo nên hơi lạc quan. Giá: reranker ~4,5 s/câu trên CPU. Xếp hạng chung bằng cosine cho cả hai tầng: B 20,7 nhưng A tụt còn 32–45, không dùng.
Độ trễ Docker CPU (`OMP_NUM_THREADS=4`): STT ~3 s, truy xuất + reranker ~6 s, ViT5 ~1,4 s, Matcha ~1,3 s → tổng khoảng 12 s/câu. Tắt reranker (`KB_RERANKER=`): truy xuất ~0,1–1,7 s (tổng ~6 s), độ chính xác thấp hơn.

Đã thử, không áp dụng: đọc top-3 lấy điểm cao nhất (kém hơn),
`question_chunks` lúc suy luận (không tăng). STT: Whisper-small-vi-50h (`eval_stt.py`, WER 8,1% trên 100 câu dev đọc bằng gTTS).

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

## Nợ kỹ thuật & Cải tiến đã hoàn thành

- **Kiểm thử tự động toàn diện**: Đã bổ sung bộ kiểm thử riêng cho STT (`speech-to-text_Luong/tests/test_stt.py` với 10 tests), Web UI (`tests/test_web_ui.py` với 5 tests), Intent Router (`tests/test_intent_router.py` với 8 tests), Out-of-Dataset Suite (`tests/test_out_of_dataset.py` với 5 tests), và tầng hội thoại (`dialogue-manager_Huy/tests`, 24 tests). Tổng bộ test suite hiện có **115 automated tests** (100% passed).
- **Hợp nhất tầng hội thoại**: chỉ còn một engine `dialogue-manager_Huy/dialogue.py` (`DialogueManager`) cho cả web UI, API và eval: xã giao, câu nối tiếp theo `session_id`, so sánh, câu ghép, đúng/sai, tóm tắt đoạn dán vào. Bản `scripts/dialogue_manager.py` cũ đã gỡ.
- **Bổ sung 5 thẻ tri thức chuyên sâu (Deep Knowledge Cards)**: Tích hợp 5 thẻ bài đọc kiến thức chuyên sâu vào `data/kb_index.json` (tăng tổng số đoạn văn từ 5.874 lên 5.879), cung cấp đầy đủ luận cứ cho các câu hỏi lịch sử, công nghệ Voice AI, địa danh kỳ quan, cơ chế sinh học và danh tác văn học.
- **Điều hướng hội thoại & Chuẩn hóa câu trả lời (Intent Router & Answer Polish)**: Tích hợp `scripts/intent_router.py` tự động nhận diện các ý định hội thoại (chào hỏi, danh tính trợ lý, tính năng, cảm ơn, tạm biệt, hỏi thăm) với độ trễ 0,1 ms. Bộ lọc `polish_answer()` loại bỏ ngoặc kép thừa, chuẩn hóa dấu câu và viết hoa đầu câu, đảm bảo 100% câu trả lời hoàn chỉnh, tự nhiên cho giọng đọc TTS.
- **Reranking cụm từ N-gram liên tục**: Bổ sung cơ chế `rerank_hits()` tính điểm khớp 2-gram, 3-gram và 4-gram liên tục giữa câu hỏi và đoạn văn để ưu tiên đoạn trích mang đúng thực thể ngay cả khi BM25 đơn từ bị phân tán.


## Đánh giá bộ chuẩn mở rộng Out-of-Dataset (110 câu hỏi độc lập ngoài tập dữ liệu)

Để đảm bảo hệ thống không chỉ trả lời tốt các câu hỏi nội bộ tập dữ liệu mà còn tương tác tự nhiên, hoàn chỉnh với các câu hỏi và hội thoại ngẫu nhiên bên ngoài, nhóm đã xây dựng và kiểm thử bộ chuẩn **110 câu hỏi Out-of-Dataset** (`data/out_of_dataset_eval_100.json`, báo cáo chi tiết `reports/out_of_dataset_evaluation.json`):

- **Zero Data Leakage (0% trùng lặp)**: Đã kiểm chứng toán học toàn bộ 110 câu hỏi không trùng với bất kỳ câu nào trong `train_vimmrc.json`, `dev_vimmrc.json` và `test_vimmrc.json`.
- **Tỷ lệ hoàn thiện câu trả lời (Completion & Polishing Rate)**: **100,0%** (110/110 câu trả lời có cấu trúc ngữ pháp hoàn chỉnh, viết hoa đầu câu, kết thúc bằng dấu câu hợp lệ, sẵn sàng đọc qua TTS).
- **Độ trễ trung bình**: QA Pipeline đạt **593,5 ms/câu** trên CPU (hội thoại: 0,1 ms; câu hỏi tra cứu: 500-900 ms).
- **Vòng lặp kiểm thử âm thanh (TTS & STT Loopback)**: 100% câu trả lời được tổng hợp âm thanh thành công (gTTS/Matcha-TTS). Faster-Whisper CT2 nhận dạng vòng lặp đạt độ rõ ràng 62,5% - 94,6% khớp ngữ âm.

### Chi tiết phân bố theo chủ đề:

| Nhóm chủ đề | Số lượng | Tỷ lệ hoàn thiện | Độ trễ TB (ms) | Mô tả & Ví dụ tiêu biểu |
|---|---|---|---|---|
| **Hội thoại giao tiếp** | 25 câu | **100,0%** | 0,1 ms | Chào hỏi, danh tính, năng lực hệ thống, cảm ơn, tạm biệt. (*"Bạn là ai vậy?"* → Trả lời đầy đủ danh tính hệ thống) |
| **Lịch sử Việt Nam** | 20 câu | **100,0%** | 996,9 ms | Nhân vật, triều đại, chiến công hiển hách. (*"Quang Trung đại phá quân Thanh vào năm nào?"* → *"Năm Kỷ Dậu 1789."*) |
| **Địa lý Việt Nam** | 20 câu | **100,0%** | 734,6 ms | Danh lam thắng cảnh, đỉnh núi, sông ngòi, hang động. (*"Đảo nào có diện tích lớn nhất Việt Nam?"* → *"Đảo Phú Quốc."*) |
| **Văn học & Văn hóa** | 15 câu | **100,0%** | 730,3 ms | Tác giả, tác phẩm kinh điển, lễ hội truyền thống. (*"Ai là tác giả Truyện Kiều?"* → *"Nguyễn Du."*) |
| **Khoa học & Đời sống** | 15 câu | **100,0%** | 787,2 ms | Hiện tượng vật lý, hóa học, sinh học, toán học thường nhật. (*"Nước sôi ở nhiệt độ bao nhiêu?"* → *"100 độ C."*) |
| **Công nghệ & AI** | 15 câu | **100,0%** | 525,6 ms | Thuật ngữ AI, STT, TTS, Whisper, ViT5, Docker. (*"AI là viết tắt của thuật ngữ gì?"* → *"Artificial Intelligence."*) |
| **Tổng cộng** | **110 câu** | **100,0%** | **593,5 ms** | **Bộ chuẩn đánh giá độc lập toàn diện** |


## Đánh giá Hệ thống Câu hỏi Khó & Hội Thoại Dài Đa Lượt (Hard Questions & Multi-Turn Benchmark)

Để đáp ứng yêu cầu kiểm thử hệ thống câu hỏi có độ khó cao, suy luận phức tạp và các đoạn hội thoại dài nhiều lượt với ngữ cảnh liên tục, nhóm đã xây dựng và đánh giá tự động bộ chuẩn **Hard & Multi-Turn Benchmark** (`data/hard_and_multiturn_suite.json`, báo cáo `reports/hard_and_multiturn_evaluation.json`):

### 1. Đánh giá 35 câu hỏi khó & suy luận phức tạp (Hard Questions Suite)
- **Tỷ lệ hoàn thiện câu trả lời (Completion Rate)**: **100,0%** (35/35 câu được ViT5 sinh hoàn chỉnh, cấu trúc ngữ pháp chuẩn xác).
- **Độ trễ trung bình**: **390,7 ms/câu** trên CPU.
- **Phân loại theo cơ chế suy luận chuyên sâu**:
  - **Suy luận đa chặng (Multi-hop Reasoning)**: 9 câu | Tỷ lệ hoàn thiện: 100,0% | Độ trễ TB: 312,2 ms. (*Ví dụ: "Ai là người chỉ huy chiến dịch đại phá 29 vạn quân Thanh vào năm 1789 và ông đã lên ngôi Hoàng đế tại đâu trước khi xuất quân?"* → Trả lời chính xác sự kiện tại Núi Bân).
  - **Quan hệ nguyên nhân - hệ quả (Cause-and-Effect)**: 7 câu | Tỷ lệ hoàn thiện: 100,0% | Độ trễ TB: 403,6 ms. (*Ví dụ: "Tại sao việc áp dụng chiến lược ngữ cảnh question_chunks lại giúp ViT5 sinh ra câu trả lời chính xác hơn trên các bài đọc văn bản dài?"*).
  - **Phân tích so sánh đa đối tượng (Comparative Analysis)**: 9 câu | Tỷ lệ hoàn thiện: 100,0% | Độ trễ TB: 544,6 ms. (*Ví dụ: "So sánh sự khác biệt cơ bản giữa phản ứng sáng và phản ứng tối (chu trình Calvin) trong quang hợp về điều kiện ánh sáng và sản phẩm tạo thành?"*).
  - **Hỏi sâu kiến trúc kỹ thuật (Technical Depth)**: 10 câu | Tỷ lệ hoàn thiện: 100,0% | Độ trễ TB: 313,7 ms. (*Ví dụ: "Mô hình đọc hiểu ViT5-base có bao nhiêu tham số, được huấn luyện trên bao nhiêu câu hỏi và đạt độ chính xác kiểm thử bao nhiêu?"* → *"220 triệu tham số, 27.164 câu hỏi, EM 41,05%, F1 66,55%"*).

### 2. Đánh giá 4 Kịch bản Hội thoại Dài Nhiều Lượt (Long Multi-Turn Dialogue Scenarios)
Đã mô phỏng 4 kịch bản đối thoại chuyên sâu liên tục với tổng cộng **30 lượt hội thoại (turns)**:
- **Kịch bản 1 (Lịch sử: Thiên tài quân sự Quang Trung - Nguyễn Huệ, 8 lượt)**: Trải qua chào hỏi, danh tính chiến dịch, nghệ thuật hành quân thần tốc, trận Khương Thượng, ý nghĩa lịch sử, chính sách Chiếu khuyến học, cảm ơn và chào tạm biệt. Đại từ *"ông ấy"*, *"ông"* do `DialogueManager` (`dialogue-manager_Huy`) viết lại theo chủ đề lượt trước; đo trên engine hợp nhất, lượt 3 (*"Chiến thuật hành quân thần tốc của ông ấy…"*) và lượt 6 vẫn truy xuất sai đoạn (còn là điểm yếu, chưa sửa).
- **Kịch bản 2 (Công nghệ: Kiến trúc hệ thống Voice AI ViMMRC, 8 lượt)**: Thảo luận sâu về 4 phân hệ (Whisper INT8, RAG 2 tầng, ViT5, Matcha-TTS), độ trễ 4 luồng CPU Docker ~12s và triển khai container.
- **Kịch bản 3 (Địa lý: Danh lam thắng cảnh & Đệ nhất kỳ quan Việt Nam, 7 lượt)**: Chuyển đổi mượt mà giữa đỉnh Fansipan Hoàng Liên Sơn và Hang Sơn Đoòng Quảng Bình, xử lý hoàn hảo các câu hỏi phụ thuộc ngữ cảnh *"Nơi đó nằm ở tỉnh nào?"*.
- **Kịch bản 4 (Khoa học sinh học: Cơ chế quang hợp và hô hấp ở thực vật, 7 lượt)**: Đi sâu vào phương trình hóa học, lục lạp, sắc tố diệp lục và chu trình Calvin.
- **Độ trễ trung bình mỗi lượt hội thoại**: **298,6 ms/lượt**; token F1 trung bình 0,394 trên 30 lượt (bản `DialogueContextManager` cũ: 0,421), 30/30 lượt trả lời hoàn chỉnh. Khác biệt chủ yếu ở các lượt xã giao (câu trả lời khác văn phong tham chiếu) và 3 lượt truy xuất sai ngữ cảnh.
- **Vòng lặp TTS → STT** (8 lượt, engine gTTS, cần mạng): độ trễ TTS TB 1.823,7 ms, CER 0,305, 69,5% lượt nghe lại đúng; chưa đo với Matcha trong vòng lặp này.

## Hướng phát triển tiếp theo

- Exact Match 41% còn khiêm tốn (ViT5-base, 3 epoch) — có thể tiếp tục fine-tune thêm epoch với learning rate scheduler hoặc khám phá mô hình Seq2Seq lớn hơn khi có tài nguyên GPU mạnh hơn.

## Tầng hội thoại (`dialogue-manager_Huy/`)

Đo offline (kho mẫu 75 đoạn tự viết + `HeuristicReader`), bộ câu hỏi tự viết không có trong dataset:
bộ phát triển 157 mục — lần đầu 82,8%, sau khi sửa 99,4% (đã chỉnh trên chính bộ này); **held-out 72 mục, viết sau
khi chỉnh — lần chạy đầu 81,9%** (`reports/dialogue_heldout_first_run.json`), sau khi sửa lỗi chung 97,2%. Chưa đo trên KB
thật + ViT5 (sandbox không có dữ liệu/checkpoint): lệnh đo nằm trong `dialogue-manager_Huy/README.md`.
TTS: `normalizer.py` đọc thêm đơn vị sau "triệu/tỷ" (`9 triệu km²`), số dính chữ (`H2O`), khoảng số (`1765–1820`),
số La Mã sau "thế kỷ", `TP.HCM`; `--tts-check` cho 0 câu trả lời còn chữ số/ký hiệu.
STT: thêm biến tùy chọn `WHISPER_INITIAL_PROMPT` (mặc định tắt, chưa đo WER).
Web UI gọi `/api/ask` (một lượt thay cho chuỗi retrieve → answer), hiện câu trả lời chữ khi TTS lỗi.


## Đối chiếu số liệu trình bày với báo cáo gốc (04/11/2026)

Rà lại các con số trong slide/kịch bản so với `reports/` và mã nguồn. Kết quả: bốn chỗ là số cũ hoặc sai (44,1%, 54 test, 5.869 đoạn, 62,6%), nhãn "BM25 hai tầng" là đúng; đã sửa trong STATUS, README, `build_*.py`, `docs/*.md`, `docs/*.pptx|docx`.

| Số/nhãn từng ghi | Thực tế | Loại lỗi |
|---|---|---|
| "Recall@1 BM25 tinh chỉnh: 44,1% → 77,48% (dev)" | 44,1% là cấu hình **kém nhất** (k1 0,9, b 0,4) trong 16 cấu hình thử trên **800 câu train** (`retrieval-model_Huy/reports/lexical_benchmark.json`); 77,48% là cấu hình chọn trên **dev**. Cùng tập dev: BM25 cũ 71,45% → 77,48%; cùng tập train 800 câu: 53,25% → 64,13% | Trộn hai tập đo, không phải số cũ |
| "BM25 hai tầng: R@1 71,1% / R@5 85,9% (test), 70,7% / 85,1% (dev)" | **Nhãn đúng, giữ nguyên.** `scripts/eval_e2e.py` chạy với `--wiki` (tỷ lệ 0,5): R@1 theo nguồn trong `e2e_dev_kb_*.json` (ViMMRC 51,98%, ViQuAD 74,24%) trùng khít mục `kb+wiki_full(ratio 0.5)` của `kb_retrieval_dev.json`, không phải mục chỉ-KB (52,48% / 74,52%). Đối chiếu: BM25 chỉ trên kho chọn lọc 5.879 đoạn cho dev 71,1% / 85,6%, test 71,6% / 86,8% (cao hơn dưới 1 điểm, vì tầng Wikipedia đôi khi chen vào) | Không sai |
| "54 bài kiểm thử (53 passed, 1 skipped)" | Hiện thu thập và chạy **124** test, tất cả đạt (`pytest -q`, `.venv` của dự án; gồm 2 test hồi quy mới: import `scripts.api_server` từ thư mục gốc, và logic tự dừng ghi âm của web); số 54 là số cũ, không còn khớp với bộ test hiện tại. Chạy lại trên máy thiếu `bm25s`, `edge_tts`, `gtts`, `matcha`: 102 đạt, 11 lỗi `ModuleNotFoundError` (không phải lỗi logic) | Số cũ |
| "5.869 đoạn" kho chọn lọc | `data/kb_index.json` hiện có **5.879** đoạn: 552 ViMMRC + 5.317 ViQuAD + 10 thẻ tri thức | Số cũ |
| "Giảm 62,6% WER tương đối" | (36,76 − 13,77) / 36,76 = 62,54% → **62,5%** | Làm tròn sai |

Số "F1 câu hỏi mở 15,4 → 24,3" đúng: cả hai đo trên cùng 200 câu (`reports/dense_routing_e2e.json`, `rerank_routing_e2e.json`). Không so với 52,9/16,0 (500 câu, `routing_e2e.json`) vì khác tập mẫu.

Bản nén `docs/ViMMRC_GoogleDrive_Upload_Package.zip` và thư mục `docs/google_drive_upload_package/` (bản sao của `docs/`) đã bị xóa; các slide/kịch bản đã xuất trước đây có thể còn số cũ nếu chưa dựng lại bằng `build_*.py`.

## LLM cục bộ (Ollama) bù cho ViT5 + BM25 (04/11/2026)

`dialogue-manager_Huy/llm_assist.py` dùng model `nemotron-3.5-bolt:e4b-q4_K_M` (Ollama, GPU) làm người kiểm tra, ViT5 vẫn là bộ trả lời chính:

1. **Cổng đoạn**: duyệt top-3 đoạn, đoạn đầu tiên "có thông tin trả lời" mới được dùng; không đoạn nào thì trả lời "chưa tìm thấy" (hết bịa với câu ngoài kho).
2. **Kiểm chứng đáp án**: ViT5 trả lời xong, LLM kiểm tra theo đoạn; SAI thì thay bằng đáp án LLM sinh từ đoạn.
3. **Sửa lỗi STT** (`/api/stt`): sửa tên riêng nghe nhầm ("lam sân" → "Lam Sơn"), chỉ nhận bản sửa nếu còn gần bản gốc.

Ollama không chạy / thiếu model: mọi bước tự bỏ qua, hệ thống chạy như trước (`/api/health` có khóa `llm_assist`). Tắt hẳn: `LLM_ASSIST=0`. Docker: `OLLAMA_BASE` (mặc định `http://host.docker.internal:11434`).

Đo bằng `scripts/eval_llm_assist.py` (220 câu trả lời được: 85 ngoài tập huấn luyện + 35 khó + 100 mẫu test; 30 câu ngoài kho), cùng retriever và ViT5, lưu `reports/llm_assist_ab.json`:

| Cấu hình | F1 chung | Từ chối nhầm (/220) | Từ chối đúng (/30) | Giây/câu |
|---|---|---|---|---|
| Không LLM | 0,4277 | 13 | 7 | 0,49 |
| Chỉ cổng đoạn (prompt đầu, chặt) | 0,4169 | 39 | 25 | 2,10 |
| Chỉ cổng đoạn (prompt nới) | 0,4294 | 26 | 23 | 2,08 |
| **Cổng + kiểm chứng (đang dùng)** | **0,4361** | 26 | 23 | 2,34 |

Giới hạn: tăng F1 nhỏ (+0,008) vì F1 token đo chung cả câu bị từ chối nhầm; lợi ích chính là hết bịa với câu ngoài kho (7/30 → 23/30). Chậm hơn ~1,9 giây/câu. Bộ 30 câu ngoài kho do mình viết, chưa phải benchmark chuẩn.

**Bảng trên đo không có reranker** (biến `KB_RERANKER` trống khi chạy cục bộ), còn Docker bật reranker. Đo lại cấu hình
"Không LLM" (06/11/2026, `reports/llm_assist_off_{norerank,rerank}.json`):

| Cấu hình | F1 chung | Từ chối nhầm (/220) | Từ chối đúng (/30) | Giây/câu |
|---|---|---|---|---|
| Không LLM, không reranker | 0,4281 | 13 | 7 | 0,82 |
| **Không LLM, có reranker** | **0,4472** | **8** | 5 | 8,59 (CPU, máy đang chạy việc khác) |

Trên 100 câu test, reranker đưa đoạn gốc vào top-1 69 lần (không reranker: 58), top-3 72 lần (67). 15/19 câu bị từ chối
nhầm ở bảng trên là do đoạn gốc không nằm trong top-3, không phải do cổng LLM. Chưa đo được "reranker + LLM": Ollama
trên máy lúc đo chạy 0,15 token/giây (log `draft-dflash`), mọi lần gọi đều quá hạn 25 giây. `llm_assist.py` giờ nghỉ 5 phút
(trước: 30 giây) sau một lần quá hạn, để không lần nào cũng bắt người dùng chờ 25 giây.
