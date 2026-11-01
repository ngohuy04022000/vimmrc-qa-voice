# TÀI LIỆU KỊCH BẢN THUYẾT TRÌNH 5 - 10 PHÚT (BÁO CÁO NHANH CHO GIẢNG VIÊN & HỘI ĐỒNG)
## ĐỀ TÀI: HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0 (ViMMRC VOICE Q&A)

* **Môn học:** Học máy tiên tiến và ứng dụng (Chương trình Cao học Công nghệ Thông tin)  
* **Thời lượng:** Khung 5 - 10 phút (Thời lượng lý tưởng: ~7 - 8 phút | Tổng số chữ: ~1.050 từ | Nhịp độ nói: 125 - 140 từ/phút)  
* **Người thuyết trình đại diện:** Ngô Trí Huy (Nhóm trưởng)  
* **Mục tiêu báo cáo:** Tóm lược súc tích, làm nổi bật ngay tính mới, kiến trúc 4 chặng, các đóng góp kỹ thuật cốt lõi (Retrieval hai tầng, MRC ViT5 sinh tự do, TTS Matcha-TTS Flow Matching), bảng đối sánh thực nghiệm định lượng và sản phẩm Full-stack chạy thực tế trong Docker.

---

### PHÂN BỔ THỜI LƯỢNG 6 SLIDE (TỔNG: 8:00 | KHUNG 5 - 10 PHÚT)

* **Slide 1 (0:00 - 1:15 | 75s):** Giới thiệu Đề tài, Hội đồng, Thành viên & Đặt vấn đề
* **Slide 2 (1:15 - 2:45 | 90s):** Mục tiêu Nghiên cứu & Kiến trúc Pipeline 4 Chặng End-to-End
* **Slide 3 (2:45 - 4:15 | 90s):** Ba Đóng góp Kỹ thuật Nổi bật (Retrieval hai tầng, MRC sinh tự do, TTS Flow Matching)
* **Slide 4 (4:15 - 5:45 | 90s):** Kết quả Thực nghiệm & Benchmark Định lượng Then chốt Toàn Hệ thống
* **Slide 5 (5:45 - 7:00 | 75s):** Sản phẩm Hoàn chỉnh Full-Stack, Đóng gói Docker & Minh họa Live Demo
* **Slide 6 (7:00 - 8:00 | 60s):** Tổng kết Giá trị Đạt được, Khả năng Ứng dụng & Hướng Phát triển

---

## NỘI DUNG VÀ KỊCH BẢN CHI TIẾT TỪNG SLIDE (6 SLIDES)

### SLIDE 1: GIỚI THIỆU ĐỀ TÀI & ĐẶT VẤN ĐỀ
* **Thời lượng dự kiến:** 1 phút 15 giây (0:00 - 1:15)
* **Người trình bày:** Ngô Trí Huy (Nhóm trưởng đại diện báo cáo)
* **Nội dung hiển thị trên Slide:**
  * **Tên đề tài:** HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0 (ViMMRC Voice Q&A System)
  * **Học viên thực hiện:**
    * **Ngô Trí Huy** (Lead): Phân hệ Truy xuất BM25 + Dense + Reranker, Mô hình Đọc hiểu ViT5 sinh câu trả lời tự do, Tích hợp backend & kho tri thức.
    * **Huỳnh Công Lương**: Phân hệ Nhận dạng Giọng nói (Whisper-small LoRA 50h, CTranslate2 INT8, VAD), Giao diện Web Angular 22 SPA, Đóng gói Docker.
    * **Trương Hoàng Duy**: Phân hệ Tổng hợp Tiếng nói (Matcha-TTS Flow Matching OT-CFM, Vocoder HiFi-GAN), Frontend tách thanh điệu `vi_tone_v2`, Benchmark âm học.
  * **Vấn đề cốt lõi:**
    * Các hệ thống Đọc hiểu máy (MRC) hiện nay hầu hết bị bó hẹp ở dạng văn bản gõ phím (text-only).
    * Hạn chế lớn trong môi trường rảnh tay (lái xe, trợ lý gia đình) hoặc hỗ trợ người khiếm thị.
  * **Mục tiêu nghiên cứu:**
    * Chuyển đổi bài toán MRC thành chu trình khép kín: **Hỏi bằng giọng nói $\rightarrow$ Tìm kiếm ngữ cảnh $\rightarrow$ Đọc hiểu suy luận $\rightarrow$ Trả lời bằng giọng nói tự nhiên**.
    * Hoạt động hoàn toàn cục bộ (100% Offline) trên CPU thông thường, bảo mật dữ liệu riêng tư, không phụ thuộc API đám mây trả phí.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô trong Hội đồng! Hôm nay, em xin đại diện nhóm báo cáo kết quả thực hiện đồ án môn Học máy tiên tiến và ứng dụng: **'Hệ thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0'**.  
  > Nhóm gồm 3 thành viên: em Ngô Trí Huy, nhóm trưởng, phụ trách Phân hệ Truy xuất ngữ cảnh và Mô hình Đọc hiểu MRC; bạn Huỳnh Công Lương phụ trách Nhận dạng giọng nói STT, Giao diện Web và Docker; bạn Trương Hoàng Duy phụ trách Tổng hợp tiếng nói TTS và Đánh giá âm học.  
  > Động lực lớn nhất của đề tài xuất phát từ việc: phần lớn các hệ thống đọc hiểu hiện nay chỉ tương tác qua văn bản gõ phím, rất hạn chế trong các tình huống rảnh tay như đang lái xe hay hỗ trợ người khiếm thị. Mục tiêu của nhóm là xây dựng một chu trình hoàn chỉnh khép kín: người dùng hỏi trực tiếp bằng giọng nói, hệ thống tự động tìm kiếm ngữ cảnh, đọc hiểu suy luận và phát âm thanh câu trả lời tự nhiên ngay trên máy tính thông thường."

---

### SLIDE 2: MỤC TIÊU & KIẾN TRÚC PIPELINE 4 CHẶNG END-TO-END
* **Thời lượng dự kiến:** 1 phút 30 giây (1:15 - 2:45)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Sơ đồ luồng dữ liệu 4 Chặng (End-to-End Pipeline):**
    $$\text{Micro (Audio 16kHz)} \xrightarrow{\text{STT}} \text{Văn bản câu hỏi} \xrightarrow{\text{Retrieval}} \text{Đoạn văn liên quan} \xrightarrow{\text{MRC}} \text{Đáp án tự do} \xrightarrow{\text{TTS}} \text{Loa (Audio 22.05kHz)}$$
  * **4 Phân hệ phối hợp chặt chẽ:**
    1. **Chặng 1: STT:** Whisper-small fine-tune LoRA 50h VietSpeech $\rightarrow$ CTranslate2 INT8 (WER 13,77% / CER 6,67% trên 1.802 mẫu test VietSpeech) + Bộ lọc VAD cắt khoảng lặng + Lazy Loading.
    2. **Chặng 2: Retrieval:** Kho tri thức hai tầng (5.869 đoạn ViMMRC & ViQuAD + 1,48 triệu đoạn Wikipedia tiếng Việt); kết hợp BM25 + dense (`multilingual-e5-small`) và `bge-reranker-v2-m3` (+0,25 tầng 1).
    3. **Chặng 3: MRC:** ViT5-base Seq2Seq sinh câu trả lời tự do từ ngữ cảnh và câu hỏi, không cần phương án trắc nghiệm sẵn (EM 41.05%, token F1 66.55% trên 2.716 câu test).
    4. **Chặng 4: TTS:** Matcha-TTS (Optimal-Transport Conditional Flow Matching) 10 bước ODE trên CPU + frontend `vi_tone_v2` + Vocoder HiFi-GAN (RTF 0.52, CER 0.85%).
  * **Cơ chế Chịu lỗi Đa tầng (Fail-Safe Pipeline):** Tự nạp mô hình Lazy Loading; Fallback MRC trích câu khi checkpoint chưa tải; Fallback TTS ưu tiên Matcha $\rightarrow$ VITS $\rightarrow$ Edge-TTS $\rightarrow$ gTTS.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để hiện thực hóa mục tiêu trên, nhóm đã thiết kế kiến trúc pipeline 4 chặng đồng bộ:  
  > Chặng 1, STT: Nhận âm thanh từ micro người dùng, mô hình Whisper-small fine-tune LoRA 50h VietSpeech chuyển thành văn bản, chạy trên engine CTranslate2 INT8 với bộ lọc VAD cắt khoảng lặng, đạt WER 13,77% so với 36,76% của bản gốc.  
  > Chặng 2, Retrieval: Quét trên kho tri thức hai tầng gồm 5.869 đoạn văn ViMMRC và ViQuAD kết hợp 1,48 triệu đoạn Wikipedia tiếng Việt bằng BM25 và dense, sau đó reranker bge-reranker-v2-m3 chấm lại để chọn đoạn văn chính xác nhất.  
  > Chặng 3, MRC: Mô hình ViT5-base đọc ngữ cảnh và sinh câu trả lời tự do ngắn gọn, không cần các phương án trắc nghiệm sẵn.  
  > Chặng 4, TTS: Mô hình Matcha-TTS dựa trên Conditional Flow Matching tổng hợp câu trả lời thành giọng đọc truyền cảm qua loa.  
  > Hệ thống có cơ chế dự phòng tự động ở từng chặng, chạy cục bộ 100% trên CPU thông thường với độ trễ đo thực tế khoảng 12 giây mỗi câu, và khoảng 6 giây khi tắt reranker."

---

### SLIDE 3: BA ĐÓNG GÓP KỸ THUẬT NỔI BẬT
* **Thời lượng dự kiến:** 1 phút 30 giây (2:45 - 4:15)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Đóng góp 1 - Retrieval: BM25 Tinh chỉnh + Kho Tri thức Hai Tầng + Reranker:**
    * Tinh chỉnh thực nghiệm: $k_1 = 2.1, b = 1.0$ tối ưu cho văn bản tiếng Việt.
    * Bổ sung cơ chế **Bigram Phrase Boost (+0.4)** ưu tiên cụm từ ghép, giúp tăng +7,27% Recall@1.
    * Mở rộng kho tri thức hai tầng: 5.869 đoạn chuyên biệt + 1,48 triệu đoạn Wikipedia tiếng Việt; reranker giúp F1 câu hỏi mở tăng từ 15,4% lên 24,3%.
  * **Đóng góp 2 - MRC: ViT5-base Sinh Câu Trả Lời Tự Do (Loại Bỏ Hoàn Toàn Trắc Nghiệm):**
    * Gộp 2 bộ dữ liệu chuẩn: ViMMRC 2.0 (5.273 câu) + UIT-ViQuAD2.0 (21.891 câu) = **27.164 câu hỏi**.
    * Phân chia zero-leakage theo cấp độ bài đọc (Train 21.733 / Dev 2.715 / Test 2.716).
    * ViT5 sinh câu trả lời tự do chính xác, ngắn gọn, đạt EM 41,05% và token F1 66,55% trên tập test.
  * **Đóng góp 3 - TTS: Matcha-TTS Flow Matching & Frontend Tách Thanh Điệu `vi_tone_v2`:**
    * Ứng dụng giải thuật Optimal-Transport Conditional Flow Matching (OT-CFM) giải ODE chỉ 10 bước trên CPU, đạt RTF 0,52 (nhanh gấp đôi thời gian thực).
    * Đề xuất frontend `vi_tone_v2` bóc tách thanh điệu (0–5) khỏi nguyên âm, giải quyết triệt để lỗi dấu hỏi/ngã/nặng.
    * Tối ưu thuật toán căn chỉnh MAS bằng Numba JIT và tinh chỉnh Vocoder HiFi-GAN 50.000 bước.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Đề tài đạt được 3 đóng góp kỹ thuật trọng tâm:  
  > Thứ nhất, ở phân hệ Truy xuất, nhóm tinh chỉnh siêu tham số BM25 đạt k1=2.1, b=1.0 và đề xuất cơ chế Bigram Phrase Boost cộng điểm cho cụm từ ghép tiếng Việt, giúp tăng Recall@1 thêm 7,27%. Đồng thời nhóm xây dựng kho tri thức hai tầng kết hợp Wikipedia tiếng Việt và cơ chế reranking tăng F1 câu hỏi kiến thức mở từ 15,4% lên 24,3%.  
  > Thứ hai, ở phân hệ Đọc hiểu, nhóm chuyển đổi toàn diện từ bài toán trắc nghiệm sang hỏi đáp tự do, kết hợp bộ dữ liệu ViMMRC 2.0 và UIT-ViQuAD2.0 với 27.164 câu, phân tách nghiêm ngặt zero-leakage theo bài đọc. ViT5-base sinh câu trả lời tự nhiên, đạt F1 66,55% và EM 41,05% trên tập test.  
  > Thứ ba, ở phân hệ TTS, nhóm ứng dụng thành công kỹ thuật Flow Matching tiên tiến với frontend vi_tone_v2 tách dấu thanh độc lập và tối ưu thuật toán căn chỉnh MAS bằng Numba JIT, giúp mô hình phát âm chuẩn xác cả 6 thanh điệu tiếng Việt."

---

### SLIDE 4: KẾT QUẢ THỰC NGHIỆM & BENCHMARK THEN CHỐT
* **Thời lượng dự kiến:** 1 phút 30 giây (4:15 - 5:45)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Bảng kết quả định lượng tổng hợp đối sánh các phân hệ & baseline:**

| Phân hệ / Mô hình | Chỉ số then chốt | Giá trị đạt được | Đối sánh Baseline | Ý nghĩa thực tiễn & Bối cảnh |
| :--- | :--- | :--- | :--- | :--- |
| **Retrieval (BM25 hai tầng)** | Recall@1 / Recall@5 | **71.1% / 85.9%** | Kho đơn tầng (không wiki) | Tìm đúng đoạn văn ngay ở top 1 và top 5 (Test 2.545 câu) |
| **Pipeline cuối (dense + rerank)** | Answer F1: kho / mở | **60.7% / 24.3%** | BM25 thuần: 58.0% / 15.4% | Reranker cải thiện rõ rệt câu kiến thức mở (+8.9% F1) |
| **STT (Whisper LoRA 50h)** | WER / CER (VietSpeech) | **13.77% / 6.67%** | Whisper gốc: 36.76% / 19.43% | Giảm 62.6% WER tương đối; CTranslate2 nhanh gấp 4.1x CPU |
| **MRC (ViT5-base Seq2Seq)** | Exact Match / Token F1 | **41.05% / 66.55%** | Extractive Baseline: ~21.5% / ~43.2% | Sinh câu trả lời tự do ngắn gọn, đúng trọng tâm (Test 2.716 câu) |
| **TTS (Matcha-TTS Flow Matching)** | Lỗi ký tự (CER qua ASR) | **0.85%** (1.9% PhoWhisper) | VITS: 4.7% (Người thật: 0.7%) | Phát âm rõ chữ, tiệm cận mức trần giọng người thật |
| **TTS (Matcha cao độ log-F0)** | Sai số cao độ (log-F0) | **0.91 bán cung** (22.1 Hz) | VITS: 4.29 bán cung / Edge: 2.69 | Thanh điệu chuẩn xác, tự nhiên tiệm cận dịch vụ thương mại |
| **Tốc độ (Matcha CPU)** | Real-Time Factor (RTF) | **0.52 - 0.53** | Ngưỡng thời gian thực: < 1.0 | Nhanh gấp đôi thời gian thực trên CPU Intel Core i5/i7 |
| **Độ trễ toàn trình (Docker CPU)** | Voice-to-Voice Latency | **~12 giây** (tắt rerank: ~6s) | Mục tiêu CPU: hoàn toàn offline | STT ~3s, RAG+Rerank ~6s, ViT5 ~1.4s, TTS ~1.3s |
| **Kiểm thử tự động (Quality)** | Automated Test Suite | **54/54 tests passed** (100%) | Không có kiểm thử tự động | Bao phủ toàn diện REST API, VAD, Normalizer, Fallback |

* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô, các kết quả thực nghiệm trên bảng là minh chứng định lượng cho hiệu quả của hệ thống:  
  > Ở phân hệ STT, fine-tune LoRA 50 giờ giúp giảm hơn 22,9 điểm WER trên tập test VietSpeech 1.802 mẫu, đưa WER xuống 13,77% và CER xuống 6,67%; lượng hóa INT8 giúp tăng tốc 4,1 lần trên CPU.  
  > Ở phân hệ Retrieval, trên 2.545 câu test với kho tri thức hai tầng, BM25 đạt Recall@1 71,1% và Recall@5 85,9%.  
  > Ở phân hệ MRC, mô hình ViT5 đạt Exact Match 41,05% và token F1 66,55% trên 2.716 câu test độc lập.  
  > Ở phân hệ TTS, Matcha-TTS 10 bước đạt CER chỉ 0,85%, sai số cao độ log-F0 chỉ 0,91 bán cung, vượt trội hoàn toàn so với VITS MMS có CER 4,7% và log-F0 4,29 bán cung. Tốc độ RTF đạt 0,52 trên CPU, tức là nhanh gấp đôi thời gian thực."

---

### SLIDE 5: SẢN PHẨM HOÀN CHỈNH & LIVE DEMO
* **Thời lượng dự kiến:** 1 phút 15 giây (5:45 - 7:00)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Kiến trúc Sản phẩm Full-Stack sẵn sàng triển khai:**
    * **Giao diện Web SPA (Angular 22):** Thiết kế hiện đại, responsive, có biểu đồ Pipeline Flow Status theo dõi tiến trình thời gian thực (Micro $\rightarrow$ STT $\rightarrow$ RAG $\rightarrow$ MRC $\rightarrow$ TTS $\rightarrow$ Loa).
    * **Backend API (FastAPI RESTful):** Kiến trúc module hóa cao, hỗ trợ Lazy Loading nạp mô hình vào RAM theo luồng an toàn (Thread-Safe Lock).
    * **Đóng gói Docker Multi-Stage:** Stage 1 (`node:22-alpine`) biên dịch Angular assets; Stage 2 (`python:3.11-slim`) triển khai PyTorch CPU, tối ưu kích thước image.
    * **Tự động hóa & Kiểm chuẩn:** Khởi chạy một lệnh bằng Docker Compose; vượt qua toàn diện **54/54 ca kiểm thử tự động**.
  * **Kịch bản Live Demo: *"Ai là tác giả của Truyện Kiều?"*:**
    * **1. Thu âm Micro:** Người dùng bấm giữ mic, nói tự nhiên. Web Audio API thu âm chuẩn PCM 16kHz.
    * **2. Nhận dạng STT (~3s):** Whisper LoRA 50h lọc nhiễu VAD, giải mã thành văn bản câu hỏi tiếng Việt có dấu.
    * **3. Truy xuất RAG (~6s):** BM25 + dense quét kho hai tầng; `bge-reranker-v2-m3` chọn chính xác đoạn Wikipedia "Truyện Kiều".
    * **4. Đọc hiểu MRC (~1.4s):** ViT5-base đọc hiểu ngữ cảnh và câu hỏi, sinh câu trả lời tự do: *"Nguyễn Du"*.
    * **5. Tổng hợp TTS (~1.3s):** Text Normalizer chuẩn hóa và Matcha-TTS tổng hợp âm thanh giọng nói truyền cảm, trình duyệt tự động phát loa.
    * **$\rightarrow$ Tổng thời gian xử lý:** **~12 giây** trên Docker CPU thông thường (~6 giây khi tắt reranker).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Về mặt kỹ nghệ phần mềm, nhóm đã tích hợp hoàn chỉnh hệ thống thành một ứng dụng Full-stack hoàn chỉnh: Backend FastAPI mô-đun hóa với cơ chế thread-safe lazy loading kết hợp Frontend Angular hiển thị trực quan luồng dữ liệu đang chạy qua 4 chặng. Toàn bộ giải pháp được đóng gói tự động hóa 100% bằng Docker multi-stage container và vượt qua toàn bộ 54 trên 54 ca kiểm thử tự động.  
  > Trong kịch bản demo thực tế: khi người dùng bấm micro hỏi 'Ai là tác giả của Truyện Kiều?', phân hệ STT nhận dạng câu hỏi trong khoảng 3 giây; bộ truy xuất lấy ứng viên và reranker chọn chính xác đoạn Wikipedia về tác phẩm; ViT5 suy luận và sinh đáp án 'Nguyễn Du'; cuối cùng Matcha-TTS phát âm thanh câu trả lời ra loa chỉ sau 1,3 giây. Toàn bộ chu trình mất khoảng 12 giây trên Docker CPU và khoảng 6 giây khi tắt reranker."

---

### SLIDE 6: TỔNG KẾT & HƯỚNG PHÁT TRIỂN
* **Thời lượng dự kiến:** 1 phút 00 giây (7:00 - 8:00)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Các giá trị khoa học & thực tiễn đạt được:**
    * **Hệ thống Voice Q&A Tiếng Việt Khép kín:** Xây dựng trọn vẹn chu trình đa phương thức từ âm thanh micro đến câu trả lời giọng nói qua loa, chạy offline 100% trên CPU phổ thông.
    * **Làm chủ Công nghệ Tạo sinh SOTA:** Làm chủ thành công mô hình Flow Matching (Matcha-TTS) kết hợp frontend tách thanh điệu `vi_tone_v2` giải quyết triệt để vấn đề dấu thanh tiếng Việt.
    * **Mở rộng Đọc hiểu Tự do:** Chuyển đổi bài toán trắc nghiệm hạn chế sang hỏi đáp tự do open-domain trên kho tri thức hai tầng với 1,48 triệu đoạn văn Wikipedia.
    * **Kỹ nghệ Phần mềm Chuẩn mực:** Kiến trúc micro-services module hóa, API rõ ràng, kiểm thử tự động 54/54 test cases đạt, đóng gói Docker triển khai một lệnh.
  * **Định hướng phát triển trong tương lai:**
    * **Tăng tốc phần cứng GPU:** Triển khai trên GPU máy chủ (TensorRT / ONNX) để rút ngắn độ trễ toàn trình xuống dưới 2 giây.
    * **Tối ưu hóa Reranker câu hỏi mở:** Tiếp tục fine-tune `bge-reranker-v2-m3` trên dữ liệu tiếng Việt thực tế để phân biệt tốt hơn giữa câu hỏi trong kho và kiến thức mở bách khoa.
    * **Tích hợp Mô hình Ngôn ngữ Lớn (LLM):** Thử nghiệm kết hợp các mô hình LLM tiếng Việt (Vistral, PhoGPT, Qwen2.5-Vi) để tổng hợp câu trả lời phong phú và hỗ trợ hội thoại đa lượt.
    * **Mở rộng ứng dụng thực tiễn:** Ứng dụng vào hệ thống tra cứu thủ tục hành chính công, cổng thông tin đào tạo trường đại học và trợ lý ảo hỗ trợ người khiếm thị.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Tóm lại, đồ án của nhóm đã hiện thực hóa thành công một hệ thống Voice Q&A tiếng Việt hoàn chỉnh, khép kín chu trình đa phương thức từ âm thanh đến ngữ nghĩa rồi trở lại âm thanh. Hệ thống chạy hoàn toàn cục bộ trên CPU máy tính thông thường, bảo đảm quyền riêng tư và làm chủ các công nghệ học máy tiên tiến từ Flow Matching đến Transformer.  
  > Trong định hướng phát triển tiếp theo, nhóm sẽ triển khai trên GPU để rút ngắn độ trễ toàn trình xuống dưới 2 giây, tiếp tục tinh chỉnh bộ reranker cho các câu hỏi mở phức tạp, và thử nghiệm tích hợp các mô hình ngôn ngữ lớn (LLMs tiếng Việt) để hỗ trợ hội thoại đàm thoại đa lượt.  
  > Nhóm chúng em xin chân thành cảm ơn sự hướng dẫn tận tình của Thầy Cô! Rất mong nhận được những góp ý quý báu từ Hội đồng để nhóm tiếp tục hoàn thiện đề tài."
