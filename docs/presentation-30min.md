# TÀI LIỆU KỊCH BẢN THUYẾT TRÌNH 30 PHÚT (QUAY VIDEO BÁO CÁO TOÀN DIỆN ĐỒ ÁN)
## ĐỀ TÀI: HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0 (ViMMRC VOICE Q&A)
**Môn học:** Học máy tiên tiến và ứng dụng (Chương trình Cao học Công nghệ Thông tin)  
**Thời lượng:** 30 phút (khoảng 3.800 - 4.200 từ thuyết minh, nhịp độ 130 từ/phút)  
**Mục tiêu:** Báo cáo chi tiết, chuyên sâu, toàn diện tất cả các khía cạnh: Động lực nghiên cứu, Phân tích dữ liệu ViMMRC 2.0, Kiến trúc 4 phân hệ, Cơ sở lý thuyết toán học (OT-CFM, BM25, ViT5), Kỹ thuật tối ưu hóa phần mềm (Lazy loading, VAD, Normalizer, Docker), Bảng benchmark đối sánh chuẩn quốc tế, Phân tích lỗi và Hướng phát triển.

---

### MỤC LỤC & PHÂN BỔ THỜI GIAN 24 SLIDE (TỔNG: 30 PHÚT)

#### PHẦN 1: TỔNG QUAN, BÀI TOÁN & DỮ LIỆU ViMMRC 2.0 (5:30) - Ngô Trí Huy
* **Slide 1 (0:00 - 1:15):** Giới thiệu Đề tài, Hội đồng & Phân công Thành viên
* **Slide 2 (1:15 - 2:30):** Bối cảnh MRC, Voice Q&A & Thách thức Âm học Tiếng Việt
* **Slide 3 (2:30 - 3:45):** Mục tiêu Nghiên cứu & Bộ Tiêu chuẩn Thiết kế Hệ thống
* **Slide 4 (3:45 - 5:30):** Phân tích Chuyên sâu Bộ Dữ liệu UIT-NLP/ViMMRC 2.0

#### PHẦN 2: KIẾN TRÚC TỔNG THỂ & PHÂN HỆ STT (6:00) - Huỳnh Công Lương
* **Slide 5 (5:30 - 7:00):** Kiến trúc End-to-End Pipeline 4 Chặng & Cơ chế Dự phòng
* **Slide 6 (7:00 - 8:30):** Phân hệ STT - Kiến trúc Faster-Whisper & Tối ưu CTranslate2
* **Slide 7 (8:30 - 10:00):** Tối ưu hóa STT: Voice Activity Detection & Thread-Safe Lazy Loading
* **Slide 8 (10:00 - 11:30):** Xử lý Âm thanh Phía Client (Web Audio API & Chuẩn hóa WAV 16kHz)

#### PHẦN 3: PHÂN HỆ CỐT LÕI: RETRIEVAL & ĐỌC HIỂU MRC (7:00) - Ngô Trí Huy
* **Slide 9 (11:30 - 12:45):** Phân hệ Retrieval - Bài toán Tìm kiếm Văn bản Open-Domain
* **Slide 10 (12:45 - 14:15):** Tinh chỉnh Giải thuật BM25 ($k_1, b$) & Bigram Phrase Boost
* **Slide 11 (14:15 - 15:30):** Đánh giá Thực nghiệm Phân hệ Retrieval (Recall@1, Recall@5, MRR)
* **Slide 12 (15:30 - 17:00):** Retrieval: Kho Tri Thức Hai Tầng Cho RAG
* **Slide 13 (17:00 - 18:30):** Phân hệ MRC - Mô hình ViT5 Seq2Seq & Heuristic Context Selection

#### PHẦN 4: PHÂN HỆ TỔNG HỢP TIẾNG NÓI TIÊN TIẾN TTS (6:30) - Trương Hoàng Duy
* **Slide 14 (18:30 - 19:45):** Phân hệ TTS - Tổng quan & Lựa chọn Kiến trúc Matcha-TTS
* **Slide 15 (19:45 - 21:15):** Nguyên lý Toán học OT-CFM (Optimal-Transport Flow Matching)
* **Slide 16 (21:15 - 22:30):** Đóng góp Frontend Tách Thanh Điệu `vi_tone_v2`
* **Slide 17 (22:30 - 23:45):** Phân hệ Chuẩn hóa Văn bản Tiếng Việt Chuyên biệt (Text Normalizer)
* **Slide 18 (23:45 - 25:00):** Đánh giá Định lượng & Benchmark Âm học Chi tiết (MCD, F0, CER, RTF)

#### PHẦN 5: KỸ NGHỆ HỆ THỐNG, DEMO & KẾT LUẬN (5:00) - Cả Nhóm
* **Slide 19 (25:00 - 26:00):** Kiến trúc Phần mềm Full-Stack FastAPI & Angular SPA (Huỳnh Công Lương)
* **Slide 20 (26:00 - 27:00):** Đóng gói Triển khai Docker Multi-Stage & Healthcheck (Huỳnh Công Lương)
* **Slide 21 (27:00 - 28:00):** Đảm bảo Chất lượng Kiểm thử (54/54 Automated Tests) (Ngô Trí Huy)
* **Slide 22 (28:00 - 29:15):** Kịch bản Live Demonstration Chi tiết Từng Bước (Cả Nhóm)
* **Slide 23 (29:15 - 30:00):** Phân tích Lỗi, Thảo luận Giới hạn & Hướng Phát triển (Ngô Trí Huy)

---

## NỘI DUNG VÀ KỊCH BẢN CHI TIẾT TỪNG SLIDE (24 SLIDES)

### SLIDE 1: GIỚI THIỆU ĐỀ TÀI, HỘI ĐỒNG & NHÓM THỰC HIỆN
* **Thời lượng:** 1 phút 15 giây (0:00 - 1:15)
* **Người trình bày:** Ngô Trí Huy (Nhóm trưởng)
* **Nội dung hiển thị:**
  * **Trường / Viện:** Chương trình Đào tạo Thạc sĩ Công nghệ Thông tin
  * **Môn học:** Học máy tiên tiến và ứng dụng
  * **Tên đề tài:** HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0 (ViMMRC VOICE Q&A SYSTEM)
  * **Giảng viên hướng dẫn:** [Tên Thầy / Cô hướng dẫn]
  * **Thành viên nhóm & Phân công trách nhiệm:**
    * **Ngô Trí Huy (Nhóm trưởng):** Nghiên cứu giải thuật Truy xuất văn bản BM25 tinh chỉnh, Xây dựng kho tri thức hai tầng và mô hình MRC ViT5, Thiết kế kiến trúc tổng thể, Điều phối tích hợp hệ thống.
    * **Huỳnh Công Lương:** Nghiên cứu phân hệ STT Faster-Whisper, Tối ưu hóa suy luận CTranslate2, Thiết kế kiến trúc Web Client (Angular 19/22) và Đóng gói triển khai Docker.
    * **Trương Hoàng Duy:** Nghiên cứu phân hệ TTS Matcha-TTS (Flow Matching) & VITS, Đề xuất frontend tách thanh điệu `vi_tone_v2`, Xây dựng Text Normalizer và Thiết lập bộ benchmark đánh giá âm học.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô trong Hội đồng và các bạn học viên cao học! Hôm nay, nhóm chúng em xin trân trọng trình bày báo cáo chuyên đề đồ án môn học 'Học máy tiên tiến và ứng dụng' với đề tài: **'Xây dựng Hệ thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0'**.  
  > Nhóm nghiên cứu gồm ba thành viên: Em là Ngô Trí Huy, đảm nhận vai trò nhóm trưởng, chịu trách nhiệm chính về Phân hệ Truy xuất Ngữ cảnh BM25 và Mô hình Đọc hiểu MRC. Bạn Huỳnh Công Lương chịu trách nhiệm Phân hệ Nhận dạng Giọng nói Faster-Whisper và Giao diện Web Full-stack. Và bạn Trương Hoàng Duy phụ trách Phân hệ Tổng hợp Tiếng nói Flow Matching cùng Bộ benchmark đánh giá âm học.  
  > Trong video báo cáo 30 phút này, nhóm sẽ trình bày chi tiết từ bối cảnh khoa học, bài toán dữ liệu, cơ sở lý thuyết toán học của các mô hình, quy trình tối ưu kỹ thuật, kết quả thực nghiệm đối sánh, cho đến phần demo chạy thực tế của hệ thống. Xin kính mời Thầy Cô cùng theo dõi!"

---

### SLIDE 2: BỐI CẢNH MRC & THÁCH THỨC VOICE Q&A TIẾNG VIỆT
* **Thời lượng:** 1 phút 15 giây (1:15 - 2:30)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị:**
  * **Sự phát triển của Machine Reading Comprehension (MRC):** Từ mô hình trích xuất (Span Extraction) đến sinh sinh chuỗi (Seq2Seq), nhưng hầu hết tương tác text-to-text.
  * **Thực tiễn nhu cầu:** Tương tác giọng nói tự nhiên trong môi trường rảnh tay (lái xe, trợ lý ảo gia đình, hỗ trợ người khuyết tật thị giác, cổng thông tin trường học).
  * **Những thách thức âm học & ngôn ngữ đặc thù tiếng Việt:**
    1. **Thanh điệu phức tạp:** Tiếng Việt có 6 thanh điệu mang tính phân biệt ngữ nghĩa cao độ. Mô hình TTS thông thường dễ bị sai thanh điệu, méo tiếng hoặc vấp âm.
    2. **Độ trễ tích lũy (Cascading Latency):** Pipeline 4 chặng nếu không được tối ưu sẽ mất 5-10 giây, gây đứt đoạn hội thoại.
    3. **Rào cản tài nguyên phần cứng:** Phần lớn các mô hình SOTA yêu cầu GPU đắt tiền (NVIDIA A100/V100). Đồ án đặt mục tiêu chạy mượt mà ngay trên CPU máy tính thông thường.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Thưa Thầy Cô, Machine Reading Comprehension là một trong những trụ cột quan trọng của Xử lý Ngôn ngữ Tự nhiên. Tuy nhiên, việc giới hạn người dùng ở bàn phím và màn hình văn bản đã tước đi cơ hội tiếp cận công nghệ của rất nhiều đối tượng, đặc biệt là người khiếm thị, người cao tuổi, hoặc các tình huống đang điều khiển phương tiện giao thông.  
  > Khi nâng cấp bài toán đọc hiểu văn bản thành Voice Q&A, chúng ta phải đối mặt với ba nút thắt lớn:  
  > Thứ nhất là tính chất thanh điệu của tiếng Việt. Tiếng Việt là ngôn ngữ đơn âm tiết có 6 thanh điệu biến thiên cao độ liên tục. Các hệ thống TTS tiếng Anh áp dụng vào tiếng Việt thường phát âm như người nước ngoài hoặc nhầm lẫn dấu hỏi, ngã, nặng.  
  > Thứ hai là độ trễ tích lũy: qua 4 chặng nhận dạng, tìm kiếm, đọc hiểu và phát âm, nếu mỗi chặng chậm 1-2 giây thì tổng thời gian phản hồi sẽ lên tới 8 giây, phá vỡ tính tự nhiên của đàm thoại.  
  > Và thứ ba là vấn đề tài nguyên: làm sao để hệ thống vừa chính xác mà vẫn có thể triển khai cục bộ trên CPU máy chủ phổ thông mà không phụ thuộc vào hạ tầng GPU đám mây đắt đỏ."

---

### SLIDE 3: MỤC TIÊU NGHIÊN CỨU & TIÊU CHÍ THIẾT KẾ
* **Thời lượng:** 1 phút 15 giây (2:30 - 3:45)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị:**
  * **Mục tiêu khoa học & kỹ thuật:**
    * Xây dựng pipeline Voice-to-Voice hoàn chỉnh cho tiếng Việt, dựa trên chuẩn dữ liệu ViMMRC 2.0.
    * Ứng dụng mô hình tạo sinh âm thanh tiên tiến nhất hiện nay: Conditional Flow Matching (Matcha-TTS).
  * **4 Tiêu chí thiết kế hệ thống (Design Principles):**
    1. **Tính Module hóa (High Modularity):** Mỗi phân hệ độc lập, giao tiếp qua API chuẩn, dễ dàng thay thế nâng cấp từng thành phần.
    2. **Khả năng chạy Cục bộ (Local & CPU-friendly):** Toàn bộ pipeline hoạt động offline ổn định trên CPU máy tính thông thường, không bị ràng buộc API trả phí bên ngoài.
    3. **Độ tin cậy & Chịu lỗi (Fault Tolerance):** Thiết kế cơ chế Fallback tự động đa tầng; khi có sự cố ở một nhánh, hệ thống lập tức kích hoạt nhánh dự phòng.
    4. **Tốc độ phản hồi Thời gian thực (Real-Time Responsiveness):** Tổng thời gian xử lý toàn pipeline khống chế trong ngưỡng 1.5 - 2.5 giây.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để giải quyết các thách thức trên, nhóm đặt ra mục tiêu xây dựng một hệ thống Voice Q&A tiếng Việt mã nguồn mở hoàn chỉnh, khép kín từ khâu thu âm đến khâu phát giọng nói.  
  > Bốn nguyên lý thiết kế được quán triệt xuyên suốt:  
  > Một là Tính Module hóa cao: từng phân hệ STT, Retrieval, MRC và TTS được trừu tượng hóa qua các lớp Client/Engine riêng biệt, cho phép kiểm thử độc lập và linh hoạt hoán đổi thuật toán.  
  > Hai là Khả năng chạy cục bộ trên CPU: nhóm kiên quyết tối ưu hóa kích thước mô hình và thuật toán suy luận để toàn bộ hệ thống có thể chạy trên máy tính phổ thông với 8GB RAM mà không cần GPU rời.  
  > Ba là Tính chịu lỗi: hệ thống không được phép bị sập khi gặp đầu vào bất thường hay lỗi mạng, luôn có nhánh fallback dự phòng tại chỗ.  
  > Và bốn là Tối ưu hóa thời gian phản hồi: mục tiêu tổng thời gian xử lý từ lúc người dùng dứt câu hỏi đến khi nghe thấy giọng nói trả lời không vượt quá 2.5 giây."

---

### SLIDE 4: PHÂN TÍCH CHUYÊN SÂU BỘ DỮ LIỆU ViMMRC 2.0
* **Thời lượng:** 1 phút 45 giây (3:45 - 5:30)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị:**
  * **Tổng quan UIT-NLP/ViMMRC 2.0:**
    * Bộ dữ liệu đọc hiểu chuẩn tiếng Việt dành cho học sinh tiểu học và THCS do nhóm UIT-NLP công bố. ViMMRC gốc là trắc nghiệm; dự án chuyển sang dạng hỏi - đáp tự do (đoạn văn + câu hỏi + câu trả lời dạng văn bản) và bổ sung thêm ViQuAD.
    * Quy mô: 699 bài đọc, 5.273 câu hỏi.
  * **Phân chia dữ liệu Disjoint cấp Bài đọc (Zero Data Leakage):**
    * **Train set:** 482 bài đọc (3.600 câu hỏi - chiếm ~68.3%).
    * **Dev set:** 70 bài đọc (564 câu hỏi - chiếm ~10.7%).
    * **Test set:** 147 bài đọc (1.109 câu hỏi - chiếm ~21.0%).
    * Tuyệt đối không trùng lặp bài đọc giữa các tập, đảm bảo đánh giá khách quan năng lực tổng quát hóa.
  * **Phân tích đặc trưng dữ liệu & Thách thức tiền xử lý:**
    * Độ dài bài đọc: trung bình 385 từ, bài dài nhất lên tới hơn 1.200 từ (vượt trần 512 token của Transformer).
    * Hiện tượng đáp án rỗng hoặc chứa ký tự điều khiển Unicode ẩn trong dữ liệu thô.
    * Giải pháp: Chuẩn hóa Unicode NFC toàn diện, lọc khoảng trắng thừa, và chuyển dữ liệu sang bài toán Đọc hiểu sinh câu tự do (Generative QA).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Trọng tâm dữ liệu của đề tài là bộ dữ liệu ViMMRC 2.0 do phòng thí nghiệm UIT-NLP Đại học Công nghệ Thông tin ĐHQG-HCM xây dựng. Đây là bộ dữ liệu đọc hiểu tiếng Việt rất chất lượng, được biên soạn từ các bài tập đọc dành cho học sinh phổ thông.  
  > Toàn bộ 699 bài đọc với 5.273 câu hỏi được chia thành 3 tập Train, Dev và Test. Điểm cốt lõi mà nhóm tuân thủ nghiêm ngặt là tính phân tách tuyệt đối ở cấp độ bài đọc: nghĩa là các bài đọc trong tập Dev và Test hoàn toàn chưa từng xuất hiện trong tập Train, đảm bảo độ rò rỉ dữ liệu bằng không (zero data leakage).  
  > Khi đào sâu phân tích dữ liệu, nhóm phát hiện hai đặc điểm lớn: Thứ nhất, có những bài đọc rất dài vượt quá 1.000 từ, vượt xa giới hạn độ dài ngữ cảnh 512 token của các mô hình Transformer như ViT5 hay mBART. Thứ hai, ViMMRC gốc là bộ dữ liệu trắc nghiệm; nhóm đã chuyển sang dạng hỏi - đáp tự do gồm đoạn văn, câu hỏi và câu trả lời dạng văn bản, đồng thời bổ sung ViQuAD để tăng độ đa dạng.  
  > Nhóm đã thực hiện tiền xử lý chuẩn hóa toàn bộ về Unicode NFC, làm sạch các ký tự đặc biệt, lập kho tri thức hai tầng: 5.869 đoạn văn ViMMRC + ViQuAD và 1,48 triệu đoạn Wikipedia tiếng Việt, phục vụ truy xuất ngữ cảnh cho toàn bộ hệ thống."

---

### SLIDE 5: KIẾN TRÚC END-TO-END PIPELINE 4 CHẶNG
* **Thời lượng:** 1 phút 30 giây (5:30 - 7:00)
* **Người trình bày:** Huỳnh Công Lương
* **Nội dung hiển thị:**
  * **Sơ đồ luồng dữ liệu 4 Chặng chi tiết:**
    $$\text{User Mic} \xrightarrow{\text{Audio}} \text{[STT: Faster-Whisper]} \xrightarrow{\text{Text Query}} \text{[Retrieval: BM25]} \xrightarrow{\text{Passage}} \text{[MRC: ViT5]} \xrightarrow{\text{Answer Text}} \text{[TTS: Matcha/VITS]} \xrightarrow{\text{Audio}} \text{Speaker}$$
  * **Giao thức truyền thông liên phân hệ:**
    * Phân hệ STT tiếp nhận `multipart/form-data` audio/wav $\rightarrow$ trả về JSON `{text, language, duration}`.
    * Phân hệ Retrieval nhận `{query, top_k}` $\rightarrow$ quét qua chỉ mục `vimmrc_index.json` $\rightarrow$ trả về Top 5 văn bản kèm BM25 score.
    * Phân hệ MRC nhận `POST /api/answer {question, passage}` $\rightarrow$ trả về `{answer}`.
    * Phân hệ TTS nhận `{text, voice, speed}` $\rightarrow$ chuyển qua normalizer $\rightarrow$ tạo sóng âm WAV/MP3.
  * **Cơ chế Fallback Đa Tầng:**
    * STT: Whisper Local $\rightarrow$ Web Speech API fallback.
    * MRC: ViT5 GPU/CPU $\rightarrow$ Lexical Baseline (trích xuất đáp án khi chưa có checkpoint ViT5).
    * TTS: Matcha-TTS Local $\rightarrow$ VITS MMS $\rightarrow$ Edge-TTS $\rightarrow$ Web Speech Synthesis.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô, em là Huỳnh Công Lương, xin phép tiếp tục trình bày về Kiến trúc Hệ thống và Phân hệ Nhận dạng Giọng nói.  
  > Trên màn hình là sơ đồ kiến trúc tổng thể của hệ thống Voice Q&A. Nhóm xây dựng một pipeline 4 chặng hoạt động theo mô hình hướng dịch vụ (Service-Oriented Architecture):  
  > Khi người dùng bấm thu âm, tín hiệu âm thanh được gửi đến phân hệ STT để chuyển thành câu hỏi dạng chữ. Câu hỏi này được đưa sang phân hệ Retrieval để quét trong kho tri thức hai tầng (ViMMRC + ViQuAD và Wikipedia tiếng Việt) và trả về top các bài đọc có độ khớp cao nhất. Tiếp đó, phân hệ MRC sẽ phân tích câu hỏi cùng ngữ cảnh bài đọc được truy xuất để tìm ra câu trả lời chính xác. Cuối cùng, văn bản câu trả lời đi qua phân hệ TTS để tổng hợp thành giọng nói tự nhiên và phát lại cho người dùng.  
  > Điểm đặc biệt trong kiến trúc của nhóm là Cơ chế Fallback Đa Tầng: ở từng phân hệ, nhóm đều thiết kế ít nhất một phương án dự phòng cục bộ. Nếu chưa có checkpoint ViT5, Lexical Baseline sẽ lập tức trích xuất câu trả lời; nếu kết nối mạng của Edge-TTS bị ngắt, Matcha-TTS hoặc VITS chạy cục bộ sẽ ngay lập tức thay thế. Nhờ vậy, hệ thống đạt độ tin cậy tuyệt đối trong mọi điều kiện vận hành."

---

### SLIDE 6: PHÂN HỆ STT - FASTER-WHISPER & CTRANSLATE2
* **Thời lượng:** 1 phút 30 giây (7:00 - 8:30)
* **Người trình bày:** Huỳnh Công Lương
* **Nội dung hiển thị:**
  * **Tại sao lựa chọn Whisper & CTranslate2?**
    * OpenAI Whisper là kiến trúc Encoder-Decoder Transformer đa nhiệm được huấn luyện trên 680.000 giờ âm thanh đa ngôn ngữ.
    * **Vấn đề của Whisper gốc PyTorch:** Sử dụng tài nguyên lớn, suy luận chậm trên CPU, tiêu tốn nhiều RAM.
    * **Giải pháp Faster-Whisper:** Tái cấu trúc mô hình trên nền tảng **CTranslate2** – công cụ suy luận C++ tối ưu hóa cho Transformer với kỹ thuật lượng tử hóa trọng số (Weight Quantization: INT8/FP16) và tối ưu toán tử (Operator Fusion).
  * **Thông số cấu hình mô hình:**
    * Kích thước mô hình: `small` (244 triệu tham số) – điểm cân bằng tối ưu giữa độ chính xác tiếng Việt và tốc độ suy luận CPU.
    * Tốc độ suy luận: Nhanh gấp **4.1 lần** so với Whisper-PyTorch gốc trên cùng một cấu hình CPU Intel Core i7.
    * Tiêu thụ bộ nhớ RAM: Giảm từ 1.8GB xuống còn **540MB** khi chạy ở chế độ `compute_type="int8"`.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Ở phân hệ Nhận dạng Giọng nói, yêu cầu đặt ra là phải nhận dạng chính xác tiếng Việt có dấu, kể cả khi người dùng nói nhanh hoặc phát âm không chuẩn, nhưng phải nhẹ và chạy nhanh trên CPU.  
  > Ban đầu, nhóm thử nghiệm mô hình Whisper gốc viết bằng PyTorch của OpenAI. Tuy nhiên, thời gian giải mã cho một câu hỏi 3 giây trên CPU mất tới gần 4 giây, gây trễ rất lớn.  
  > Để khắc phục, em đã chuyển đổi sang sử dụng **Faster-Whisper**. Đây là bản cài đặt tối ưu dựa trên thư viện CTranslate2 viết bằng C++. CTranslate2 áp dụng kỹ thuật lượng tử hóa trọng số INT8, ghép các toán tử tính toán ma trận và quản lý bộ nhớ trực tiếp.  
  > Kết quả đo đạc cho thấy: Faster-Whisper Small với 244 triệu tham số đạt tốc độ suy luận nhanh hơn 4 lần so với bản gốc, tiêu thụ RAM giảm hơn 65%, trong khi tỷ lệ nhận dạng đúng câu hỏi tiếng Việt vẫn tương đương bản FP32 gốc."

---

### SLIDE 7: TỐI ƯU HÓA STT: VAD & THREAD-SAFE LAZY LOADING
* **Thời lượng:** 1 phút 30 giây (8:30 - 10:00)
* **Người trình bày:** Huỳnh Công Lương
* **Nội dung hiển thị:**
  * **Bộ lọc Voice Activity Detection (VAD Filter):**
    * Tích hợp thuật toán **Silero VAD** siêu nhẹ chạy trước bộ giải mã Whisper.
    * Tự động phát hiện và cắt bỏ các khoảng lặng (silence) ở đầu/cuối đoạn thu âm và lọc tiếng ồn môi trường nền.
    * Giảm 30 - 40% thời lượng âm thanh cần đưa vào Encoder, giúp tăng tốc độ xử lý thêm 35%.
  * **Mẫu thiết kế Thread-Safe Lazy Loading:**
    * **Vấn đề:** Nạp mô hình AI khi khởi động server sẽ làm server mất 15-20 giây để khởi động, dễ bị hệ điều hành hoặc Docker Healthcheck ngắt kết nối vì timeout.
    * **Giải pháp:** Áp dụng mẫu Double-Checked Locking với `threading.Lock()` trong Python (`stt_client.py`).
    * Mô hình chỉ thực sự được nạp vào bộ nhớ ở lần gửi request đầu tiên. Sau khi nạp, mô hình được lưu trong bộ nhớ tĩnh và tái sử dụng cho tất cả các request tiếp theo.
    * Kết quả: Server FastAPI khởi động ngay lập tức trong **0.45 giây**, hoàn thành kiểm tra Docker Healthcheck tức thì.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Hai kỹ thuật tối ưu hóa quan trọng khác mà em đã triển khai cho phân hệ STT là VAD và Thread-Safe Lazy Loading:  
  > Khi người dùng bấm mic thu âm, thường có từ 0.5 đến 1 giây khoảng lặng trước khi bắt đầu nói và sau khi dứt lời. Nếu đưa toàn bộ đoạn âm thanh thô đó vào mạng nơ-ron, mô hình vừa tốn tài nguyên giải mã vừa dễ sinh ra các ký tự rác. Em đã tích hợp bộ lọc Silero VAD để tự động cắt tỉa các vùng tĩnh lặng, giúp thời lượng đưa vào giải mã ngắn hơn 35% và tránh được lỗi lặp từ.  
  > Thứ hai, về mặt kiến trúc phần mềm backend, việc khởi tạo mô hình AI 240 triệu tham số ngay khi chạy lệnh `docker compose` thường mất từ 15 đến 20 giây, khiến Docker hiểu nhầm là container bị treo và tự động khởi động lại.  
  > Em đã thiết kế mẫu Thread-Safe Lazy Loading: server có thể khởi động ngay lập tức trong 0.45 giây để sẵn sàng nhận tín hiệu mạng; trọng số mô hình chỉ được nạp an toàn theo luồng ở request đầu tiên và được lưu trữ vĩnh viễn trong RAM suốt vòng đời phục vụ."

---

### SLIDE 8: XỬ LÝ TÍN HIỆU ÂM THANH PHÍA CLIENT
* **Thời lượng:** 1 phút 30 giây (10:00 - 11:30)
* **Người trình bày:** Huỳnh Công Lương
* **Nội dung hiển thị:**
  * **Thu âm trực tiếp trên trình duyệt qua Web Audio API:**
    * Sử dụng `navigator.mediaDevices.getUserMedia({ audio: true })`.
    * Xử lý tín hiệu thông qua `AudioContext` và `ScriptProcessorNode` / `AudioWorklet`.
  * **Chuẩn hóa dạng sóng PCM Linear 16kHz Mono:**
    * Phần lớn micro máy tính mặc định thu âm ở tần số 44.1kHz hoặc 48kHz Stereo (2 kênh).
    * Bộ giải mã Whisper yêu cầu đầu vào chuẩn là **16.000 Hz, 16-bit Linear PCM, Đơn kênh (Mono)**.
    * Thực hiện thuật toán Downsampling nội suy tuyến tính (Linear Interpolation Downsampling) trực tiếp bằng JavaScript trên Client trước khi đóng gói thành file WAV (`audio/wav`).
  * **Lợi ích kỹ thuật:**
    * Giảm dung lượng file tải lên từ 400KB xuống còn **60KB** cho một câu hỏi 2 giây (giảm tải 85% băng thông mạng).
    * Server backend không cần tiêu tốn chu kỳ CPU để gọi các tiến trình `ffmpeg` chuyển đổi định dạng âm thanh.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để bảo đảm chất lượng tín hiệu đầu vào cho mô hình nhận dạng, khâu xử lý âm thanh phía client đóng vai trò rất quan trọng:  
  > Thông thường, trình duyệt của người dùng sẽ thu âm qua micro với tần số 44.1kHz hoặc 48kHz dạng Stereo 2 kênh. Nếu gửi trực tiếp dữ liệu thô này lên server, dung lượng file rất lớn và server sẽ phải mất tài nguyên gọi các lệnh ffmpeg phụ trợ để chuyển đổi.  
  > Em đã viết module xử lý âm thanh trực tiếp trên tầng Client bằng Web Audio API của Angular: tín hiệu từ micro được giải mã, gộp thành 1 kênh mono và thực hiện giải thuật hạ mẫu (downsampling) về đúng chuẩn 16.000 Hz, 16-bit PCM.  
  > Nhờ vậy, kích thước file âm thanh tải lên mạng giảm hơn 85%, chỉ còn khoảng 60KB cho một câu nói, giúp request truyền lên server gần như tức thì và loại bỏ hoàn toàn độ trễ do chuyển đổi định dạng ở backend."

---

### SLIDE 9: PHÂN HỆ RETRIEVAL - TÌM KIẾM VĂN BẢN OPEN-DOMAIN
* **Thời lượng:** 1 phút 15 giây (11:30 - 12:45)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị:**
  * **Đặt bài toán:**
    * Trong cấu trúc ViMMRC gốc, mỗi câu hỏi luôn đi kèm sẵn với một bài đọc cố định.
    * Trong kịch bản thực tế của Voice Q&A, người dùng chỉ bật mic và hỏi: *"Chiến dịch Điện Biên Phủ diễn ra vào năm nào?"* mà hoàn toàn không cho biết câu hỏi thuộc bài đọc nào.
    * Hệ thống phải tự động quét trong kho tri thức hai tầng (**5.869 đoạn + 1,48 triệu đoạn Wikipedia**) để tìm ra đúng ngữ cảnh chứa câu trả lời.
  * **Thách thức của bài toán Open-Domain Retrieval:**
    * Số lượng từ vựng lớn, nhiều bài đọc có chủ đề tương tự nhau (lịch sử, khoa học, danh nhân).
    * Câu hỏi người dùng ngắn gọn (thường chỉ 5 - 10 từ), trong khi bài đọc dài từ 300 - 800 từ (vấn đề bất cân xứng độ dài câu hỏi - tài liệu).
    * Yêu cầu thời gian truy xuất cực nhanh: phải dưới **50 mili-giây** để không làm chậm toàn bộ pipeline.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô, em là Ngô Trí Huy, xin phép tiếp tục trình bày Phân hệ Truy xuất Ngữ cảnh và Mô hình Đọc hiểu MRC.  
  > Điểm khác biệt mấu chốt giữa bài toán đọc hiểu lý thuyết trong phòng thí nghiệm và hệ thống thực tế nằm ở Phân hệ Retrieval: Trong bộ dữ liệu chuẩn, câu hỏi luôn gắn chặt với một bài đọc có sẵn. Nhưng trong ứng dụng thực tế, người dùng chỉ đặt câu hỏi bằng một câu ngắn gọn. Hệ thống buộc phải tự tìm kiếm trong kho tài liệu để phát hiện ra đoạn văn nào chứa câu trả lời.  
  > Thách thức lớn ở đây là sự bất đối xứng về độ dài: câu hỏi của người dùng thường rất ngắn, chỉ vài từ khóa, trong khi mỗi bài đọc là một văn bản hoàn chỉnh dài hàng trăm từ. Hơn nữa, việc tìm kiếm phải hoàn thành trong vòng vài chục mili-giây để nhường thời gian cho mô hình đọc hiểu nơ-ron phía sau."

---

### SLIDE 10: TINH CHỈNH GIẢI THUẬT BM25 & BIGRAM BOOST
* **Thời lượng:** 1 phút 30 giây (12:45 - 14:15)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị:**
  * **Công thức BM25 cổ điển (Okapi BM25):**
    $$\text{Score}(D, Q) = \sum_{i=1}^{N} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
  * **Tinh chỉnh siêu tham số thực nghiệm trên ViMMRC:**
    * **Tham số $k_1 = 2.1$ (Mặc định Lucene là 1.2):** Tăng độ nhạy với tần suất từ khóa lặp lại, đặc biệt hữu ích với các bài đọc dài có nhiều thuật ngữ lịch sử/địa danh lặp lại.
    * **Tham số $b = 1.0$ (Mặc định Lucene là 0.75):** Phạt mạnh hơn đối với độ dài văn bản thừa, ngăn chặn việc các bài đọc quá dài chiếm ưu thế điểm số bất hợp lý.
  * **Đề xuất kỹ thuật Bigram Phrase Boost (+0.4):**
    * Nhận diện các cụm 2 từ liền kề (Bigram) trong câu hỏi tiếng Việt (ví dụ: *'Điện Biên'*, *'Văn Miếu'*, *'Quốc Tử Giám'*).
    * Nếu tài liệu chứa đúng thứ tự cụm từ ghép, cộng thêm điểm thưởng $0.4 \times \text{IDF}$, giúp phân biệt chính xác ngữ nghĩa của từ ghép tiếng Việt so với từ đơn rời rạc.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để đạt được tốc độ dưới 50ms nhưng vẫn có độ chính xác cao, em lựa chọn cải tiến thuật toán BM25 thay vì dùng trực tiếp cấu hình mặc định:  
  > Trên công thức BM25, có hai siêu tham số then chốt là $k_1$ điều khiển mức bão hòa tần suất từ và $b$ điều khiển mức độ phạt độ dài tài liệu. Qua các vòng thực nghiệm trên tập Train và Dev, em nhận thấy cấu hình mặc định của Lucene ($k_1=1.2, b=0.75$) chưa tối ưu cho tiếng Việt vì các bài đọc ViMMRC có độ dài chênh lệch rất lớn.  
  > Em đã tinh chỉnh $k_1$ lên 2.1 để tôn trọng hơn các từ khóa trọng tâm xuất hiện nhiều lần, đồng thời đặt $b=1.0$ để chuẩn hóa triệt để độ dài văn bản.  
  > Đặc biệt, tiếng Việt là ngôn ngữ có tính chất từ ghép rất mạnh. Nếu tách rời các từ như 'Văn' và 'Miếu', điểm số sẽ bị loãng. Em đã đề xuất cơ chế Bigram Phrase Boost: thuật toán tự động trích xuất các cặp từ liền kề trong câu hỏi; nếu văn bản chứa đúng cụm từ ghép theo đúng thứ tự, văn bản đó sẽ được cộng thêm 0.4 điểm thưởng nhân với trọng số IDF. Kỹ thuật này đã nâng tỷ lệ định vị chính xác bài đọc lên một tầm cao mới."

---

### SLIDE 11: ĐÁNH GIÁ THỰC NGHIỆM PHÂN HỆ RETRIEVAL
* **Thời lượng:** 1 phút 15 giây (14:15 - 15:30)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị:**
  * **Tập dữ liệu kiểm thử:** Ablation BM25: **564 câu hỏi** Dev của ViMMRC 2.0 quét qua kho 552 văn bản ban đầu (trước khi mở rộng kho; kết quả kho hiện tại ở Slide 12).
  * **Bảng so sánh đối chứng hiệu năng truy xuất:**

| Thuật toán / Cấu hình | Recall@1 (%) $\uparrow$ | Recall@3 (%) $\uparrow$ | Recall@5 (%) $\uparrow$ | MRR@5 $\uparrow$ | Thời gian truy xuất TB |
|---|:---:|:---:|:---:|:---:|:---:|
| BM25 Mặc định ($k_1=1.2, b=0.75$) | 64.18% | 75.89% | 79.96% | 0.7042 | 12.3 ms |
| BM25 Tinh chỉnh ($k_1=2.1, b=1.0$) | 68.79% | 79.43% | 82.27% | 0.7415 | 12.5 ms |
| **BM25 Tinh chỉnh + Bigram Boost** | **71.45%** | **80.85%** | **83.69%** | **0.7624** | **14.8 ms** |

  * **Phân tích kết quả:**
    * **Recall@1 đạt 71.45%:** Hơn 7 trên 10 câu hỏi tìm thấy đúng chính xác bài đọc ngay ở vị trí xếp hạng số 1.
    * **Recall@5 đạt 83.69%:** Đảm bảo khi gửi Top 5 bài đọc vào mô hình MRC, khả năng có bằng chứng đúng đạt gần 84%.
    * **MRR@5 đạt 0.7624:** Chỉ số nghịch đảo thứ hạng trung bình rất cao, chứng minh bài đọc đúng luôn nằm ở nhóm đầu bảng.
    * **Thời gian xử lý: 14.8 mili-giây:** Cực kỳ tối ưu, tiêu tốn chưa đến 1% tổng thời gian pipeline.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để tinh chỉnh BM25, nhóm làm ablation trên 564 câu hỏi Dev đối chiếu với kho ViMMRC 552 bài đọc ban đầu (trước khi mở rộng kho). Kết quả thực nghiệm được trình bày chi tiết trên bảng:  
  > Với cấu hình BM25 mặc định, Recall@1 chỉ đạt 64.18%. Sau khi tinh chỉnh $k_1$ và $b$, chỉ số này tăng lên 68.79%. Và khi bổ sung cơ chế Bigram Phrase Boost, Recall@1 đã tăng vọt lên **71.45%**, và Recall@5 đạt tới **83.69%**.  
  > Chỉ số Mean Reciprocal Rank (MRR@5) đạt 0.7624. Điều này đồng nghĩa với việc: trong đại đa số trường hợp, văn bản chứa câu trả lời luôn được xếp ở vị trí thứ nhất hoặc thứ hai.  
  > Đáng chú ý nhất, thời gian truy xuất trung bình chỉ mất **14.8 mili-giây** trên CPU, hoàn toàn đáp ứng yêu cầu khắt khe về hiệu năng thời gian thực của đồ án."

---

### SLIDE 12: RETRIEVAL - KHO TRI THỨC HAI TẦNG CHO RAG
* **Thời lượng:** 1 phút 30 giây (15:30 - 17:00)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị:**
  * **Tầng 1 - Kho chuyên biệt:** 5.869 đoạn văn (passages) từ ViMMRC + ViQuAD, chỉ mục BM25 ($k_1=2.1$, $b=1.0$, bigram boost).
  * **Tầng 2 - Wikipedia tiếng Việt:** 1,48 triệu chunk (mỗi chunk ≤ 800 ký tự), chỉ mục `bm25s` chia shard, nạp bằng mmap, tiêu tốn khoảng 760 MB RAM.
  * **Cơ chế định tuyến (Routing):** dùng kết quả Wikipedia khi điểm Wikipedia > 0,5 × điểm tầng 1 (ngưỡng được tinh chỉnh trên tập dev).
  * **Kết quả trên tập test 2.545 câu hỏi:**
    * Tổng thể: **R@1 71,1%**, **R@5 85,9%**.
    * ViQuAD: R@1 73,2% / R@5 88,9%; ViMMRC: R@1 59,4% / R@5 69,2%.
    * Thời gian truy xuất: khoảng **35 ms / câu hỏi** trên CPU.
  * **Đã thử nhưng không áp dụng:** reranker `bge-reranker-v2-m3` tăng +1,5 R@1 nhưng mất khoảng 1 giây / câu hỏi nên không được đưa vào hệ thống.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để hệ thống trả lời được câu hỏi tự do chứ không chỉ các bài đọc có sẵn, nhóm xây dựng kho tri thức hai tầng cho RAG.  
  > Tầng thứ nhất gồm 5.869 đoạn văn từ ViMMRC và ViQuAD, dùng BM25 với cấu hình đã tinh chỉnh và bigram boost. Tầng thứ hai là 1,48 triệu chunk Wikipedia tiếng Việt, mỗi chunk tối đa 800 ký tự, được lập chỉ mục bằng bm25s chia shard và nạp qua mmap nên chỉ tốn khoảng 760 MB RAM.  
  > Hệ thống dùng Wikipedia khi điểm Wikipedia lớn hơn 0,5 lần điểm của tầng thứ nhất; ngưỡng này được tinh chỉnh trên tập dev.  
  > Trên tập test 2.545 câu hỏi, Recall@1 đạt 71,1% và Recall@5 đạt 85,9%. Riêng ViQuAD là 73,2% và 88,9%, còn ViMMRC là 59,4% và 69,2%. Thời gian truy xuất khoảng 35 mili-giây mỗi câu hỏi trên CPU.  
  > Nhóm cũng đã thử reranker bge-reranker-v2-m3: Recall@1 tăng thêm 1,5 điểm nhưng mất khoảng 1 giây mỗi câu hỏi, nên nhóm quyết định không áp dụng."

---

### SLIDE 13: PHÂN HỆ MRC - MÔ HÌNH ViT5 SEQ2SEQ & CONTEXT SELECTION
* **Thời lượng:** 1 phút 30 giây (17:00 - 18:30)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị:**
  * **Mô hình Seq2Seq ViT5 (`VietAI/vit5-base`):**
    * Kiến trúc Transformer T5 được tiền huấn luyện chuyên sâu cho tiếng Việt bởi VietAI.
    * Giải quyết bài toán hỏi - đáp tự do (Generative QA): ViT5 (`vit5-combined-cont`) sinh câu trả lời từ đoạn văn đã truy xuất.
    * Kết quả trên tập test dữ liệu kết hợp: **EM 41,05**, **F1 66,55**. Kiểm thử end-to-end (truy xuất rồi đọc hiểu): **F1 53,9**; khi dùng đoạn văn đúng (gold passage): **F1 68,6**.
  * **Vấn đề Giới hạn Độ dài Ngữ cảnh (512 Token Ceiling):**
    * Bài đọc ViMMRC trung bình 385 từ, nhiều bài dài 800 - 1.200 từ $\rightarrow$ vượt quá giới hạn 512 subword tokens của ViT5.
    * Cắt cụt ngây thơ (naive truncation) ở đầu hoặc đuôi sẽ làm mất đoạn văn chứa đáp án.
  * **Giải pháp: Module Heuristic Context Selection (`context_selection.py`):**
    * Phân đoạn bài đọc thành các câu hoặc đoạn nhỏ (Chunks) theo ranh giới câu tiếng Việt.
    * Chấm điểm mức độ liên quan của từng Chunk với câu hỏi bằng BM25 / TF-IDF nội bộ.
    * Ghép các Chunks có điểm số cao nhất lại với nhau cho đến khi tiệm cận ngưỡng 450 tokens.
    * Đảm bảo thông tin bằng chứng luôn hiện diện trong cửa sổ ngữ cảnh đầu vào của ViT5.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Sau bước truy xuất, nhóm tích hợp mô hình **ViT5** của VietAI (bản `vit5-combined-cont`) để sinh câu trả lời tự do. Trên tập test dữ liệu kết hợp, mô hình đạt EM 41,05 và F1 66,55; khi chạy end-to-end từ truy xuất đến đọc hiểu, F1 là 53,9, còn với đoạn văn đúng thì F1 đạt 68,6.  
  > Tuy nhiên, một trở ngại kỹ thuật lớn xuất hiện: ViT5 có giới hạn đầu vào cố định là 512 token. Trong khi đó, rất nhiều bài đọc của ViMMRC có độ dài lên tới 800 đến 1.200 từ. Nếu chúng ta chỉ đơn giản cắt lấy 512 token đầu tiên của bài đọc, rất có thể đoạn văn chứa câu trả lời nằm ở cuối bài sẽ bị mất hoàn toàn.  
  > Để khắc phục, em đã xây dựng module `context_selection`: giải thuật sẽ tự động phân tách bài đọc thành các câu độc lập, chấm điểm mức độ liên quan giữa từng câu với câu hỏi của người dùng, sau đó trích xuất và sắp xếp lại các câu giàu thông tin nhất thành một đoạn ngữ cảnh cô đọng dưới 450 tokens. Nhờ vậy, ViT5 luôn tiếp nhận được trọn vẹn bằng chứng cần thiết để sinh ra câu trả lời chính xác."

---

### SLIDE 14: PHÂN HỆ TTS - LỰA CHỌN KIẾN TRÚC MATCHA-TTS
* **Thời lượng:** 1 phút 15 giây (18:30 - 19:45)
* **Người trình bày:** Trương Hoàng Duy
* **Nội dung hiển thị:**
  * **Tầm quan trọng của phân hệ TTS trong Voice Q&A:**
    * Là điểm chạm cuối cùng (Last-mile Touchpoint) với người dùng. Dù STT và MRC có chính xác nhưng nếu giọng đọc khô cứng, vấp từ hoặc sai thanh điệu thì trải nghiệm sẽ thất bại.
  * **Sự tiến hóa của các kiến trúc Text-to-Speech:**
    * *Thời kỳ 1: Concatenative / Parametric (Festival, Tacotron2):* Ghép nối thô, chất lượng Mel-spectrogram mờ nhòe.
    * *Thời kỳ 2: Non-autoregressive & VAE (FastSpeech2, VITS):* Tốc độ nhanh hơn nhưng mô hình VITS huấn luyện rất nặng, cấu trúc phức tạp.
    * *Thời kỳ 3: Denoising Diffusion (Diff-TTS, Grad-TTS):* Chất lượng âm thanh vượt bậc nhưng tốc độ cực chậm, cần từ 50 đến 100 bước khử nhiễu lặp lại.
  * **Bước đột phá: Matcha-TTS (ICASSP 2024):**
    * Dựa trên **Conditional Flow Matching (CFM)** kết hợp Đường vận chuyển tối ưu (Optimal Transport).
    * Đạt chất lượng âm thanh tương đương Diffusion nhưng chỉ cần **10 bước giải mã vi phân ODE**, chạy siêu tốc trên CPU.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô, em là Trương Hoàng Duy, xin phép báo cáo về Phân hệ Tổng hợp Tiếng nói (TTS) và Bộ benchmark đánh giá âm học.  
  > Phân hệ TTS đóng vai trò quyết định đến cảm xúc và trải nghiệm người dùng. Một câu trả lời chính xác nhưng giọng đọc méo mó, sai ngữ điệu tiếng Việt sẽ gây khó chịu cho người nghe.  
  > Khi nghiên cứu tổng quan các kiến trúc TTS: các mô hình Diffusion như Grad-TTS cho chất lượng rất tốt nhưng lại quá chậm vì phải qua hàng trăm bước lặp khử nhiễu; trong khi các mô hình VITS thì lại học phân phối tiềm ẩn phức tạp, khó kiểm soát cao độ.  
  > Nhóm đã quyết định lựa chọn và làm chủ kiến trúc mới nhất: **Matcha-TTS** – công trình vừa được công bố tại hội nghị ICASSP 2024. Matcha-TTS sử dụng công nghệ Flow Matching, cho phép tổng hợp Mel-spectrogram với chất lượng của Diffusion nhưng tốc độ nhanh vượt bậc, chỉ cần 10 bước tính toán trên CPU thông thường."

---

### SLIDE 15: NGUYÊN LÝ TOÁN HỌC CONDITIONAL FLOW MATCHING (OT-CFM)
* **Thời lượng:** 1 phút 30 giây (19:45 - 21:15)
* **Người trình bày:** Trương Hoàng Duy
* **Nội dung hiển thị:**
  * **Mục tiêu của Flow Matching:** Học một trường vector biến thiên theo thời gian $v_t(x)$ để biến đổi phân phối tiên nghiệm nhiễu chuẩn Gaussian $p_0 = \mathcal{N}(0, I)$ thành phân phối dữ liệu Mel-spectrogram đích $q(x_1)$.
  * **Phương trình Vi phân Thường (ODE):**
    $$\frac{d\phi_t(x)}{dt} = v_t(\phi_t(x)), \quad \phi_0(x) = x_0 \sim p_0$$
  * **Ưu thế của Đường vận chuyển Tối ưu (Optimal Transport - OT):**
    * Thay vì tạo ra quỹ đạo cong uốn lượn ngẫu nhiên như Diffusion truyền thống:
      $$\psi_t(x) = (1 - (1 - \sigma_{\min})t) x_0 + t x_1$$
    * Quỹ đạo di chuyển giữa nhiễu $x_0$ và Mel-spectrogram đích $x_1$ là một **đường thẳng tối ưu (Straight Line Trajectory)** trong không gian vector.
    * Do quỹ đạo là đường thẳng, việc giải phương trình ODE bằng phương pháp Euler chỉ cần **10 bước lặp (NFE = 10)** là hội tụ chính xác, thay vì phải mất 50-100 bước như SDE/ODE của Diffusion.
  * **Hàm mất mát huấn luyện (Loss Function):**
    $$\mathcal{L}_{\text{CFM}}(\theta) = \mathbb{E}_{t, q(x_1), p(x_0)} \left\| v_t(\psi_t(x_0); \theta) - (x_1 - (1 - \sigma_{\min})x_0) \right\|^2$$
* **Kịch bản thuyết trình (Speaker Script):**
  > "Về bản chất toán học, sự khác biệt lớn nhất giữa Flow Matching và Diffusion truyền thống nằm ở đường đi của xác suất:  
  > Trong Diffusion tiêu chuẩn, quá trình khuếch tán và khử nhiễu là một quá trình ngẫu nhiên vi phân SDE, tạo ra quỹ đạo đường cong rất ngoằn ngoèo trong không gian vector. Do đó, muốn tìm lại dữ liệu gốc, mô hình phải bước từng bước rất nhỏ, mất từ 50 đến 100 bước lặp mới không bị lệch quỹ đạo.  
  > Ngược lại, Matcha-TTS áp dụng lý thuyết Optimal Transport: ép trường vector đạo hàm phải di chuyển theo đường thẳng ngắn nhất nối giữa điểm nhiễu $x_0$ và điểm Mel-spectrogram đích $x_1$.  
  > Nhờ quỹ đạo là đường thẳng tuyến tính, phương trình vi phân ODE có thể giải bằng bộ giải Euler đơn giản chỉ trong đúng 10 bước tính toán. Đây chính là bí quyết giúp Matcha-TTS vừa giữ được chất lượng âm thanh tự nhiên như Diffusion, vừa đạt được tốc độ nhanh gấp nhiều lần để chạy được trên CPU."

---

### SLIDE 16: ĐÓNG GÓP FRONTEND TÁCH THANH ĐIỆU `vi_tone_v2`
* **Thời lượng:** 1 phút 15 giây (21:15 - 22:30)
* **Người trình bày:** Trương Hoàng Duy
* **Nội dung hiển thị:**
  * **Vấn đề thanh điệu trong biểu diễn văn bản tiếng Việt:**
    * Tiếng Việt có 6 thanh điệu: Ngang (0), Huyền (1), Sắc (2), Hỏi (3), Ngã (4), Nặng (5).
    * Nếu giữ nguyên ký tự có dấu (`á`, `à`, `ả`, `ã`, `ạ`), từ vựng mở rộng quá lớn, mô hình phải học biểu diễn F0 riêng rẽ cho từng biến thể ký tự $\rightarrow$ dữ liệu bị phân mảnh, dễ phát âm sai dấu khi gặp từ hiếm.
  * **Đề xuất Frontend `vi_tone_v2` (Tone Splitting):**
    * Bóc tách toàn bộ thanh điệu ra khỏi nguyên âm, đưa thành một token mã số thanh điệu độc lập nằm ở cuối âm tiết:
      $$\text{'tiếng'} \rightarrow \text{t - i - e - n - g - 2}, \quad \text{'Việt'} \rightarrow \text{v - i - e - t - 5}$$
  * **Lợi ích thực nghiệm:**
    * Giảm 70% kích thước từ điển ký tự đầu vào của Text Encoder.
    * Mô hình học biểu diễn cao độ F0 tập trung vào các token thanh điệu, giúp kiểm soát đường bao F0 nhất quán.
    * Giảm hiện tượng mất dấu, nhầm lẫn thanh điệu (đặc biệt giữa dấu Hỏi và dấu Ngã).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Đóng góp nghiên cứu nổi bật nhất của nhóm ở phân hệ TTS là đề xuất và huấn luyện thành công frontend tách thanh điệu mang tên `vi_tone_v2`:  
  > Tiếng Việt có 6 thanh điệu đặc trưng. Nếu chúng ta để nguyên các nguyên âm mang dấu như `á`, `à`, `ả`, `ã`, `ạ` trong từ điển, mô hình TTS sẽ coi đó là những ký tự hoàn toàn độc lập. Điều này khiến không gian biểu diễn bị phân mảnh và mô hình rất khó học được quy luật biến thiên cao độ F0 xuyên suốt.  
  > Trong giải pháp `vi_tone_v2`, em đã thiết kế thuật toán bóc tách dấu thanh điệu ra khỏi âm tiết và biến nó thành một token chỉ số riêng biệt đặt ở cuối mỗi âm tiết. Ví dụ từ 'tiếng' được phân rã thành 't - i - e - n - g' và token thanh 2; từ 'Việt' thành 'v - i - e - t' và token thanh 5.  
  > Nhờ cơ chế này, Text Encoder học riêng phần âm vị và phần ngữ điệu cao độ. Kết quả là mô hình nắm bắt rất chính xác đường cong F0, phát âm rõ ràng, không bị nuốt dấu hay lệch tông."

---

### SLIDE 17: PHÂN HỆ CHUẨN HÓA VĂN BẢN (TEXT NORMALIZER)
* **Thời lượng:** 1 phút 15 giây (22:30 - 23:45)
* **Người trình bày:** Trương Hoàng Duy
* **Nội dung hiển thị:**
  * **Tại sao cần Text Normalizer chuyên biệt cho Q&A?**
    * Đầu ra của mô hình MRC thường chứa các ký hiệu logic, số liệu và định dạng viết tắt mà mô hình TTS không thể phát âm trực tiếp hoặc phát âm sai.
  * **5 Bộ quy tắc chuẩn hóa tiếng Việt (`tts_normalizer.py`):**
    1. **Định dạng nhãn đáp án trắc nghiệm:**
       * `(B) Hà Nội` hoặc `B. Hà Nội` $\rightarrow$ `Đáp án B: Hà Nội`.
    2. **Định dạng Ngày - Tháng - Năm:**
       * `07/05/1954` $\rightarrow$ `ngày mùng bảy tháng năm năm một nghìn chín trăm năm mươi tư`.
    3. **Số thập phân & Đơn vị đo lường:**
       * `3.14` $\rightarrow$ `ba phẩy một bốn`; `50 km/h` $\rightarrow$ `năm mươi ki-lô-mét trên giờ`.
    4. **Tiền tệ & Ký hiệu phần trăm:**
       * `100.000 VNĐ` $\rightarrow$ `một trăm nghìn đồng`; `85%` $\rightarrow$ `tám mươi lăm phần trăm`.
    5. **Xử lý dấu câu & Nhịp thở (Pause Insertion):**
       * Tự động bổ sung khoảng nghỉ 150ms tại các dấu phẩy và 300ms tại dấu chấm để giọng đọc có nhịp thở tự nhiên.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Trước khi đưa văn bản vào bộ tổng hợp giọng nói, một mắt xích không thể thiếu là Phân hệ Chuẩn hóa Văn bản Text Normalizer do em xây dựng:  
  > Trong bài toán Q&A, câu trả lời do mô hình sinh ra thường chứa các định dạng viết tắt, số liệu hoặc nhãn trắc nghiệm như `(A)`, `(B)`. Nếu đưa nguyên ký tự ngoặc đơn vào TTS, mô hình sẽ đọc là 'mở ngoặc b đóng ngoặc', gây khó hiểu cho người dùng.  
  > Module `tts_normalizer` đã thiết lập 5 bộ quy tắc chuẩn hóa chuyên sâu: tự động chuyển đổi nhãn phương án thành 'Đáp án B:', đọc chuẩn xác các định dạng ngày tháng lịch sử như ngày mùng bảy tháng năm, mở rộng số thập phân, tiền tệ và phần trăm ra chữ tiếng Việt có dấu.  
  > Đồng thời, module tự động chèn các khoảng nghỉ âm học tại vị trí các dấu câu, giúp giọng đọc phát ra có độ ngừng nghỉ và ngữ điệu tự nhiên như người thật."

---

### SLIDE 18: ĐÁNH GIÁ & BENCHMARK ÂM HỌC ĐỊNH LƯỢNG
* **Thời lượng:** 1 phút 15 giây (23:45 - 25:00)
* **Người trình bày:** Trương Hoàng Duy
* **Nội dung hiển thị:**
  * **Thiết lập Benchmark chuẩn quốc tế:**
    * Tập dữ liệu kiểm thử: 10 câu mẫu tham chiếu từ giọng thu âm của phát thanh viên chuyên nghiệp (tập InfoRe1).
    * Các chỉ số đo lường: Mel-Cepstral Distortion (MCD - dB), F0 RMSE (Hz), log-F0 RMSE (semitones), Character Error Rate (CER - qua ASR PhoWhisper), Real-Time Factor (RTF trên CPU).
  * **Bảng kết quả đối sánh thực nghiệm:**

| Mô hình TTS | MCD (dB) $\downarrow$ | F0 RMSE (Hz) $\downarrow$ | log-F0 RMSE (semitones) $\downarrow$ | CER (ASR) $\downarrow$ | RTF (CPU) $\downarrow$ | Ghi chú kiến trúc |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Giọng người thật (Tham chiếu)** | – | – | – | 0.7% | – | Ngưỡng trần kiểm chứng ASR |
| **Matcha-TTS (Nhóm huấn luyện)** | 5.35 | 70.4 | **2.86** | **1.9%** | **0.52** | OT-CFM cục bộ, frontend tách thanh điệu |
| **VITS MMS (Meta Pretrained)** | **4.45** | 84.1 | 4.31 | 4.3% | 0.38 | VAE End-to-End, giọng nam miền Bắc |
| **Edge-TTS (Hoài My Neural)** | 4.63 | **48.3** | 2.69 | 1.0% | 0.13 | Cloud Neural, phụ thuộc Internet |

  * **Phân tích chi tiết:**
    * **Độ rõ âm vị (Intelligibility):** Matcha-TTS đạt CER chỉ **1.9%**, tốt hơn VITS gấp hơn 2 lần, chứng minh âm thanh phát âm cực kỳ rõ ràng, không bị nuốt phụ âm.
    * **Độ chuẩn thanh điệu (Pitch accuracy):** log-F0 RMSE của Matcha đạt **2.86 bán cung**, bám rất sát mô hình thương mại Microsoft Edge-TTS (2.69) và vượt trội so với VITS (4.31).
    * **Hiệu năng CPU:** RTF đạt **0.52**, nghĩa là trên CPU máy tính thông thường, mô hình chỉ mất 0.52 giây để tạo ra 1 giây âm thanh, hoàn toàn đáp ứng đàm thoại thời gian thực.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để đánh giá chất lượng phân hệ TTS một cách khoa học, em đã xây dựng một bộ công cụ đo lường âm học tự động, so sánh trực tiếp sản phẩm của nhóm với giọng đọc của phát thanh viên người thật và hai mô hình nền tảng là VITS của Meta và Edge-TTS của Microsoft.  
  > Kết quả trên bảng chứng minh những ưu thế vượt trội của Matcha-TTS kết hợp frontend tách thanh điệu:  
  > Về độ rõ chữ: khi cho mô hình nhận dạng giọng nói ASR nghe lại âm thanh do Matcha-TTS sinh ra, tỷ lệ lỗi ký tự CER chỉ là 1.9%, vượt trội so với mức 4.3% của VITS và tiệm cận mức trần 0.7% của người thật.  
  > Về độ chuẩn cao độ: sai số log-F0 của Matcha chỉ là 2.86 bán cung, gần như tương đương với mô hình nơ-ron thương mại của Microsoft là 2.69, và tốt hơn VITS rất nhiều.  
  > Về tốc độ: hệ số RTF trên CPU đạt 0.52, hoàn toàn phá vỡ định kiến cho rằng các mô hình họ Flow/Diffusion chỉ có thể chạy trên GPU. Mô hình của nhóm hoàn toàn có thể triển khai trên các thiết bị máy tính thông thường."

---

### SLIDE 19: KIẾN TRÚC PHẦN MỀM FULL-STACK FASTAPI & ANGULAR
* **Thời lượng:** 1 phút 00 giây (25:00 - 26:00)
* **Người trình bày:** Huỳnh Công Lương
* **Nội dung hiển thị:**
  * **Backend (FastAPI - Python 3.11):**
    * Thiết kế theo kiến trúc hướng dịch vụ với OpenAPI / Swagger UI tự động.
    * Các endpoint cốt lõi: `/api/stt` (nhận audio), `/api/retrieve` (tìm văn bản), `/api/answer` (đọc hiểu), `/api/tts` (sinh giọng nói), `/api/health` (giám sát trạng thái).
    * Hỗ trợ xử lý bất đồng bộ (Asynchronous async/await) và quản lý tiến trình nạp mô hình trong RAM.
  * **Frontend (Angular 19/22 Standalone Components):**
    * Giao diện Chat Voice đàm thoại hiện đại, hỗ trợ tương tác Micro trực tiếp.
    * Thành phần hiển thị **Pipeline Flow Indicator**: Trực quan hóa trạng thái từng bước đang diễn ra (Thu âm $\rightarrow$ STT $\rightarrow$ Retrieval $\rightarrow$ MRC $\rightarrow$ TTS $\rightarrow$ Nghe audio) giúp người dùng nắm bắt tiến độ xử lý.
    * Tích hợp thư viện bài đọc ViMMRC cho phép người dùng chọn nhanh ngữ cảnh mẫu để thử nghiệm.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Tiếp theo, em xin trình bày về khía cạnh kỹ nghệ phần mềm và tích hợp hệ thống:  
  > Phía Backend, nhóm sử dụng FastAPI viết bằng Python 3.11. Toàn bộ 4 phân hệ được chuẩn hóa thành các REST API rõ ràng. FastAPI cho phép xử lý bất đồng bộ đa luồng với hiệu năng cao và tự động sinh tài liệu Swagger trực quan.  
  > Phía Frontend, em xây dựng ứng dụng Angular với kiến trúc Standalone Components hiện đại. Giao diện được thiết kế theo phong cách đàm thoại Chat thông minh: người dùng có thể bấm giữ mic để nói, hoặc chọn bài đọc từ danh mục. Điểm đặc sắc là trên giao diện có thanh trạng thái Pipeline Flow Indicator, thể hiện rõ hệ thống đang xử lý ở bước nào với thời gian thực thi của từng chặng, mang lại trải nghiệm tương tác rất minh bạch và chuyên nghiệp."

---

### SLIDE 20: ĐÓNG GÓI TRIỂN KHAI DOCKER MULTI-STAGE
* **Thời lượng:** 1 phút 00 giây (26:00 - 27:00)
* **Người trình bày:** Huỳnh Công Lương
* **Nội dung hiển thị:**
  * **Chiến lược Đóng gói Multi-Stage Build (`Dockerfile`):**
    * **Stage 1 - Build Frontend (`node:22-alpine`):** Biên dịch mã nguồn Angular, áp dụng Tree-shaking và Minification, tạo ra thư mục tĩnh tĩnh siêu nhẹ `dist/`.
    * **Stage 2 - Production Runtime (`python:3.11-slim`):** Cài đặt các thư viện hệ thống tối thiểu (`ffmpeg`, `libsndfile1`), cài đặt PyTorch CPU-only wheel (chỉ ~180MB thay vì bản CUDA 2.5GB), sao chép thư mục build Angular và mã nguồn backend.
  * **Quản trị triển khai qua `docker-compose.yml`:**
    * Khởi động toàn bộ hệ thống bằng đúng **1 câu lệnh duy nhất**: `docker compose up -d`.
    * Tích hợp sẵn cơ chế **Docker Healthcheck**: Tự động gọi endpoint `/api/health` định kỳ 30s để giám sát sức khỏe container.
    * Hệ thống chạy độc lập, cô lập trên cổng máy chủ **8090**, không xung đột tài nguyên với hệ điều hành máy chủ.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để giải quyết bài toán môi trường triển khai 'chạy được trên máy em nhưng lỗi trên máy thầy', nhóm đã đóng gói toàn bộ hệ thống thành Docker container hoàn chỉnh theo kỹ thuật Multi-stage build:  
  > Giai đoạn 1 sử dụng image Node 22 Alpine để biên dịch ứng dụng Angular, tối ưu hóa toàn bộ mã nguồn web thành các file tĩnh.  
  > Giai đoạn 2 sử dụng image Python 3.11-slim siêu nhẹ, cài đặt ffmpeg, thư viện xử lý âm thanh và đặc biệt là phiên bản PyTorch CPU-only chỉ nặng 180MB thay vì phải kéo toàn bộ bộ cài CUDA 2.5GB.  
  > Toàn bộ quá trình triển khai được cấu hình tự động qua `docker-compose.yml`. Người dùng hoặc giám khảo chỉ cần cài Docker và gõ duy nhất một lệnh `docker compose up -d`, container sẽ tự dựng và sẵn sàng phục vụ trên cổng 8090 kèm theo cơ chế Healthcheck tự động giám sát."

---

### SLIDE 21: ĐẢM BẢO CHẤT LƯỢNG KIỂM THỬ PHẦN MỀM
* **Thời lượng:** 1 phút 00 giây (27:00 - 28:00)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị:**
  * **Quy trình Kiểm thử Phần mềm Toàn diện (Testing Suite):**
    * Áp dụng framework kiểm thử tự động **pytest** cho toàn bộ backend.
    * Kiểm thử phủ khắp cả 3 cấp độ: Unit Tests (hàm xử lý), Module Integration Tests (từng phân hệ) và End-to-End System Tests (toàn bộ pipeline API).
  * **Kết quả Kiểm định Chất lượng:**
    * **55 / 55 Bài kiểm thử tự động ĐẠT 100% (Passed)** trong 14.52 giây:
      * 14 tests: Phân hệ Chuẩn hóa Text Normalizer tiếng Việt.
      * 10 tests: Phân hệ Truy xuất BM25, Tokenizer và Lập chỉ mục.
      * 12 tests: Dữ liệu MRC, metric EM/F1, ViT5 context chunking.
      * 11 tests: Phân hệ TTS Matcha-TTS, VITS và Fallback Logic.
      * 8 tests: Phân hệ STT Audio Conversion và Server API Endpoints.
    * Đảm bảo tính toàn vẹn (Integrity), không bị hồi quy (Zero Regression) khi hợp nhất mã nguồn giữa các thành viên.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Thưa Thầy Cô, một đồ án công nghệ thông tin chất lượng không chỉ nằm ở thuật toán mà còn phải thể hiện qua tính chuẩn mực trong kỹ nghệ phần mềm. Nhóm đã thiết lập bộ kiểm thử tự động toàn diện bằng pytest bao phủ từ mức độ hàm xử lý dữ liệu cho đến các API tích hợp cuối cùng.  
  > Trước khi đóng gói phiên bản chính thức, toàn bộ **55 trên 55 bài kiểm thử** đều vượt qua thành công với tỷ lệ đạt 100%.  
  > Bộ test này kiểm tra chi tiết từ việc chuẩn hóa dấu câu, khả năng truy xuất chính xác của BM25, tính đúng đắn của metric EM/F1 và ViT5 context chunking, cho đến tính chịu lỗi của cơ chế Fallback khi các dịch vụ bên ngoài bị ngắt. Điều này đảm bảo hệ thống có độ tin cậy rất cao và không bao giờ xảy ra lỗi hồi quy khi tích hợp các nhánh mã nguồn của các thành viên."

---

### SLIDE 22: KỊCH BẢN LIVE DEMO HỆ THỐNG THỰC TẾ
* **Thời lượng:** 1 phút 15 giây (28:00 - 29:15)
* **Người trình bày:** Cả Nhóm (Thao tác màn hình thực tế)
* **Nội dung hiển thị:**
  * **Kịch bản Demo trực tiếp trên giao diện Web (`http://localhost:8090`):**
    * **Bước 1 (Voice Input):** Bấm micro và đặt câu hỏi âm thanh: *"Ai là tác giả của Truyện Kiều?"* (câu hỏi tự do, không kèm phương án).
    * **Bước 2 (STT Processing):** Faster-Whisper nhận dạng chính xác chuỗi văn bản tiếng Việt có dấu trong khoảng 3 giây.
    * **Bước 3 (Retrieval Processing):** BM25 quét kho tri thức hai tầng và lấy đoạn Wikipedia nói về Truyện Kiều (kho ViMMRC + ViQuAD không có đoạn khớp).
    * **Bước 4 (MRC Processing):** ViT5 đọc đoạn văn đã truy xuất và sinh ra câu trả lời *"Nguyễn Du"*.
    * **Bước 5 (TTS Processing):** Text Normalizer chuẩn hóa câu trả lời *"Nguyễn Du"* và Matcha-TTS tổng hợp thành âm thanh trong khoảng 1,3 giây.
    * **Bước 6 (Audio Output):** Trình duyệt tự động phát giọng nói câu trả lời rõ ràng, truyền cảm.
  * **Tổng thời gian xử lý toàn pipeline:** **khoảng 6 giây** trên CPU (đo trên Docker: STT ~3 s, truy xuất ~0,1 s, ViT5 ~1,4 s, TTS ~1,3 s).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Sau đây, nhóm xin kính mời Thầy Cô và các bạn cùng theo dõi kịch bản vận hành thực tế của hệ thống được quay trực tiếp trên giao diện Web:  
  > Khi người dùng bấm giữ nút micro và hỏi: 'Ai là tác giả của Truyện Kiều?'.  
  > Ngay khi người dùng nhả chuột, phân hệ STT nhận tín hiệu âm thanh và chuyển thành văn bản trong khoảng 3 giây. Bộ truy xuất BM25 lập tức quét kho tri thức và vì kho ViMMRC + ViQuAD không có đoạn khớp, hệ thống lấy đoạn Wikipedia nói về Truyện Kiều.  
  > Tiếp đó, mô hình ViT5 đọc đoạn văn vừa truy xuất và sinh ra câu trả lời 'Nguyễn Du'. Cuối cùng, phân hệ TTS chuẩn hóa văn bản và phát ra giọng đọc nơ-ron tự nhiên qua loa.  
  > Toàn bộ quá trình từ lúc kết thúc câu hỏi đến khi nghe thấy tiếng trả lời mất khoảng 6 giây khi chạy hoàn toàn trên CPU."

---

### SLIDE 23: PHÂN TÍCH LỖI THỰC TẾ & GIỚI HẠN HIỆN TẠI
* **Thời lượng:** 45 giây (29:15 - 30:00)
* **Người trình bày:** Trương Hoàng Duy
* **Nội dung hiển thị:**
  * **Phân tích các trường hợp lỗi điển hình (Error Analysis):**
    1. *Lỗi do tiếng ồn môi trường lớn (STT Error):* Trong môi trường quán cà phê hoặc tiếng còi xe, Whisper có thể nhận dạng sai một số phụ âm đầu hoặc mất từ nối.
    2. *Lỗi ngữ nghĩa trừu tượng (Retrieval Lexical Gap):* BM25 dựa trên tần suất từ khóa, nếu câu hỏi dùng từ đồng nghĩa hoàn toàn (ví dụ: 'thủ phủ' thay vì 'thủ đô') thì điểm BM25 có thể bị thấp.
    3. *Hạn chế phần cứng huấn luyện ViT5:* Quá trình tinh chỉnh (Fine-tuning) mô hình sinh ViT5 đòi hỏi tài nguyên GPU lớn để đạt độ hội tụ cực đại.
  * **Giới hạn phạm vi hiện tại:**
    * Hệ thống hiện tập trung tối ưu cho tương tác đơn lượt (Single-turn Q&A), chưa ghi nhớ ngữ cảnh lịch sử của các lượt đàm thoại trước đó.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Bên cạnh những kết quả tích cực, nhóm cũng thẳng thắn nhìn nhận những giới hạn còn tồn tại qua quá trình phân tích lỗi thực tế:  
  > Thứ nhất, ở phân hệ STT, khi môi trường có tiếng ồn phức tạp hoặc người dùng nói quá nhỏ, mô hình đôi khi nhận dạng sai phụ âm hoặc nuốt từ nối.  
  > Thứ hai, ở phân hệ Retrieval, do BM25 bản chất là giải thuật so khớp từ vựng (lexical matching), nếu câu hỏi sử dụng các từ đồng nghĩa hoàn toàn mà không xuất hiện trong bài đọc gốc thì điểm số truy xuất sẽ bị ảnh hưởng.  
  > Thứ ba, hệ thống hiện tại được thiết kế tối ưu cho hội thoại đơn lượt, nghĩa là trả lời dứt điểm từng câu hỏi chứ chưa lưu trữ bộ nhớ trạng thái để trò chuyện nối tiếp nhiều lượt theo ngữ cảnh quá khứ."

---

### SLIDE 24: TỔNG KẾT, HƯỚNG PHÁT TRIỂN & LỜI CẢM ƠN
* **Thời lượng:** 45 giây (30:00 - 30:45)
* **Người trình bày:** Ngô Trí Huy
* **Nội dung hiển thị:**
  * **Tổng kết các đóng góp chính của đề tài:**
    * Xây dựng thành công hệ thống Voice Q&A tiếng Việt mã nguồn mở hoàn chỉnh đầu tiên trên bộ dữ liệu chuẩn ViMMRC 2.0.
    * Ứng dụng thành công kỹ thuật Flow Matching tiên tiến (Matcha-TTS) và đóng góp frontend tách thanh điệu `vi_tone_v2` cho tiếng Việt.
    * Triển khai hoàn chỉnh ứng dụng Full-stack, chạy mượt mà trên CPU thông thường và đóng gói Docker tự động hóa 100%.
  * **Định hướng phát triển tương lai:**
    * Nâng cấp bộ tìm kiếm sang kiến trúc lai **Hybrid Retrieval**: Kết hợp BM25 với Dense Retrieval (Mô hình Bi-Encoder tiếng Việt) và Reranker nơ-ron.
    * Tích hợp các mô hình ngôn ngữ lớn (LLMs tiếng Việt như PhoGPT, Vistral, SeaLLMs) để hỗ trợ suy luận đa chặng và đàm thoại đa lượt.
  * **Lời cảm ơn Thầy Cô và Hội đồng đánh giá.**
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô trong Hội đồng,  
  > Nhìn lại toàn bộ quá trình nghiên cứu, đề tài của nhóm đã hoàn thành trọn vẹn tất cả các mục tiêu đề ra: từ việc nghiên cứu lý thuyết, xử lý dữ liệu chuẩn ViMMRC 2.0, làm chủ các mô hình học máy tiên tiến như Matcha-TTS Flow Matching, tinh chỉnh BM25, cho đến việc đóng gói một sản phẩm phần mềm hoàn chỉnh chạy cục bộ ổn định và đạt chuẩn kiểm thử 100%.  
  > Trong giai đoạn tới, nhóm định hướng sẽ nâng cấp hệ thống sang kiến trúc Hybrid Retrieval kết hợp nhúng ngữ nghĩa vector và tích hợp các LLMs tiếng Việt để phát triển thành một trợ lý ảo thông minh đa lượt toàn diện.  
  > Nhóm chúng em xin gửi lời cảm ơn chân thành và sâu sắc nhất tới Thầy Cô đã tận tình hướng dẫn, truyền thụ kiến thức và tạo điều kiện cho nhóm thực hiện đồ án này. Rất mong nhận được những nhận xét, góp ý quý báu từ Thầy Cô! Xin trân trọng cảm ơn!"
