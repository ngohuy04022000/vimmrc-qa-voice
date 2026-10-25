# TÀI LIỆU THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN / SEMINAR
## ĐỀ TÀI: HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0 (ViMMRC VOICE Q&A)
**Môn học:** Học máy tiên tiến và ứng dụng  
**Nhóm thực hiện:**
1. **Ngô Trí Huy** (Nhóm trưởng): Phân hệ Truy xuất Ngữ cảnh (Retrieval), Mô hình Đọc hiểu (MRC - ViT5 & ChoiceRanker), Thiết kế Kiến trúc & Tích hợp.
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
* **Slide 7:** Phân hệ 3: Mô hình Đọc hiểu Máy (MRC - ChoiceRanker & ViT5)
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
    * Ngô Trí Huy: Retrieval BM25, MRC (ChoiceRanker & ViT5), Backend Integration.
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
    * Bộ dữ liệu đọc hiểu trắc nghiệm chuẩn tiếng Việt dành cho học sinh tiểu học đến THCS.
    * Cấu trúc: Đoạn văn (Article) + Câu hỏi (Question) + 4 Phương án lựa chọn (A, B, C, D) + Đáp án đúng (Answer).
  * **Phân chia dữ liệu (Splits):**
    * Tập Train: 482 bài đọc (3.600 câu hỏi).
    * Tập Dev: 70 bài đọc (564 câu hỏi).
    * Tập Test: 147 bài đọc (1.109 câu hỏi).
    * Đảm bảo tính phân tách tuyệt đối (disjoint) ở cấp độ bài đọc, không rò rỉ dữ liệu (zero leakage).
  * **Đặc điểm & Thách thức:**
    * Ngữ cảnh dài (nhiều bài vượt quá 512 token).
    * Nhiều phương án lựa chọn gây nhiễu, có phương án rỗng trong dữ liệu thô.
    * Đòi hỏi giải pháp vừa trả lời được câu hỏi trắc nghiệm vừa có khả năng trả lời tự luận mở.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Trọng tâm dữ liệu của đề tài là bộ dữ liệu ViMMRC 2.0 do UIT-NLP phát triển. Bộ dữ liệu gồm 699 bài đọc với hơn 5.200 câu hỏi, được chia thành 3 tập train, dev và test tách biệt hoàn toàn theo bài đọc.  
  > Thách thức lớn của ViMMRC nằm ở chỗ: các bài đọc có độ dài biến thiên, nhiều câu hỏi đòi hỏi suy luận từ nhiều câu khác nhau trong bài, và dữ liệu gốc có dạng trắc nghiệm 4 lựa chọn. Nhóm đã tiền xử lý nghiêm ngặt: chuẩn hóa mã hóa Unicode NFC, loại bỏ ký tự rỗng và thiết kế cơ chế đánh giá kép: vừa đánh giá xếp hạng 4 đáp án, vừa đánh giá sinh chuỗi tự do."

---

#### SLIDE 4: KIẾN TRÚC HỆ THỐNG TỔNG THỂ (PIPELINE 4 CHẶNG)
* **Thời lượng dự kiến:** 1.5 phút
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Sơ đồ luồng xử lý End-to-End:**
    $$\text{Micro (Audio)} \xrightarrow{\text{STT}} \text{Văn bản câu hỏi} \xrightarrow{\text{Retrieval}} \text{Đoạn văn liên quan} \xrightarrow{\text{MRC}} \text{Đáp án} \xrightarrow{\text{TTS}} \text{Loa (Audio)}$$
  * **4 Phân hệ nòng cốt:**
    1. **STT Module:** Faster-Whisper trích xuất câu hỏi từ audio 16kHz.
    2. **Retrieval Module:** BM25 tối ưu hóa truy xuất top đoạn văn từ 552 bài đọc ViMMRC.
    3. **MRC Module:** ChoiceRanker (TF-IDF + Logistic Regression) cho trắc nghiệm & ViT5 Transformer cho câu hỏi mở.
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
  * **Giải thuật BM25 Tối ưu hóa (Optimized BM25):**
    * Chỉ số hóa toàn bộ **552 bài đọc độc bản** từ tập Train và Dev của ViMMRC 2.0 (`data/vimmrc_index.json`).
    * Tinh chỉnh siêu tham số thực nghiệm: $k_1 = 2.1$ (độ bão hòa tần suất từ), $b = 1.0$ (chuẩn hóa độ dài bài đọc).
    * Bổ sung cơ chế **Bigram Phrase Boost** (+0.4): Ưu tiên các đoạn văn chứa cụm từ ghép có thứ tự chính xác.
  * **Kết quả đo lường trên tập Dev (564 câu hỏi):**
    * **Recall@1:** **71.45%** (chọn đúng bài đọc ngay ở vị trí số 1).
    * **Recall@5:** **83.69%** (bài đọc đúng nằm trong top 5).
    * **MRR@5:** **0.7624** (Mean Reciprocal Rank đạt mức rất cao trên văn bản tiếng Việt).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Tiếp theo là phân hệ Truy xuất Đoạn văn do em phụ trách. Khi người dùng hỏi một câu như 'Thủ đô của Việt Nam là gì?', hệ thống phải tìm ra bài đọc tương ứng trong hàng trăm văn bản.  
  > Em đã lập chỉ mục cho toàn bộ 552 bài đọc ViMMRC bằng thuật toán BM25 nâng cao. Thay vì sử dụng tham số mặc định của Lucene, em tinh chỉnh $k_1=2.1$ và $b=1.0$, kết hợp tính năng Bigram Phrase Boost để ưu tiên các cụm từ ghép tiếng Việt.  
  > Kết quả đánh giá trên 564 câu hỏi dev cho thấy: Recall@1 đạt 71.45%, và Recall@5 đạt tới 83.69% với chỉ số MRR đạt 0.762. Điều này chứng minh BM25 tinh chỉnh hoàn toàn đáp ứng tốt vai trò cung cấp ngữ cảnh chính xác cho mô hình đọc hiểu."

---

#### SLIDE 7: PHÂN HỆ 3 - MÔ HÌNH ĐỌC HIỂU (MRC MODEL)
* **Thời lượng dự kiến:** 2 phút
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị trên Slide:**
  * **Hướng tiếp cận kép linh hoạt:**
    1. **ChoiceRanker (Trắc nghiệm 4 lựa chọn):**
       * Trích xuất vector đặc trưng: TF-IDF n-gram ký tự/từ của Passage, Query và từng Option; độ dài tương đối; tỷ lệ trùng khớp cụm từ chính xác.
       * Phân loại bằng Logistic Regression với tối ưu hóa siêu tham số $C=10$.
       * Đạt độ chính xác **51.95%** trên Dev (293/564 câu), vượt trội so với Lexical Baseline (**43.62%**) và Random Baseline (**25.18%**).
    2. **ViT5 Sequence-to-Sequence (Câu hỏi tự luận mở):**
       * Kiến trúc Transformer T5 tiếng Việt (`VietAI/vit5-base`).
       * Cơ chế Context Chunking Heuristic (`context_selection.py`): giải quyết bài toán văn bản vượt giới hạn 512 token mà không làm mất thông tin bằng chứng.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Ở phân hệ Đọc hiểu MRC, nhóm phát triển hai nhánh mô hình song song:  
  > Đối với bài toán trắc nghiệm chuẩn ViMMRC, em xây dựng mô hình **ChoiceRanker**. Mô hình trích xuất ma trận đặc trưng kết hợp giữa TF-IDF đa mức, mức độ bao phủ từ vựng và tỷ lệ khớp cụm từ, sau đó đưa qua bộ phân loại Logistic Regression. Mô hình đạt độ chính xác 51.95% trên tập Dev, vượt hơn 8.3% so với baseline từ khóa và gấp đôi chọn ngẫu nhiên.  
  > Đối với các câu hỏi tự luận không có đáp án cho trước, hệ thống tích hợp mô hình **ViT5** của VietAI. Em đã thiết kế module `context_selection` để chọn lọc các phân đoạn ngữ cảnh giàu thông tin nhất, đảm bảo mô hình không bị cắt cụt bằng chứng quan trọng khi văn bản dài vượt quá 512 token."

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
    * **Text Normalizer chuyên biệt:** Tự động chuyển đổi các định dạng đáp án trắc nghiệm (`(B)` $\rightarrow$ `Đáp án B:`), ngày tháng (`07/05/1954`), số thập phân, tiền tệ và ký hiệu viết tắt.
    * **HiFi-GAN Neural Vocoder:** Tái tạo sóng âm 22.05kHz trong trẻo, chèn khoảng nghỉ dấu câu tự nhiên.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy/Cô, em là Trương Hoàng Duy, xin phép trình bày phân hệ Tổng hợp Tiếng nói (TTS).  
  > Điểm nhấn nghiên cứu của phân hệ này là nhóm đã làm chủ và huấn luyện thành công kiến trúc **Matcha-TTS** – công nghệ Flow Matching tiên tiến nhất hiện nay từ hội nghị ICASSP 2024. Khác với Diffusion truyền thống cần hàng trăm bước khử nhiễu, Matcha-TTS sử dụng đường vận chuyển tối ưu thẳng, cho phép tạo Mel-spectrogram chất lượng cao chỉ sau 10 bước Euler trên CPU.  
  > Đóng góp quan trọng thứ hai là em đã đề xuất và triển khai frontend `vi_tone_v2`: bóc tách 6 thanh điệu tiếng Việt thành các token chuyên biệt. Kỹ thuật này giúp mô hình nắm bắt ngữ điệu và đường bao F0 tự nhiên hơn hẳn. Ngoài ra, module `normalizer` đi kèm xử lý triệt để việc đọc nhãn trắc nghiệm, số liệu và ngày tháng trước khi tổng hợp."

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
    * Bộ kiểm thử tự động **55/55 bài tests ĐẠT (100% Passed)** phủ khắp toàn bộ các phân hệ từ mức hàm đến API Server.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Về khía cạnh kỹ nghệ phần mềm, nhóm đã tích hợp toàn bộ các phân hệ thành một khối thống nhất:  
  > Phía Frontend, em xây dựng ứng dụng Angular với giao diện trực quan, có biểu đồ trạng thái thể hiện rõ hệ thống đang chạy ở bước nào trong pipeline. Người dùng có thể bấm mic nói hoặc chọn bài đọc từ thư viện.  
  > Toàn bộ dự án được đóng gói thành container Docker đa tầng: tự build giao diện web và khởi chạy server FastAPI chỉ bằng đúng một lệnh `docker compose up -d`. Đồ án đạt tỷ lệ kiểm thử thành công 100% với 55 trên 55 test cases tự động, đảm bảo tính ổn định và khả năng tái lập cao nhất."

---

#### SLIDE 11: KỊCH BẢN DEMO HỆ THỐNG THỰC TẾ
* **Thời lượng dự kiến:** 2 phút
* **Người trình bày:** Nhóm thực hiện (Demo trực tiếp hoặc video clip)
* **Nội dung hiển thị trên Slide:**
  * **Tình huống Demo minh họa:**
    * **Đầu vào giọng nói:** Người dùng bấm micro và hỏi: *"Thủ đô của Việt Nam là gì?"* kèm 4 lựa chọn: *Huế, Hà Nội, Đà Nẵng, Cần Thơ*.
  * **Quy trình xử lý nội bộ:**
    1. **STT:** Whisper nhận dạng chính xác câu hỏi tiếng Việt có dấu.
    2. **Retrieval:** BM25 tự động quét kho 552 văn bản và truy xuất đúng bài đọc mã số `train:0288` về Văn Miếu - Quốc Tử Giám Hà Nội (điểm số 26.97).
    3. **MRC:** ChoiceRanker phân tích ngữ cảnh bài đọc và chấm điểm: Phương án B đạt 0.807 (cao nhất).
    4. **TTS:** Normalizer chuẩn hóa thành *"Đáp án B: Hà Nội"* và Edge-TTS/Matcha-TTS tổng hợp thành âm thanh MP3/WAV.
  * **Đầu ra:** Trình duyệt tự động phát câu trả lời giọng nói truyền cảm cho người dùng nghe.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Sau đây, nhóm xin kính mời Thầy/Cô và các bạn cùng theo dõi kịch bản chạy thử nghiệm thực tế của hệ thống.  
  > Khi người dùng bấm nút thu âm và đặt câu hỏi: 'Thủ đô của Việt Nam là gì?', phân hệ STT ngay lập tức chuyển đổi thành văn bản. Bộ truy xuất BM25 lập tức quét trong 552 bài đọc và trả về đúng bài đọc số 288 về Văn Miếu - Quốc Tử Giám với điểm khớp 26.97.  
  > Ngay sau đó, ChoiceRanker tính toán và nhận diện phương án B đạt xác suất áp đảo 80.7%. Cuối cùng, phân hệ TTS chuẩn hóa văn bản và phát ra câu trả lời bằng giọng đọc nơ-ron tự nhiên. Toàn bộ chu trình từ lúc người dùng dứt lời đến khi nghe câu trả lời chỉ mất khoảng 1.5 đến 2 giây."

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
    * BM25 là phương pháp so khớp từ khóa lexical, chưa nắm bắt được trọn vẹn ngữ nghĩa tiềm ẩn (semantic) đối với các câu hỏi phức tạp.
    * Checkpoint ViT5 cần tài nguyên GPU lớn hơn để huấn luyện hội tụ hoàn toàn số epoch cao.
  * **Hướng phát triển:**
    * Nâng cấp bộ truy xuất sang dạng lai kết hợp Dense Retrieval (Bi-Encoder embeddings) và Reranker.
    * Tích hợp các mô hình ngôn ngữ lớn (LLMs tiếng Việt) để hỗ trợ hội thoại đa lượt (multi-turn dialog).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Tóm lại, qua đề tài này, nhóm chúng em đã giải quyết trọn vẹn bài toán tích hợp giữa Nhận dạng giọng nói, Truy xuất văn bản, Đọc hiểu máy và Tổng hợp giọng nói tiếng Việt với mã nguồn mở và khả năng chạy cục bộ hiệu quả.  
  > Trong tương lai, nhóm định hướng sẽ nâng cấp bộ tìm kiếm sang kiến trúc lai Dense Retrieval kết hợp mô hình nhúng ngữ nghĩa, đồng thời mở rộng khả năng đối thoại đa lượt với người dùng.  
  > Nhóm chúng em xin chân thành cảm ơn sự lắng nghe và chỉ dẫn quý báu của Thầy/Cô. Rất mong nhận được những câu hỏi và đóng góp ý kiến từ Thầy/Cô và các bạn! Xin trân trọng cảm ơn!"
