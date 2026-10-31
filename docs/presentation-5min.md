# TÀI LIỆU KỊCH BẢN THUYẾT TRÌNH 5 PHÚT (BÁO CÁO NHANH CHO GIẢNG VIÊN)
## ĐỀ TÀI: HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0 (ViMMRC VOICE Q&A)
**Môn học:** Học máy tiên tiến và ứng dụng  
**Thời lượng:** 5 phút (khoảng 600 - 700 từ nói, nhịp độ 120 - 130 từ/phút)  
**Mục tiêu:** Báo cáo tóm lược, súc tích, làm nổi bật ngay: Vấn đề giải quyết, Kiến trúc 4 chặng, Các đóng góp kỹ thuật cốt lõi, Kết quả thực nghiệm định lượng và Demo thực tế.

---

### PHÂN CÔNG & THỜI LƯỢNG TỪNG SLIDE (TỔNG: 5 PHÚT)
* **Slide 1 (0:00 - 0:45):** Giới thiệu Đề tài, Thành viên & Đặt vấn đề
* **Slide 2 (0:45 - 1:45):** Mục tiêu & Kiến trúc Hệ thống 4 Chặng End-to-End
* **Slide 3 (1:45 - 2:45):** Ba Đóng góp Kỹ thuật Nổi bật (Retrieval, MRC, TTS)
* **Slide 4 (2:45 - 3:45):** Kết quả Đo lường & Benchmark Định lượng Then chốt
* **Slide 5 (3:45 - 4:30):** Sản phẩm Hoàn chỉnh, Đóng gói Docker & Minh họa Live Demo
* **Slide 6 (4:30 - 5:00):** Tổng kết, Khả năng Ứng dụng & Hướng Phát triển

---

## NỘI DUNG VÀ KỊCH BẢN CHI TIẾT TỪNG SLIDE

### SLIDE 1: GIỚI THIỆU ĐỀ TÀI & ĐẶT VẤN ĐỀ
* **Thời lượng:** 45 giây (0:00 - 0:45)
* **Người trình bày:** Ngô Trí Huy (Nhóm trưởng)
* **Nội dung hiển thị trên Slide:**
  * **Tên đề tài:** Hệ Thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0 (ViMMRC Voice Q&A System)
  * **Học viên thực hiện:**
    * **Ngô Trí Huy** (Lead): Retrieval BM25 + dense + reranker, Mô hình đọc hiểu ViT5 sinh câu trả lời, Tích hợp backend & kho tri thức.
    * **Huỳnh Công Lương**: Nhận dạng giọng nói (Whisper-small LoRA 50h, CTranslate2), Giao diện Web Angular 22, Docker.
    * **Trương Hoàng Duy**: Tổng hợp giọng nói (Matcha-TTS Flow Matching & VITS), Benchmark âm học.
  * **Vấn đề cốt lõi:**
    * Các hệ thống Đọc hiểu máy (MRC) hiện nay hầu hết bị bó hẹp ở dạng văn bản gõ phím (text-only).
    * Mục tiêu của nhóm là chuyển đổi bài toán MRC thành chu trình **Hỏi bằng giọng nói $\rightarrow$ Trả lời bằng giọng nói** tự nhiên, chạy cục bộ (riêng tư) trên CPU; đo thực tế ~12 giây/câu trên Docker CPU (~6 giây khi tắt reranker).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy, nhóm em báo cáo đồ án môn Học máy tiên tiến và ứng dụng: **Hệ thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0**.  
  > Nhóm có 3 thành viên: em Ngô Trí Huy phụ trách Truy xuất và Đọc hiểu; Huỳnh Công Lương phụ trách Nhận dạng giọng nói, Web và Docker; Trương Hoàng Duy phụ trách Tổng hợp giọng nói.  
  > Động lực: các hệ thống đọc hiểu hiện nay chủ yếu chỉ gõ chữ, bất tiện khi rảnh tay hoặc cho người khiếm thị. Nhóm xây dựng chu trình khép kín: hỏi bằng giọng nói, hệ thống tự tìm văn bản, suy luận và trả lời bằng giọng nói."

---

### SLIDE 2: MỤC TIÊU & KIẾN TRÚC PIPELINE 4 CHẶNG
* **Thời lượng:** 60 giây (0:45 - 1:45)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Sơ đồ luồng dữ liệu 4 Chặng (End-to-End Pipeline):**
    $$\text{Micro (Audio 16kHz)} \xrightarrow{\text{STT}} \text{Văn bản câu hỏi} \xrightarrow{\text{Retrieval}} \text{Bài đọc liên quan} \xrightarrow{\text{MRC}} \text{Đáp án} \xrightarrow{\text{TTS}} \text{Loa (Audio 22kHz)}$$
  * **4 Phân hệ phối hợp:**
    1. **STT:** Whisper-small fine-tune LoRA 50h VietSpeech → CTranslate2 int8 (WER 13,77% / CER 6,67% trên 1.802 mẫu test VietSpeech; Whisper small gốc 36,76% / 19,43%) + Bộ lọc VAD + Thread-safe Lazy Loading.
    2. **Retrieval:** BM25 + dense (multilingual-e5-small) lấy tối đa 9 ứng viên trên kho tri thức hai tầng (5.869 đoạn ViMMRC + ViQuAD và 1,48 triệu đoạn Wikipedia tiếng Việt), reranker bge-reranker-v2-m3 chọn đoạn tốt nhất (đoạn tầng 1 cộng +0,25).
    3. **MRC:** ViT5-base fine-tune sinh câu trả lời tự do từ câu hỏi và bài đọc.
    4. **TTS:** Matcha-TTS (Flow Matching) + VITS + Edge-TTS dự phòng.
  * **Thiết kế chịu lỗi (Fault-Tolerant):** Hệ thống có cơ chế Fallback tự động ở từng chặng, chạy cục bộ trên CPU thông thường mà không cần GPU (Edge-TTS/gTTS dự phòng cần Internet).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kiến trúc gồm 4 chặng:  
  > Chặng 1, STT: Whisper-small fine-tune LoRA 50h VietSpeech, chuyển sang CTranslate2 int8 để chạy nhanh trên CPU, đạt WER 13,77% so với 36,76% của bản gốc chưa fine-tune.  
  > Chặng 2, Retrieval: BM25 và dense cùng lấy tối đa 9 ứng viên từ kho hai tầng - 5.869 đoạn ViMMRC và ViQuAD, cộng 1,48 triệu đoạn Wikipedia tiếng Việt - rồi reranker bge-reranker-v2-m3 chấm lại và chọn đoạn tốt nhất, ưu tiên nhẹ cho đoạn trong kho tầng 1.  
  > Chặng 3, MRC: mô hình ViT5 suy luận và sinh câu trả lời tự do từ bài đọc và câu hỏi, không cần phương án lựa chọn sẵn.  
  > Chặng 4, TTS: Matcha-TTS tổng hợp giọng nói tự nhiên từ câu trả lời.  
  > Mỗi chặng đều có cơ chế dự phòng tự động: ViT5 chưa nạp xong thì dùng bộ trích câu dự phòng, Matcha-TTS lỗi thì chuyển sang VITS hoặc Edge-TTS."

---

### SLIDE 3: BA ĐÓNG GÓP KỸ THUẬT NỔI BẬT
* **Thời lượng:** 60 giây (1:45 - 2:45)
* **Người trình bày:** Ngô Trí Huy / Trương Hoàng Duy
* **Nội dung hiển thị trên Slide:**
  * **Đóng góp 1 - Retrieval BM25 Tối ưu hóa:**
    * Tinh chỉnh tham số thực nghiệm: $k_1 = 2.1$, $b = 1.0$.
    * Bổ sung cơ chế **Bigram Phrase Boost (+0.4)** ưu tiên từ ghép tiếng Việt, giúp tìm chính xác bài đọc chỉ với 1 câu hỏi ngắn.
  * **Đóng góp 2 - Đọc hiểu sinh câu trả lời tự do (ViT5):**
    * Người dùng chỉ cần đặt câu hỏi bằng lời tự nhiên.
    * Fine-tune ViT5-base trên 27.164 câu (train 21.733) gộp ViMMRC 2.0 + UIT-ViQuAD2.0, chia theo bài đọc (21.733 / 2.715 / 2.716).
    * Kết quả test: EM 41,05%, token F1 66,55%; trả lời ngắn gọn ("Hà Nội", "82 tấm bia").
  * **Đóng góp 3 - Làm chủ Kiến trúc Matcha-TTS (Flow Matching):**
    * Ứng dụng thành công **Optimal-Transport Conditional Flow Matching (OT-CFM)** từ ICASSP 2024.
    * Đề xuất **Frontend tách thanh điệu `vi_tone_v2`**: Tách 6 thanh điệu thành token độc lập (ví dụ `hồ` $\rightarrow$ `h ô 2`), giúp mô hình nắm bắt cao độ F0 cực kỳ ổn định.
* **Kịch bản thuyết trình (Speaker Script):**
  > "3 đóng góp kỹ thuật trọng tâm:  
  > Một, ở khâu truy xuất, thay vì dùng BM25 mặc định, nhóm tinh chỉnh siêu tham số $k_1=2.1, b=1.0$ và đề xuất Bigram Phrase Boost cộng điểm cho cụm từ ghép tiếng Việt, giúp tìm đúng bài đọc chỉ với một câu hỏi ngắn.  
  > Hai, ở phân hệ Đọc hiểu, hệ thống trả lời câu hỏi tự do. Nhóm fine-tune ViT5-base trên 27.164 câu gộp từ ViMMRC 2.0 và UIT-ViQuAD2.0, đạt F1 66,55% và Exact Match 41,05% trên tập test, trả lời gọn như 'Hà Nội' thay vì trích nguyên cả câu.  
  > Ba, nhóm làm chủ và huấn luyện thành công kiến trúc Matcha-TTS theo trường phái Flow Matching, với frontend `vi_tone_v2` tự thiết kế để tách 6 thanh điệu tiếng Việt thành token độc lập, giúp mô hình nắm bắt cao độ và ngữ điệu tự nhiên hơn."

---

### SLIDE 4: KẾT QUẢ THỰC NGHIỆM & BENCHMARK THEN CHỐT
* **Thời lượng:** 60 giây (2:45 - 3:45)
* **Người trình bày:** Trương Hoàng Duy / Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Bảng kết quả định lượng tổng hợp trên tập Test/Dev:**

| Phân hệ / Mô hình | Chỉ số then chốt | Giá trị đạt được | So sánh Baseline | Ý nghĩa thực tiễn |
|---|---|:---:|:---:|---|
| **Retrieval (BM25 hai tầng, trước khi thêm reranker)** | Recall@1 / Recall@5 (test 2.545 câu) | **71.1% / 85.9%** | — | Tìm đúng đoạn văn ngay ở top 1 và top 5 |
| **Pipeline cuối (reranker + ưu tiên kho +0,25)** | Answer F1: 200 câu có trong kho / 200 câu kiến thức mở | **60.7 / 24.3** | BM25 thuần: 58.0 / 15.4 | Reranker cải thiện rõ ở câu kiến thức mở (mức cộng chọn trên chính các câu này, hơi lạc quan) |
| **Retrieval (BM25; ablation cũ, chỉ kho ViMMRC 552 đoạn)** | Recall@1 (dev 564 câu) | **71.45%** | Lucene DF: 64.2% | Ablation tinh chỉnh k1, b, bigram boost |
| **Toàn chuỗi BM25 → ViT5 (pipeline BM25)** | EM / F1 (test 2.545 câu) | **32.3% / 53.9%** | Đưa đúng đoạn văn: F1 68.6% | Độ chính xác khi tự tìm rồi đọc |
| **MRC (ViT5 fine-tune)** | EM / token F1 (Test 2.716 câu) | **41.05% / 66.55%** | Trích câu khớp nhất (chưa đo) | Trả lời ngắn gọn, đúng trọng tâm |
| **TTS (Matcha-TTS)** | Tỷ lệ lỗi chữ (CER) | **1.9%** | VITS: 4.3% (Người thật: 0.7%) | Phát âm rõ chữ, ít lỗi hơn VITS gấp 2 lần |
| **TTS (Matcha-TTS)** | Sai số cao độ (log-F0) | **2.86 semitones** | VITS: 4.31 / Edge-TTS: 2.69 | Thanh điệu chuẩn xác, gần bằng mô hình thương mại |
| **Tốc độ (Matcha CPU)**| Real-Time Factor (RTF)| **0.52** | Yêu cầu thời gian thực: < 1.0 | Nhanh gấp 2 lần thời gian thực trên CPU i5/i7 |

* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy, kết quả định lượng trên bảng là minh chứng cho hiệu quả của hệ thống:  
  > Ở phân hệ Retrieval, trên 2.545 câu test với kho tri thức hai tầng, BM25 đạt Recall@1 71,1% và Recall@5 85,9%. Với pipeline cuối có reranker và dense, F1 câu trả lời trên câu kiến thức mở tăng từ 15,4 lên 24,3, và trên câu có đoạn trong kho từ 58,0 lên 60,7.  
  > Ở phân hệ MRC, ViT5 fine-tune đạt token F1 66,55% và Exact Match 41,05% trên 2.716 câu test.  
  > Đặc biệt ở phân hệ TTS, Matcha-TTS đạt tỷ lệ lỗi ký tự CER chỉ 1,9%, gần mức trần giọng người thật 0,7% và tốt hơn VITS hơn 2 lần. Sai số cao độ log-F0 đạt 2,86 bán cung, tiệm cận mô hình thương mại Edge-TTS. Chỉ số RTF đạt 0,52, nghĩa là TTS nhanh gấp đôi thời gian thực."

---

### SLIDE 5: SẢN PHẨM HOÀN CHỈNH & KỊCH BẢN DEMO
* **Thời lượng:** 45 giây (3:45 - 4:30)
* **Người trình bày:** Huỳnh Công Lương
* **Nội dung hiển thị trên Slide:**
  * **Sản phẩm hoàn thiện:**
    * **Web UI (Angular 22):** Giao diện Chat trực quan, hiển thị tiến trình pipeline (Thu âm $\rightarrow$ STT $\rightarrow$ Retrieval $\rightarrow$ MRC $\rightarrow$ TTS $\rightarrow$ Nghe audio).
    * **Backend (FastAPI):** Kiến trúc RESTful modules hóa, hỗ trợ Lazy Loading.
    * **Đóng gói Docker:** Multi-stage build (`node:22-alpine` + `python:3.11-slim`), cô lập cổng 8090, 54/54 test cases ĐẠT 100%.
  * **Minh họa luồng Demo thực tế (End-to-End Test):**
    * Người dùng hỏi: *"Ai là tác giả của Truyện Kiều?"*.
    * Retrieval lấy ứng viên từ BM25 + dense, reranker chọn đoạn Wikipedia "Truyện Kiều" (~6 giây; tổng khoảng 12 giây/câu trên CPU Docker).
    * ViT5 sinh câu trả lời: *"Nguyễn Du"*.
    * Matcha-TTS đọc câu trả lời bằng giọng nơ-ron.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Sản phẩm là ứng dụng Full-stack: FastAPI và Angular, giao diện Chat hiển thị luồng pipeline đang chạy. Đóng gói Docker một lệnh, 54/54 bài kiểm thử tự động đạt.  
  > Demo: người dùng hỏi 'Ai là tác giả của Truyện Kiều?', hệ thống truy xuất và dùng reranker chọn đoạn Wikipedia về Truyện Kiều, ViT5 sinh câu trả lời 'Nguyễn Du', Matcha-TTS đọc câu trả lời."

---

### SLIDE 6: TỔNG KẾT & HƯỚNG PHÁT TRIỂN
* **Thời lượng:** 30 giây (4:30 - 5:00)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Các giá trị đạt được:**
    * Xây dựng trọn vẹn hệ thống Voice Q&A tiếng Việt mã nguồn mở, hoạt động cục bộ trên CPU.
    * Khép kín chu trình đa phương thức (Âm thanh - Văn bản - Ngữ nghĩa - Âm thanh).
    * Huấn luyện thành công mô hình Flow Matching (Matcha-TTS) với cơ chế tách thanh điệu tiếng Việt.
  * **Hướng nâng cấp tiếp theo:**
    * Chạy GPU để giảm độ trễ.
    * Tinh chỉnh reranker và định tuyến cho câu hỏi kiến thức chung.
    * Thử LLM tiếng Việt (như PhoGPT / Vistral) để sinh câu trả lời.
  * **Lời cảm ơn & Xin ý kiến nhận xét của Thầy.**
* **Kịch bản thuyết trình (Speaker Script):**
  > "Tóm lại, nhóm đã xây dựng hoàn chỉnh hệ thống Voice Q&A tiếng Việt, chạy cục bộ trên CPU, làm chủ các kỹ thuật từ Flow Matching đến MRC.  
  > Hướng tiếp theo: chạy GPU giảm độ trễ, tinh chỉnh reranker cho câu hỏi kiến thức chung, và thử LLM tiếng Việt.  
  > Nhóm xin cảm ơn Thầy và mong nhận góp ý để hoàn thiện đồ án."
