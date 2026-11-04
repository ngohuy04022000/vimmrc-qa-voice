# TÀI LIỆU KỊCH BẢN THUYẾT TRÌNH 30 PHÚT (QUAY VIDEO BÁO CÁO TOÀN DIỆN ĐỒ ÁN)
## ĐỀ TÀI: HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0 (ViMMRC VOICE Q&A)
**Môn học:** Học máy tiên tiến và ứng dụng (Chương trình Cao học Công nghệ Thông tin)  
**Thời lượng:** 30 phút (khoảng 3.600 từ thuyết minh, nhịp độ ~120 - 125 từ/phút)  
**Mục tiêu:** Báo cáo chi tiết, chuyên sâu, toàn diện tất cả các khía cạnh: Động lực nghiên cứu, Phân tích dữ liệu ViMMRC 2.0, Kiến trúc 4 phân hệ, Cơ sở lý thuyết toán học (OT-CFM, BM25, ViT5), Kỹ thuật tối ưu hóa phần mềm (Lazy loading, VAD, Normalizer, Docker), Bảng benchmark đối sánh chuẩn quốc tế, Phân tích lỗi và Hướng phát triển.

---

### MỤC LỤC & PHÂN BỔ THỜI GIAN 24 SLIDE (TỔNG: 30 PHÚT)

#### PHẦN 1: TỔNG QUAN, BÀI TOÁN & DỮ LIỆU ViMMRC 2.0 (5:30)
* **Slide 1 (0:00 - 1:15):** Giới thiệu Đề tài, Hội đồng & Phân công Thành viên
* **Slide 2 (1:15 - 2:30):** Bối cảnh MRC, Voice Q&A & Thách thức Âm học Tiếng Việt
* **Slide 3 (2:30 - 3:45):** Mục tiêu Nghiên cứu & Bộ Tiêu chuẩn Thiết kế Hệ thống
* **Slide 4 (3:45 - 5:30):** Phân tích Chuyên sâu Bộ Dữ liệu ViMMRC 2.0 + UIT-ViQuAD2.0

#### PHẦN 2: KIẾN TRÚC TỔNG THỂ & PHÂN HỆ STT (5:30)
* **Slide 5 (5:30 - 6:45):** Kiến trúc End-to-End Pipeline 4 Chặng & Cơ chế Dự phòng
* **Slide 6 (6:45 - 8:15):** Phân hệ STT - Whisper-small LoRA 50h & Tối ưu CTranslate2
* **Slide 7 (8:15 - 9:30):** Tối ưu hóa STT: Voice Activity Detection & Thread-Safe Lazy Loading
* **Slide 8 (9:30 - 11:00):** Xử lý Âm thanh Phía Client

#### PHẦN 3: PHÂN HỆ CỐT LÕI: RETRIEVAL & ĐỌC HIỂU MRC (6:00)
* **Slide 9 (11:00 - 12:15):** Phân hệ Retrieval - Bài toán Tìm kiếm Văn bản Open-Domain
* **Slide 10 (12:15 - 13:30):** Tinh chỉnh Giải thuật BM25 ($k_1, b$) & Bigram Phrase Boost
* **Slide 11 (13:30 - 14:45):** Đánh giá Thực nghiệm Phân hệ Retrieval
* **Slide 12 (14:45 - 16:00):** Retrieval: Kho Tri Thức Hai Tầng Cho RAG
* **Slide 13 (16:00 - 17:00):** Phân hệ MRC - Mô hình ViT5 Seq2Seq & Giới hạn 512 Token

#### PHẦN 4: PHÂN HỆ TỔNG HỢP TIẾNG NÓI TTS (6:30)
* **Slide 14 (17:00 - 18:15):** Phân hệ TTS - Tổng quan & Lựa chọn Kiến trúc Matcha-TTS
* **Slide 15 (18:15 - 19:45):** Nguyên lý Toán học OT-CFM
* **Slide 16 (19:45 - 21:00):** Đóng góp Frontend Tách Thanh Điệu `vi_tone_v2`
* **Slide 17 (21:00 - 22:15):** Phân hệ Chuẩn hóa Văn bản Tiếng Việt Chuyên biệt
* **Slide 18 (22:15 - 23:30):** Đánh giá Định lượng & Benchmark Âm học Chi tiết

#### PHẦN 5: KỸ NGHỆ HỆ THỐNG, DEMO & KẾT LUẬN (6:30)
* **Slide 19 (23:30 - 24:30):** Kiến trúc Phần mềm Full-Stack FastAPI & Angular SPA
* **Slide 20 (24:30 - 25:30):** Đóng gói Triển khai Docker Multi-Stage & Healthcheck
* **Slide 21 (25:30 - 26:30):** Đảm bảo Chất lượng Kiểm thử (54 Bài Kiểm thử Tự động)
* **Slide 22 (26:30 - 28:00):** Kịch bản Live Demonstration Chi tiết Từng Bước
* **Slide 23 (28:00 - 29:00):** Phân tích Lỗi & Các Giới hạn của Hệ thống
* **Slide 24 (29:00 - 30:00):** Tổng kết Đóng góp, Định hướng Phát triển & Lời cảm ơn

---

## NỘI DUNG VÀ KỊCH BẢN CHI TIẾT TỪNG SLIDE (24 SLIDES)

### SLIDE 1: GIỚI THIỆU ĐỀ TÀI, HỘI ĐỒNG & NHÓM THỰC HIỆN
* **Thời lượng:** 1 phút 15 giây (0:00 - 1:15)
* **Nội dung hiển thị:**
  * **Trường / Viện:** Chương trình Đào tạo Thạc sĩ Công nghệ Thông tin
  * **Môn học:** Học máy tiên tiến và ứng dụng
  * **Tên đề tài:** HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0 (ViMMRC VOICE Q&A SYSTEM)
  * **Giảng viên hướng dẫn:** [Tên Thầy / Cô hướng dẫn]
  * **Thành viên thực hiện:**
    * **Ngô Trí Huy**
    * **Huỳnh Công Lương**
    * **Trương Hoàng Duy**
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô trong Hội đồng và các bạn học viên cao học! Hôm nay, nhóm chúng em xin báo cáo đồ án môn học 'Học máy tiên tiến và ứng dụng' với đề tài: 'Xây dựng Hệ thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0'.  
  > Nhóm gồm 3 thành viên: em Ngô Trí Huy, bạn Huỳnh Công Lương và bạn Trương Hoàng Duy.  
  > Trong video 30 phút này, nhóm sẽ trình bày toàn diện từ bối cảnh, dữ liệu, cơ sở toán học, tối ưu kỹ thuật, kết quả thực nghiệm đến demo thực tế. Kính mời Thầy Cô cùng theo dõi!"
---

### SLIDE 2: BỐI CẢNH MRC & THÁCH THỨC VOICE Q&A TIẾNG VIỆT
* **Thời lượng:** 1 phút 15 giây (1:15 - 2:30)
* **Nội dung hiển thị:**
  * **Sự phát triển của Machine Reading Comprehension (MRC):** Từ mô hình trích xuất (Span Extraction) đến sinh sinh chuỗi (Seq2Seq), nhưng hầu hết tương tác text-to-text.
  * **Thực tiễn nhu cầu:** Tương tác giọng nói tự nhiên trong môi trường rảnh tay (lái xe, trợ lý ảo gia đình, hỗ trợ người khuyết tật thị giác, cổng thông tin trường học).
  * **Những thách thức âm học & ngôn ngữ đặc thù tiếng Việt:**
    1. **Thanh điệu phức tạp:** Tiếng Việt có 6 thanh điệu mang tính phân biệt ngữ nghĩa cao độ. Mô hình TTS thông thường dễ bị sai thanh điệu, méo tiếng hoặc vấp âm.
    2. **Độ trễ cộng dồn:** Pipeline gồm 4 chặng nối tiếp nên thời gian của các chặng cộng dồn lại; đo thực tế ~12 giây/câu trên Docker CPU.
    3. **Rào cản tài nguyên phần cứng & riêng tư:** Phần lớn các mô hình SOTA yêu cầu GPU đắt tiền (NVIDIA A100/V100). Đồ án đặt mục tiêu chạy cục bộ ngay trên CPU máy tính thông thường, dữ liệu giọng nói không phải gửi lên dịch vụ đám mây.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Thưa Thầy Cô, Machine Reading Comprehension là trụ cột quan trọng của Xử lý Ngôn ngữ Tự nhiên. Tuy nhiên, việc giới hạn ở bàn phím và văn bản gây bất tiện trong môi trường rảnh tay như lái xe hoặc với người khiếm thị.  
  > Khi chuyển sang Voice Q&A tiếng Việt, nhóm đối mặt với 3 thách thức lớn:  
  > Thứ nhất, tính chất thanh điệu: tiếng Việt có 6 thanh điệu biến thiên cao độ. Mô hình TTS thông thường dễ sai dấu hỏi, ngã, nặng hoặc mất tự nhiên.  
  > Thứ hai, độ trễ tích lũy: pipeline gồm 4 chặng nối tiếp nhau, tổng thời gian cộng dồn lại; đo thực tế khoảng 12 giây mỗi câu trên Docker CPU.  
  > Thứ ba, yêu cầu chạy cục bộ: hệ thống cần hoạt động ổn định trên CPU phổ thông để bảo mật dữ liệu giọng nói, không phụ thuộc API trả phí."
---

### SLIDE 3: MỤC TIÊU NGHIÊN CỨU & TIÊU CHÍ THIẾT KẾ
* **Thời lượng:** 1 phút 15 giây (2:30 - 3:45)
* **Nội dung hiển thị:**
  * **Mục tiêu khoa học & kỹ thuật:**
    * Xây dựng pipeline Voice-to-Voice hoàn chỉnh cho tiếng Việt, dựa trên bộ dữ liệu ViMMRC 2.0 và UIT-ViQuAD2.0.
    * Ứng dụng mô hình tổng hợp giọng nói Conditional Flow Matching (Matcha-TTS, ICASSP 2024).
  * **4 Tiêu chí thiết kế hệ thống (Design Principles):**
    1. **Tính Module hóa (High Modularity):** Mỗi phân hệ độc lập, giao tiếp qua API chuẩn, dễ dàng thay thế nâng cấp từng thành phần.
    2. **Khả năng chạy Cục bộ (Local & CPU-friendly):** Toàn bộ pipeline chạy cục bộ ổn định trên CPU máy tính thông thường, không dùng API trả phí bên ngoài (Edge-TTS/gTTS dự phòng cần Internet).
    3. **Chịu lỗi (Fault Tolerance):** Có cơ chế dự phòng ở từng phân hệ; khi có sự cố ở một nhánh, hệ thống chuyển sang nhánh dự phòng.
    4. **Đo lường thời gian phản hồi (Measured Latency):** Chạy cục bộ trên CPU; đo thực tế ~12 giây/câu trên Docker CPU (~6 giây khi tắt reranker).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để giải quyết các thách thức đó, nhóm đặt mục tiêu xây dựng một hệ thống Voice Q&A tiếng Việt hoàn chỉnh, khép kín từ thu âm đến phát giọng nói. Bốn nguyên lý thiết kế xuyên suốt gồm:  
  > Một là Tính Module hóa: từng phân hệ STT, Retrieval, MRC và TTS được trừu tượng hóa qua các lớp Client riêng biệt, cho phép kiểm thử độc lập và linh hoạt nâng cấp thuật toán.  
  > Hai là Chạy cục bộ trên CPU: tối ưu hóa kích thước mô hình và suy luận để toàn bộ pipeline chạy ổn định trên máy tính phổ thông với 8GB RAM mà không bắt buộc có GPU rời.  
  > Ba là Tính chịu lỗi: mỗi phân hệ đều có cơ chế dự phòng tự động khi gặp dữ liệu bất thường hoặc gián đoạn mạng.  
  > Bốn là Đo lường thực tế: nhóm đo đạc chi tiết từng thành phần trên Docker CPU, đạt khoảng 12 giây mỗi câu khi bật reranker và khoảng 6 giây khi tắt reranker."
---

### SLIDE 4: PHÂN TÍCH CHUYÊN SÂU BỘ DỮ LIỆU ViMMRC 2.0
* **Thời lượng:** 1 phút 45 giây (3:45 - 5:30)
* **Nội dung hiển thị:**
  * **Nguồn dữ liệu: ViMMRC 2.0 + UIT-ViQuAD2.0:**
    * ViMMRC 2.0 (5.273 câu): bộ dữ liệu đọc hiểu tiếng Việt dành cho học sinh do nhóm UIT-NLP công bố; bản gốc là trắc nghiệm, dự án chuyển sang dạng hỏi - đáp tự do (đoạn văn + câu hỏi + câu trả lời dạng văn bản).
    * UIT-ViQuAD2.0: 28.454 câu gốc → 21.891 câu sau khi loại câu không có đáp án.
    * Tổng cộng: 27.164 câu hỏi.
  * **Phân chia dữ liệu theo bài đọc (Zero Data Leakage):**
    * **Train set:** 21.733 câu hỏi (~80.0%).
    * **Dev set:** 2.715 câu hỏi (~10.0%).
    * **Test set:** 2.716 câu hỏi (~10.0%).
    * Không trùng lặp bài đọc giữa các tập, đảm bảo đánh giá khách quan năng lực tổng quát hóa.
  * **Phân tích đặc trưng dữ liệu & Thách thức tiền xử lý:**
    * Độ dài bài đọc: trung bình 385 từ, bài dài nhất lên tới hơn 1.200 từ (vượt trần 512 token của Transformer).
    * Hiện tượng đáp án rỗng hoặc chứa ký tự điều khiển Unicode ẩn trong dữ liệu thô.
    * Giải pháp: Chuẩn hóa Unicode NFC toàn diện, lọc khoảng trắng thừa, và chuyển dữ liệu sang bài toán Đọc hiểu sinh câu tự do (Generative QA).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Trọng tâm dữ liệu của đề tài bắt đầu từ bộ dữ liệu đọc hiểu ViMMRC 2.0 do UIT-NLP công bố, gồm 5.273 câu hỏi trắc nghiệm tiếng Việt dành cho học sinh. Để mở rộng cho bài toán hỏi đáp tự do, nhóm đã gộp ViMMRC 2.0 với bộ dữ liệu UIT-ViQuAD2.0 gồm 21.891 câu hỏi tự luận trên Wikipedia, tạo thành kho dữ liệu tổng cộng 27.164 câu.  
  > Dữ liệu được phân chia theo bài đọc thành 3 tập: Train 21.733 câu, Dev 2.715 câu và Test 2.716 câu. Nhóm tuân thủ nghiêm ngặt nguyên tắc phân tách ở cấp độ bài đọc: các văn bản trong tập Dev và Test hoàn toàn chưa từng xuất hiện trong tập Train, đảm bảo zero leakage.  
  > Về tiền xử lý, bài đọc trong dữ liệu có độ dài từ 120 đến hơn 1.200 từ. Nhóm đã chuẩn hóa Unicode NFC, loại bỏ ký tự điều khiển ẩn và lập kho tri thức hai tầng gồm 5.879 đoạn văn ViMMRC và ViQuAD kết hợp 1,48 triệu đoạn Wikipedia tiếng Việt, làm cơ sở tri thức vững chắc cho hệ thống."
---

### SLIDE 5: KIẾN TRÚC END-TO-END PIPELINE 4 CHẶNG
* **Thời lượng:** 1 phút 15 giây (5:30 - 6:45)
* **Nội dung hiển thị:**
  * **Sơ đồ luồng dữ liệu 4 Chặng chi tiết:**
    $$\text{User Mic} \xrightarrow{\text{Audio}} \text{[STT: Whisper-small LoRA 50h, CT2 int8]} \xrightarrow{\text{Text Query}} \text{[Retrieval: BM25 + Dense + Reranker]} \xrightarrow{\text{Passage}} \text{[MRC: ViT5]} \xrightarrow{\text{Answer Text}} \text{[TTS: Matcha/VITS]} \xrightarrow{\text{Audio}} \text{Speaker}$$
  * **Giao thức truyền thông liên phân hệ:**
    * `GET /api/health` $\rightarrow$ `{status, retrieval, retrieval_passages, reader, tts_engine, frontend_served}`.
    * `POST /api/stt` (multipart audio) $\rightarrow$ `{text}`.
    * `POST /api/retrieve {question, top_k?}` $\rightarrow$ `{passages:[{id,text,score}]}` trên `kb_index.json` + `kb_wiki_full` (BM25 + dense, reranker chấm chung).
    * `POST /api/answer {question, passage}` $\rightarrow$ `{answer}`.
    * `POST /api/tts {text, engine?, voice?, rate?}` $\rightarrow$ file audio (qua normalizer).
  * **Cơ chế Fallback:**
    * MRC: ViT5 GPU/CPU $\rightarrow$ Lexical Baseline (trích xuất đáp án khi chưa có checkpoint ViT5).
    * TTS: Matcha-TTS Local $\rightarrow$ VITS MMS $\rightarrow$ Edge-TTS $\rightarrow$ gTTS.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô, em là Huỳnh Công Lương, xin trình bày về Kiến trúc Hệ thống và Phân hệ STT.  
  > Trên màn hình là kiến trúc 4 chặng:  
  > Người dùng nói vào mic, âm thanh gửi tới phân hệ STT để chuyển thành văn bản câu hỏi. Câu hỏi đi vào phân hệ Retrieval tìm kiếm trên kho tri thức hai tầng và trả về đoạn văn liên quan nhất. Tiếp đó, phân hệ MRC dùng ViT5 đọc hiểu và sinh câu trả lời tự do. Cuối cùng, phân hệ TTS tổng hợp thành giọng nói tự nhiên phát qua loa.  
  > Hệ thống có cơ chế Fallback ở từng chặng: chưa nạp checkpoint ViT5 thì dùng bộ trích xuất lexical; chuỗi TTS ưu tiên Matcha-TTS, lỗi sẽ chuyển sang gTTS (VITS và Edge-TTS chỉ dùng khi chọn thủ công), đảm bảo không bao giờ gián đoạn."
---

### SLIDE 6: PHÂN HỆ STT - WHISPER-SMALL LORA 50H & CTRANSLATE2
* **Thời lượng:** 1 phút 30 giây (6:45 - 8:15)
* **Nội dung hiển thị:**
  * **Tại sao lựa chọn Whisper & CTranslate2?**
    * OpenAI Whisper là kiến trúc Encoder-Decoder Transformer đa nhiệm được huấn luyện trên 680.000 giờ âm thanh đa ngôn ngữ.
    * **Vấn đề của Whisper gốc PyTorch:** Sử dụng tài nguyên lớn, suy luận chậm trên CPU, tiêu tốn nhiều RAM.
    * **Giải pháp Faster-Whisper:** Tái cấu trúc mô hình trên nền tảng **CTranslate2** – công cụ suy luận C++ tối ưu hóa cho Transformer với kỹ thuật lượng tử hóa trọng số (Weight Quantization: INT8/FP16) và tối ưu toán tử (Operator Fusion).
  * **Mô hình đang triển khai:** Whisper-small fine-tune LoRA 50h VietSpeech → CTranslate2 int8; **WER 13,77% / CER 6,67%** trên 1.802 mẫu test VietSpeech (Whisper small gốc: 36,76% / 19,43%).
  * **Thông số cấu hình mô hình:**
    * Kích thước mô hình: `small` (244 triệu tham số) – điểm cân bằng giữa độ chính xác tiếng Việt và tốc độ suy luận CPU.
    * Tốc độ suy luận (một lần đo riêng với Whisper-PyTorch gốc): nhanh gấp **4.1 lần** so với bản PyTorch trên cùng CPU Intel Core i7.
    * Tiêu thụ bộ nhớ RAM: Giảm từ 1.8GB xuống còn **540MB** khi chạy ở chế độ `compute_type="int8"`.
    * Độ trễ: PyTorch gốc ~3.8s cho câu hỏi 3s (đo riêng) và STT trong Docker CPU ~3 giây; hai con số thuộc hai cấu hình đo khác nhau.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Ở phân hệ STT, mục tiêu là nhận dạng tiếng Việt chính xác có dấu trên CPU với mức chiếm dụng bộ nhớ hợp lý.  
  > Nhóm triển khai mô hình Whisper-small được fine-tune LoRA trên 50 giờ dữ liệu VietSpeech, sau đó chuyển đổi sang CTranslate2 với lượng tử hóa INT8.  
  > Kết quả đánh giá trên 1.802 mẫu test VietSpeech cho thấy: mô hình đạt tỷ lệ lỗi từ WER 13,77% và tỷ lệ lỗi ký tự CER 6,67%, giảm hơn 22,9 điểm phần trăm WER so với mô hình Whisper-small gốc chưa fine-tune có WER 36,76% và CER 19,43%.  
  > Về tài nguyên, thư viện CTranslate2 giúp giảm đáng kể bộ nhớ RAM và tăng tốc tính toán ma trận trên CPU. Trong môi trường Docker CPU, thời gian nhận dạng thực tế mất khoảng 3 giây cho một câu hỏi đàm thoại, đáp ứng tốt yêu cầu xử lý cục bộ của đồ án."
---

### SLIDE 7: TỐI ƯU HÓA STT: VAD & THREAD-SAFE LAZY LOADING
* **Thời lượng:** 1 phút 15 giây (8:15 - 9:30)
* **Nội dung hiển thị:**
  * **Bộ lọc Voice Activity Detection (VAD Filter):**
    * Bật bộ lọc VAD tích hợp trong Faster-Whisper (`vad_filter=True`, dựa trên Silero VAD).
    * Tự động phát hiện và cắt bỏ các khoảng lặng (silence) ở đầu/cuối đoạn thu âm và lọc tiếng ồn môi trường nền.
    * Giảm 30-40% thời gian xử lý.
  * **Mẫu thiết kế Thread-Safe Lazy Loading:**
    * **Vấn đề:** Nạp mô hình AI khi khởi động server sẽ làm server mất 15-20 giây để khởi động, dễ bị hệ điều hành hoặc Docker Healthcheck ngắt kết nối vì timeout.
    * **Giải pháp:** Áp dụng mẫu Double-Checked Locking với `threading.Lock()` trong Python (`speech-to-text_Luong/stt_server.py`).
    * Mô hình chỉ thực sự được nạp vào bộ nhớ ở lần gửi request đầu tiên. Sau khi nạp, mô hình được lưu trong bộ nhớ tĩnh và tái sử dụng cho tất cả các request tiếp theo.
    * Kết quả: Server FastAPI khởi động trong **0.45 giây**, vượt kiểm tra Docker Healthcheck.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Hai giải pháp tối ưu quan trọng ở phân hệ STT là bộ lọc VAD và cơ chế Lazy Loading:  
  > Khi người dùng bấm mic thu âm, đoạn âm thanh luôn chứa khoảng lặng trước và sau câu nói. Nếu nạp toàn bộ vào Whisper, mô hình vừa tốn thời gian giải mã vừa dễ bị lặp từ. Nhóm đã bật bộ lọc VAD tích hợp trong Faster-Whisper để tự động cắt các đoạn im lặng và tạp âm nền, giúp giảm 30 đến 40% thời lượng âm thanh cần đưa vào giải mã.  
  > Thứ hai, việc nạp mô hình AI ngay khi khởi động server thường mất 15 đến 20 giây, khiến Docker Healthcheck dễ báo timeout. Nhóm áp dụng mẫu thiết kế Thread-Safe Lazy Loading với Lock trong Python: server FastAPI khởi động nhanh trong khoảng 0,45 giây để mở cổng mạng; mô hình chỉ nạp vào RAM ở request đầu tiên và được lưu trữ tĩnh phục vụ xuyên suốt phiên làm việc."
---

### SLIDE 8: XỬ LÝ TÍN HIỆU ÂM THANH PHÍA CLIENT
* **Thời lượng:** 1 phút 30 giây (9:30 - 11:00)
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
  > "Khâu xử lý tín hiệu âm thanh phía client đóng vai trò then chốt cho chất lượng nhận dạng:  
  > Trình duyệt thông thường thu âm qua micro với tần số 44.1kHz hoặc 48kHz dạng Stereo 2 kênh. Nếu tải trực tiếp dữ liệu thô này lên server, dung lượng file rất lớn và server phải mất chu kỳ CPU gọi ffmpeg để giải mã.  
  > Nhóm đã phát triển module xử lý âm thanh trực tiếp trên Web Client bằng Web Audio API của Angular: tín hiệu từ micro được giải mã qua AudioContext, gộp thành 1 kênh mono và thực hiện hạ mẫu qua OfflineAudioContext về đúng chuẩn 16.000 Hz, 16-bit Linear PCM WAV theo yêu cầu của Whisper.  
  > Nhờ xử lý trước tại client, kích thước file âm thanh giảm hơn 85%, chỉ còn khoảng 60KB cho một câu nói 2 giây, giúp truyền tải qua mạng gần như tức thời và giải phóng hoàn toàn gánh nặng chuyển đổi định dạng ở backend."
---

### SLIDE 9: PHÂN HỆ RETRIEVAL - TÌM KIẾM VĂN BẢN OPEN-DOMAIN
* **Thời lượng:** 1 phút 15 giây (11:00 - 12:15)
* **Nội dung hiển thị:**
  * **Đặt bài toán:**
    * Trong cấu trúc ViMMRC gốc, mỗi câu hỏi luôn đi kèm sẵn với một bài đọc cố định.
    * Trong kịch bản thực tế của Voice Q&A, người dùng chỉ bật mic và hỏi: *"Chiến dịch Điện Biên Phủ diễn ra vào năm nào?"* mà hoàn toàn không cho biết câu hỏi thuộc bài đọc nào.
    * Hệ thống phải tự động quét trong kho tri thức hai tầng (**5.879 đoạn + 1,48 triệu đoạn Wikipedia**) để tìm ra đúng ngữ cảnh chứa câu trả lời.
  * **Thách thức của bài toán Open-Domain Retrieval:**
    * Số lượng từ vựng lớn, nhiều bài đọc có chủ đề tương tự nhau (lịch sử, khoa học, danh nhân).
    * Câu hỏi người dùng ngắn gọn (thường chỉ 5 - 10 từ), trong khi bài đọc dài từ 300 - 800 từ (vấn đề bất cân xứng độ dài câu hỏi - tài liệu).
    * Chi phí thời gian: BM25 tầng 1 ~15 ms; toàn bộ truy xuất lai + reranker ~6 giây/câu.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô, em là Ngô Trí Huy, xin tiếp tục trình bày Phân hệ Truy xuất Ngữ cảnh và Mô hình Đọc hiểu MRC.  
  > Khác với bài toán đọc hiểu lý thuyết nơi câu hỏi luôn có sẵn bài đọc đi kèm, trong hệ thống Voice Q&A thực tế, người dùng chỉ đặt một câu hỏi ngắn gọn. Hệ thống phải tự tìm trong kho tài liệu để xác định đoạn văn chứa câu trả lời.  
  > Thách thức lớn là sự bất đối xứng độ dài: câu hỏi người dùng chỉ có 5 đến 10 từ khóa, trong khi mỗi đoạn văn dài hàng trăm từ. Hơn nữa, việc tìm kiếm ứng viên ở tầng 1 cần diễn ra rất nhanh, chỉ khoảng 15 mili-giây, để nhường quỹ thời gian cho mô hình reranker và mô hình đọc hiểu nơ-ron phía sau. Nếu truy xuất sai đoạn văn, toàn bộ pipeline phía sau chắc chắn sẽ đưa ra câu trả lời không chính xác."
---

### SLIDE 10: TINH CHỈNH GIẢI THUẬT BM25 & BIGRAM BOOST
* **Thời lượng:** 1 phút 15 giây (12:15 - 13:30)
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
  > "Để tầng truy xuất BM25 vừa nhẹ vừa chính xác, em đã cải tiến thuật toán BM25 qua hai bước:  
  > Thứ nhất, trên công thức Okapi BM25, em tinh chỉnh siêu tham số k1 lên 2,1 để tăng độ bão hòa với các từ khóa trọng tâm lặp lại, và đặt b bằng 1,0 để chuẩn hóa mạnh theo độ dài của văn bản, thay cho cấu hình mặc định của Lucene vốn chưa tối ưu cho các bài đọc chênh lệch độ dài.  
  > Thứ hai, tiếng Việt có đặc thù từ ghép rất mạnh; nếu tách rời các từ như 'Điện' và 'Biên', điểm số sẽ bị loãng. Em đề xuất cơ chế Bigram Phrase Boost: trích xuất các cặp từ liền kề trong câu hỏi; nếu đoạn văn chứa đúng cụm từ theo đúng thứ tự, đoạn văn được cộng thêm 0,4 điểm thưởng nhân trọng số IDF. Kỹ thuật này giúp phân biệt rõ nghĩa từ ghép và tăng độ chính xác truy xuất rõ rệt."
---

### SLIDE 11: ĐÁNH GIÁ THỰC NGHIỆM PHÂN HỆ RETRIEVAL
* **Thời lượng:** 1 phút 15 giây (13:30 - 14:45)
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
    * **Thời gian xử lý:** BM25 tầng 1 ~15 ms; toàn bộ truy xuất lai + reranker ~6 giây/câu.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Hiệu quả của việc tinh chỉnh BM25 được chứng minh qua thực nghiệm ablation trên 564 câu hỏi Dev đối chiếu với kho ViMMRC 552 bài đọc ban đầu:  
  > Với BM25 mặc định, Recall@1 đạt 64,18% và Recall@5 đạt 79,96%. Khi tinh chỉnh k1 và b, Recall@1 tăng lên 68,79%. Khi kết hợp thêm Bigram Phrase Boost, Recall@1 đạt 71,45% và Recall@5 đạt tới 83,69%, chỉ số MRR@5 đạt 0,7624.  
  > Điều này khẳng định rằng trong đại đa số trường hợp, đoạn văn chứa câu trả lời đúng luôn nằm ở vị trí thứ nhất hoặc thứ hai trong danh sách xếp hạng.  
  > Về tốc độ, thời gian quét BM25 tầng 1 chỉ mất khoảng 15 mili-giây trên CPU. Đây là tiền đề vững chắc trước khi nhóm mở rộng quy mô kho dữ liệu sang kiến trúc hai tầng toàn diện."
---

### SLIDE 12: RETRIEVAL - KHO TRI THỨC HAI TẦNG CHO RAG
* **Thời lượng:** 1 phút 15 giây (14:45 - 16:00)
* **Nội dung hiển thị:**
  * **Tầng 1 - Kho chuyên biệt:** 5.879 đoạn văn (passages) từ ViMMRC + ViQuAD, chỉ mục BM25 ($k_1=2.1$, $b=1.0$, bigram boost).
  * **Tầng 2 - Wikipedia tiếng Việt:** 1,48 triệu chunk (mỗi chunk ≤ 800 ký tự) với cả chỉ mục BM25 (`bm25s` chia shard) và chỉ mục vector dense (`multilingual-e5-small`, 384 chiều, float16 mmap ~1,1 GB).
  * **Ứng viên và reranker:** mỗi câu hỏi lấy top-3 BM25 tầng 1 + top-3 BM25 Wikipedia + top-3 dense Wikipedia (≤ 9 ứng viên); reranker `bge-reranker-v2-m3` (cross-encoder) chấm chung, đoạn tầng 1 được cộng +0,25, điểm cao nhất thắng.
  * **BM25 hai tầng (trước khi thêm reranker), test 2.545 câu hỏi:**
    * Tổng thể: **R@1 71,1%**, **R@5 85,9%**.
    * ViQuAD: R@1 73,2% / R@5 88,9%; ViMMRC: R@1 59,4% / R@5 69,2%.
  * **So sánh pipeline cuối (answer F1, 200 câu có đoạn trong kho / 200 câu kiến thức mở):** BM25 thuần 58,0 / 15,4; BM25 + dense Wikipedia 57,9 / 16,9; **reranker + ưu tiên kho +0,25 (đang dùng) 60,7 / 24,3**. Mức cộng được chọn trên chính các câu này nên hơi lạc quan.
  * **Độ trễ:** truy xuất + reranker ~6 giây / câu trên CPU Docker; tắt reranker (`KB_RERANKER=`) còn ~0,1–1,7 giây với độ chính xác thấp hơn.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để trả lời các câu hỏi kiến thức mở, nhóm đã xây dựng kho tri thức hai tầng cho RAG:  
  > Tầng 1 gồm 5.879 đoạn văn chọn lọc từ ViMMRC và ViQuAD. Tầng 2 gồm 1,48 triệu đoạn trích từ Wikipedia tiếng Việt, được đánh chỉ mục kép: BM25 chia shard và chỉ mục vector dense multilingual-e5-small 384 chiều lưu float16 khoảng 1,1 GB.  
  > Với mỗi câu hỏi, hệ thống lấy top 3 từ BM25 tầng 1, top 3 từ BM25 Wikipedia và top 3 từ dense Wikipedia, tổng cộng tối đa 9 ứng viên. Reranker cross-encoder bge-reranker-v2-m3 chấm điểm chung tất cả ứng viên, trong đó đoạn tầng 1 được cộng ưu tiên 0,25 điểm.  
  > Đánh giá trên tập test 2.545 câu, BM25 hai tầng đạt Recall@1 71,1% và Recall@5 85,9%. Khi có reranker, F1 câu trả lời trên câu kiến thức mở tăng từ 15,4 lên 24,3, và câu có trong kho tăng từ 58,0 lên 60,7, cho thấy hiệu quả rõ rệt của kiến trúc truy xuất lai hai tầng."
---

### SLIDE 13: PHÂN HỆ MRC - MÔ HÌNH ViT5 SEQ2SEQ & GIỚI HẠN 512 TOKEN
* **Thời lượng:** 1 phút 00 giây (16:00 - 17:00)
* **Nội dung hiển thị:**
  * **Mô hình Seq2Seq ViT5 (`VietAI/vit5-base`):**
    * Kiến trúc Transformer T5 được tiền huấn luyện chuyên sâu cho tiếng Việt bởi VietAI.
    * Giải quyết bài toán hỏi - đáp tự do (Generative QA): ViT5 (`vit5-combined-cont`) sinh câu trả lời từ đoạn văn đã truy xuất.
    * Kết quả trên tập test dữ liệu kết hợp (2.716 câu): **EM 41,05**, **F1 66,55**. Kiểm thử end-to-end (truy xuất rồi đọc hiểu): **F1 53,9**; khi dùng đoạn văn đúng (gold passage): **F1 68,6**.
  * **Vấn đề Giới hạn Độ dài Ngữ cảnh (512 Token Ceiling):**
    * Bài đọc ViMMRC trung bình 385 từ, nhiều bài dài 800 - 1.200 từ $\rightarrow$ vượt quá giới hạn 512 subword tokens của ViT5.
    * Cắt cụt ngây thơ (naive truncation) ở đầu hoặc đuôi sẽ làm mất đoạn văn chứa đáp án.
  * **Chọn ngữ cảnh:** Đã thử chọn ngữ cảnh theo câu hỏi (`question_chunks`) nhưng không cải thiện; mặc định cắt 512 token đầu (head).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Sau khi có đoạn văn ngữ cảnh, nhóm sử dụng mô hình ViT5-base của VietAI để đọc hiểu và sinh câu trả lời tự do, không cần các phương án trắc nghiệm sẵn có.  
  > Về giới hạn ngữ cảnh 512 token: nhiều bài đọc dài từ 800 đến 1.200 từ. Nhóm đã thử nghiệm chọn lọc phân đoạn ngữ cảnh theo câu hỏi nhưng độ chính xác không cải thiện, do đó nhóm chọn giải pháp chuẩn hóa lấy 512 token đầu của đoạn văn.  
  > Kết quả huấn luyện mô hình ViT5 trên bộ dữ liệu mở rộng đạt Exact Match 41,05% và token F1 66,55% trên 2.716 câu test độc lập. Khi chạy toàn chuỗi từ khâu truy xuất đến sinh câu trả lời, F1 toàn chuỗi đạt 53,9%, khẳng định mô hình sinh câu trả lời chuẩn xác và mạch lạc."
---

### SLIDE 14: PHÂN HỆ TTS - LỰA CHỌN KIẾN TRÚC MATCHA-TTS
* **Thời lượng:** 1 phút 15 giây (17:00 - 18:15)
* **Nội dung hiển thị:**
  * **Tầm quan trọng của phân hệ TTS trong Voice Q&A:**
    * Là điểm chạm cuối cùng (Last-mile Touchpoint) với người dùng. Dù STT và MRC có chính xác nhưng nếu giọng đọc khô cứng, vấp từ hoặc sai thanh điệu thì trải nghiệm sẽ thất bại.
  * **Sự tiến hóa của các kiến trúc Text-to-Speech:**
    * *Thời kỳ 1: Concatenative / Parametric (Festival, Tacotron2):* Ghép nối thô, chất lượng Mel-spectrogram mờ nhòe.
    * *Thời kỳ 2: Non-autoregressive & VAE (FastSpeech2, VITS):* Tốc độ nhanh hơn nhưng mô hình VITS huấn luyện rất nặng, cấu trúc phức tạp.
    * *Thời kỳ 3: Denoising Diffusion (Diff-TTS, Grad-TTS):* Chất lượng âm thanh vượt bậc nhưng tốc độ cực chậm, cần từ 50 đến 100 bước khử nhiễu lặp lại.
  * **Lựa chọn kiến trúc: Matcha-TTS (ICASSP 2024):**
    * Dựa trên **Conditional Flow Matching (CFM)** kết hợp Đường vận chuyển tối ưu (Optimal Transport).
    * Đạt chất lượng âm thanh gần với Diffusion nhưng giải ODE nhanh (20 bước Euler mặc định, 10 bước ở chế độ nhanh).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô, em là Trương Hoàng Duy, xin báo cáo về Phân hệ Tổng hợp Tiếng nói (TTS) và Bộ benchmark đánh giá âm học.  
  > Phân hệ TTS là điểm chạm trực tiếp quyết định cảm nhận của người dùng. Một câu trả lời chính xác nhưng giọng đọc khô cứng hay sai thanh điệu sẽ làm giảm trải nghiệm tương tác.  
  > Tổng quan các thế hệ TTS: Tacotron2 hay FastSpeech2 dễ bị nhòe phổ Mel; mô hình VITS có cấu trúc tiềm ẩn phức tạp, khó kiểm soát cao độ; trong khi các mô hình Diffusion như Grad-TTS tuy hay nhưng cần 50 đến 100 bước khử nhiễu lặp lại, quá chậm để chạy trên CPU.  
  > Nhóm đã làm chủ kiến trúc mới nhất: Matcha-TTS từ hội nghị ICASSP 2024. Dựa trên Flow Matching, Matcha-TTS cho chất lượng âm thanh tự nhiên như Diffusion nhưng giải mã cực nhanh, chỉ cần 10 bước tính toán trên CPU thông thường."
---

### SLIDE 15: NGUYÊN LÝ TOÁN HỌC CONDITIONAL FLOW MATCHING (OT-CFM)
* **Thời lượng:** 1 phút 30 giây (18:15 - 19:45)
* **Nội dung hiển thị:**
  * **Mục tiêu của Flow Matching:** Học một trường vector biến thiên theo thời gian $v_t(x)$ để biến đổi phân phối tiên nghiệm nhiễu chuẩn Gaussian $p_0 = \mathcal{N}(0, I)$ thành phân phối dữ liệu Mel-spectrogram đích $q(x_1)$.
  * **Phương trình Vi phân Thường (ODE):**
    $$\frac{d\phi_t(x)}{dt} = v_t(\phi_t(x)), \quad \phi_0(x) = x_0 \sim p_0$$
  * **Ưu thế của Đường vận chuyển Tối ưu (Optimal Transport - OT):**
    * Thay vì tạo ra quỹ đạo cong uốn lượn ngẫu nhiên như Diffusion truyền thống:
      $$\psi_t(x) = (1 - (1 - \sigma_{\min})t) x_0 + t x_1$$
    * Quỹ đạo di chuyển giữa nhiễu $x_0$ và Mel-spectrogram đích $x_1$ là một **đường thẳng tối ưu (Straight Line Trajectory)** trong không gian vector.
    * Do quỹ đạo là đường thẳng, việc giải phương trình ODE bằng phương pháp Euler chỉ cần **10–20 bước lặp (mặc định NFE = 20)** là hội tụ chính xác, thay vì phải mất 50-100 bước như SDE/ODE của Diffusion.
  * **Hàm mất mát huấn luyện (Loss Function):**
    $$\mathcal{L}_{\text{CFM}}(\theta) = \mathbb{E}_{t, q(x_1), p(x_0)} \left\| v_t(\psi_t(x_0); \theta) - (x_1 - (1 - \sigma_{\min})x_0) \right\|^2$$
* **Kịch bản thuyết trình (Speaker Script):**
  > "Về nguyên lý toán học, sự khác biệt lớn nhất giữa Flow Matching và Diffusion nằm ở quỹ đạo xác suất:  
  > Trong Diffusion tiêu chuẩn, quá trình khuếch tán vi phân SDE tạo ra quỹ đạo cong uốn lượn ngẫu nhiên trong không gian vector, buộc mô hình phải bước từng bước rất nhỏ để không lệch hướng, tốn hàng chục bước lặp.  
  > Ngược lại, Matcha-TTS áp dụng lý thuyết Optimal Transport Conditional Flow Matching: ép trường vector đạo hàm di chuyển theo đường thẳng tối ưu nối trực tiếp từ nhiễu Gaussian x0 đến Mel-spectrogram đích x1.  
  > Vì quỹ đạo là đường thẳng tuyến tính, phương trình vi phân ODE có thể giải bằng phương pháp Euler chỉ trong khoảng 10 đến 20 bước lặp (hệ thống dùng 20). Nhờ đó, Matcha-TTS giữ được độ chi tiết âm thanh của Diffusion nhưng tốc độ suy luận nhanh gấp nhiều lần, hoàn toàn khả thi khi chạy trên CPU."
---

### SLIDE 16: ĐÓNG GÓP FRONTEND TÁCH THANH ĐIỆU `vi_tone_v2`
* **Thời lượng:** 1 phút 15 giây (19:45 - 21:00)
* **Nội dung hiển thị:**
  * **Vấn đề thanh điệu trong biểu diễn văn bản tiếng Việt:**
    * Tiếng Việt có 6 thanh điệu: Ngang (0), Sắc (1), Huyền (2), Hỏi (3), Ngã (4), Nặng (5).
    * Nếu giữ nguyên ký tự có dấu (`á`, `à`, `ả`, `ã`, `ạ`), từ vựng mở rộng quá lớn, mô hình phải học biểu diễn F0 riêng rẽ cho từng biến thể ký tự $\rightarrow$ dữ liệu bị phân mảnh, dễ phát âm sai dấu khi gặp từ hiếm.
  * **Đề xuất Frontend `vi_tone_v2` (Tone Splitting):**
    * Bóc tách toàn bộ thanh điệu ra khỏi nguyên âm, đưa thành một token mã số thanh điệu độc lập nằm ở cuối âm tiết:
      $$\text{'tiếng'} \rightarrow \text{t i e n g 1}, \quad \text{'hồ'} \rightarrow \text{h ô 2}, \quad \text{'Việt'} \rightarrow \text{v i e t 5}, \quad \text{'Hồ Chí Minh'} \rightarrow \text{h ô 2 ... ch i 1 ... m i n h 0}$$
  * **Lợi ích thực nghiệm:**
    * Giảm 70% kích thước từ điển ký tự đầu vào của Text Encoder.
    * Mô hình học biểu diễn cao độ F0 tập trung vào các token thanh điệu, giúp kiểm soát đường bao F0 nhất quán.
    * Giảm hiện tượng mất dấu, nhầm lẫn thanh điệu (đặc biệt giữa dấu Hỏi và dấu Ngã).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Đóng góp trọng tâm của nhóm ở phân hệ TTS là đề xuất frontend tách thanh điệu vi_tone_v2:  
  > Tiếng Việt có 6 thanh điệu. Nếu để nguyên nguyên âm có dấu trong từ điển, từ vựng ký tự nở rộng gấp nhiều lần và mô hình coi các biến thể là ký tự rời rạc, rất khó học quy luật biến thiên cao độ F0.  
  > Giải pháp vi_tone_v2 bóc tách thanh điệu thành token độc lập ở cuối mỗi âm tiết: 0 ngang, 1 sắc, 2 huyền, 3 hỏi, 4 ngã, 5 nặng. Ví dụ 'tiếng' tách thành 't i e n g' và token 1; 'hồ' thành 'h ô' và token 2; 'Việt' thành 'v i e t' và token 5.  
  > Nhờ vậy, Text Encoder học tách biệt giữa âm vị và cao độ F0, giảm 70% kích thước từ điển và giảm rõ rệt hiện tượng lẫn lộn dấu hỏi, dấu ngã."
---

### SLIDE 17: PHÂN HỆ CHUẨN HÓA VĂN BẢN (TEXT NORMALIZER)
* **Thời lượng:** 1 phút 15 giây (21:00 - 22:15)
* **Nội dung hiển thị:**
  * **Tại sao cần Text Normalizer chuyên biệt cho Q&A?**
    * Đầu ra của mô hình MRC thường chứa các ký hiệu logic, số liệu và định dạng viết tắt mà mô hình TTS không thể phát âm trực tiếp hoặc phát âm sai.
  * **5 Bộ quy tắc chuẩn hóa tiếng Việt (`text-to-speech_Duy/src/normalizer.py`):**
    1. **Định dạng Ngày - Tháng - Năm:**
       * `07/05/1954` $\rightarrow$ `ngày bảy tháng năm năm một nghìn chín trăm năm mươi tư`.
    2. **Số thập phân & Đơn vị đo lường:**
       * `3.14` $\rightarrow$ `ba phẩy một bốn`; `50 km/h` $\rightarrow$ `năm mươi ki-lô-mét trên giờ`.
    3. **Tiền tệ & Ký hiệu phần trăm:**
       * `100.000 VNĐ` $\rightarrow$ `một trăm nghìn đồng`; `85%` $\rightarrow$ `tám mươi lăm phần trăm`.
    4. **Nhãn đáp án / liệt kê:**
       * Nhãn như `(A)`, `B.` $\rightarrow$ `Đáp án A:`, `Đáp án B:`.
    5. **Xử lý dấu câu & Khoảng nghỉ (Pause Insertion):**
       * Tự động chèn khoảng nghỉ 150ms tại dấu phẩy, 250ms tại dấu chấm phẩy/hai chấm và 400ms tại dấu chấm câu.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Trước khi tổng hợp âm thanh, văn bản câu trả lời đi qua module Text Normalizer chuyên biệt:  
  > Câu trả lời do mô hình sinh ra thường chứa số liệu, ngày tháng lịch sử hoặc ký hiệu viết tắt. Nếu đưa nguyên văn bản thô vào TTS, mô hình sẽ đọc sai hoặc ngắt nghỉ không đúng chỗ.  
  > Module normalizer của nhóm thiết lập 5 bộ quy tắc chuẩn hóa: đọc các định dạng ngày tháng như ngày bảy tháng năm, mở rộng số thập phân, tiền tệ và phần trăm ra chữ tiếng Việt có dấu, đồng thời chuyển đổi các nhãn đáp án dạng ngoặc đơn thành cụm từ rõ ràng.  
  > Ngoài ra, bước hậu xử lý tự động chèn các khoảng nghỉ âm học 150 mili-giây tại dấu phẩy và 400 mili-giây tại dấu chấm, giúp giọng đọc phát ra có nhịp ngắt câu tự nhiên."
---

### SLIDE 18: ĐÁNH GIÁ & BENCHMARK ÂM HỌC ĐỊNH LƯỢNG
* **Thời lượng:** 1 phút 15 giây (22:15 - 23:30)
* **Nội dung hiển thị:**
  * **Thiết lập Benchmark chuẩn quốc tế:**
    * Tập dữ liệu kiểm thử: các câu mẫu tham chiếu từ giọng thu âm của phát thanh viên chuyên nghiệp (tập InfoRe1).
    * Các chỉ số đo lường: Mel-Cepstral Distortion (MCD - dB), F0 RMSE (Hz), log-F0 RMSE (semitones), Character Error Rate (CER - qua ASR PhoWhisper), Real-Time Factor (RTF trên CPU).
  * **Bảng kết quả đối sánh thực nghiệm:**

| Mô hình TTS | MCD (dB) $\downarrow$ | F0 RMSE (Hz) $\downarrow$ | log-F0 RMSE (semitones) $\downarrow$ | CER (ASR) $\downarrow$ | RTF (CPU) $\downarrow$ | Ghi chú kiến trúc |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Giọng người thật (Tham chiếu)** | – | – | – | 0.7% | – | Ngưỡng trần kiểm chứng ASR |
| **Matcha-TTS (Nhóm huấn luyện)** | 3.05 | 21.6 | **0.88** | **0.8%** | **0.64** | OT-CFM cục bộ, frontend tách thanh điệu |
| **VITS MMS (Meta Pretrained)** | **4.40** | 82.7 | 4.29 | 4.7% | 0.29 | VAE End-to-End, giọng nam miền Bắc |

  * **Phân tích chi tiết:**
    * **Độ rõ âm vị (Intelligibility):** Matcha-TTS đạt CER **0.8%**, thấp hơn VITS gần 6 lần, cho thấy phát âm rõ chữ và ít mất phụ âm.
    * **Độ chuẩn thanh điệu (Pitch accuracy):** log-F0 RMSE của Matcha đạt **0.88 bán cung**, tốt hơn rất nhiều so với VITS (4.29).
    * **Hiệu năng CPU:** RTF đạt **0.64**, nghĩa là trên CPU máy tính thông thường, mô hình chỉ mất 0.64 giây để tạo ra 1 giây âm thanh, tức là TTS nhanh hơn thời gian thực.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Nhóm đã thiết lập bộ benchmark âm học định lượng chuẩn quốc tế, so sánh trực tiếp Matcha-TTS với giọng phát thanh viên người thật và mô hình nền tảng VITS MMS của Meta:  
  > Về độ rõ chữ: khi dùng mô hình nhận dạng ASR PhoWhisper kiểm chứng lại, tỷ lệ lỗi ký tự CER của Matcha-TTS đạt 0,8%, thấp hơn gần 6 lần so với mức 4,7% của VITS và gần mức trần 0,7% của người thật.  
  > Về độ chuẩn cao độ: sai số log-F0 của Matcha đạt 0,88 bán cung, thấp hơn rất nhiều so với 4,29 bán cung của VITS.  
  > Về tốc độ: hệ số RTF trên CPU đạt 0,64, nghĩa là chỉ mất khoảng 0,6 giây để tổng hợp một câu nói dài một giây, hoàn toàn đáp ứng yêu cầu đàm thoại thời gian thực mà không cần GPU."
---

### SLIDE 19: KIẾN TRÚC PHẦN MỀM FULL-STACK FASTAPI & ANGULAR
* **Thời lượng:** 1 phút 00 giây (23:30 - 24:30)
* **Nội dung hiển thị:**
  * **Backend (FastAPI - Python 3.11):**
    * Thiết kế theo kiến trúc hướng dịch vụ với OpenAPI / Swagger UI tự động.
    * Các endpoint cốt lõi: `/api/stt` (nhận audio), `/api/retrieve` (tìm văn bản), `/api/answer` (đọc hiểu), `/api/tts` (sinh giọng nói), `/api/health` (giám sát trạng thái).
    * Hỗ trợ xử lý bất đồng bộ (Asynchronous async/await) và quản lý tiến trình nạp mô hình trong RAM.
  * **Frontend (Angular 22 Standalone Components):**
    * Giao diện Chat Voice đàm thoại hiện đại, hỗ trợ tương tác Micro trực tiếp.
    * Thành phần hiển thị **Pipeline Flow Indicator**: Trực quan hóa trạng thái từng bước đang diễn ra (Thu âm $\rightarrow$ STT $\rightarrow$ Retrieval $\rightarrow$ MRC $\rightarrow$ TTS $\rightarrow$ Nghe audio) giúp người dùng nắm bắt tiến độ xử lý.
    * Tích hợp thư viện bài đọc ViMMRC cho phép người dùng chọn nhanh ngữ cảnh mẫu để thử nghiệm.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Về khía cạnh kỹ nghệ phần mềm, nhóm đã tích hợp toàn bộ hệ thống thành một ứng dụng Full-stack hoàn chỉnh:  
  > Phía Backend, nhóm sử dụng FastAPI viết bằng Python 3.11. Toàn bộ 4 phân hệ được chuẩn hóa thành các REST API rõ ràng, hỗ trợ xử lý bất đồng bộ và tự động sinh tài liệu Swagger UI.  
  > Phía Frontend, em xây dựng ứng dụng Angular với kiến trúc Standalone Components hiện đại. Giao diện Chat Voice trực quan hỗ trợ tương tác micro và hiển thị thanh trạng thái Pipeline Flow Indicator theo thời gian thực, giúp người dùng theo dõi minh bạch từng bước xử lý từ nhận dạng giọng nói đến phát âm thanh."
---

### SLIDE 20: ĐÓNG GÓI TRIỂN KHAI DOCKER MULTI-STAGE
* **Thời lượng:** 1 phút 00 giây (24:30 - 25:30)
* **Nội dung hiển thị:**
  * **Chiến lược Đóng gói Multi-Stage Build (`Dockerfile`):**
    * **Stage 1 - Build Frontend (`node:22-alpine`):** Biên dịch mã nguồn Angular, áp dụng Tree-shaking và Minification, tạo ra thư mục tĩnh tĩnh siêu nhẹ `dist/`.
    * **Stage 2 - Production Runtime (`python:3.11-slim`):** Cài đặt các thư viện hệ thống tối thiểu (`ffmpeg`, `libsndfile1`), cài đặt PyTorch CPU-only wheel (chỉ ~180MB thay vì bản CUDA 2.5GB), sao chép thư mục build Angular và mã nguồn backend.
  * **Quản trị triển khai qua `docker-compose.yml`:**
    * Khởi động toàn bộ hệ thống bằng đúng **1 câu lệnh duy nhất**: `docker compose up -d`.
    * Tích hợp sẵn cơ chế **Docker Healthcheck**: Tự động gọi endpoint `/api/health` định kỳ 30s để giám sát sức khỏe container.
    * Hệ thống chạy độc lập, cô lập trên cổng máy chủ **8090** (Docker map 8090 → 8000), không xung đột tài nguyên với hệ điều hành máy chủ.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để đảm bảo tính tái lập và triển khai thuận tiện, nhóm đã đóng gói toàn bộ hệ thống vào container Docker theo kỹ thuật Multi-Stage build:  
  > Stage 1 dùng Node 22 Alpine để biên dịch mã nguồn Angular thành các file tĩnh tối ưu.  
  > Stage 2 dùng image Python 3.11-slim gọn nhẹ, cài đặt ffmpeg, thư viện âm thanh và phiên bản PyTorch CPU-only nặng khoảng 180MB thay vì bản CUDA 2,5GB.  
  > Quá trình triển khai được cấu hình tự động qua docker-compose. Chỉ bằng một lệnh 'docker compose up -d', toàn bộ hệ thống sẽ khởi chạy và sẵn sàng phục vụ trên cổng 8090 kèm theo cơ chế Healthcheck tự động định kỳ giám sát."
---

### SLIDE 21: ĐẢM BẢO CHẤT LƯỢNG KIỂM THỬ PHẦN MỀM
* **Thời lượng:** 1 phút 00 giây (25:30 - 26:30)
* **Nội dung hiển thị:**
  * **Quy trình Kiểm thử Phần mềm Toàn diện (Testing Suite):**
    * Áp dụng framework kiểm thử tự động **pytest** cho toàn bộ backend.
    * Kiểm thử phủ khắp cả 3 cấp độ: Unit Tests (hàm xử lý), Module Integration Tests (từng phân hệ) và End-to-End System Tests (toàn bộ pipeline API).
  * **Kết quả Kiểm định Chất lượng:**
    * **Bộ 115 bài kiểm thử tự động** (thời gian chạy ~1–2 phút):
      * 12 tests: Phân hệ TTS (Matcha/VITS/Edge-TTS fallback, normalizer, tokenizer vi_tone_v2) — 12/12 passed.
      * 15 tests: Phân hệ Truy xuất BM25, Tokenizer và Lập chỉ mục — 15/15 passed.
      * 18 tests: Dữ liệu MRC, metric EM/F1, context selection, dataset gộp, smoke train — 17 passed, 1 skipped (`accelerate` trên CPU).
      * 5 tests: Server API Endpoints và Healthcheck — 5/5 passed.
      * 4 tests: Chuỗi tích hợp retrieval → MRC → TTS — 4/4 passed.
    * Đảm bảo tính toàn vẹn (Integrity), phát hiện sớm lỗi hồi quy khi hợp nhất mã nguồn giữa các thành viên.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Nhóm áp dụng quy trình kiểm thử tự động toàn diện bằng framework pytest để đảm bảo tính ổn định của toàn bộ mã nguồn.  
  > Trước khi đóng gói phiên bản chính thức, bộ 115 bài kiểm thử tự động được dùng để kiểm tra hồi quy.  
  > Bộ test kiểm tra đa tầng từ chuẩn hóa văn bản, giải thuật BM25, mô hình đọc hiểu ViT5, động cơ tổng hợp TTS đến các endpoint API của server. Nhờ kiểm thử chặt chẽ, nhóm phát hiện sớm lỗi hồi quy khi tích hợp mã nguồn giữa các thành viên, giúp hệ thống vận hành ổn định."
---

### SLIDE 22: KỊCH BẢN LIVE DEMO HỆ THỐNG THỰC TẾ
* **Thời lượng:** 1 phút 30 giây (26:30 - 28:00)
* **Nội dung hiển thị:**
  * **Kịch bản Demo trực tiếp trên giao diện Web (`http://localhost:8090`):**
    * **Bước 1 (Voice Input):** Bấm micro và đặt câu hỏi âm thanh: *"Ai là tác giả của Truyện Kiều?"* (câu hỏi tự do).
    * **Bước 2 (STT Processing):** Whisper-small LoRA 50h (CTranslate2 int8) nhận dạng chuỗi văn bản tiếng Việt có dấu trong khoảng 3 giây.
    * **Bước 3 (Retrieval Processing):** BM25 + dense lấy ứng viên từ kho tri thức hai tầng, reranker chọn đoạn Wikipedia "Truyện Kiều" (~6 giây).
    * **Bước 4 (MRC Processing):** ViT5 đọc đoạn văn đã truy xuất và sinh ra câu trả lời *"Nguyễn Du"*.
    * **Bước 5 (TTS Processing):** Text Normalizer chuẩn hóa câu trả lời *"Nguyễn Du"* và Matcha-TTS tổng hợp thành âm thanh trong khoảng 1,3 giây.
    * **Bước 6 (Audio Output):** Trình duyệt tự động phát giọng nói câu trả lời rõ ràng, truyền cảm.
  * **Tổng thời gian xử lý toàn pipeline:** **khoảng 12 giây** trên CPU (đo trên Docker, `OMP_NUM_THREADS=4`: STT ~3 s, truy xuất + reranker ~6 s, ViT5 ~1,4 s, TTS ~1,3 s); tắt reranker (`KB_RERANKER=`) còn khoảng 6 giây nhưng độ chính xác thấp hơn. Câu "Sông dài nhất thế giới là sông nào?" cũng trả lời đúng "Sông Amazon" trong Docker.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Sau đây, nhóm xin kính mời Thầy Cô và các bạn cùng theo dõi kịch bản chạy thử nghiệm thực tế của hệ thống:  
  > Người dùng bấm giữ nút micro trên giao diện web và hỏi: 'Ai là tác giả của Truyện Kiều?'.  
  > Ngay khi nhả mic, phân hệ STT nhận tín hiệu âm thanh và chuyển thành văn bản trong khoảng 3 giây. Bộ truy xuất lập tức lấy các ứng viên từ BM25 tầng 1, BM25 Wikipedia và dense Wikipedia, sau đó reranker bge-reranker-v2-m3 định vị chính xác đoạn Wikipedia nói về Truyện Kiều.  
  > Mô hình ViT5 tiếp nhận ngữ cảnh và sinh ra câu trả lời 'Nguyễn Du'. Cuối cùng, phân hệ TTS chuẩn hóa văn bản và phát âm thanh câu trả lời bằng giọng đọc nơ-ron tự nhiên qua loa.  
  > Tổng thời gian xử lý toàn chu trình mất khoảng 12 giây khi chạy hoàn toàn trên CPU Docker; nếu tắt reranker thì thời gian phản hồi rút ngắn còn khoảng 6 giây."
---

### SLIDE 23: PHÂN TÍCH LỖI THỰC TẾ & GIỚI HẠN HIỆN TẠI
* **Thời lượng:** 1 phút 00 giây (28:00 - 29:00)
* **Nội dung hiển thị:**
  * **Phân tích các trường hợp lỗi điển hình (Error Analysis):**
    1. *Lỗi do tiếng ồn môi trường lớn (STT Error):* Trong môi trường quán cà phê hoặc tiếng còi xe, Whisper có thể nhận dạng sai một số phụ âm đầu hoặc mất từ nối.
    2. *Lỗi ngữ nghĩa trừu tượng (Retrieval Lexical Gap):* BM25 dựa trên tần suất từ khóa, nếu câu hỏi dùng từ đồng nghĩa hoàn toàn (ví dụ: 'thủ phủ' thay vì 'thủ đô') thì điểm BM25 có thể bị thấp.
    3. *Câu hỏi kiến thức chung vẫn có thể sai:* ví dụ "Thủ đô của Việt Nam là gì?" trả về "Sài Gòn" vì một đoạn ViQuAD tầng 1 về TP. Hồ Chí Minh thắng; F1 trên câu kiến thức mở mới ~24.
    4. *Giới hạn ViT5:* Đã train thêm 2 epoch: F1 66,02 → 66,55 nhưng dev loss tăng; cải thiện tiếp cần thêm dữ liệu hoặc dò siêu tham số.
  * **Giới hạn phạm vi hiện tại:**
    * Hệ thống hiện tập trung tối ưu cho tương tác đơn lượt (Single-turn Q&A), chưa ghi nhớ ngữ cảnh lịch sử của các lượt đàm thoại trước đó.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Nhóm cũng phân tích các trường hợp lỗi và giới hạn thực tế:  
  > Thứ nhất, ở phân hệ STT, trong môi trường ồn hoặc người nói quá nhỏ, mô hình đôi khi nhận dạng sai phụ âm đầu hoặc mất từ nối.  
  > Thứ hai, ở phân hệ Retrieval, BM25 so khớp từ khóa nên nếu câu hỏi dùng từ đồng nghĩa vắng bóng trong văn bản thì điểm số bị ảnh hưởng; một số câu kiến thức mở còn sai do đoạn tầng 1 lấn át điểm số.  
  > Thứ ba, hệ thống hiện tối ưu cho hội thoại đơn lượt, trả lời từng câu độc lập chứ chưa lưu trữ trạng thái để trò chuyện đa lượt."
---

### SLIDE 24: TỔNG KẾT, HƯỚNG PHÁT TRIỂN & LỜI CẢM ƠN
* **Thời lượng:** 1 phút 00 giây (29:00 - 30:00)
* **Nội dung hiển thị:**
  * **Tổng kết các đóng góp chính của đề tài:**
    * Xây dựng thành công hệ thống Voice Q&A tiếng Việt mã nguồn mở hoàn chỉnh dựa trên ViMMRC 2.0 và UIT-ViQuAD2.0.
    * Ứng dụng thành công kỹ thuật Flow Matching tiên tiến (Matcha-TTS) và đóng góp frontend tách thanh điệu `vi_tone_v2` cho tiếng Việt.
    * Triển khai hoàn chỉnh ứng dụng Full-stack, chạy cục bộ trên CPU thông thường (Edge-TTS/gTTS dự phòng cần Internet) và đóng gói Docker.
  * **Định hướng phát triển tương lai:**
    * Chạy GPU để giảm độ trễ (hiện ~12 giây/câu trên CPU Docker).
    * Tinh chỉnh reranker và định tuyến cho câu hỏi kiến thức chung.
    * Thử LLM tiếng Việt (như PhoGPT, Vistral, SeaLLMs) để sinh câu trả lời.
  * **Lời cảm ơn Thầy Cô và Hội đồng đánh giá.**
* **Kịch bản thuyết trình (Speaker Script):**
  > "Nhìn lại quá trình nghiên cứu, đề tài đã hoàn thành các mục tiêu: xây dựng hệ thống Voice Q&A tiếng Việt khép kín trên ViMMRC và ViQuAD, làm chủ Matcha-TTS Flow Matching với frontend vi_tone_v2, chạy cục bộ ổn định trên CPU và đóng gói Docker 100%.  
  > Định hướng tương lai: nhóm sẽ triển khai trên GPU để giảm độ trễ dưới 2 giây, tinh chỉnh reranker cho câu hỏi kiến thức mở, và thử nghiệm mô hình LLM tiếng Việt để nâng cao năng lực suy luận.  
  > Nhóm em xin chân thành cảm ơn sự hướng dẫn tận tình của Thầy Cô! Rất mong nhận được góp ý quý báu từ Hội đồng. Em xin trân trọng cảm ơn!"