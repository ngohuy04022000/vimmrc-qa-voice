# TÀI LIỆU THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN / SEMINAR
## ĐỀ TÀI: HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0 (ViMMRC VOICE Q&A)
**Môn học:** Học máy tiên tiến và ứng dụng  
**Nhóm thực hiện:**
1. **Ngô Trí Huy** (Nhóm trưởng): Phân hệ Truy xuất Ngữ cảnh (Retrieval), Mô hình Đọc hiểu (MRC - ViT5), Thiết kế Kiến trúc & Tích hợp.
2. **Huỳnh Công Lương**: Phân hệ Nhận dạng Giọng nói (Speech-to-Text - Faster-Whisper), Phát triển Giao diện Web Client (Angular 19/22).
3. **Trương Hoàng Duy**: Phân hệ Tổng hợp Tiếng nói (Text-to-Speech - Matcha-TTS Flow Matching & VITS), Chuẩn hóa Văn bản & Benchmark Đánh giá Âm học.

---

### MỤC LỤC KHUNG THUYẾT TRÌNH (12 SLIDE / 15 - 20 PHÚT)

* **Slide 1:** Giới thiệu Đề tài, Thành viên & Đặt vấn đề
* **Slide 2:** Mục tiêu Nghiên cứu & Phạm vi Ứng dụng
* **Slide 3:** Phân tích Bộ Dữ liệu ViMMRC 2.0 & Nhiệm vụ Đọc hiểu
* **Slide 4:** Kiến trúc Tổng thể Pipeline 4 Chặng (End-to-End Pipeline)
* **Slide 5:** Phân hệ 1: Nhận dạng Tiếng nói (Speech-to-Text - Whisper)
* **Slide 6:** Phân hệ 2: Truy xuất Ngữ cảnh Đoạn văn (BM25 Retrieval)
* **Slide 7:** Phân hệ 3: Mô hình Đọc hiểu Máy (MRC - ViT5)
* **Slide 8:** Phân hệ 4: Tổng hợp Tiếng nói Tiên tiến (Matcha-TTS Flow Matching)
* **Slide 9:** Kết quả Đánh giá & Benchmark Định lượng Phân hệ TTS
* **Slide 10:** Tích hợp Hệ thống, Giao diện Web & Đóng gói Docker Container
* **Slide 11:** Kịch bản Demo Hệ thống Thực tế (Live Demonstration)
* **Slide 12:** Tổng kết Đóng góp, Giới hạn & Hướng Phát triển Tương lai

---

### NỘI DUNG VÀ KỊCH BẢN CHI TIẾT TỪNG SLIDE

#### SLIDE 1: GIỚI THIỆU ĐỀ TÀI & NHÓM THỰC HIỆN
* **Thời lượng dự kiến:** 1.5 phút
* **Người trình bày:** Ngô Trí Huy (Nhóm trưởng)
* **Nội dung hiển thị trên Slide:**
  * **Tên đề tài:** Hệ Thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0 (ViMMRC Voice Q&A System)
  * **Môn học:** Học máy tiên tiến và ứng dụng
  * **Giảng viên hướng dẫn:** [Tên Giảng viên / Bộ môn]
  * **Thành viên & Phân công:**
    * Ngô Trí Huy: Retrieval BM25, MRC (ViT5), Backend Integration.
    * Huỳnh Công Lương: Speech-to-Text (Faster-Whisper), Angular Web Interface.
    * Trương Hoàng Duy: Text-to-Speech (Matcha-TTS, VITS Baseline, Audio Evaluation).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy/Cô và các bạn đồng môn! Hôm nay, nhóm chúng em xin đại diện báo cáo kết quả thực hiện đồ án môn học 'Học máy tiên tiến và ứng dụng' với đề tài: **'Xây dựng Hệ thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0'**.  
  > Nhóm gồm có ba thành viên: Em là Ngô Trí Huy, phụ trách phân hệ Truy xuất Ngữ cảnh và Mô hình Đọc hiểu; bạn Huỳnh Công Lương phụ trách phân hệ Nhận dạng Giọng nói và Giao diện Web; và bạn Trương Hoàng Duy phụ trách phân hệ Tổng hợp Giọng nói và Đánh giá âm học. Sau đây, em xin phép bắt đầu phần trình bày tổng quan về đề tài."

---

#### SLIDE 2: ĐẶT VẤN ĐỀ & MỤC TIÊU NGHIÊN CỨU
* **Thời lượng dự kiến:** 1.5 phút
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Bối cảnh & Hạn chế:**
    * Các hệ thống Machine Reading Comprehension (MRC) truyền thống chủ yếu tương tác dạng văn bản (text-only).
    * Giới hạn khả năng tiếp cận trong các tình huống rảnh tay (hands-free): lái xe, hỗ trợ người khiếm thị, thiết bị thông minh (Smart Speaker / Kiosk).
  * **Mục tiêu đề tài:**
    * Mở rộng bài toán đọc hiểu văn bản tiếng Việt thành một chu trình khép kín bằng giọng nói tự nhiên.
    * Xây dựng pipeline tích hợp hoàn chỉnh: **Âm thanh câu hỏi $\rightarrow$ Nhận dạng chữ $\rightarrow$ Tìm kiếm tài liệu $\rightarrow$ Suy luận đáp án $\rightarrow$ Phát giọng nói trả lời**.
    * Đảm bảo hệ thống hoạt động ổn định, độ trễ thấp, có khả năng chạy offline/cục bộ và đóng gói triển khai sẵn sàng.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Thưa Thầy/Cô, trong kỷ nguyên số hóa, bài toán Đọc hiểu máy (MRC) đã đạt được nhiều bước tiến lớn. Tuy nhiên, phần lớn các hệ thống hiện nay vẫn dừng lại ở dạng nhập/xuất văn bản thuần túy. Điều này tạo ra rào cản lớn đối với người dùng trong các ngữ cảnh rảnh tay như đang di chuyển, lái xe, hoặc với người cao tuổi và người khiếm thị.  
  > Xuất phát từ thực tiễn đó, mục tiêu của nhóm chúng em là xây dựng một hệ thống Voice Q&A tiếng Việt toàn diện: cho phép người dùng hỏi trực tiếp bằng giọng nói, hệ thống tự động tìm kiếm đoạn văn liên quan trong kho dữ liệu, suy luận đáp án chính xác và phản hồi lại bằng giọng nói nhân tạo mượt mà, tự nhiên."

---

#### SLIDE 3: BỘ DỮ LIỆU ViMMRC 2.0 & NHIỆM VỤ ĐỌC HIỂU
* **Thời lượng dự kiến:** 1.5 phút
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Dataset UIT-NLP/ViMMRC 2.0:**
    * Bộ dữ liệu đọc hiểu chuẩn tiếng Việt dành cho học sinh tiểu học đến THCS. ViMMRC gốc là trắc nghiệm; dự án chuyển sang dạng hỏi - đáp tự do và bổ sung thêm ViQuAD.
    * Cấu trúc sau chuyển đổi: Đoạn văn (Passage) + Câu hỏi (Question) + Câu trả lời dạng văn bản (Answer).
  * **Phân chia dữ liệu (Splits):**
    * Tập Train: 482 bài đọc (3.600 câu hỏi).
    * Tập Dev: 70 bài đọc (564 câu hỏi).
    * Tập Test: 147 bài đọc (1.109 câu hỏi).
    * Đảm bảo tính phân tách tuyệt đối (disjoint) ở cấp độ bài đọc, không rò rỉ dữ liệu (zero leakage).
  * **Đặc điểm & Thách thức:**
    * Ngữ cảnh dài (nhiều bài vượt quá 512 token).
    * Dữ liệu thô có đáp án rỗng, cần làm sạch và chuyển sang dạng câu trả lời văn bản.
    * Đòi hỏi giải pháp trả lời được câu hỏi tự do bằng cách sinh câu trả lời từ đoạn văn truy xuất.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Trọng tâm dữ liệu của đề tài là bộ dữ liệu ViMMRC 2.0 do UIT-NLP phát triển. Bộ dữ liệu gồm 699 bài đọc với hơn 5.200 câu hỏi, được chia thành 3 tập train, dev và test tách biệt hoàn toàn theo bài đọc.  
  > Thách thức lớn của ViMMRC nằm ở chỗ: các bài đọc có độ dài biến thiên, nhiều câu hỏi đòi hỏi suy luận từ nhiều câu khác nhau trong bài, và dữ liệu gốc có dạng trắc nghiệm. Nhóm đã chuyển ViMMRC sang dạng hỏi - đáp tự do gồm đoạn văn, câu hỏi và câu trả lời dạng văn bản, bổ sung thêm ViQuAD, đồng thời tiền xử lý nghiêm ngặt: chuẩn hóa mã hóa Unicode NFC và loại bỏ ký tự rỗng."

---

#### SLIDE 4: KIẾN TRÚC HỆ THỐNG TỔNG THỂ (PIPELINE 4 CHẶNG)
* **Thời lượng dự kiến:** 1.5 phút
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Sơ đồ luồng xử lý End-to-End:**
    $$\text{Micro (Audio)} \xrightarrow{\text{STT}} \text{Văn bản câu hỏi} \xrightarrow{\text{Retrieval}} \text{Đoạn văn liên quan} \xrightarrow{\text{MRC}} \text{Đáp án} \xrightarrow{\text{TTS}} \text{Loa (Audio)}$$
  * **4 Phân hệ nòng cốt:**
    1. **STT Module:** Faster-Whisper trích xuất câu hỏi từ audio 16kHz.
    2. **Retrieval Module:** Truy xuất hai tầng (5.869 đoạn văn ViMMRC + ViQuAD và 1,48 triệu chunk Wikipedia tiếng Việt) bằng BM25 + dense, reranker bge-reranker-v2-m3 chọn đoạn văn tốt nhất.
    3. **MRC Module:** ViT5 Transformer sinh câu trả lời tự do từ đoạn văn truy xuất (có Lexical Baseline dự phòng).
    4. **TTS Module:** Matcha-TTS (Conditional Flow Matching) & VITS (MMS) tổng hợp âm thanh giọng nói.
  * **Cơ chế dự phòng (Resilience Architecture):** Fallback tự động đa tầng đảm bảo hệ thống không bao giờ gặp lỗi gián đoạn.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Trên màn hình là sơ đồ kiến trúc tổng thể của hệ thống. Luồng dữ liệu vận hành tuần tự qua 4 chặng:  
  > Đầu tiên, tín hiệu giọng nói từ micro người dùng được gửi tới phân hệ STT để chuyển thành văn bản. Câu hỏi văn bản tiếp tục được đưa vào bộ truy xuất BM25 để tìm ra ngữ cảnh bài đọc liên quan nhất từ kho dữ liệu. Sau đó, mô hình MRC tiếp nhận cặp (câu hỏi, ngữ cảnh) để suy luận câu trả lời. Cuối cùng, câu trả lời dạng văn bản đi qua bộ tổng hợp TTS để tái tạo thành giọng nói tự nhiên phát qua loa.  
  > Toàn bộ pipeline được thiết kế với cơ chế Fallback tự động: nếu một engine hoặc kết nối gặp sự cố, hệ thống tự kích hoạt nhánh dự phòng mà không làm gián đoạn trải nghiệm người dùng."

---

#### SLIDE 5: PHÂN HỆ 1 - NHẬN DẠNG TIẾNG NÓI (SPEECH-TO-TEXT)
* **Thời lượng dự kiến:** 1.5 phút
* **Người trình bày:** Huỳnh Công Lương
* **Nội dung hiển thị trên Slide:**
  * **Công nghệ cốt lõi:**
    * **Faster-Whisper:** Triển khai OpenAI Whisper trên nền tảng CTranslate2, tăng tốc độ suy luận gấp 4 lần và giảm 50% bộ nhớ.
    * Kích thước mô hình: `small` (244M tham số), hỗ trợ tiếng Việt bản địa chính xác.
  * **Kỹ thuật tối ưu hóa:**
    * Bộ lọc phát hiện hoạt tính giọng nói (Voice Activity Detection - VAD) loại bỏ khoảng lặng và tạp âm môi trường.
    * Cơ chế **Thread-Safe Lazy Loading**: Trì hoãn việc nạp trọng số mô hình cho đến khi có request đầu tiên, giúp API server khởi động tức thì trong 0.5s.
  * **Xử lý Audio phía Client:**
    * Trình duyệt thu âm trực tiếp qua Web Audio API, mã hóa dạng sóng WAV Linear PCM 16kHz đơn kênh (Mono).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy/Cô, em là Huỳnh Công Lương, xin trình bày phân hệ Nhận dạng Tiếng nói (STT).  
  > Để nhận dạng câu hỏi người dùng, nhóm lựa chọn Faster-Whisper. Đây là kiến trúc tối ưu hóa sử dụng CTranslate2, mang lại tốc độ giải mã nhanh gấp 4 lần so với Whisper gốc của OpenAI. Chúng em tích hợp VAD filter để tự động cắt tỉa các đoạn im lặng và tạp âm nền.  
  > Đặc biệt, ở backend, em áp dụng cơ chế Lazy Loading đồng bộ theo luồng: server có thể khởi động ngay lập tức mà không bị đơ giao diện; mô hình chỉ nạp vào RAM ở lần gọi đầu tiên và tái sử dụng vĩnh viễn trong suốt phiên làm việc."

---

#### SLIDE 6: PHÂN HỆ 2 - TRUY XUẤT NGỮ CẢNH (PASSAGE RETRIEVAL)
* **Thời lượng dự kiến:** 1.5 phút
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Bài toán:** Trong kịch bản thực tế, người dùng chỉ đặt câu hỏi mà không cung cấp bài đọc. Hệ thống phải tự tìm bài đọc liên quan nhất trong toàn bộ kho tài liệu.
  * **Truy xuất lai BM25 + Dense + Reranker:**
    * **Kho tri thức hai tầng:** tầng 1 gồm **5.869 đoạn văn** từ ViMMRC + ViQuAD (BM25 $k_1 = 2.1$, $b = 1.0$, **Bigram Phrase Boost** +0,4); tầng 2 gồm **1,48 triệu chunk Wikipedia tiếng Việt** với cả chỉ mục BM25 (`bm25s` chia shard) và chỉ mục vector dense (`multilingual-e5-small`, 384 chiều, float16 mmap ~1,1 GB).
    * **Ứng viên:** top-3 BM25 tầng 1 + top-3 BM25 Wikipedia + top-3 dense Wikipedia (≤ 9 ứng viên).
    * **Reranker** `bge-reranker-v2-m3` (cross-encoder) chấm chung tất cả; đoạn tầng 1 được cộng +0,25, điểm cao nhất thắng.
  * **Kết quả đo lường:**
    * **BM25 hai tầng (trước khi thêm reranker), test 2.545 câu:** Recall@1 **71,1%** (ViQuAD 73,2%; ViMMRC 59,4%); Recall@5 **85,9%** (ViQuAD 88,9%; ViMMRC 69,2%).
    * **So sánh pipeline cuối (answer F1, 200 câu có trong kho / 200 câu kiến thức mở):** BM25 thuần 58,0 / 15,4; BM25 + dense Wikipedia 57,9 / 16,9; **reranker + ưu tiên kho +0,25 (đang dùng) 60,7 / 24,3**. Mức cộng được chọn trên chính các câu này nên hơi lạc quan.
    * **Tốc độ:** truy xuất + reranker ~6 giây / câu trên CPU Docker; có thể tắt reranker (`KB_RERANKER=`) để truy xuất còn ~0,1–1,7 giây với độ chính xác thấp hơn.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Tiếp theo là phân hệ Truy xuất Đoạn văn do em phụ trách. Khi người dùng hỏi một câu như 'Ai là tác giả của Truyện Kiều?', hệ thống phải tìm ra bài đọc tương ứng trong hàng trăm văn bản.  
  > Em xây dựng kho tri thức hai tầng: tầng một là 5.869 đoạn văn từ ViMMRC và ViQuAD dùng BM25 tinh chỉnh $k_1=2.1$, $b=1.0$ cùng Bigram Phrase Boost; tầng hai là 1,48 triệu chunk Wikipedia tiếng Việt, có cả chỉ mục BM25 và chỉ mục vector dense multilingual-e5-small. Với mỗi câu hỏi, hệ thống lấy top 3 từ mỗi nguồn, tối đa 9 ứng viên, rồi reranker bge-reranker-v2-m3 chấm chung; đoạn tầng một được cộng thêm 0,25 và đoạn điểm cao nhất thắng.  
  > Với BM25 hai tầng, trước khi thêm reranker, trên tập test 2.545 câu Recall@1 đạt 71,1% và Recall@5 đạt 85,9%. Ở pipeline cuối, F1 câu trả lời trên câu kiến thức mở tăng từ 15,4 lên 24,3 và trên câu có đoạn trong kho từ 58,0 lên 60,7, dù mức cộng 0,25 được chọn trên chính các câu này nên hơi lạc quan. Truy xuất cùng reranker mất khoảng 6 giây mỗi câu trên CPU."

---

#### SLIDE 7: PHÂN HỆ 3 - MÔ HÌNH ĐỌC HIỂU (MRC MODEL)
* **Thời lượng dự kiến:** 2 phút
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **ViT5 Sequence-to-Sequence (hỏi - đáp tự do):**
    * Kiến trúc Transformer T5 tiếng Việt (`vit5-combined-cont`), nhận `POST /api/answer {question, passage}` và trả về `{answer}`.
    * Kết quả trên tập test dữ liệu kết hợp: **EM 41,05**, **F1 66,55**. Kiểm thử end-to-end (truy xuất rồi đọc hiểu): **F1 53,9**; với gold passage: **F1 68,6**.
    * Cơ chế Context Chunking Heuristic (`context_selection.py`): giải quyết bài toán văn bản vượt giới hạn 512 token mà không làm mất thông tin bằng chứng.
    * Dự phòng: nếu chưa có checkpoint ViT5, Lexical Baseline trích xuất câu trả lời.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Ở phân hệ Đọc hiểu MRC, hệ thống tích hợp mô hình **ViT5** của VietAI để sinh câu trả lời tự do. Trên tập test dữ liệu kết hợp, mô hình đạt EM 41,05 và F1 66,55; khi chạy end-to-end từ truy xuất đến đọc hiểu, F1 là 53,9, còn với đoạn văn đúng thì F1 đạt 68,6. Nếu chưa có checkpoint ViT5, Lexical Baseline sẽ trích xuất câu trả lời thay thế.  
  > Em đã thiết kế module `context_selection` để chọn lọc các phân đoạn ngữ cảnh giàu thông tin nhất, đảm bảo mô hình không bị cắt cụt bằng chứng quan trọng khi văn bản dài vượt quá 512 token."

---

#### SLIDE 8: PHÂN HỆ 4 - TỔNG HỢP TIẾNG NÓI (TEXT-TO-SPEECH)
* **Thời lượng dự kiến:** 2 phút
* **Người trình bày:** Trương Hoàng Duy
* **Nội dung hiển thị trên Slide:**
  * **Mô hình chủ đạo: Matcha-TTS (ICASSP 2024):**
    * Dựa trên **Optimal-Transport Conditional Flow Matching (OT-CFM)**: giải phương trình vi phân vi mô (ODE) theo đường thẳng tối ưu từ nhiễu Gaussian tới Mel-spectrogram.
    * Giải mã nhanh vượt trội: Chỉ cần 10 bước Euler, đạt **RTF 0.52 trên CPU** (nhanh gấp 2 lần thời gian thực mà không cần GPU).
  * **Đóng góp kỹ thuật nổi bật:**
    * **Frontend tách thanh điệu (`vi_tone_v2`):** Tách 6 thanh điệu tiếng Việt (ngang, huyền, sắc, hỏi, ngã, nặng) thành token độc lập ở cuối âm tiết (ví dụ: `hồ` $\rightarrow$ `h ô 2`). Giúp mô hình học biểu diễn cao độ nhất quán, tránh bùng nổ kích thước từ vựng.
    * **Text Normalizer chuyên biệt:** Tự động chuyển đổi các nhãn dạng `(A)`, `(B)` (`(B)` $\rightarrow$ `Đáp án B:`), ngày tháng (`07/05/1954`), số thập phân, tiền tệ và ký hiệu viết tắt.
    * **HiFi-GAN Neural Vocoder:** Tái tạo sóng âm 22.05kHz trong trẻo, chèn khoảng nghỉ dấu câu tự nhiên.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy/Cô, em là Trương Hoàng Duy, xin phép trình bày phân hệ Tổng hợp Tiếng nói (TTS).  
  > Điểm nhấn nghiên cứu của phân hệ này là nhóm đã làm chủ và huấn luyện thành công kiến trúc **Matcha-TTS** – công nghệ Flow Matching tiên tiến nhất hiện nay từ hội nghị ICASSP 2024. Khác với Diffusion truyền thống cần hàng trăm bước khử nhiễu, Matcha-TTS sử dụng đường vận chuyển tối ưu thẳng, cho phép tạo Mel-spectrogram chất lượng cao chỉ sau 10 bước Euler trên CPU.  
  > Đóng góp quan trọng thứ hai là em đã đề xuất và triển khai frontend `vi_tone_v2`: bóc tách 6 thanh điệu tiếng Việt thành các token chuyên biệt. Kỹ thuật này giúp mô hình nắm bắt ngữ điệu và đường bao F0 tự nhiên hơn hẳn. Ngoài ra, module `normalizer` đi kèm xử lý triệt để việc đọc các nhãn như (A), (B), số liệu và ngày tháng trước khi tổng hợp."

---

#### SLIDE 9: ĐÁNH GIÁ & BENCHMARK ĐỊNH LƯỢNG PHÂN HỆ TTS
* **Thời lượng dự kiến:** 1.5 phút
* **Người trình bày:** Trương Hoàng Duy
* **Nội dung hiển thị trên Slide:**
  * **Bảng so sánh đối sánh thực nghiệm (trên 10 câu mẫu tham chiếu giọng người thật InfoRe1):**

| Mô hình | MCD (dB) $\downarrow$ | F0 RMSE (Hz) $\downarrow$ | log-F0 RMSE (semitones) $\downarrow$ | CER (ASR) $\downarrow$ | RTF (CPU) $\downarrow$ | Đặc điểm kiến trúc |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Giọng người thật (Tham chiếu)** | – | – | – | 0.7% | – | Mức trần kiểm chứng ASR PhoWhisper |
| **Matcha-TTS (Nhóm huấn luyện)** | 5.35 | 70.4 | **2.86** | **1.9%** | **0.52** | OT-CFM cục bộ, frontend tách thanh điệu |
| **VITS MMS (Meta Pretrained)** | **4.45** | 84.1 | 4.31 | 4.3% | 0.38 | VAE End-to-End, giọng nam |
| **Edge-TTS (Hoài My Neural)** | 4.63 | **48.3** | 2.69 | 1.0% | 0.13 | Cloud Neural, phụ thuộc kết nối Internet |

  * **Phân tích kết quả:**
    * Matcha-TTS đạt tỷ lệ lỗi ký tự CER cực thấp: **1.9%**, bám sát mức trần của ASR (0.7%) và vượt trội so với VITS (4.3%).
    * Lỗi cao độ log-F0 của Matcha đạt **2.86 bán cung**, tiệm cận mô hình thương mại Edge-TTS (2.69) và tốt hơn nhiều so với VITS (4.31).
    * Tốc độ suy luận CPU đạt RTF 0.52, hoàn toàn đáp ứng khả năng tương tác đàm thoại thời gian thực.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để đánh giá khách quan chất lượng âm thanh, em đã thiết lập một bộ benchmark định lượng chuẩn quốc tế, so sánh trực tiếp với giọng thu âm của người thật.  
  > Kết quả trên bảng cho thấy: Matcha-TTS đạt độ rõ tiếng nói vượt bậc với CER chỉ 1.9%, ít lỗi hơn VITS hơn 2 lần. Về độ chuẩn thanh điệu, sai số log-F0 chỉ 2.86 bán cung, gần như tương đương với mô hình nơ-ron thương mại của Microsoft Edge.  
  > Với chỉ số RTF đạt 0.52 trên CPU thông thường, mô hình của chúng em chỉ mất 0.5 giây để đọc một câu âm thanh dài 1 giây, hoàn toàn sẵn sàng cho các ứng dụng thực tế mà không cần trang bị GPU đắt tiền."

---

#### SLIDE 10: TÍCH HỢP HỆ THỐNG, GIAO DIỆN WEB & DOCKER
* **Thời lượng dự kiến:** 1.5 phút
* **Người trình bày:** Huỳnh Công Lương
* **Nội dung hiển thị trên Slide:**
  * **Kiến trúc Full-Stack Thống nhất:**
    * **Backend (FastAPI):** Tích hợp trọn vẹn cả 4 phân hệ qua REST API `/api/stt`, `/api/retrieve`, `/api/answer`, `/api/tts` và `/api/health`.
    * **Frontend (Angular):** Giao diện Chat trực quan, hiển thị pipeline flow status từng bước (Thu âm $\rightarrow$ STT $\rightarrow$ Retrieval $\rightarrow$ MRC $\rightarrow$ TTS $\rightarrow$ Playback), hỗ trợ micro và thư viện bài đọc.
  * **Đóng gói Triển khai Docker (Multi-stage Build):**
    * Stage 1 (`node:22-alpine`): Biên dịch Angular frontend thành assets tĩnh tối ưu.
    * Stage 2 (`python:3.11-slim`): Cài đặt ffmpeg, libsndfile, PyTorch CPU wheel siêu nhẹ và backend.
    * Quản lý bằng `docker-compose.yml`, tích hợp Healthcheck tự động, chạy cô lập trên cổng 8090.
  * **Chất lượng Kiểm thử Phần mềm:**
    * Bộ kiểm thử tự động **54/54 bài tests ĐẠT (100% Passed)** phủ khắp toàn bộ các phân hệ từ mức hàm đến API Server.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Về khía cạnh kỹ nghệ phần mềm, nhóm đã tích hợp toàn bộ các phân hệ thành một khối thống nhất:  
  > Phía Frontend, em xây dựng ứng dụng Angular với giao diện trực quan, có biểu đồ trạng thái thể hiện rõ hệ thống đang chạy ở bước nào trong pipeline. Người dùng có thể bấm mic nói hoặc chọn bài đọc từ thư viện.  
  > Toàn bộ dự án được đóng gói thành container Docker đa tầng: tự build giao diện web và khởi chạy server FastAPI chỉ bằng đúng một lệnh `docker compose up -d`. Đồ án đạt tỷ lệ kiểm thử thành công 100% với 54 trên 54 test cases tự động, đảm bảo tính ổn định và khả năng tái lập cao nhất."

---

#### SLIDE 11: KỊCH BẢN DEMO HỆ THỐNG THỰC TẾ
* **Thời lượng dự kiến:** 2 phút
* **Người trình bày:** Nhóm thực hiện (Demo trực tiếp hoặc video clip)
* **Nội dung hiển thị trên Slide:**
  * **Tình huống Demo minh họa:**
    * **Đầu vào giọng nói:** Người dùng bấm micro và hỏi: *"Ai là tác giả của Truyện Kiều?"* (câu hỏi tự do, không kèm phương án).
  * **Quy trình xử lý nội bộ:**
    1. **STT:** Whisper nhận dạng chính xác câu hỏi tiếng Việt có dấu.
    2. **Retrieval:** BM25 + dense lấy ứng viên từ kho tri thức hai tầng, reranker chọn đoạn Wikipedia "Truyện Kiều".
    3. **MRC:** ViT5 đọc đoạn văn đã truy xuất và sinh ra câu trả lời *"Nguyễn Du"*.
    4. **TTS:** Normalizer chuẩn hóa câu trả lời và Edge-TTS/Matcha-TTS tổng hợp thành âm thanh MP3/WAV.
  * **Đầu ra:** Trình duyệt tự động phát câu trả lời giọng nói truyền cảm cho người dùng nghe.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Sau đây, nhóm xin kính mời Thầy/Cô và các bạn cùng theo dõi kịch bản chạy thử nghiệm thực tế của hệ thống.  
  > Khi người dùng bấm nút thu âm và đặt câu hỏi: 'Ai là tác giả của Truyện Kiều?', phân hệ STT ngay lập tức chuyển đổi thành văn bản. Bộ truy xuất lấy ứng viên từ BM25 và dense, rồi reranker chọn đoạn Wikipedia về Truyện Kiều.  
  > Ngay sau đó, ViT5 đọc đoạn văn vừa truy xuất và sinh ra câu trả lời 'Nguyễn Du'. Cuối cùng, phân hệ TTS chuẩn hóa văn bản và phát ra câu trả lời bằng giọng đọc nơ-ron tự nhiên. Toàn bộ chu trình từ lúc người dùng dứt lời đến khi nghe câu trả lời mất khoảng 12 giây khi chạy trên CPU Docker (STT ~3 giây, truy xuất + reranker ~6 giây, ViT5 ~1,4 giây, TTS ~1,3 giây); nếu tắt reranker thì còn khoảng 6 giây nhưng độ chính xác thấp hơn. Câu 'Sông dài nhất thế giới là sông nào?' cũng trả lời đúng 'Sông Amazon' trong Docker."

---

#### SLIDE 12: TỔNG KẾT, GIỚI HẠN & HƯỚNG PHÁT TRIỂN
* **Thời lượng dự kiến:** 1.5 phút
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Các kết quả đạt được:**
    * Xây dựng thành công hệ thống Voice Q&A tiếng Việt trọn vẹn đầu tiên dựa trên ViMMRC 2.0.
    * Ứng dụng thành công kỹ thuật Flow Matching (Matcha-TTS) và frontend tách thanh điệu cho tiếng Việt.
    * Tích hợp kiến trúc phân tán linh hoạt, chạy được cả offline trên CPU thông thường và triển khai nhanh qua Docker.
  * **Hạn chế hiện tại:**
    * Một số câu hỏi kiến thức chung vẫn sai, ví dụ "Thủ đô của Việt Nam là gì?" trả về "Sài Gòn" vì đoạn ViQuAD tầng 1 về TP. Hồ Chí Minh thắng; F1 kiến thức mở mới ~24.
    * Độ trễ ~12 giây/câu trên CPU Docker do reranker chiếm ~6 giây.
    * Checkpoint ViT5 cần tài nguyên GPU lớn hơn để huấn luyện hội tụ hoàn toàn số epoch cao.
  * **Hướng phát triển:**
    * Chạy GPU để giảm độ trễ.
    * Tinh chỉnh reranker và định tuyến cho câu hỏi kiến thức chung.
    * Thử LLM tiếng Việt để sinh câu trả lời.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Tóm lại, qua đề tài này, nhóm chúng em đã giải quyết trọn vẹn bài toán tích hợp giữa Nhận dạng giọng nói, Truy xuất văn bản, Đọc hiểu máy và Tổng hợp giọng nói tiếng Việt với mã nguồn mở và khả năng chạy cục bộ hiệu quả.  
  > Trong tương lai, nhóm định hướng sẽ chạy hệ thống trên GPU để giảm độ trễ, tinh chỉnh reranker và định tuyến cho câu hỏi kiến thức chung, đồng thời thử LLM tiếng Việt để sinh câu trả lời.  
  > Nhóm chúng em xin chân thành cảm ơn sự lắng nghe và chỉ dẫn quý báu của Thầy/Cô. Rất mong nhận được những câu hỏi và đóng góp ý kiến từ Thầy/Cô và các bạn! Xin trân trọng cảm ơn!"
