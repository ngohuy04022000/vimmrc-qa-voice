# BỘ PROMPT TẠO SLIDE THUYẾT TRÌNH TOÀN DIỆN (KHÔNG GIỚI HẠN SỐ SLIDE – ĐẦY ĐỦ NHẤT CÓ THỂ) TRÊN CLAUDE CHAT

**Đề tài:** Hệ thống Hỏi – Đáp Đọc hiểu Văn bản bằng Giọng nói Tiếng Việt (ViMMRC Voice Q&A)  
**Môn học:** Học máy tiên tiến và ứng dụng  
**Nguồn dữ liệu chuẩn:**  
1. [`Bao_cao_Speech_to_Text_ViMMRC.docx.pdf`](docs/Bao_cao_Speech_to_Text_ViMMRC.docx.pdf) — Báo cáo thực nghiệm Speech-to-Text (Huỳnh Công Lương, 19 trang).  
2. [`Huy_TT15-20p_Bao_Cao_Retrieval_MRC.docx.pdf`](docs/Huy_TT15-20p_Bao_Cao_Retrieval_MRC.docx.pdf) — Báo cáo Retrieval, MRC & Tầng hội thoại (Ngô Trí Huy, 17 trang).  
3. [`Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx.pdf`](docs/Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx.pdf) — Báo cáo Text-to-Speech Matcha-TTS & HiFi-GAN (Trương Hoàng Duy, 25 trang).  
4. **Mã nguồn thực tế toàn dự án:** `speech-to-text_Luong/`, `retrieval-model_Huy/`, `mrc-model_Huy/`, `dialogue-manager_Huy/`, `text-to-speech_Duy/`, `web-interface_Luong/`, `scripts/api_server.py`, `Dockerfile`, `docker-compose.yml`, `STATUS.md` và `reports/`.

---

## HƯỚNG DẪN TẢI FILE LẦN LƯỢT TRÊN CLAUDE CHAT (4 LƯỢT – TỔNG CỘNG ~37+ SLIDES CHI TIẾT)

Vì Claude Chat giới hạn số file tải lên mỗi tin nhắn và có giới hạn độ dài phản hồi (output tokens) cho mỗi lượt trả lời, để **không bị giới hạn số lượng slide** và **không bị cắt cụt nội dung**, chúng ta chia thành **4 Lượt (trong cùng 1 cửa sổ chat Claude)**:

| Lượt chat | File cần tải lên Claude Chat ở lượt đó | Phạm vi Slide & Nội dung thực hiện |
| :--- | :--- | :--- |
| **Lượt 1** | Đính kèm **1 file:** [`docs/Bao_cao_Speech_to_Text_ViMMRC.docx.pdf`](docs/Bao_cao_Speech_to_Text_ViMMRC.docx.pdf) | Khởi tạo Hệ màu hài hòa (Design System), tạo **Slide 1 → Slide 11** (Tổng quan Hệ thống 6 chặng + Toàn bộ 15 mục báo cáo STT của Huỳnh Công Lương & thực nghiệm ảnh hưởng STT lên Retrieval). |
| **Lượt 2** | Đính kèm **1 file:** [`docs/Huy_TT15-20p_Bao_Cao_Retrieval_MRC.docx.pdf`](docs/Huy_TT15-20p_Bao_Cao_Retrieval_MRC.docx.pdf) | Tạo **Slide 12 → Slide 21** (Toàn bộ 8 chương báo cáo của Ngô Trí Huy: Tối ưu BM25 postings, Kho 2 tầng 5.879 đoạn KB + 1,48M đoạn Wiki mmap float16, Cross-Encoder Reranker `KB +0,25`, Hợp nhất 27.164 câu hỏi, Huấn luyện ViT5 3 giai đoạn, Thử nghiệm âm với LLM 9B, Tầng hội thoại `DialogueManager` & Phân tích độ trễ). |
| **Lượt 3** | Đính kèm **1 file:** [`docs/Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx.pdf`](docs/Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx.pdf) | Tạo **Slide 22 → Slide 31** (Toàn bộ 8 chương báo cáo của Trương Hoàng Duy + mã nguồn `text-to-speech_Duy/src/`: Luồng số hóa 6 bước, Text Normalizer tiếng Việt, Toán học OT-CFM vs Diffusion, Bóc tách thanh điệu Unicode NFD 41 token, MAS Numba JIT, Huấn luyện 2 giai đoạn 150k + HiFi-GAN 50k bước, Hậu xử lý khoảng lặng/fade/denoiser, Đánh giá MCD/pYIN F0/log-F0/PhoWhisper CER/RTF). |
| **Lượt 4** | *Không cần tải thêm PDF* *(Có thể đính kèm thêm ảnh chụp Web UI từ `docs/screenshots/` nếu muốn)* | Tạo **Slide 32 → Slide 37+** (Kiến trúc tích hợp FastAPI `api_server.py`, Giao diện Web Angular 19/22 Signals, Docker Multi-Stage & tối ưu `OMP_NUM_THREADS=4`, 113 Automated Tests, Bộ chuẩn 110 câu Out-of-Dataset & 35 câu Hard Multi-Turn, Kịch bản Demo E2E, Tổng kết toàn diện) & **Xuất bản toàn bộ bộ Slide hoàn chỉnh**. |

---

## LƯỢT 1: KHỞI TẠO HỆ THỐNG THIẾT KẾ + TỔNG QUAN DỰ ÁN + TOÀN BỘ PHÂN HỆ 1 (STT)
*(Đính kèm file: `Bao_cao_Speech_to_Text_ViMMRC.docx.pdf` và copy toàn bộ khung dưới đây dán vào Claude Chat)*

```markdown
Bạn là một Chuyên gia Thiết kế Slide Học thuật & Kỹ nghệ Hệ thống AI (Principal AI Presentation Designer & ML Systems Architect).
Tôi cần bạn thiết kế một **Bộ Slide Thuyết trình Báo cáo Đồ án Môn học "Học máy tiên tiến và ứng dụng"** cho đề tài:
**"HỆ THỐNG HỎI – ĐÁP ĐỌC HIỂU VĂN BẢN BẰNG GIỌNG NÓI TIẾNG VIỆT (ViMMRC VOICE Q&A)"**.

### I. NGUYÊN TẮC CỐT LÕI: KHÔNG GIỚI HẠN SỐ LƯỢNG SLIDE – ĐẦY ĐỦ VÀ CHI TIẾT NHẤT CÓ THỂ
1. **Không giới hạn số lượng slide:** Tuyệt đối KHÔNG gộp ép nhiều nội dung nặng vào 1 slide. Mỗi chương/mục quan trọng, mỗi cơ sở toán học, mỗi bảng số liệu thực nghiệm, mỗi biểu đồ đường cong huấn luyện và mỗi sơ đồ kiến trúc phải được trình bày trên một Slide riêng biệt, thoáng đãng, sắc nét (tổng bộ slide dự kiến **37+ slides**, hoặc nhiều hơn tùy theo mức độ chi tiết).
2. **Làm việc theo 4 Lượt (4 Phases) để vượt giới hạn tải file & giới hạn token đầu ra của Claude:**
   - **Lượt 1 (Hiện tại):** Tôi tải lên báo cáo **Phân hệ 1 – Speech-to-Text (`Bao_cao_Speech_to_Text_ViMMRC.docx.pdf`)** cùng kiến trúc tổng thể hệ thống. Bạn hãy đọc kỹ tài liệu, xác nhận toàn bộ số liệu và **thiết kế chi tiết từ Slide 1 đến Slide 11** (hoặc nhiều hơn nếu cần tách bảng/biểu đồ). Sau đó **DỪNG LẠI** chờ tôi xác nhận.
   - **Lượt 2:** Tôi sẽ tải lên báo cáo **Phân hệ 2 & 3 – Retrieval, MRC & Tầng hội thoại (`Huy_TT15-20p_Bao_Cao_Retrieval_MRC.docx.pdf`)** để thiết kế tiếp **Slide 12 đến Slide 21**.
   - **Lượt 3:** Tôi sẽ tải lên báo cáo **Phân hệ 4 – Text-to-Speech Matcha-TTS & HiFi-GAN (`Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx.pdf`)** để thiết kế tiếp **Slide 22 đến Slide 31**.
   - **Lượt 4:** Thiết kế **Slide 32 đến Slide 37+** (Tích hợp Backend FastAPI, Giao diện Web Angular, Docker Multi-Stage, 113 bài kiểm thử tự động, Đánh giá mở rộng 110 câu Out-of-Dataset & 35 câu Hard Multi-Turn, Kịch bản Demo & Tổng kết) và xuất bản thành phẩm hoàn chỉnh.

---

### II. HỆ THỐNG MÀU SẮC HÀI HÒA & QUY CHUẨN TRỰC QUAN (DESIGN SYSTEM 16:9)
1. **Bảng màu Học thuật Hiện đại (Harmonious Academic-Tech Palette):**
   - **Slide Bìa & Slide Chuyển Phần (Section Divider):** Nền tối sang trọng **Deep Slate Navy (`#0F172A`)** kết hợp dải chuyển sắc tinh tế (`#1E3A8A` → `#0D9488`), chữ trắng (`#FFFFFF`), phụ đề **Cool Slate (`#94A3B8`)**.
   - **Slide Nội dung (Content Slides):** Nền sáng dịu mắt **Soft Pearl White (`#F8FAFC`)**, các khối nội dung đặt trong thẻ **Card trắng (`#FFFFFF`)** bo góc `12px`, viền mảnh (`#E2E8F0`), đổ bóng mềm. Chữ tiêu đề/nội dung chính màu **Charcoal Slate (`#1E293B`)**, chữ ghi chú/nguồn màu **Muted Slate (`#64748B`)**.
   - **Mã màu định danh từng phân hệ (Color-Coding nhất quán xuyên suốt toàn bộ các slide):**
     - **Phân hệ 1 – STT (Huỳnh Công Lương):** **Tech Blue (`#2563EB`, nền thẻ nhạt `#EFF6FF`, viền `#BFDBFE`)**
     - **Phân hệ 2 – Retrieval 2 tầng (Ngô Trí Huy):** **Teal Emerald (`#0D9488`, nền thẻ nhạt `#F0FDFA`, viền `#99F6E4`)**
     - **Phân hệ 3 – MRC ViT5 & Tầng Hội thoại (Ngô Trí Huy):** **Royal Indigo (`#4F46E5`, nền thẻ nhạt `#EEF2FF`, viền `#C7D2FE`)**
     - **Phân hệ 4 – TTS Matcha-TTS & HiFi-GAN (Trương Hoàng Duy):** **Crimson Rose (`#E11D48`, nền thẻ nhạt `#FFF1F2`, viền `#FECDD3`)**
     - **Tích hợp Full-Stack / Kết quả Tốt nhất / Cảnh báo Kỹ thuật:** **Forest Green (`#15803D`, nền `#DCFCE7`)** & **Amber Gold (`#D97706`, nền `#FEF3C7`)**.
2. **Yêu cầu Trực quan trên MỖI Slide (Bắt buộc):**
   - Mỗi slide phải có **Header chuẩn** (Badge phân hệ + Số thứ tự Slide + Tiêu đề rõ ràng + Người trình bày) và **Footer chuẩn** (Tên đề tài ViMMRC Voice Q&A + Nguồn minh chứng từ mã nguồn/báo cáo).
   - Mỗi slide bắt buộc phải có **ít nhất 1–2 thành phần trực quan**: Sơ đồ kiến trúc/luồng dữ liệu vẽ bằng **SVG/HTML sắc nét**, **Bảng số liệu định dạng đẹp** (có tô màu nổi bật dòng kết quả tốt nhất), **Biểu đồ cột/đường (SVG Bar/Line Chart)** dựng chính xác từ số liệu thật trong báo cáo, **Hộp công thức toán học (LaTeX)**, hoặc **Khối mã nguồn/cấu hình kỹ thuật**.
   - Kèm theo **Speaker Notes (Lời thuyết trình chi tiết)** ở cuối mỗi slide để người báo cáo trình bày sâu sắc, mạch lạc.

---

### III. NỘI DUNG CHI TIẾT CẦN THIẾT KẾ TRONG LƯỢT 1 (SLIDE 1 → SLIDE 11)
Hãy kết hợp tài liệu `Bao_cao_Speech_to_Text_ViMMRC.docx.pdf` đính kèm với thông tin kiến trúc tổng thể dưới đây để thiết kế đầy đủ **Slide 1 đến Slide 11**:

#### 1. CỤM SLIDE TỔNG QUAN HỆ THỐNG (SLIDE 1 – 3)
- **Slide 1 (Bìa Báo cáo):**
  - Tên đề tài: **HỆ THỐNG HỎI – ĐÁP ĐỌC HIỂU VĂN BẢN BẰNG GIỌNG NÓI TIẾNG VIỆT (Vietnamese Multiple-choice Machine Reading Comprehension Voice Q&A – ViMMRC Voice Q&A)**.
  - Học phần: **Học máy tiên tiến và ứng dụng**.
  - 3 Thẻ phân công thành viên chi tiết:
    1. **Huỳnh Công Lương:** Phân hệ Nhận dạng Tiếng nói (STT – Tinh chỉnh `openai/whisper-small` bằng LoRA trên VietSpeech 20h & 50h, lượng tử hóa CTranslate2 INT8, API `stt_server.py`) & Giao diện Web Angular (`web-interface_Luong/`) + Đóng gói Docker.
    2. **Ngô Trí Huy:** Phân hệ Truy xuất Ngữ cảnh 2 tầng (`retrieval-model_Huy/`: BM25 tự cài đặt + Wikipedia 1,48 triệu đoạn `bm25s` & vector `multilingual-e5-small` + Reranker `bge-reranker-v2-m3`), Mô hình Đọc hiểu Máy (`mrc-model_Huy/`: tinh chỉnh `VietAI/vit5-base` trên 27.164 câu gộp ViMMRC 2.0 + UIT-ViQuAD2.0), Tầng Hội thoại (`dialogue-manager_Huy/`) & Tích hợp Backend (`scripts/api_server.py`).
    3. **Trương Hoàng Duy:** Phân hệ Tổng hợp Tiếng nói (`text-to-speech_Duy/`: huấn luyện `Matcha-TTS` OT-CFM 150k bước & tinh chỉnh `HiFi-GAN` Vocoder 50k bước trên InfoRe1 25h, thiết kế từ điển tách thanh điệu độc lập 41 token `vi_tokenizer.py`, tối ưu MAS bằng Numba JIT, chuẩn hóa văn bản `normalizer.py`, hậu xử lý ngữ điệu & điều phối 4 engine).
- **Slide 2 (Bối cảnh, Thách thức & Mục tiêu Thiết kế Toàn Hệ thống):**
  - Hạn chế của các hệ thống đọc hiểu văn bản truyền thống (chỉ nhập/xuất chữ) trong ngữ cảnh rảnh tay, hỗ trợ người khiếm thị, giáo dục tương tác.
  - 4 Thách thức kỹ thuật cốt lõi của Voice Q&A tiếng Việt: (1) Sai sót nhận dạng tên riêng/con số ở STT làm lệch truy xuất đoạn văn; (2) Kho tri thức vừa có bài đọc sách giáo khoa (ViMMRC) vừa cần mở rộng ra triệu đoạn Wikipedia trên RAM máy cá nhân; (3) Hệ thống 6 thanh điệu tiếng Việt đòi hỏi TTS đọc chuẩn dấu thanh và xử lý ký hiệu đáp án/ngày tháng/đơn vị đo; (4) Yêu cầu chạy hoàn toàn trên **CPU phổ thông**, hoạt động **Offline 100%** bảo mật dữ liệu và có cơ chế **Fallback đa tầng**.
- **Slide 3 (Kiến trúc Chuỗi Xử lý Tổng thể 6 Bước – End-to-End Pipeline):**
  - *Vẽ Sơ đồ kiến trúc tổng thể 6 khối lớn (kèm định dạng dữ liệu truyền qua mỗi bước):*
    - **Bước 1 – Đầu vào Giọng nói:** Người dùng đặt câu hỏi qua Micro trên Web UI (Web Audio API thu âm PCM 16kHz mono / Blob `question.wav`).
    - **Bước 2 – Nhận dạng Tiếng nói (STT):** `POST /api/stt` → Mô hình `Whisper-small` đã fine-tune LoRA 50h (CTranslate2 INT8, `beam_size=5`, `vad_filter=True`) → Chuỗi văn bản câu hỏi tiếng Việt.
    - **Bước 3 – Tầng Hội thoại & Truy xuất Ngữ cảnh 2 Tầng:** `POST /api/ask` → `DialogueManager` làm sạch từ đệm, giải quyết câu nối tiếp theo `session_id`, định tuyến ý định → `TieredRetriever` lấy top-3 từ Kho chọn lọc (5.879 đoạn, BM25 tự cài đặt có bigram) + top-3 từ Wikipedia (1,48 triệu đoạn, `bm25s`) + top-3 từ Wikipedia Dense (`multilingual-e5-small` 384 chiều) → Bộ xếp hạng lại Cross-Encoder `bge-reranker-v2-m3` chấm chung (cộng thưởng `+0,25` cho đoạn thuộc KB khi điểm thô $> -2,0$).
    - **Bước 4 – Đọc hiểu Máy dạng Sinh (Generative MRC):** Mô hình `VietAI/vit5-base` (đã tinh chỉnh 2 giai đoạn trên 27.164 câu hỏi) nhận cặp `(câu hỏi, đoạn văn)` sinh đáp án ngắn → `answer_composer` biên tập thành câu trả lời hoàn chỉnh (hoặc từ chối khi độ phủ từ khóa `support < 0,34`).
    - **Bước 5 – Tổng hợp Tiếng nói (TTS):** `POST /api/tts` → `normalize_vietnamese_text` chuẩn hóa số/ngày tháng/nhãn đáp án → Tách âm vị & thanh điệu độc lập 41 token → `Matcha-TTS` giải ODE Euler (10–20 bước) sinh phổ Mel 80 kênh → `HiFi-GAN` tinh chỉnh tái tạo sóng âm 22,05 kHz + Denoiser + Cắt lặng -30dB & Fade 10ms.
    - **Bước 6 – Đầu ra Giao diện Web Angular:** Trình duyệt nhận sóng âm chuẩn 22,05 kHz WAV, tự động phát lại đồng thời hiển thị câu trả lời, đoạn văn bằng chứng và trạng thái từng chặng.

---

#### 2. CỤM SLIDE CHUYÊN SÂU PHÂN HỆ 1: SPEECH-TO-TEXT (SLIDE 4 – 11)
*(Trích xuất đầy đủ từ `Bao_cao_Speech_to_Text_ViMMRC.docx.pdf` và mã nguồn `speech-to-text_Luong/`)*

- **Slide 4 [STT – Bài toán, Vị trí & Cơ sở Lý thuyết Whisper-Small + LoRA (Mục 1 & 2)]:**
  - **Phát biểu bài toán & Vị trí (Hình 1):** Nhận tín hiệu âm thanh câu hỏi tiếng Việt $\rightarrow$ xuất văn bản cho Retrieval & MRC. Nhấn mạnh: mô hình không dự đoán đáp án trực tiếp, nhưng sai sót ở **tên riêng, con số, từ khóa nghi vấn** sẽ làm đổi nghĩa câu hỏi ở các khâu sau.
  - **Kiến trúc `openai/whisper-small` (~244 triệu tham số):** Transformer Encoder–Decoder; âm thanh đưa về **16 kHz mono**, `WhisperProcessor` trích đặc trưng **log-Mel spectrogram**, cấu hình `language="vi"`, `task="transcribe"` (nhận dạng cùng ngôn ngữ, không phải dịch).
  - **Cơ sở toán học LoRA (Low-Rank Adaptation):**
    $$W = W_0 + \frac{\alpha}{r} B A, \quad W_0 \in \mathbb{R}^{d \times k}, \; B \in \mathbb{R}^{d \times r}, \; A \in \mathbb{R}^{r \times k}, \; r \ll \min(d, k)$$
    - Giữ cố định trọng số nền $W_0$, chỉ học ma trận hạng thấp $A, B$ gắn vào `q_proj` và `v_proj` của cơ chế Attention với `r = 16`, `alpha = 32`, `dropout = 0,05`.
    - *Bảng tóm tắt lựa chọn kỹ thuật (Trang 3):* Giảm số tham số cần cập nhật xuống **1.769.472 tham số trainable (~0,73% tổng tham số)**; lưu ý kỹ thuật chuẩn xác: LoRA giảm tham số cập nhật và trạng thái optimizer nhưng không loại bỏ chi phí bộ nhớ lưu activations.

- **Slide 5 [STT – Nguồn Dữ liệu VietSpeech, Streaming & Thuật toán Tách Tập (Mục 3)]:**
  - **Nguồn dữ liệu VietSpeech (MMLab-UIT):** Hơn **1.100 giờ** tiếng nói tiếng Việt, **1.026.047 mẫu**, 16 kHz, quy mô ~131 GB từ nhiều vùng giọng và nguồn xã hội.
  - **Kỹ thuật Streaming & Lọc mẫu (`prepare_vietspeech.py`):**
    - Không tải trọn bộ 131 GB mà dùng `load_dataset(..., streaming=True)` với `shuffle_buffer = 10.000`, `seed = 42`, giải mã raw audio bằng `soundfile` và xuất ra định dạng nén không mất dữ liệu **FLAC** (`{sample_id}.flac`).
    - Tiêu chí lọc: Loại transcript rỗng, chuẩn hóa khoảng trắng, chỉ giữ audio có thời lượng **0,5 – 30 giây**, bỏ mẫu lỗi giải mã.
  - **Thuật toán tách tập theo nhóm Transcript (`split_for`):**
    - Vì schema thực tế không có trường `speaker_id` đầy đủ, script chuẩn hóa transcript về chữ thường, băm **SHA-1** (`int(sha1(group_key).hexdigest()[:8], 16) % 100`) để ánh xạ cố định vào 3 bucket: `train (<80)`, `validation (80..89)`, `test (90..99)` và cấp quota theo thời lượng.
    - *Bảng thống kê Bộ thí nghiệm 20 giờ (Trang 4):*
      - **Train:** `14.393 mẫu` | `16,0004 giờ`
      - **Validation:** `1.797 mẫu` | `2,0004 giờ`
      - **Test:** `1.802 mẫu` | `2,0002 giờ`
      - **Tổng cộng:** `17.992 mẫu` | `20,0010 giờ`.

- **Slide 6 [STT – Mở rộng lên Thí nghiệm 50 Giờ & Hậu kiểm Chống Rò rỉ (Mục 4)]:**
  - **Nguyên tắc mở rộng công bằng (`expand_vietspeech.py`):**
    - **Giữ cố định tuyệt đối tập Validation (1.797 mẫu) và Test (1.802 mẫu)** từ bộ 20 giờ để phép đo đối sánh có cùng thước đo chuẩn.
    - Sử dụng cơ chế **hard-link** (`os.link`) cho các file FLAC kế thừa để tiết kiệm dung lượng ổ đĩa, chỉ stream bổ sung mẫu mới vào tập Train.
    - Điều kiện nhận mẫu Train mới: Không thuộc `fixed_groups` (nhóm transcript của validation/test), có mã băm SHA-1 rơi đúng vào bucket `train (<80)` và chưa trùng `sample_id` (`sha1(f"{index}:{text}")[:20]`).
  - *Bảng đối sánh quy mô dữ liệu 20 giờ vs 50 giờ (Trang 5):*
    - **Train:** `14.393 mẫu / 16,0004 giờ` $\rightarrow$ **`41.212 mẫu / 46,0005 giờ`** (Tăng thêm **+26.819 mẫu**, tương đương **+30 giờ**; tỷ lệ thời lượng thành ~92% / 4% / 4%).
    - **Validation:** `1.797 mẫu / 2,0004 giờ` $\rightarrow$ **`1.797 mẫu / 2,0004 giờ (Giữ nguyên 100%)`**.
    - **Test:** `1.802 mẫu / 2,0002 giờ` $\rightarrow$ **`1.802 mẫu / 2,0002 giờ (Giữ nguyên 100%)`**.
    - **Tổng:** `17.992 mẫu / 20,0010 giờ` $\rightarrow$ **`44.811 mẫu / 50,0011 giờ`**.
  - **4 bước hậu kiểm nghiêm ngặt trước huấn luyện (`validate_expansion.py`):** Đối chiếu từng bản ghi validation/test; kiểm tra giao tập group `train ∩ val = 0`, `train ∩ test = 0`, `val ∩ test = 0`; xác minh toàn bộ 44.811 file FLAC đọc được; tách riêng thư mục output để bảo toàn model 20h làm phương án dự phòng.

- **Slide 7 [STT – Môi trường Phần cứng, Cấu hình & Quy trình Tinh chỉnh (Mục 5 & 6)]:**
  - *Bảng 3 – Phiên bản môi trường thực nghiệm đã kiểm tra (Trang 6):*
    - **GPU:** NVIDIA GeForce RTX 5060 Ti, 16 GB VRAM | **OS:** Ubuntu 24.04 trên WSL2
    - **Python / PyTorch:** `3.11.17` / `2.14.1+cu130` (CUDA 13.0)
    - **Thư viện:** `Transformers 4.57.6` | `PEFT 0.21.2` | `Datasets 3.6.0` | `JiWER 4.0.0` | `CTranslate2 4.8.2`.
  - *Bảng cấu hình tham số huấn luyện (`train_lora.py`, Trang 6):*
    - `base_model`: `openai/whisper-small` (run 50h train mới từ đầu trên base model, không train nối tiếp từ adapter 20h).
    - `batch_size = 4`, `gradient_accumulation_steps = 8` $\rightarrow$ **Effective Batch Size = 32** trên 1 GPU.
    - `learning_rate = 1e-4`, `warmup_ratio = 0,05`, `bf16 = True` (do `Seq2SeqTrainer` quản lý autocast), tối đa `3 epochs`.
    - `eval_steps = 250`, `save_steps = 250`, `save_total_limit = 3`, `load_best_model_at_end = True` theo `metric_for_best_model = "wer"`.
  - *Sơ đồ quy trình tinh chỉnh & xử lý nhãn (`WhisperDataCollator`, Trang 7):*
    - Trích đặc trưng trước khi nạp model với `num_proc = 1` và `writer_batch_size = 100` (tránh lỗi multiprocessing/fork sau khi khởi tạo CUDA và giảm áp lực ghi cache Arrow).
    - Padding vị trí nhãn bằng **`-100`** để hàm mất mát Cross-Entropy bỏ qua phần đệm; cắt bỏ `bos_token_id` đầu chuỗi nhãn khi đã đồng nhất.

- **Slide 8 [STT – Phương pháp Đánh giá & Kết quả trên Tập Test Cố định 1.802 Mẫu (Mục 7 & 8)]:**
  - **Chỉ số đo lường (`evaluate_models.py` dùng JiWER):**
    $$\text{WER (\%)} = 100 \times \frac{S + D + I}{N}, \qquad \text{CER (\%)} = 100 \times \frac{S_{\text{char}} + D_{\text{char}} + I_{\text{char}}}{N_{\text{char}}}$$
    - Lưu ý học thuật quan trọng: Chấm trực tiếp trên chuỗi dự đoán/tham chiếu (không hạ chữ thường hay xóa dấu câu sau khi đọc), và trong tiếng Việt mỗi đơn vị phân tách bằng khoảng trắng là **âm tiết (syllable)** chứ không phải từ ghép.
  - *Bảng Kết quả trên 1.802 mẫu Test cố định & Biểu đồ cột đôi Hình 2 (Trang 9):*
    - `openai/whisper-small` (Baseline gốc): **WER = 36,76% | CER = 19,43%**
    - `Whisper Small + LoRA, bộ 20 giờ` (1.350 steps, best step 1.250): **WER = 15,20% | CER = 7,29%**
    - **`Whisper Small + LoRA, bộ 50 giờ` (2.750 steps, best step 2.750): WER = 13,77% | CER = 6,67%** *(Tô nổi bật)*
    - `NhutP/ViWhisper-small (*)` (Mốc tham khảo): WER = 0,82% | CER = 0,54% *(Ghi chú rõ: có nguy cơ đã học trùng dữ liệu test thuộc VietSpeech, không phải đối chứng độc lập sạch)*.
  - *Bảng 8.1 – Phân tích mức độ cải thiện (Trang 9):*
    - **Gốc $\rightarrow$ LoRA 20 giờ:** Giảm **21,56 điểm WER** (**-58,64% tương đối**) | Giảm **12,14 điểm CER** (**-62,46% tương đối**).
    - **Gốc $\rightarrow$ LoRA 50 giờ:** Giảm **23,00 điểm WER** (**-62,56% tương đối**) | Giảm **12,76 điểm CER** (**-65,65% tương đối**).
    - **LoRA 20 giờ $\rightarrow$ LoRA 50 giờ:** Giảm thêm **1,44 điểm WER** (**-9,47% tương đối**) | Giảm thêm **0,62 điểm CER** (**-8,50% tương đối**).

- **Slide 9 [STT – Diễn biến Đường cong Validation & Giải phẫu Cơ chế Early Stopping (Mục 9 & 10)]:**
  - *Biểu đồ đường đôi Hình 3 (Validation WER % và Validation CER % từ `trainer_state.json`) & Bảng số liệu toàn trình qua 10 mốc step (Trang 10):*
    - Step `250`: 20h (`22,09%` / `11,93%`) vs 50h (`18,56%` / `8,99%`)
    - Step `500`: 20h (`17,48%` / `8,60%`) vs 50h (`17,38%` / `8,43%`)
    - Step `750`: 20h (`17,18%` / `8,44%`) vs 50h (`16,65%` / `8,06%`)
    - Step `1000`: 20h (`16,71%` / `8,09%`) vs 50h (`16,47%` / `8,02%`)
    - Step `1250`: **20h đạt Best (`16,63%` / `8,14%`)** vs 50h (`16,08%` / `7,77%`)
    - Step `1500 → 2000 → 2250 → 2500 → 2750` (Run 50h): `15,66%` $\rightarrow$ `15,11%` $\rightarrow$ `15,09%` $\rightarrow$ `15,21%` $\rightarrow$ **Best `14,93%` (CER `7,27%`) tại step 2.750**.
  - *Bảng phân tích cơ chế Early Stopping tại Step 2.750 (Trang 11 – Giải thích vì sao step 2.750 vừa là best checkpoint vừa là điểm dừng ở epoch 2,1351):*
    - Cấu hình `EarlyStoppingCallback(patience=3, threshold=0.2)` (ngưỡng 0,2 điểm phần trăm tuyệt đối):
      - **Step 2.000:** Val WER = `15,1085%` (Cải thiện `0,4744` điểm $\ge 0,2$ $\rightarrow$ Bộ đếm = `0`)
      - **Step 2.250:** Val WER = `15,0929%` (Giảm `0,0156` điểm $< 0,2$ $\rightarrow$ Bộ đếm = `1`)
      - **Step 2.500:** Val WER = `15,2057%` (Tăng so với best $\rightarrow$ Bộ đếm = `2`)
      - **Step 2.750:** Val WER = `14,9296%` (Tạo cực tiểu mới nên `Trainer` cập nhật làm `best_model`, nhưng mức giảm `0,1633` điểm vẫn $< 0,2$ nên bộ đếm đạt `3` $\rightarrow$ Kích hoạt dừng sớm!).

- **Slide 10 [STT – Merge, Lượng tử hóa CTranslate2 INT8 & Tích hợp API FastAPI (Mục 11 & 12)]:**
  - *Sơ đồ chuỗi chuyển đổi mô hình triển khai (`merge_lora.py` & `convert_ct2.py`, Trang 12):*
    `best_adapter (LoRA) + openai/whisper-small` $\xrightarrow{\text{merge\_and\_unload()}}$ `Checkpoint Transformers hoàn chỉnh (Safe Serialization)` $\xrightarrow{\text{CTranslate2 Converter (INT8)}}$ `models/whisper-small-vi-50h-ct2 (~241,48 MiB / 253 MB)` $\xrightarrow{\text{faster-whisper}}$ `FastAPI Server (stt_server.py)`.
  - *Bảng cấu hình suy luận Production (Trang 12):* Thư viện `faster-whisper / CTranslate2` | Mặc định `CPU, compute_type="int8"` (loại bỏ sự phụ thuộc vào CUDA runtime DLL trên Windows) | `language="vi", beam_size=5` | `vad_filter=True` | `condition_on_previous_text=False` | Thứ tự tự động chọn model: `WHISPER_MODEL env` $\rightarrow$ `whisper-small-vi-50h-ct2` $\rightarrow$ `whisper-small-vi-ct2` $\rightarrow$ `small`.
  - *Bảng Hợp đồng API & Quản lý Tài nguyên/Lỗi (`stt_server.py`, Trang 13):*
    - Endpoints: `GET /`, `GET /health` (trả `model_loaded`), `GET /docs`, `POST /api/stt` (nhận multipart `file = <audio>`, trả `{"text": "..."}`).
    - Cơ chế an toàn: Lazy-load qua `@lru_cache(maxsize=1)`, chạy inference trong `run_in_threadpool` kèm `MODEL_LOCK = Lock()` tuần tự hóa truy cập, xóa file tạm trong khối `finally`.
    - Bảng mã lỗi HTTP chuẩn xác: `400` (File rỗng) | `413` (Vượt giới hạn `MAX_UPLOAD_BYTES = 25 MiB`) | `415` (Sai định dạng MIME ngoài WAV/MP3/FLAC/OGG/WebM/M4A/MP4) | `422` (Không phát hiện tiếng nói) | `500` (Lỗi giải mã/nhận dạng nội bộ).

- **Slide 11 [STT – 8 Vấn đề Thực tế, Tác động lên Retrieval, Giới hạn & Kết luận (Mục 13, 14, 15 + `reports/stt_dev.json`)]:**
  - *Bảng 13 – 8 Vấn đề kỹ thuật thực tế & Cách xử lý trong quá trình thực hiện (Trang 14):*
    1. Dataset 131 GB quá lớn $\rightarrow$ Streaming subset + tách riêng audio, cache, checkpoint.
    2. Quyền truy cập Hugging Face $\rightarrow$ Đăng nhập terminal `hf auth login`, tuyệt đối không ghi token vào mã nguồn.
    3. Xung đột thư viện giải mã âm thanh PyAV 19 $\rightarrow$ Ghim ràng buộc `av < 19`.
    4. Phụ thuộc CUDA DLL trên Windows $\rightarrow$ Mặc định `CPU INT8` cho server production.
    5. Rủi ro treo multiprocessing/fork sau khi khởi tạo CUDA $\rightarrow$ Đặt `preprocessing_workers = 1`, trích đặc trưng trước khi nạp model.
    6. Xung đột kiểu dữ liệu BF16 khi generation $\rightarrow$ Nạp model ở precision chuẩn, để `Seq2SeqTrainer` tự quản lý autocast BF16.
    7. Arrow cache phình to & nghẽn WSL2 I/O $\rightarrow$ Giảm `writer_batch_size = 100`, chuyển cache sang ổ vật lý `D:\` ngoài VHD ổ C.
    8. Sự cố ổ C còn 5,2 GB làm ext4 trong VHD chuyển sang `read-only` $\rightarrow$ Dọn cache, kiểm tra `ext4`, compact VHD, xác minh lại toàn bộ 44.811 file FLAC trước khi train tiếp.
  - **Bổ sung kết quả kiểm thử liên kết STT $\rightarrow$ Retrieval từ mã nguồn (`reports/stt_dev.json`, `scripts/eval_stt.py`):**
    - Trên 100 câu hỏi ViMMRC dev tổng hợp giọng đọc, `whisper-small-vi-50h-ct2` đạt **WER 8,14%**, nhưng làm Recall@1 của Retrieval giảm từ **69,0% (văn bản gốc) xuống 59,0%** do các lỗi đồng âm ở tên riêng lịch sử/địa danh (ví dụ: *"Hai Bà Trưng"* $\rightarrow$ *"hai bà trương"* / *"hay bà chân"*, *"Côlômbô"* $\rightarrow$ *"colombo"*). Đây là minh chứng thực nghiệm trực tiếp cho mục 1.1 & 14.2 của báo cáo!

Hãy trình bày **xác nhận số liệu Lượt 1**, và **thiết kế trực quan đầy đủ Slide 1 đến Slide 11** vào Artifact (với màu sắc hài hòa, bảng biểu, biểu đồ SVG, sơ đồ luồng và Speaker Notes chi tiết). Sau đó dừng lại chờ tôi xác nhận để sang Lượt 2!
```

---

## LƯỢT 2: TOÀN BỘ PHÂN HỆ 2 & 3 – RETRIEVAL 2 TẦNG, ĐỌC HIỂU VIT5 & TẦNG HỘI THOẠI (SLIDE 12 – 21)
*(Sau khi Claude hoàn thành Lượt 1, đính kèm file: `Huy_TT15-20p_Bao_Cao_Retrieval_MRC.docx.pdf` và copy khung dưới đây gửi tiếp)*

```markdown
Tôi xác nhận hoàn thành **Lượt 1 (Slide 1 – 11)**.
Bây giờ chúng ta sang **Lượt 2: Thiết kế chi tiết từ Slide 12 đến Slide 21** (không giới hạn nếu cần tách thêm slide cho thoáng) cho toàn bộ báo cáo của **Ngô Trí Huy (`Huy_TT15-20p_Bao_Cao_Retrieval_MRC.docx.pdf`)** kết hợp mã nguồn thực tế trong `retrieval-model_Huy/`, `mrc-model_Huy/` và `dialogue-manager_Huy/`.

### YÊU CẦU NỘI DUNG, CÔNG THỨC, BẢNG BIỂU & ĐỒ THỊ CHO SLIDE 12 – 21
Giữ vững hệ màu đã thiết kế (**Teal Emerald `#0D9488`** cho Retrieval và **Royal Indigo `#4F46E5`** cho MRC & Hội thoại), trình bày đầy đủ tất cả các bảng, biểu đồ và công thức sau:

- **Slide 12 [Huy – Chương 1 & 2]: Bối cảnh, 5 Đóng góp Chính, Hợp đồng Giao diện & Luồng 6 Giai đoạn**
  - **Vị trí & 3 bài toán nối tiếp (Hình 1.1):** (1) Truy xuất đoạn văn từ kho 1,48 triệu đoạn $\rightarrow$ (2) Đọc hiểu sinh đáp án tự do bằng ViT5 $\rightarrow$ (3) Tầng hội thoại xử lý câu nói tự nhiên và soạn câu trả lời hoàn chỉnh cho TTS.
  - **5 Đóng góp kỹ thuật trọng tâm (Mục 1.3):** Tự cài đặt & tối ưu BM25 (R@1 `71,45% → 77,48%`); Kho tri thức 2 tầng kết hợp BM25 + Dense `multilingual-e5-small` + Reranker `bge-reranker-v2-m3`; Hợp nhất dữ liệu đọc hiểu 27.164 câu chia theo đoạn văn; Tinh chỉnh ViT5 2 giai đoạn (EM `41,05%`, F1 `66,55%`) kèm thực nghiệm kết quả âm (ViMMRC-only & LLM 9B); Tầng hội thoại regex/heuristic đạt `81,9%` lần chạy đầu trên tập held-out.
  - *Bảng 2.1 – Hợp đồng giao diện Python giữa các module (Trang 3):*
    - `Retrieval`: `Retriever.search(q, top_k)` $\rightarrow$ `Danh sách {id, passage, score}` | `Retriever.retrieve(q)` $\rightarrow$ `Đoạn văn tốt nhất (str)`.
    - `MRC`: `MRCClient.answer_question(q, passage)` $\rightarrow$ `Đáp án (str)`.
    - `Hội thoại`: `DialogueManager.respond(text, session_id, passage)` $\rightarrow$ `{answer, kind, resolved_question, passage, ...}`.
  - *Bảng 2.2 – 6 giai đoạn xử lý của một lượt hỏi đáp qua `/api/ask` (Trang 4):* (1) Làm sạch câu nói $\rightarrow$ (2) Định tuyến ý định $\rightarrow$ (3) Truy xuất đa nguồn $\rightarrow$ (4) Xếp hạng lại (Reranker) $\rightarrow$ (5) Đọc hiểu ViT5 $\rightarrow$ (6) Soạn câu trả lời hoàn chỉnh.

- **Slide 13 [Huy – Chương 3]: Cơ sở Lý thuyết BM25, Truy xuất Vector (Dense), Reranker & ViT5 Seq2Seq**
  - **Công thức xếp hạng từ khóa BM25 & Trọng số IDF (Công thức 3.1 & 3.2, Trang 5):**
    $$\text{score}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d)(k_1 + 1)}{f(t, d) + k_1 \left(1 - b + b \frac{|d|}{\text{avgdl}}\right)}, \qquad \text{IDF}(t) = \ln\left(1 + \frac{N - n_t + 0,5}{n_t + 0,5}\right)$$
    - Giải thích rõ: Chuẩn hóa Unicode NFC, tách từ theo âm tiết (`\w+`); vì BM25 chỉ khớp bề mặt từ vựng nên cần bổ sung Dense Retrieval & Cross-Encoder Reranker.
  - **Truy xuất Vector (`intfloat/multilingual-e5-small`) & Cross-Encoder (`BAAI/bge-reranker-v2-m3`):**
    - Bi-encoder `e5-small`: Mã hóa độc lập câu hỏi (tiền tố `"query: "`) và đoạn văn (tiền tố `"passage: "`) thành vector **384 chiều**, chuẩn hóa L2 và tính tích vô hướng.
    - Cross-encoder `bge-reranker-v2-m3`: Đọc đồng thời cặp `(câu hỏi, đoạn văn)` qua cơ chế Self-Attention đầy đủ để chấm điểm liên quan ngữ nghĩa sâu cho tập ứng viên nhỏ.
  - **Đọc hiểu dạng sinh (Generative QA) với `VietAI/vit5-base`:** Kiến trúc Transformer Encoder–Decoder T5 tiếng Việt (~220M tham số); đầu vào `"Trả lời câu hỏi dựa trên đoạn văn. Câu hỏi: ... Đoạn văn: ..."` sinh trực tiếp chuỗi đáp án, dùng chung cho cả dữ liệu trắc nghiệm và tự luận.

- **Slide 14 [Huy – Mục 4.1]: Tối ưu Bộ Truy xuất BM25 Tự Cài đặt & Thực nghiệm Chọn Tham số**
  - **Tối ưu cấu trúc dữ liệu chỉ mục đảo (`retrieval_client.py`):** Chỉ chấm điểm các đoạn chứa từ của câu hỏi thông qua danh sách *postings* (`_postings` & `_bigram_postings`), giúp **tăng tốc độ truy vấn gấp 2,74 lần** (`0,0518 giây` so với `0,1420 giây` khi quét toàn bộ kho trên 200 câu hỏi) mà giữ nguyên 100% kết quả top-5.
  - **Công thức thưởng cụm từ liền kề (Bigram Phrase Boost – Công thức 3.3, Trang 6):**
    $$\text{score}'(q, d) = \text{score}_{\text{uni}}(q, d) + \lambda \cdot \text{score}_{\text{bi}}(q, d), \quad \lambda = 0,4$$
    - Giúp phân biệt chính xác các thực thể/từ ghép đứng cạnh nhau (như *"Quang Trung"*, *"Hai Bà Trưng"*) với các đoạn chỉ chứa từng âm tiết rời rạc.
  - **Quy trình chọn cấu hình chống rò rỉ (`benchmark_retrieval.py`):** Lấy mẫu cố định 800 câu hỏi từ tập Train (`seed=42`), duyệt 16 cấu hình ứng viên theo thứ tự ưu tiên `Recall@1 → MRR@5 → Recall@5`, sau khi khóa cấu hình thắng mới đo kiểm chứng đúng 1 lần trên tập Dev (564 câu).
  - *Bảng 4.1 (So sánh cấu hình BM25 cũ vs Cấu hình chọn) & Biểu đồ cột đôi Hình 4.1 (Trang 6–7):*
    - Tham số: $k_1$: `1,5 → 2,1` | $b$: `0,75 → 1,0` | Bỏ từ dừng câu hỏi (23 từ `QUERY_STOPWORDS` chỉ áp dụng cho unigram): `Không → Có` | Hệ số bigram $\lambda$: `0 → 0,4`.
    - Kết quả trên **Train 800 câu:** Recall@1 `53,2% → 64,1%` | Recall@5 `67,4% → 75,6%` | MRR@5 `58,9 → 68,7`.
    - Kết quả trên **Dev 564 câu (Kiểm chứng):** **Recall@1 tăng từ `71,45% → 77,48%`** (+6,03 điểm %) | **Recall@5 tăng từ `83,69% → 86,52%`** | **MRR@5 tăng từ `0,7624 → 0,8123`**.

- **Slide 15 [Huy – Mục 4.2 & Mã nguồn `kb_retriever.py`]: Kiến trúc Kho Tri thức Hai Tầng Quy mô Triệu Đoạn & Xếp hạng lại**
  - *Vẽ Sơ đồ Hình 2.1 (Luồng truy xuất ngữ cảnh 2 tầng kết hợp BM25, Dense Vector & Reranker) kèm Bảng 4.2 (Trang 4 & Trang 7):*
    - **Tầng 1 – Kho chọn lọc (`data/kb_index.json`):** **5.879 đoạn** (552 bài đọc ViMMRC + 5.317 đoạn UIT-ViQuAD + 10 thẻ tri thức chuyên sâu) $\rightarrow$ Truy xuất bằng BM25 tự cài đặt ($k_1=2,1, b=1,0, \lambda=0,4$) $\rightarrow$ Lấy **Top-3**.
    - **Tầng 2a – Wikipedia BM25 (`data/kb_wiki_full`):** **1,48 triệu đoạn Wikipedia tiếng Việt** chia thành **4 shard** $\rightarrow$ Truy xuất bằng thư viện `bm25s` (không dùng bigram vì chỉ mục bigram cho 1,48M đoạn vượt quá RAM laptop) $\rightarrow$ Lấy **Top-3**.
    - **Tầng 2b – Wikipedia Dense (`embeddings.npy`):** **1,48 triệu đoạn** mã hóa bằng `multilingual-e5-small` (384 chiều) $\rightarrow$ Lấy **Top-3**.
  - **Kỹ thuật tối ưu bộ nhớ (Memory-Mapped I/O) trong `kb_retriever.py` để chạy 1,48 triệu đoạn trên Laptop/CPU:**
    - Văn bản đoạn văn không nạp vào RAM mà lưu trên đĩa (`passages.jsonl`) kèm mảng vị trí byte `offsets.npy` (`int64`); chỉ khi trúng top-k mới dùng `file.seek(offset)` để đọc.
    - Ma trận nhúng vector `1,48M × 384` được lưu dạng **`float16` (~1,1 GB)** và mở bằng `np.load(..., mmap_mode="r")`; khi tính tích vô hướng, chương trình ép kiểu sang `float32` theo từng khối **100.000 dòng** (`emb[s:s+100_000]`) giúp vừa nhanh trên CPU vừa không tràn RAM.
  - **Công thức Xếp hạng lại có Thưởng Điều kiện (Dynamic Gated Bonus – Công thức 3.4, Trang 7):**
    $$s_{\text{final}}(q, d) = r(q, d) + \beta \cdot \mathbb{1}[d \in \text{KB}, \; r(q, d) > -2], \quad \beta = 0,25$$
    - Giải thích sâu sắc: Điểm BM25 giữa hai tầng không so sánh trực tiếp được vì khác chỉ mục. Đưa tối đa 9 ứng viên vào `bge-reranker-v2-m3` chấm chung và cộng thưởng `+0,25` cho đoạn thuộc KB, nhưng **chỉ cộng khi điểm thô $r(q,d) > -2,0$** để ngăn đoạn KB sai (điểm rất âm) thắng nhầm đoạn Wikipedia đúng ở các câu hỏi kiến thức mở!

- **Slide 16 [Huy – Mục 4.3, 5.1 & `context_selection.py`]: Hợp nhất Dữ liệu Đọc hiểu (27.164 Câu) & Xử lý Đoạn văn Dài**
  - **Giải quyết hạn chế dữ liệu nhỏ (`build_combined_dataset.py` & Bảng 4.3, Trang 8):**
    - **ViMMRC 2.0:** `5.273 câu hỏi` (trắc nghiệm 4 đáp án trích từ sách giáo khoa; lấy văn bản của phương án đúng làm đáp án đích).
    - **UIT-ViQuAD2.0 (đã lọc):** `21.891 câu hỏi` (tự luận trích từ Wikipedia, lọc bỏ các câu `is_impossible` không có đáp án từ 28.454 câu gốc).
    - **Tổng hợp:** **`27.164 câu hỏi`**, gộp chung và chia lại theo tỷ lệ **80% / 10% / 10% theo đơn vị đoạn văn (`seed = 42`)**: **Train: `21.733` | Dev: `2.715` | Test: `2.716`**.
  - **Cơ chế kiểm soát rò rỉ dữ liệu bằng mã băm (`validate_split_disjoint` trong `train.py`):**
    - Trước khi nạp mô hình, `train.py` băm `SHA-256` toàn bộ nội dung bài đọc của 3 tập và kiểm tra giao tập `train ∩ dev = ∅`, `train ∩ test = ∅`, `dev ∩ test = ∅`, đồng thời xuất báo cáo `truncation_report` thống kê số mẫu vượt quá 512 token.
  - **Chiến lược chọn đoạn con cho văn bản dài (`context_selection.py`):**
    - Giải quyết giới hạn `max_input_tokens = 512` của ViT5: Chia bài đọc dài thành các khối 96 token, tính điểm TF-IDF có trọng số log-IDF với các từ khóa câu hỏi để ghép các phân đoạn giàu bằng chứng nhất (`question_chunks`) thay vì chỉ cắt cụt phần cuối (`head`).

- **Slide 17 [Huy – Mục 5.2]: Quy trình 3 Giai đoạn Huấn luyện Mô hình ViT5, Phát hiện Quá khớp & Sửa Lỗi Kỹ thuật**
  - **Thiết lập huấn luyện (`train.py`):** Mô hình nền `VietAI/vit5-base` (~220M tham số), tinh chỉnh toàn bộ trọng số trên GPU với `BF16`, `batch_size = 1`, `gradient_accumulation = 16` ($\rightarrow$ **Effective Batch = 16**), `gradient_checkpointing = True`, `max_input_tokens = 512`, `max_target_tokens = 64`, nhãn padding mask bằng `-100`. Chọn checkpoint tốt nhất theo **Exact Match trên tập Dev**.
  - *Bảng 5.1 (Thiết lập 3 giai đoạn huấn luyện) & Biểu đồ đôi Hình 5.1 (Diễn biến Dev EM % và Dev Loss qua 5 epoch tích lũy, Trang 9–10):*
    - **Giai đoạn 1 (`vit5-combined`):** Khởi tạo từ `VietAI/vit5-base`, train `3 epochs` với `lr = 3e-5` $\rightarrow$ Dev EM tăng từ ~39,1% (epoch 1) lên `40,9%` (epoch 2) và đạt **`42,95%` (epoch 3)**; Dev Loss giảm xuống `~0,67–0,69`.
    - **Giai đoạn 2 (`vit5-combined-cont` – Đang dùng trong Production):** Khởi tạo từ `vit5-combined`, train tiếp `2 epochs` với `lr = 1e-5` nhỏ hơn, lưu checkpoint mỗi `450 bước` $\rightarrow$ Dev EM đạt đỉnh **`43,24%` tại bước 2.250**, nhưng **Dev Loss tăng vọt từ `0,69` lên `0,84`** trong khi Train Loss tiếp tục giảm $\rightarrow$ Phát hiện chính xác dấu hiệu bắt đầu **quá khớp (overfitting)** nên dừng lại đúng lúc!
    - **Giai đoạn 3 thử nghiệm (`vit5-vimmrc-ft` – Kết quả âm):** Tinh chỉnh tiếp riêng trên ViMMRC thuần (`3 epochs`), Dev EM dừng quanh `10,63%` và Dev Loss tăng đều (`2,18 → 2,36`), toàn chuỗi chỉ chênh vài phần mười điểm F1 $\rightarrow$ Bác bỏ giả thuyết "fine-tune hẹp thêm giúp tăng điểm", giữ checkpoint hợp nhất `vit5-combined-cont`.
  - **Hai lỗi kỹ thuật quan trọng đã phát hiện và khắc phục (Mục 5.2.3):**
    1. Lỗi `OverflowError: can't convert negative int to unsigned` khi đánh giá cuối epoch 1 do `generate()` sinh ra cả giá trị `-100` trong `predictions` $\rightarrow$ Sửa bằng `np.where(predictions == -100, tokenizer.pad_token_id, predictions)` cho cả `predictions` và `labels`.
    2. Thư viện `transformers >= 5.x` không tương thích cấu trúc `vocab` của tokenizer ViT5 đã lưu và tự import TensorFlow gây treo $\rightarrow$ Ghim `transformers < 4.58` và đặt `TRANSFORMERS_NO_TF=1`.

- **Slide 18 [Huy – Mục 6.1, 6.2, 6.3, 6.4]: Kết quả Thực nghiệm Truy xuất, Đọc hiểu & Toàn chuỗi End-to-End**
  - **Phương pháp tách 3 mức đo độc lập (Mục 6.1):** Tách biệt lỗi của (1) *Retrieval* (`Recall@k`, `MRR@k`), (2) *Reader độc lập khi đưa đúng đoạn văn chuẩn* (`Exact Match`, `Token F1`), và (3) *Toàn chuỗi End-to-End khi đọc đoạn do Retriever chọn* (`scripts/eval_e2e.py`).
  - *Bảng 6.1 – Kết quả truy xuất đoạn văn (Trang 11):*
    - Kho đóng ViMMRC Dev (70 đoạn, 564 câu): BM25 cũ (`R@1: 71,45% | R@5: 83,69% | MRR@5: 0,7624`) $\rightarrow$ **Cấu hình chọn (`R@1: 77,48% | R@5: 86,52% | MRR@5: 0,8123`)**.
    - Kho mở rộng 5.879 đoạn (trước reranker): Dev hợp nhất (`R@1: 70,7% | R@5: 85,1%`) | **Test hợp nhất 2.545 câu (`R@1: 71,1% | R@5: 85,9%`, trong đó ViQuAD R@1 đạt `73,24%`, ViMMRC đạt `59,38%`)**.
  - *Bảng 6.2 – Kết quả mô hình đọc hiểu khi đưa đúng đoạn văn (Test 2.716 câu, Trang 12):*
    - `vit5-combined`: Test EM `41,05%` | Test Token F1 `66,02%`
    - **`vit5-combined-cont` (Đang dùng):** **Test EM `41,05%` | Test Token F1 `66,55%`** *(Giải thích: F1 cao hơn EM 25,5 điểm vì đáp án tham chiếu là cụm dài, mô hình diễn đạt khác ký tự nhưng đúng ý)*.
  - *Bảng 6.3 & Biểu đồ cột Hình 6.1 – So sánh Token F1 giữa Đọc đoạn đúng vs Toàn chuỗi trên Dev (2.570 câu) & Test (2.545 câu) (Trang 12):*
    - **Dev (`vit5-combined-cont`, 2.570 câu):** Đoạn đúng F1 `68,7%` $\rightarrow$ Toàn chuỗi: **EM `33,4%` | F1 `54,6%`** (ViQuAD F1 `60,6%`, ViMMRC F1 `22,5%`).
    - **Test (`vit5-combined-cont`, 2.545 câu):** Đoạn đúng F1 `68,6%` $\rightarrow$ Toàn chuỗi: **EM `32,3%` | F1 `53,9%`** (ViQuAD F1 `59,6%`, ViMMRC F1 `22,4%`).
    - Nhận xét: Toàn chuỗi mất `~14,7 điểm F1` (`68,6% → 53,9%`) do lỗi truy xuất sai đoạn văn.

- **Slide 19 [Huy – Mục 6.4 & 6.5]: Thực nghiệm Chọn Tầng Kho Tri thức (Reranking) & Đối sánh với Mô hình Ngôn ngữ Lớn (LLM 9B)**
  - *Biểu đồ cột đôi Hình 6.2 – So sánh Answer F1 của 7 phương án chọn tầng kho tri thức (Trang 13, đo trên Nhóm A: câu có đoạn trong KB & Nhóm B: câu kiến thức mở trên Wikipedia):*
    1. `BM25 ngưỡng 0,5`: Nhóm A `53,7%` | Nhóm B `14,1%`
    2. `BM25 ngưỡng 0,4`: Nhóm A `52,9%` | Nhóm B `16,0%`
    3. `Độ tự tin ViT5`: Nhóm A `44,7%` | Nhóm B `19,4%`
    4. `BM25 + Dense Wiki`: Nhóm A `57,9%` | Nhóm B `16,9%`
    5. **`Reranker bge-reranker-v2-m3 (KB +0,25)` [Báo cáo gốc]: Nhóm A tăng vọt lên `60,7%` | Nhóm B tăng lên `24,3%`** *(Điểm cân bằng tối ưu)*. **Cải tiến mới nhất trong mã nguồn (`rerank_logit_routing_e2e.json`):** Cộng **`+3,0` trong không gian logit** trước hàm sigmoid (vì sigmoid bão hòa gần `1,0`) giúp nâng tiếp **Nhóm A lên `60,8%` và Nhóm B lên `26,7%`**!
    6. `Reranker (KB +0,5)`: Nhóm A `61,7%` | Nhóm B giảm còn `23,8%`
    7. `Reranker (Không cộng thưởng)`: Nhóm A tụt xuống `55,1%` | Nhóm B `27,4%`.
  - *Bảng 6.4 – Thực nghiệm dùng Mô hình Ngôn ngữ Lớn (LLM 9B `ornith-1.5:9b` qua Ollama, `llm_eval.py`, Trang 13–14) & Mở rộng So sánh 8 Bộ Đọc (`reader_bench.json`):*
    - `ViT5 fine-tune, LLM chấm theo ý nghĩa (200 câu)`: **LLM-judge `61,0%`** | EM ký tự `43,5%` | Token F1 `65,6%`.
    - `ViT5 fine-tune, LLM chấm theo ý nghĩa (50 câu cùng seed)`: **LLM-judge `50,0%`** | EM ký tự `44,0%` | Token F1 `63,0%`.
    - `LLM 9B sinh trực tiếp, không dùng ViT5 (50 câu cùng seed)`: **LLM-judge `54,0%`** | EM ký tự `32,0%` | Token F1 `61,7%`.
    - **Mở rộng thực nghiệm mới nhất trong repo (`scripts/eval_readers.py`, `reports/reader_bench.json` & `llm_assist.py`):**
      - So sánh 8 ứng viên Reader trên cùng 220 đoạn truy xuất: `xlmr-large-viquad` (`0,469`), `vi-mrc-large` (`0,468`, toàn chuỗi 220 câu đạt F1 `0,4583`, tốc độ `0,6s/câu` CPU), `vit5-combined` (`0,453`), `vit5-combined-cont` (`0,446`), `vit5-vimmrc-ft` (`0,444`), `xlm-roberta-large-squad2` (`0,430`), `mdeberta-v3-base-squad2` (`0,418`), `Qwen2.5-1.5B` (`0,418`).
      - Tích hợp thêm module tùy chọn `dialogue-manager_Huy/llm_assist.py` (`nemotron-3.5-bolt:e4b-q4_K_M` qua Ollama) hỗ trợ 3 chốt chặn: (1) *Cổng kiểm duyệt đoạn văn* (từ chối đúng `23/30` câu ngoài kho so với `7/30` khi không dùng LLM), (2) *Kiểm chứng đáp án*, và (3) *Sửa lỗi tên riêng STT* (`"lam sân"` $\rightarrow$ `"Lam Sơn"`).

- **Slide 20 [Huy – Mục 4.4, 6.6 & `dialogue-manager_Huy/`]: Kiến trúc Tầng Hội thoại Không Mô hình & Kết quả Đánh giá**
  - *Sơ đồ kiến trúc chi tiết 4 module trong `dialogue-manager_Huy/`:*
    1. **`utterance.py` (`clean_utterance` & `question_type`):** Lặp tối đa 6 vòng bóc tách từ đệm giọng nói Whisper hay chép ra (`"ừm"`, `"ờ"`, `"dạ vâng"`), lời mào đầu (`"cho mình hỏi là"`, `"bạn có biết ... không"`) và trợ từ cuối câu (`"vậy bạn"`, `"nhé"`, `"ạ"`), nhưng bảo toàn các cụm ngữ nghĩa (`"như thế"`, `"lúc đó"`, `"người ấy"`). Phân loại 12 dạng câu hỏi (`summary, why, how, describe, yesno, time, quantity, person, location, list, definition, choice`).
    2. **`smalltalk.py` (`detect_intent` & `try_arithmetic`):** Xử lý tức thì (0,1 ms) các câu chào hỏi, giới thiệu bản thân, ngày/giờ, ghi nhớ tên người dùng, và giải toán số học bằng chữ tiếng Việt (*"một trăm trừ ba mươi lăm bằng mấy"*).
    3. **`dialogue.py` (`DialogueManager`):** Quản lý ngữ cảnh đa lượt theo `session_id`:
       - Viết lại câu hỏi nối tiếp (`resolve_followup`: *"còn Hàn Quốc thì sao?"* $\rightarrow$ *"Thủ đô của Hàn Quốc là gì"*; thay đại từ *"ông ấy"*, *"bà ấy"*, *"nơi đó"* bằng chủ thể lượt trước).
       - Tách câu hỏi ghép nhiều vế (`split_multi_question`: vế sau tự động mượn chủ ngữ của vế trước).
       - Xử lý câu hỏi So sánh (`parse_comparison`: truy xuất riêng cho từng thực thể A và B rồi đối chiếu số liệu) và câu hỏi Đúng/Sai (`_yesno`: kiểm tra mâu thuẫn tên riêng, con số, từ phủ định, phương hướng Bắc/Nam với câu bằng chứng).
    4. **`answer_composer.py` (`compose_answer` & `support`):** Biến cụm trả lời ngắn của ViT5 (*"Tokyo"*) thành câu hoàn chỉnh cho giọng đọc TTS (*"Thủ đô của Nhật Bản là Tokyo."*), ghép thêm câu bằng chứng cho câu hỏi *tại sao/như thế nào*, và **từ chối lịch sự (*"chưa tìm thấy thông tin"*)** khi độ phủ từ khóa `support(q, passage) < 0,34` hoặc thiếu tên riêng của câu hỏi!
  - *Bảng 6.5 – Kết quả đánh giá Tầng hội thoại (`eval_dialogue.py`, Trang 14):*
    - **Bộ phát triển (157 mục / 190 lượt, 11 thể loại):** Lần chạy đầu `130/157 = 82,8%` | Sau khi sửa lỗi chung `156/157 = 99,4%`.
    - **Bộ Held-out độc lập (72 mục / 79 lượt, viết sau khi đã chỉnh hệ thống):** **Lần chạy đầu `59/72 = 81,9%`** *(Con số khách quan, trung thực nhất)* | Sau khi sửa lỗi chung `70/72 = 97,2%`. Kiểm tra `--tts-check`: **0 câu trả lời còn sót chữ số/ký hiệu gây lỗi đọc TTS**.

- **Slide 21 [Huy – Chương 7 & 8]: Tổng hợp 9 Khó khăn Kỹ thuật, Phân tích Độ trễ CPU & Định hướng Phát triển**
  - *Bảng 7.1 – 9 Khó khăn kỹ thuật thực tế và Giải pháp khắc phục triệt để (Trang 15):* Trình bày trọn vẹn 9 cặp vấn đề – giải pháp từ báo cáo của Huy.
  - *Biểu đồ phân rã Độ trễ (Latency Breakdown) trên Docker CPU 4 luồng (`OMP_NUM_THREADS=4`, Trang 14):*
    - **Cấu hình chuẩn (Bật Reranker – Tổng ~12 giây/câu):** STT Whisper INT8 (`~3,0s`) + Truy xuất 2 tầng & Reranker BGE (`~6,0s`) + Đọc hiểu ViT5 (`~1,4s`) + Tổng hợp giọng nói Matcha-TTS (`~1,3s`).
    - **Cấu hình tốc độ cao (Tắt Reranker `KB_RERANKER=""` – Tổng ~6 giây/câu):** Khâu truy xuất giảm mạnh còn `0,1 – 1,7s`, đánh đổi giảm độ chính xác trên câu hỏi khó.
    - **Phát hiện kỹ nghệ quan trọng trong `docker-compose.yml`:** Mặc định PyTorch tạo 1 luồng/core làm nghẽn CPU chia sẻ (khiến ViT5 mất `25–300 giây/câu` ở 20 luồng); việc khóa `OMP_NUM_THREADS=4` giúp kéo thời gian suy luận ViT5 xuống chỉ còn **`~1,4 giây/câu`**!
  - **Hạn chế & Hướng phát triển (Chương 8, Trang 16):** Tách từ ghép tiếng Việt trước khi lập chỉ mục BM25; fine-tune Dense Encoder trên dữ liệu đề tài; áp dụng `question_chunks` đồng bộ cả lúc train và inference; đánh giá hội thoại đa lượt trực tiếp trên kho đầy đủ + ViT5.

Hãy trình bày **xác nhận số liệu Lượt 2** và **thiết kế trực quan đầy đủ Slide 12 đến Slide 21** vào Artifact (kèm đầy đủ công thức, bảng biểu, đồ thị SVG và Speaker Notes). Sau đó dừng lại chờ tôi xác nhận để sang Lượt 3!
```

---

## LƯỢT 3: TOÀN BỘ PHÂN HỆ 4 – TỔNG HỢP TIẾNG NÓI MATCHA-TTS & HIFI-GAN (SLIDE 22 – 31)
*(Sau khi Claude hoàn thành Lượt 2, đính kèm file: `Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx.pdf` và copy khung dưới đây gửi tiếp)*

```markdown
Tôi xác nhận hoàn thành **Lượt 2 (Slide 12 – 21)**.
Bây giờ chúng ta sang **Lượt 3: Thiết kế chi tiết từ Slide 22 đến Slide 31** (không giới hạn nếu cần tách thêm slide) cho toàn bộ báo cáo 25 trang của **Trương Hoàng Duy (`Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx.pdf`)** kết hợp mã nguồn thực tế trong `text-to-speech_Duy/src/` (`vi_tokenizer.py`, `normalizer.py`, `matcha_engine.py`, `tts_engine.py`, `evaluator.py`).

### YÊU CẦU NỘI DUNG, CÔNG THỨC, BẢNG BIỂU, ĐỒ THỊ & MÃ NGUỒN CHO SLIDE 22 – 31
Giữ vững hệ màu đã thiết kế (sử dụng màu **Crimson Rose `#E11D48`**, **Deep Navy `#1E3A8A`** và **Forest Green `#15803D`** khớp với sơ đồ trong báo cáo của Duy), trình bày đầy đủ 100% các nội dung sau:

- **Slide 22 [TTS – Chương 1]: Bối cảnh, Vai trò trong Hệ thống, 4 Mục tiêu & 6 Đóng góp Khoa học – Kỹ thuật**
  - **Vai trò khâu đầu ra cuối cùng (Hình 1.1, Trang 1):** Tiếp nhận văn bản đáp án từ MRC (ViT5) và chuyển đổi thành giọng nói tiếng Việt tự nhiên, chuẩn ngữ âm phản hồi qua Web UI.
  - **4 Mục tiêu nghiên cứu (Mục 1.2, Trang 2):** (1) *Độ chính xác ngữ âm:* Đọc chuẩn 6 thanh điệu (ngang, sắc, huyền, hỏi, ngã, nặng) và ngắt nghỉ theo dấu câu; (2) *Tối ưu tài nguyên tính toán:* Chạy ổn định trên CPU thông thường với `RTF < 1,0`, không cần GPU rời; (3) *Xử lý văn bản đặc thù:* Chuẩn hóa hoàn chỉnh nhãn đáp án trắc nghiệm, số liệu, ngày tháng, phần trăm, đơn vị đo; (4) *Tính tự chủ & ổn định cao:* Hoạt động hoàn toàn ngoại tuyến (100% Offline) kèm cơ chế dự phòng đa tầng.
  - **6 Đóng góp chính của đề tài (Mục 1.3, Trang 2–3):**
    1. Huấn luyện thành công `Matcha-TTS` tiếng Việt bằng Transfer Learning từ checkpoint tiếng Anh (Mehta và cộng sự, 2024) trên tập dữ liệu `InfoRe1` (25 giờ).
    2. Thiết kế giải pháp **tách thanh điệu độc lập cuối âm tiết**, thu gọn bảng ký hiệu ngữ âm xuống đúng **41 token (-58,2%)**, khắc phục triệt để hiện tượng dữ liệu thưa (*data sparsity*).
    3. Tối ưu thuật toán căn chỉnh thời gian đơn điệu **MAS (Monotonic Alignment Search)** bằng **Numba JIT**, chạy tốc độ ngang C++ mà không cần trình biên dịch Cython/GCC/MSVC.
    4. Tinh chỉnh đối kháng **HiFi-GAN Vocoder** suốt **50.000 bước** trực tiếp trên phổ Mel nhân tạo do chính Matcha-TTS sinh ra, **triệt tiêu 100% hiện tượng rè và tạp âm kim loại**.
    5. Xây dựng quy trình chuẩn hóa ngôn ngữ tự nhiên chuyên biệt cho câu trả lời đọc hiểu tiếng Việt và kiến trúc điều phối lai 4 engine (Offline + Online Cloud).
    6. Thực nghiệm đo đạc định lượng khách quan (`MCD`, `F0 RMSE`, `log-F0 RMSE` qua pYIN, `CER` qua `PhoWhisper` của VinAI Research, `RTF` trên CPU 8 luồng) đối sánh với `VITS MMS` (Meta) và dịch vụ đám mây.

- **Slide 23 [TTS – Chương 2]: Đặc tả Dữ liệu I/O, Giao thức Tích hợp & Sơ đồ Luồng Xử lý 6 Giai đoạn**
  - **Quy cách dữ liệu vào/ra (Mục 2.1, Trang 4):**
    - *Đầu vào:* Chuỗi văn bản thô từ MRC chứa Markdown, nhãn đáp án, số liệu (ví dụ: `"**Đáp án:** (B) Chiến thắng Điện Biên Phủ ngày 07/05/1954."`).
    - *Đầu ra:* Tín hiệu âm thanh dạng sóng (Waveform) chuẩn phát thanh tần số lấy mẫu **22,05 kHz định dạng `.wav` (PCM 16-bit mono)** hoặc nén `.mp3`, âm sắc trong trẻo, không nhiễu nền.
    - *Giao thức tích hợp kép:* Cung cấp đồng thời thư viện nội bộ **Python SDK (`synthesize()`)** và dịch vụ web **RESTful API (`POST /api/tts`)**.
  - *Sơ đồ Hình 2.1 & Bảng 2.1 – 6 Giai đoạn thực hiện chính trong quy trình tổng hợp tiếng nói (Trang 5–6):*
    1. **Chuẩn hóa ngôn ngữ (Text Normalization):** Lọc Markdown, mở rộng nhãn `(B)` $\rightarrow$ `'Đáp án B:'`, chuyển ngày tháng, chữ số, phần trăm, đơn vị đo thành chữ.
    2. **Phân cụm ngữ nghĩa (Phrase Splitting):** Cắt câu dài theo dấu câu (`, ; : . ! ? \n`), tối ưu độ dài từng cụm phục vụ tổng hợp cục bộ.
    3. **Tách Token & Dấu thanh (`vi_tokenizer.py`):** Tách dấu thanh ra cuối âm tiết (`0..5`), thu gọn 58,2% từ điển còn 41 token, xen kẽ blank token `id=0`.
    4. **Dự đoán phổ Mel (`Matcha-TTS`):** Text Encoder (Conv1D + RoPE) + Duration Predictor (MAS Numba JIT) + Giải mã OT-CFM (10–20 bước Euler) $\rightarrow$ Phổ Mel 80 kênh tần số.
    5. **Tái tạo sóng âm (`Vocoder HiFi-GAN`):** Tinh chỉnh 50.000 bước trên phổ Mel nhân tạo + Bộ lọc `Denoiser` khử sạch tiếng rè kim loại $\rightarrow$ Sóng âm chuẩn 22,05 kHz.
    6. **Hậu xử lý & Xuất file (`Post-processing`):** Cắt lặng (`-30 dB`, biên `50 ms`), làm mượt biên `Fade-in/out 10 ms`, chèn khoảng lặng (`0,15s – 0,45s`), chuẩn hóa âm lượng đỉnh `-1 dBFS` $\rightarrow$ Xuất `.wav` / `.mp3`.

- **Slide 24 [TTS – Mục 2.2.1 & Mã nguồn `normalizer.py`]: Minh họa Luồng Biến đổi Dữ liệu Số 6 Bước & Giải thuật Chuẩn hóa Văn bản**
  - *Vẽ Sơ đồ Hình 2.2 – Luồng biến đổi dữ liệu kỹ thuật số thực tế qua 6 bước xử lý (Trang 7):*
    - **Đầu vào thô (Từ MRC):** `"**Đáp án:** (B) Chiến thắng Điện Biên Phủ ngày 07/05/1954."`
    - **Bước 1 (Chuẩn hóa ngôn ngữ):** `"Đáp án B: Chiến thắng Điện Biên Phủ ngày bảy tháng năm năm một nghìn chín trăm năm mươi tư."`
    - **Bước 2 (Phân cụm ngữ nghĩa):** Cụm 1: `"Đáp án B"` $\rightarrow$ Dấu `':'` (Lặng `0,25 giây`) | Cụm 2: `"Chiến thắng ... năm mươi tư"` $\rightarrow$ Dấu `'.'` (Lặng `0,40 giây`).
    - **Bước 3 (Mã hóa Token & Thanh điệu):** `"Chiến thắng"` $\rightarrow$ Âm vị `['c','h','i','ê','n','1', ' ', 't','h','ă','n','g','1']` $\rightarrow$ Chuỗi ID `[5, 10, 11, 8, 16, 36, 1, 23, 10, 3, 16, 9, 36]`.
    - **Bước 4 (Matcha-TTS OT-CFM):** Giải ODE Euler (20 bước) sinh Tensor phổ Mel: `Kích thước [Batch = 1, Mel = 80, Frames = 412]` (80 kênh tần số Mel, 412 khung $\sim$ thời lượng `4,78 giây`).
    - **Bước 5 (Vocoder HiFi-GAN):** Tái tạo mảng sóng âm 1 chiều (`float32`): `[105.472 mẫu]` tại tần số lấy mẫu chuẩn `22.050 Hz (Mono)`.
    - **Bước 6 (Hậu xử lý & Xuất file):** Cắt lặng (`-30 dB`, biên `50 ms`), `Fade-in / Fade-out 10 ms` + Ghép khoảng lặng `0,25 giây` $\rightarrow$ Xuất tệp `.wav PCM 16-bit`.
  - **Chi tiết giải thuật trong `text-to-speech_Duy/src/normalizer.py`:**
    - Quy tắc biến âm số đếm tiếng Việt tự nhiên trong `_read_3_digits`: đọc **`"mốt"`** (khi hàng chục $> 1$ và đơn vị $= 1$), **`"tư"`** (khi hàng chục $> 1$ và đơn vị $= 4$), **`"lăm"`** (khi hàng chục $\ge 1$ và đơn vị $= 5$), **`"lẻ"`** (khi hàng trăm $> 0$ và hàng chục $= 0$).
    - Xử lý đa dạng mẫu câu hỏi đáp học thuật: Số La Mã sau từ khóa (`"thế kỷ XX"` $\rightarrow$ `"thế kỷ hai mươi"`), khoảng số (`"1765–1820"` $\rightarrow$ `"1765 đến 1820"`), công thức hóa học/ký hiệu (`"H2O"`, `"CO2"` tách số đọc riêng), từ viết tắt (`"TP.HCM"`, `"TCN"`, `"SCN"`), đơn vị kép đứng sau hệ số chữ (`"9 triệu km²"` $\rightarrow$ `"chín triệu ki-lô-mét vuông"`).

- **Slide 25 [TTS – Chương 3]: Cơ sở Lý thuyết Kiến trúc Matcha-TTS & Toán học Khớp Dòng chảy Vận chuyển Tối ưu (OT-CFM)**
  - **Cấu trúc 3 khối chức năng của Matcha-TTS (Mehta và cộng sự, ICASSP 2024 – Mục 3.1, Trang 8):**
    1. **Bộ mã hóa văn bản (Text Encoder):** Các tầng tích chập 1D (Conv1D) kết hợp Transformer tích hợp **mã hóa vị trí quay (Rotary Position Embedding – RoPE)** giúp mô hình tổng quát hóa tốt trên các câu văn có độ dài biến thiên.
    2. **Bộ dự đoán thời lượng (Duration Predictor):** Dự đoán số khung phổ Mel cho từng âm vị; trong huấn luyện, độ dài thực tế được gán nhãn tự động nhờ thuật toán **Monotonic Alignment Search (MAS)** kế thừa từ Glow-TTS (Kim và cộng sự, 2020).
    3. **Bộ giải mã dòng chảy (Decoder U-Net 1D):** Kiến trúc U-Net 1 chiều kết hợp khối Transformer học trường vận tốc vector $v_\theta(x_t, t \mid \mu)$ để biến đổi nhiễu trắng Gaussian thành phổ Mel 80 kênh.
  - **Hệ thống 4 phương trình toán học cốt lõi của OT-CFM (Lipman và cộng sự, 2023 – Mục 3.2, Trang 8–9):**
    - **(3.1) Phương trình nội suy quỹ đạo vận chuyển tối ưu thẳng:**
      $$x_t = \big(1 - (1 - \sigma_{\min})t\big)x_0 + t x_1, \quad t \in [0, 1], \quad \sigma_{\min} = 10^{-4}$$
      *(trong đó $x_0 \sim \mathcal{N}(0, I)$ là nhiễu chuẩn tắc, $x_1$ là phổ Mel thực tế mục tiêu)*.
    - **(3.2) Hàm mất mát hồi quy bình phương tối thiểu trường vận tốc:**
      $$\mathcal{L}_{\text{CFM}}(\theta) = \mathbb{E}_{t, x_0, x_1} \left[ \left\| v_\theta(x_t, t \mid \mu) - \big(x_1 - (1 - \sigma_{\min})x_0\big) \right\|^2 \right]$$
    - **(3.3) Phương trình vi phân thường (ODE) trong giai đoạn suy luận:**
      $$\frac{dx_t}{dt} = v_\theta(x_t, t \mid \mu)$$
    - **(3.4) Lược đồ giải rời rạc xấp xỉ tiến Euler trên máy tính:**
      $$x_{t + \Delta t} = x_t + \Delta t \cdot v_\theta(x_t, t \mid \mu)$$
  - *Đồ thị trực quan Hình 3.1 (Trang 10 – So sánh quỹ đạo suy luận Diffusion truyền thống vs Matcha-TTS OT-CFM):*
    - **(a) Mô hình Khuếch tán (Diffusion):** Quỹ đạo cong phức tạp, phải khử nhiễu qua **100 đến 1.000 bước lặp** tốn kém.
    - **(b) Matcha-TTS (OT-CFM):** Quỹ đạo vận chuyển tối ưu là **đường thẳng nối trực tiếp $x_0 \rightarrow x_1$**, trường vận tốc vector hầu như không đổi dọc theo $t$ $\rightarrow$ Chỉ cần **10 đến 20 bước giải Euler** là đạt phổ Mel chất lượng cao, giảm tải tính toán hơn 10 lần trên CPU!

- **Slide 26 [TTS – Mục 4.1 & Mã nguồn `vi_tokenizer.py`]: Giải pháp Tách Thanh điệu Độc lập & Bộ Từ điển Tối ưu 41 Token**
  - **Phân tích thách thức chữ Quốc ngữ (Mục 4.1.1, Trang 11):** Gắn trực tiếp 6 dấu thanh vào 12 nguyên âm tạo ra bảng từ vựng phình to **98 tokens**. Các tổ hợp nguyên âm mang dấu hiếm gặp (`ẵ`, `ỵ`, `ự`...) gây hiện tượng **dữ liệu thưa (data sparsity)**, làm vector nhúng (embedding) kém chính xác và bắt mô hình phải học lại đường cong cao độ (F0 contour) của cùng một thanh điệu trên hàng chục nguyên âm khác nhau.
  - **Cơ chế phân tách bằng chuẩn hóa Unicode NFD trong `vi_tokenizer.py` (`syllable_tokens`):**
    - Đưa âm tiết về dạng phân rã **Unicode NFD** (`unicodedata.normalize("NFD", syllable)`), bóc riêng 5 ký tự dấu thanh tổ hợp (`\u0301` sắc $\rightarrow$ `'1'`, `\u0300` huyền $\rightarrow$ `'2'`, `\u0309` hỏi $\rightarrow$ `'3'`, `\u0303` ngã $\rightarrow$ `'4'`, `\u0323` nặng $\rightarrow$ `'5'`, mặc định không dấu $\rightarrow$ `'0'` ngang) đặt làm token cuối âm tiết; sau đó tổ hợp lại phần chữ cái cơ sở về **Unicode NFC** để giữ nguyên dấu phụ tạo nguyên âm (`ă, â, ê, ô, ơ, ư`).
    - Xử lý từ viết tắt & chữ ngoại lai (`spell_out`): Đánh vần từ viết tắt in hoa 1–5 ký tự qua `LETTER_NAMES` (`"B"` $\rightarrow$ `"bê"`, `"TTS"` $\rightarrow$ `"tê tê ét"`), ánh xạ chữ ngoại lai `f → ph`, `j → gi`, `w → u`, `z → d`, và chèn xen kẽ token trống `blank '_'` (`id=0`) tạo chuỗi độ dài $2n + 1$: `[0, t_1, 0, t_2, ..., 0]` phục vụ căn chỉnh MAS.
  - *Bảng 4.1 – Minh họa quy tắc tách token ngữ âm và nhãn thanh điệu độc lập ở cuối âm tiết (Trang 11–12):*
    - `hồ` (Phụ âm `h` + Nguyên âm `ô` + Thanh huyền) $\rightarrow$ **`h, ô, 2`** (Nhãn `2` – Thanh huyền)
    - `nội` (Phụ âm `n` + Nguyên âm đôi `ôi` + Thanh nặng) $\rightarrow$ **`n, ô, i, 5`** (Nhãn `5` – Thanh nặng)
    - `gươm` (Phụ âm `g` + Nguyên âm đôi `ươ` + Âm cuối `m` + Thanh ngang) $\rightarrow$ **`g, ư, ơ, m, 0`** (Nhãn `0` – Thanh ngang)
    - `thắng` (Phụ âm ghép `th` + Nguyên âm `ă` + Âm cuối `ng` + Thanh sắc) $\rightarrow$ **`t, h, ă, n, g, 1`** (Nhãn `1` – Thanh sắc)
    - `ửng` (Nguyên âm `ư` + Âm cuối `ng` + Thanh hỏi) $\rightarrow$ **`ư, n, g, 3`** (Nhãn `3` – Thanh hỏi)
    - `mãi` (Phụ âm `m` + Nguyên âm `a` + Bán âm `i` + Thanh ngã) $\rightarrow$ **`m, a, i, 4`** (Nhãn `4` – Thanh ngã).
  - *Bảng 4.2 & Biểu đồ đôi Hình 4.1 – Hiệu quả thu gọn từ điển 58,2% (98 tokens $\rightarrow$ 41 tokens) và cơ cấu 41 token (Trang 12–13):*
    1. **Chữ cái cơ sở:** **29 tokens (70,7%)** — `22 chữ cái Latinh + 7 ký tự đặc thù (ă, â, đ, ê, ô, ơ, ư)` $\rightarrow$ Biểu diễn cấu trúc âm sắc nguyên âm và phụ âm.
    2. **Ký hiệu thanh điệu độc lập:** **6 tokens (14,6%)** — `0 (ngang), 1 (sắc), 2 (huyền), 3 (hỏi), 4 (ngã), 5 (nặng)` $\rightarrow$ Điều khiển đường bao tần số cơ bản (F0 contour); mọi nguyên âm đều đóng góp gradient cập nhật 6 token này!
    3. **Dấu câu ngữ pháp:** **4 tokens (9,8%)** — `, . ? !` $\rightarrow$ Định vị ranh giới ngữ đoạn và ngắt nghỉ.
    4. **Ký tự điều khiển:** **2 tokens (4,9%)** — `Ký tự trắng (space) và ký tự trống (blank '_')` $\rightarrow$ Phân tách từ và căn chỉnh thời gian MAS.

- **Slide 27 [TTS – Mục 4.2]: Tối ưu Thuật toán Căn chỉnh Thời gian Đơn điệu (MAS) bằng Numba JIT**
  - **Vấn đề của bản gốc Matcha-TTS / Glow-TTS (Kim và cộng sự, 2020):** Giải thuật quy hoạch động tìm đường căn chỉnh tối ưu giữa chuỗi token văn bản $t_x$ và khung phổ Mel $t_y$ được viết bằng **Cython**, bắt buộc máy chủ/môi trường cài đặt trình biên dịch C++ (`GCC` hoặc `MSVC Build Tools`), thường xuyên gây lỗi biên dịch khi đóng gói Docker hoặc triển khai đa nền tảng (Windows/Linux/macOS).
  - **Giải pháp cải tiến (Bảng 4.3, Trang 13–14):** Tái cấu trúc hoàn toàn giải thuật quy hoạch động bằng thư viện biên dịch tức thời **Numba JIT (`@numba.jit(nopython=True, nogil=True)`)** giải phóng Global Interpreter Lock (GIL):
    - *Hiển thị đầy đủ khối mã nguồn Bảng 4.3 (`monotonic_alignment_search_jit`):* Ma trận quy hoạch động `Q[x, y] = max(v_prev, Q[x, y - 1]) + value_matrix[x, y]` và vòng lặp truy vết ngược `for y in range(t_y - 1, -1, -1)` tìm đường đi đơn điệu `path[index, y] = 1.0`.
    - **Hiệu quả:** Đạt tốc độ thực thi mã máy ngang ngửa C++ nguyên bản nhưng giữ 100% tính thuần Python, giúp `setup_matcha.py` tự động vá mã nguồn và chạy trơn tru trên mọi hệ điều hành và container Docker.

- **Slide 28 [TTS – Mục 4.3, 4.4 & `matcha_engine.py`, `tts_engine.py`]: Hậu xử lý Ngữ điệu Ngắt nghỉ & Kiến trúc Điều phối Đa Mô hình**
  - **Giải pháp hậu xử lý âm học 3 bước khắc phục dữ liệu thiếu dấu câu (Mục 4.3, Trang 14–15):**
    - Do tập dữ liệu huấn luyện `InfoRe1` không chứa đầy đủ dấu câu ngữ pháp nên mô hình âm học gốc dễ đọc liền một hơi. Nhóm thiết kế thuật toán hậu xử lý trong `MatchaTTSEngine`:
      1. *Phân tách câu theo ngữ đoạn (`_split_phrases`):* Cắt văn bản theo các mốc dấu câu `, ; : . ! ? … \n`.
      2. *Chèn khoảng lặng tham số hóa (`PHRASE_PAUSES` – Biểu đồ ngang Hình 4.2, Trang 15):*
         - Dấu phẩy (`,`): nghỉ **`150 ms (0,15 giây)`**
         - Dấu hai chấm / chấm phẩy (`:`, `;`): nghỉ **`250 ms (0,25 giây)`**
         - Dấu kết thúc câu (`.`, `!`, `?`): nghỉ **`400 ms (0,40 giây)`**
         - Xuống dòng chuyển đoạn (`\n`): nghỉ **`450 ms (0,45 giây)`**.
      3. *Lọc tạp âm biên, khử nhiễu & chống tiếng Click (`_trim_silence` & `Denoiser`):*
         - Đưa sóng âm từ HiFi-GAN qua bộ lọc `Denoiser(vocoder, mode="zeros", strength=0.00025)`.
         - Cắt bỏ phần tĩnh lặng/nhiễu ở hai đầu mỗi cụm theo ngưỡng năng lượng RMS **`-30 dB`** (khung 10 ms), nhưng **giữ lại biên an toàn `50 ms`** để không cắt phạm vào phụ âm cuối!
         - Áp dụng hàm vuốt biên tuyến tính **`Fade-in / Fade-out 10 ms`** ở hai đầu mỗi phân đoạn nhằm triệt tiêu hoàn toàn tiếng lách tách (*click sound*) khi ghép nối, sau đó chuẩn hóa biên độ đỉnh về mức `0.9` (~ `-1 dBFS`).
  - *Bảng 4.4 – Kiến trúc điều phối lai 4 giải pháp TTS & Cơ chế dự phòng 2 cấp (`tts_engine.py`, Trang 15–16):*
    - **Matcha-TTS:** Tự huấn luyện (`Acoustic 150k + Vocoder 50k`) $\rightarrow$ Lựa chọn cốt lõi cho môi trường cục bộ, 100% không cần Internet.
    - **VITS MMS (`facebook/mms-tts-vie`):** Mô hình mã nguồn mở của Meta (Pratap và cộng sự, 2023) $\rightarrow$ Làm hệ thống chuẩn đối sánh (Baseline) cục bộ.
    - **Microsoft Edge-TTS (`vi-VN-HoaiMyNeural` / `NamMinhNeural`):** Mạng nơ-ron đám mây quy mô lớn (Azure Cloud, tích hợp cơ chế tự động thử lại `MAX_RETRIES = 3` và `nest_asyncio`) $\rightarrow$ Lựa chọn ưu tiên khi có mạng để đạt chất âm biểu cảm cao nhất.
    - **Google TTS (`gTTS`):** Dịch vụ đám mây dự phòng tiêu chuẩn $\rightarrow$ Kênh dự phòng an toàn cuối cùng.
    - **Fallback 2 cấp độ:** Cấp 1 tại *Vocoder* (tự động tải và chuyển sang `hifigan_universal.pt` nếu thiếu `matcha_vi_hifigan.pt`); Cấp 2 tại *Engine* (tự động định tuyến sang engine dự phòng khi lỗi phần cứng hoặc mất mạng).

- **Slide 29 [TTS – Chương 5]: Dữ liệu Phòng thu InfoRe1 & Quy trình Hai Giai đoạn Huấn luyện Chuyên sâu**
  - **Nguồn dữ liệu & Tiền xử lý tín hiệu (Mục 5.1, Trang 17):**
    - Bộ dữ liệu tiếng Việt chuẩn phòng thu **InfoRe1** (InfoRe Technology, 2020): **~25 giờ** thu âm của một nữ phát thanh viên miền Bắc.
    - Tiền xử lý âm thanh: Chuẩn hóa về **22,05 kHz mono**; cắt lặng đầu cuối; chuẩn hóa cường độ âm lượng RMS về **`-20 dBFS`**; trích xuất phổ **Mel-spectrogram 80 kênh** (`FFT size = 1024`, `hop size = 256 mẫu`, dải tần `0 – 8.000 Hz`).
    - Phân chia tập dữ liệu nghiêm ngặt: Các mẫu từ chỉ số **`14.800` trở đi** được tách riêng làm **tập kiểm thử độc lập (Test set)** hoàn toàn không tham gia tối ưu trọng số; `100 câu` làm tập Validation và phần còn lại dùng cho huấn luyện.
  - *Bảng 5.1 – Thiết lập tham số kỹ thuật cho 2 giai đoạn huấn luyện chuyên sâu (Trang 17–18):*
    - **Giai đoạn 1 – Mô hình âm học (Acoustic Model `Matcha-TTS`):**
      - Kiến trúc: `Text Encoder + Duration Predictor + CFM Decoder`
      - Trọng số khởi tạo: Học chuyển giao (Transfer Learning) từ checkpoint tiền huấn luyện tiếng Anh.
      - Thời lượng: **`150.000 bước` (tương đương `327 epochs`)**.
      - Tối ưu hóa & Ổn định: `Adam (lr = 10⁻⁴)`, cắt chuẩn đạo hàm `gradient norm = 5.0`, trung bình động hàm mũ trọng số **`EMA = 0,9999`**.
    - **Giai đoạn 2 – Bộ tái tạo sóng âm (`HiFi-GAN Vocoder`):**
      - Kiến trúc: `Generator + Đa bộ phân biệt chu kỳ/đa tỷ lệ (MPD, MSD)`.
      - Trọng số khởi tạo: `Checkpoint HiFi-GAN Universal đa ngôn ngữ`.
      - Thời lượng & Dữ liệu: Đóng băng Matcha-TTS, tinh chỉnh đối kháng (Adversarial Training) với `AdamW (lr = 10⁻⁴)` suốt **`50.000 bước`** trên **`4.000 mẫu ghép giữa phổ Mel nhân tạo (do chính Matcha-TTS sinh ra) và sóng âm thật`** $\rightarrow$ Giúp HiFi-GAN học cách bù trừ sai lệch cấu trúc họa âm, **triệt tiêu hoàn toàn tiếng rè kim loại** (Mục 5.2.1).
  - **Tiêu chí chọn điểm dừng bằng ASR `PhoWhisper` & Chiến lược Checkpoint Resume (Mục 5.2.2 & 5.3, Trang 18):**
    - Vì hàm loss CFM giảm sâu từ sớm nhưng chất âm vẫn tiếp tục cải thiện, nhóm không dừng sớm theo loss mà dùng mô hình ASR **`PhoWhisper` (VinAI Research, 2023)** chấm **CER thực tế** trên tập kiểm thử qua từng snapshot để chọn ra checkpoint xuất sắc nhất tại bước **150.000**.
    - Xây dựng cơ chế **Checkpoint Resume** lưu định kỳ toàn bộ `(model weights, EMA weights, optimizer state, scheduler)` để tự động nối tiếp phiên huấn luyện liền mạch vượt qua giới hạn 12 giờ/phiên của GPU đám mây.

- **Slide 30 [TTS – Mục 6.1, 6.2, 6.3 & `evaluator.py`]: Phương pháp Đo lường Âm học & Kết quả Thực nghiệm Định lượng (CPU 8 Luồng)**
  - **Hệ thống 5 chỉ số đánh giá định lượng chuẩn quốc tế trong `evaluator.py` (Trang 19):**
    1. **MCD (Mel-Cepstral Distortion – dB $\downarrow$):** Trích xuất 24 hệ số MFCC (bỏ $c_0$ năng lượng, STFT cửa sổ Hann `1024/256`, 40 bộ lọc Mel trong dải chung `[0, 8000] Hz`, DCT-II), căn chỉnh thời gian động **DTW** với giọng thật:
       $$\text{MCD} = \frac{10\sqrt{2}}{\ln 10} \cdot \frac{1}{|P|} \sum_{(i, j) \in P} \left\| \mathbf{c}_{\text{ref}}(i) - \mathbf{c}_{\text{synth}}(j) \right\|_2$$
    2. **F0 RMSE (Hz $\downarrow$):** Ước lượng đường bao tần số cơ bản $F_0 \in [60, 400]\text{ Hz}$ bằng thuật toán mô hình Markov ẩn **pYIN** (Mauch & Dixon, 2014 – chống nhảy bát độ $\times 2, \times 1/2$), tính sai số căn bậc hai trung bình trên các khung hữu thanh đã căn chỉnh DTW.
    3. **log-F0 RMSE (Bán cung / Semitone $\downarrow$):** Chuyển $F_0$ sang thang bán cung $s = 12 \log_2(F_0)$ và trừ đi cao độ trung bình của từng câu ($s - \bar{s}$) trước khi tính RMSE $\rightarrow$ Đo **độ chuẩn xác thuần túy của đường cong thanh điệu tiếng Việt** mà không bị phụ thuộc vào độ trầm/bổng riêng của người nói!
    4. **CER (Character Error Rate – % $\downarrow$):** Đưa âm thanh tổng hợp qua mô hình ASR **`vinai/PhoWhisper-base`**, chuẩn hóa qua `clean_chars` và tính khoảng cách chỉnh sửa Levenshtein.
    5. **RTF (Real-Time Factor $\downarrow$):** $\text{RTF} = \frac{t_{\text{inference}}}{t_{\text{audio}}}$ đo trên **CPU 8 luồng** (`RTF < 1,0` là nhanh hơn thời gian thực).
  - *Bảng 6.1 & Biểu đồ 4 góc Hình 6.1 – Kết quả đánh giá định lượng trên tập kiểm thử độc lập (Môi trường CPU 8 luồng, Trang 19–20):*
    - **Giọng người thật (Tham chiếu chuẩn):** MCD: `NA` | F0 RMSE: `NA` | log-F0 RMSE: `NA` | **CER: `0,7%`** | RTF: `NA`
    - **`Matcha-TTS (Đề tài tự huấn luyện – 20 bước Euler)`:** **MCD: `3,05 dB` | F0 RMSE: `21,6 Hz` | log-F0 RMSE: `0,88 bán cung` | CER: `0,8%` | RTF (CPU): `0,64`** *(Tô nổi bật)*
    - **`Matcha-TTS (Đề tài tự huấn luyện – 10 bước Euler)`:** **MCD: `3,12 dB` | F0 RMSE: `22,1 Hz` | log-F0 RMSE: `0,91 bán cung` | CER: `0,85%` | RTF (CPU): `0,53`**
    - **VITS MMS (Meta – Cục bộ):** MCD: `4,40 dB` | F0 RMSE: `82,7 Hz` | log-F0 RMSE: `4,29 bán cung` | CER: `4,7%` | RTF (CPU): `0,29`.
  - **3 Điểm sáng kỹ thuật từ số liệu (Mục 6.3):**
    - Độ rõ phát âm **CER đạt `0,8%`**, tiệm cận sát mức sàn của chính giọng người thật (`0,7%`) và **giảm lỗi gần 6 lần** so với VITS MMS (`4,7%`).
    - Sai số thanh điệu **log-F0 RMSE chỉ `0,88 bán cung`** (tốt hơn **4,87 lần** so với `4,29 bán cung` của VITS MMS), chứng minh bộ từ điển tách thanh điệu độc lập 41 token học cao độ dấu thanh tiếng Việt cực kỳ chính xác.
    - Tốc độ thực thi trên CPU phổ thông đạt **`RTF = 0,53` (10 bước) và `0,64` (20 bước)** — mất chưa đầy 0,6 giây để sinh 1 giây âm thanh!

- **Slide 31 [TTS – Mục 6.3.2, 6.3.3, 6.4, Chương 7 & 8]: Phân tích Khách quan, Đối sánh Cục bộ vs Đám mây & Tổng kết TTS**
  - **Nhìn nhận khách quan khoa học (Mục 6.3.2 & 6.3.3, Trang 21):**
    - *Về chỉ số âm sắc (MCD & F0 RMSE):* Tập test tham chiếu thuộc cùng phát thanh viên nữ của tập `InfoRe1` mà Matcha-TTS học trực tiếp, trong khi `VITS MMS` dùng giọng nam khác; do đó `log-F0 RMSE` (đã khử trung bình giọng người nói) và `CER` là hai thước đo công bằng nhất chứng minh sự vượt trội của mô hình.
    - *Về hiện tượng ngữ điệu còn đều (Flat Prosody):* Do dữ liệu `InfoRe1` là giọng đọc tin tức báo chí ít luyến láy và quy mô mô hình gọn nhẹ (~20 triệu tham số để ưu tiên tốc độ CPU), cảm nhận tai người đối với câu dài vẫn mang tiết tấu đều nhịp hơn so với hội thoại đời thường.
  - *Bảng 6.2 – So sánh đối sánh đa tiêu chí giữa các mô hình Cục bộ (Offline) và Đám mây (Online Cloud) (Trang 21–22):*
    - So sánh đầy đủ 7 tiêu chí: **Chất lượng cảm quan (MOS)** [`Matcha-TTS`: Khá ~3,5–3,8/5,0 vs `VITS MMS`: Trung bình ~3,0/5,0 vs `Azure Edge-TTS`: Xuất sắc ~4,5–4,7/5,0] | **Quy mô kiến trúc** [`~20M` vs `~35M` vs `Hàng trăm triệu – hàng tỷ tham số`] | **Tập dữ liệu** [`~25h InfoRe1` vs `MMS đa ngữ` vs `Hàng chục nghìn giờ`] | **Yêu cầu mạng** [`100% Offline` vs `100% Offline` vs `Bắt buộc Internet liên tục`] | **Độ tin cậy hạ tầng** [`Kiểm soát tuyệt đối trên thiết bị` vs `Phụ thuộc bên thứ ba`] | **Bảo mật & Quyền riêng tư** [`Xử lý tại chỗ, an toàn tuyệt đối` vs `Phải gửi văn bản ra máy chủ ngoài`] | **Chi phí triển khai** [`Hoàn toàn miễn phí` vs `Tiềm ẩn chi phí API quy mô lớn`].
  - *Bảng 7.1 – Tổng hợp 6 khó khăn kỹ thuật thực tế & Giải pháp khắc phục của TTS (Trang 23)* cùng **Hạn chế & Định hướng phát triển (Chương 8, Trang 24):** Mở rộng ngữ liệu hội thoại giàu biểu cảm; tích hợp **Speaker Embedding** đa giọng đọc Bắc – Trung – Nam; lượng tử hóa trọng số **INT8 / ONNX Runtime** cho thiết bị biên và di động.

Hãy trình bày **xác nhận số liệu Lượt 3** và **thiết kế trực quan đầy đủ Slide 22 đến Slide 31** vào Artifact (kèm đầy đủ sơ đồ, công thức, biểu đồ Hình 3.1, 4.1, 4.2, 6.1, bảng biểu và Speaker Notes). Sau đó dừng lại chờ tôi xác nhận để sang Lượt 4 cuối cùng!
```

---

## LƯỢT 4: TÍCH HỢP FULL-STACK (FASTAPI + ANGULAR + DOCKER), KIỂM THỬ 113 TESTS, ĐÁNH GIÁ MỞ RỘNG & XUẤT BẢN TRỌN BỘ (SLIDE 32 – 37+)
*(Sau khi Claude hoàn thành Lượt 3, copy khung dưới đây gửi tiếp để hoàn thiện các slide cuối và xuất bản toàn bộ bộ slide)*

```markdown
Tôi xác nhận hoàn thành **Lượt 3 (Slide 22 – 31)**.
Bây giờ là **Lượt 4 (Bước hoàn thiện cuối cùng)**: Hãy thiết kế tiếp **Slide 32 đến Slide 37+** trình bày toàn diện phần **Kỹ nghệ Tích hợp Hệ thống Full-Stack (`scripts/api_server.py`), Giao diện Web Angular (`web-interface_Luong/`), Đóng gói Container Docker (`Dockerfile`, `docker-compose.yml`), Hệ thống 113 Bài Kiểm thử Tự động & Đánh giá Mở rộng Out-of-Dataset / Hard Multi-Turn (`STATUS.md`)**, sau đó **xuất bản toàn bộ bộ Slide hoàn chỉnh**!

### I. NỘI DUNG CHI TIẾT CHO CÁC SLIDE TÍCH HỢP, KIỂM THỬ & TỔNG KẾT (SLIDE 32 – 37+)

- **Slide 32 [Tích hợp Hệ thống – Backend FastAPI Hợp nhất (`scripts/api_server.py`)]:**
  - *Vẽ Sơ đồ Kiến trúc Tích hợp Dịch vụ Hợp nhất trên cổng `8000` (Docker cổng `8090`):*
    - Mount trực tiếp ứng dụng `stt_server.app` với các dịch vụ `TieredRetriever`, `MRCClient`, `DialogueManager`, `ConversationalIntentRouter`, `tts_synthesize` và phục vụ trực tiếp gói giao diện tĩnh Angular (`web-interface_Luong/dist/web-interface/browser`).
  - *Bảng Đặc tả Đầy đủ 7 REST API Endpoints & Cơ chế Tự động Dự phòng (Graceful Degradation):*
    1. `GET /api/health` $\rightarrow$ Trả `{status, retrieval, retrieval_passages, reader, dialogue, tts_engine, frontend_served}`.
    2. `POST /api/stt` $\rightarrow$ Nhận file audio multipart (`<= 25 MiB`), trả `{text}` qua `Faster-Whisper LoRA 50h CT2 INT8`.
    3. `POST /api/ask` $\rightarrow$ **Route hội thoại chính cho Web UI:** Nhận `{question, session_id?, passage?}`, điều phối qua `DialogueManager` $\rightarrow$ Trả `{answer, kind, intent, session_id, resolved_question, passage, parts}`.
    4. `POST /api/ask/reset` $\rightarrow$ Xóa lịch sử phiên hội thoại theo `session_id`.
    5. `POST /api/retrieve` $\rightarrow$ Route kiểm thử độc lập khâu truy xuất (`ConversationalIntentRouter` + `retriever.search` + `rerank_hits` ưu tiên khớp cụm 2-gram, 3-gram, 4-gram liên tục).
    6. `POST /api/answer` $\rightarrow$ Route kiểm thử độc lập khâu đọc hiểu (`reader.answer_question` + `polish_answer` chuẩn hóa hoa/thường và dấu câu).
    7. `POST /api/tts` $\rightarrow$ Nhận `{text, engine?, voice?, rate?}`, tổng hợp file `.wav`/`.mp3` và tự động xóa file tạm sau khi truyền xong qua `BackgroundTask`.
  - **Cơ chế Tự phát hiện Tài nguyên & Chịu lỗi (`get_qa_services`):** Tự động dò tìm kho tri thức (`kb_index.json` + `kb_wiki_full` $\rightarrow$ `vimmrc_index.json` $\rightarrow$ lùi về `seed_kb.json` 75 đoạn) và mô hình đọc hiểu (`vit5-combined-cont` $\rightarrow$ `vit5-combined` $\rightarrow$ lùi về `LexicalBaselineClient` / `HeuristicReader`), đảm bảo server luôn khởi chạy thành công 100% trong mọi môi trường.

- **Slide 33 [Giao diện Người dùng – Ứng dụng Web Angular SPA (`web-interface_Luong/`)]:**
  - *Sơ đồ Bố cục Giao diện & Luồng Trạng thái Thời gian thực (`app.component.ts`):*
    - Phát triển trên nền tảng **Angular 19/22** sử dụng cơ chế quản lý trạng thái phản ứng **Angular Signals (`signal`, `computed`)**.
    - **4 Phân khu chức năng (`AppView`):**
      1. **Màn hình Trò chuyện Giọng nói & Văn bản (`chat`):** Thu âm trực tiếp qua `AudioRecorderService` (Web Audio API 16 kHz WAV) tích hợp bộ phát hiện khoảng lặng tự động dừng ghi âm khi người dùng ngắt lời (`utils/silence-detector.ts`), khung nhập câu hỏi hoặc dán đoạn văn tùy chọn (`passageInput`), hiển thị đoạn văn bằng chứng trích xuất kèm điểm số và trình phát âm thanh tự động.
      2. **Thanh Trạng thái Pipeline 5 Chặng Trực quan (`flowSteps`):** Hiển thị tiến trình thời gian thực qua 5 bước: `Ghi âm đầu vào (Audio 16kHz)` $\rightarrow$ `Nhận dạng giọng nói (Whisper-small LoRA CT2)` $\rightarrow$ `Truy xuất tri thức (BM25 + Dense e5 + BGE Reranker)` $\rightarrow$ `Đọc hiểu suy luận (ViT5-base)` $\rightarrow$ `Tổng hợp giọng nói (Matcha-TTS + HiFi-GAN)`.
      3. **Thư viện Bài đọc Mẫu (`library`):** Phân loại theo các chủ đề (*Văn học, Lịch sử, Công nghệ, Môi trường*), cho phép chọn nhanh bài đọc để hỏi đáp trực tiếp trên văn bản đó.
      4. **Lịch sử Phiên học & Báo cáo Thống kê (`history` & `report`):** Thống kê tổng số câu hỏi, số câu trả lời thành công, tỷ lệ tương tác bằng giọng nói và số lượng tài liệu đã tham khảo.

- **Slide 34 [Đóng gói Triển khai – Kiến trúc Docker Multi-Stage & Tối ưu Hóa Vận hành CPU]:**
  - *Sơ đồ Kiến trúc `Dockerfile` 2 Tầng (Multi-Stage Build) & `docker-compose.yml`:*
    - **Stage 1 (`frontend-builder` – `node:22-alpine`):** Cài đặt dependencies và biên dịch ứng dụng Angular thành gói tài nguyên tĩnh tối ưu (`/app/dist/web-interface/browser`).
    - **Stage 2 (`runtime` – `python:3.11-slim`):**
      - Cài đặt các gói hệ thống xử lý âm thanh (`ffmpeg`, `libsndfile1`, `curl`, `git`).
      - Cài đặt PyTorch bản **CPU wheel siêu nhẹ** (`--extra-index-url https://download.pytorch.org/whl/cpu`), nạp sẵn vào image bộ mã hóa `intfloat/multilingual-e5-small` và bộ xếp hạng `BAAI/bge-reranker-v2-m3`.
      - Chạy script `setup_matcha.py` và kiểm tra sự tồn tại của cặp trọng số `matcha_vi.pt` + `matcha_vi_hifigan.pt`.
      - Cấu hình `HEALTHCHECK` tự động kiểm tra `http://localhost:8000/api/health` mỗi 30 giây.
  - *Bảng cấu hình biến môi trường chiến lược trong `docker-compose.yml`:*
    - Ánh xạ cổng `8090:8000`, gắn volume `./data:/app/data:ro`.
    - `OMP_NUM_THREADS=4`: Khắc phục triệt để hiện tượng tranh chấp luồng CPU (*thread oversubscription*) của PyTorch trên máy nhiều nhân.
    - `DIALOGUE_MIN_SUPPORT=0.34`: Ngưỡng kiểm chứng từ khóa chống trả lời bịa đặt (*hallucination*).
    - `KB_RERANKER=BAAI/bge-reranker-v2-m3`: Cho phép bật/tắt linh hoạt giữa chế độ ưu tiên độ chính xác (~12s/câu) và chế độ phản hồi nhanh (~6s/câu).

- **Slide 35 [Đảm bảo Chất lượng – 124+ Bài Kiểm thử Tự động & Bộ Chuẩn Đánh giá Mở rộng (`STATUS.md`)]:**
  - **Hệ thống Kiểm thử Tự động Toàn diện (`pytest -q`: 124+ Automated Tests – 100% Passed):**
    - Bao phủ toàn bộ các tầng: `speech-to-text_Luong/tests/test_stt.py` (10 tests), `retrieval-model_Huy/test_retrieval.py`, `mrc-model_Huy/tests/`, `text-to-speech_Duy/tests/` (kiểm tra đồng bộ `vi_tokenizer.py` với notebook, kiểm tra `normalizer.py` & `test_normalizer_extra.py`, kiểm tra các engine), `dialogue-manager_Huy/tests/` (`test_dialogue.py`, `test_llm_assist.py` kèm chốt chặn chất lượng hồi quy `dev >= 95%`, `held-out >= 90%`), `tests/test_intent_router.py` (8 tests), `tests/test_out_of_dataset.py` (5 tests), `tests/test_web_ui.py` (5 tests), `tests/test_silence_detector.py`, `tests/test_api_import.py` và `tests/test_api_server.py`.
  - *Bảng Kết quả Đánh giá Bộ chuẩn Mở rộng 110 Câu hỏi Ngoài Tập dữ liệu (`reports/out_of_dataset_evaluation.json`, Zero Data Leakage 0% trùng lặp):*
    - **Hội thoại giao tiếp (25 câu):** Hoàn thiện `100,0%` | Độ trễ TB `0,1 ms` (*"Bạn là ai vậy?"*)
    - **Lịch sử Việt Nam (20 câu):** Hoàn thiện `100,0%` | Độ trễ TB `996,9 ms` (*"Quang Trung đại phá quân Thanh vào năm nào?"* $\rightarrow$ *"Năm Kỷ Dậu 1789."*)
    - **Địa lý Việt Nam (20 câu):** Hoàn thiện `100,0%` | Độ trễ TB `734,6 ms` (*"Đảo nào có diện tích lớn nhất Việt Nam?"* $\rightarrow$ *"Đảo Phú Quốc."*)
    - **Văn học & Văn hóa (15 câu):** Hoàn thiện `100,0%` | Độ trễ TB `730,3 ms` (*"Ai là tác giả Truyện Kiều?"* $\rightarrow$ *"Nguyễn Du."*)
    - **Khoa học & Đời sống (15 câu):** Hoàn thiện `100,0%` | Độ trễ TB `787,2 ms` (*"Nước sôi ở nhiệt độ bao nhiêu?"* $\rightarrow$ *"100 độ C."*)
    - **Công nghệ & AI (15 câu):** Hoàn thiện `100,0%` | Độ trễ TB `525,6 ms` (*"AI là viết tắt của thuật ngữ gì?"* $\rightarrow$ *"Artificial Intelligence."*)
    - **Tổng cộng 110 câu + 35 câu hỏi khó suy luận đa chặng (`hard_and_multiturn_suite.json`) + 4 kịch bản hội thoại dài 30 lượt:** Đạt **100% tỷ lệ hoàn thiện câu trả lời chuẩn ngữ pháp và dấu câu** phục vụ tổng hợp giọng nói TTS.

- **Slide 36 [Kịch bản Demo Thực tế Toàn Chuỗi (End-to-End Live Walkthrough)]:**
  - *Sơ đồ minh họa trực quan 2 tình huống chạy thực tế trên hệ thống:*
    - **Tình huống 1 – Hỏi đáp Kiến thức & Nối tiếp Đa lượt bằng Giọng nói:**
      - *Lượt 1 (Người dùng nói):* `"Ừm cho mình hỏi là chiến dịch đại phá quân Thanh năm 1789 do ai chỉ huy vậy bạn?"`
      - *Xử lý:* STT chép lời $\rightarrow$ `clean_utterance` lọc bỏ `"Ừm cho mình hỏi là ... vậy bạn"` $\rightarrow$ `TieredRetriever` + `BGE Reranker` truy xuất bài đọc lịch sử Quang Trung $\rightarrow$ `ViT5` sinh đáp án $\rightarrow$ `compose_answer` soạn thành câu hoàn chỉnh $\rightarrow$ `Normalizer` chuyển `"1789"` thành chữ $\rightarrow$ `Matcha-TTS + HiFi-GAN` phát giọng nói tự nhiên.
      - *Lượt 2 (Hỏi nối tiếp):* `"Ông ấy lên ngôi Hoàng đế tại đâu trước khi xuất quân?"` $\rightarrow$ `DialogueManager` dùng `session_id` thay `"Ông ấy"` bằng `"Quang Trung - Nguyễn Huệ"` và trả lời chính xác `"tại Núi Bân (Phú Xuân - Huế)"`.
    - **Tình huống 2 – Câu hỏi Ngoài Kho Tri thức (Kiểm chứng Chống Bịa đặt / Anti-Hallucination):**
      - Khi câu hỏi chứa tên riêng hoặc khái niệm không có trong kho (`support < 0,34`), hệ thống chủ động từ chối lịch sự bằng giọng nói thay vì sinh câu trả lời sai sự thật.

- **Slide 37 [Tổng kết Toàn Dự án, Bảng Đối chiếu Thành tựu 3 Phân hệ & Định hướng Phát triển]:**
  - *Bảng Tổng hợp Thành tựu Định lượng Toàn diện của Đề tài ViMMRC Voice Q&A:*
    - **Phân hệ 1 – STT (`speech-to-text_Luong` – Huỳnh Công Lương):** Fine-tune `openai/whisper-small` bằng LoRA (`1,77M` tham số trainable = `0,73%`) trên 50 giờ VietSpeech $\rightarrow$ **Test WER giảm từ `36,76%` xuống `13,77%` (-62,56% tương đối), CER giảm từ `19,43%` xuống `6,67%`**; xuất bản CTranslate2 INT8 (`241,48 MiB`) chạy CPU.
    - **Phân hệ 2 – Retrieval 2 Tầng (`retrieval-model_Huy` – Ngô Trí Huy):** BM25 tự cài đặt bằng chỉ mục đảo nhanh gấp `2,74 lần`, tối ưu tham số nâng **Recall@1 trên Dev từ `71,45%` lên `77,48%`**; kết hợp kho chọn lọc `5.879 đoạn` + Wikipedia `1,48 triệu đoạn` (`bm25s` + `multilingual-e5-small` float16 mmap) + Reranker `bge-reranker-v2-m3 (+0,25 KB)` nâng **F1 câu hỏi trong kho lên `60,7%` và kiến thức mở lên `24,3%`**.
    - **Phân hệ 3 – Đọc hiểu MRC & Hội thoại (`mrc-model_Huy` & `dialogue-manager_Huy` – Ngô Trí Huy):** Hợp nhất `27.164 câu hỏi` (ViMMRC 2.0 + UIT-ViQuAD2.0) chia theo đoạn văn; tinh chỉnh `VietAI/vit5-base` 2 giai đoạn đạt **Test EM `41,05%`, Token F1 `66,55%`, Toàn chuỗi F1 `53,9%`**; Tầng hội thoại đạt **`81,9%` (held-out lần đầu)** và **`97,2%` (sau sửa lỗi)**.
    - **Phân hệ 4 – TTS (`text-to-speech_Duy` – Trương Hoàng Duy):** Huấn luyện `Matcha-TTS` (OT-CFM 10–20 bước Euler) `150.000 bước` + tinh chỉnh `HiFi-GAN Vocoder` `50.000 bước` trên phổ Mel nhân tạo; bộ từ điển tách thanh điệu độc lập **`41 token (-58,2%)`** và MAS Numba JIT giúp đạt **MCD `3,05 dB`, log-F0 RMSE `0,88 bán cung`, CER `0,8%` (sát giọng thật `0,7%`, tốt gấp 6 lần VITS MMS `4,7%`), RTF `0,53–0,64` trên CPU 8 luồng**.
    - **Kỹ nghệ Hệ thống & Kiểm thử (Cả nhóm):** Tích hợp Full-Stack FastAPI + Angular SPA (tự dừng ghi âm theo khoảng lặng) + Docker Multi-Stage (`OMP_NUM_THREADS=4`), vượt qua **124+ bài kiểm thử tự động (100% Passed)**.

---

### II. YÊU CẦU XUẤT BẢN BỘ SLIDE HOÀN CHỈNH
Hãy hoàn thiện **Slide 32 đến Slide 37+** và cung cấp cho tôi:
1. **Bản trình chiếu Interactive HTML/CSS/SVG Slide Deck hoàn chỉnh** (chứa đầy đủ toàn bộ các slide từ Slide 1 đến Slide 37+ với phím chuyển trang `←`/`→`, mục lục nhảy nhanh tới từng slide, nút bật/tắt Speaker Notes, nút Fullscreen và CSS `@media print` chuẩn 16:9 để xuất ra PDF chất lượng cao).
2. *(Nếu bạn có công cụ chạy mã Python)* Hãy viết và thực thi script `python-pptx` để xuất toàn bộ các slide này thành file PowerPoint `.pptx` có thể tải về trực tiếp.
```
