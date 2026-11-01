# KỊCH BẢN THUYẾT TRÌNH 5 - 10 PHÚT (BÁO CÁO NHANH CHO GIẢNG VIÊN & HỘI ĐỒNG)
## ĐỀ TÀI: HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0 (ViMMRC VOICE Q&A)

* **Môn học:** Học máy tiên tiến và ứng dụng
* **Thời lượng mục tiêu:** Khung 5 - 10 phút (~6:45 - 7:00 phút thuyết trình chuẩn, tốc độ nói tự nhiên ~125 - 130 từ/phút, tổng cộng 7 Slides)
* **File trình chiếu tương ứng:** `docs/ViMMRC_Presentation_5min.pptx`
* **File kịch bản Word tương ứng:** `docs/ViMMRC_KichBan_5phut.docx`
* **Thành viên thực hiện:**
  1. **Ngô Trí Huy**
  2. **Huỳnh Công Lương**
  3. **Trương Hoàng Duy**

---

### SLIDE 1: HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT DỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0
* **Thời lượng dự kiến:** 0:00 - 1:00 (60s)
* **Nội dung hiển thị trên Slide:**
  * **Tên đề tài:** Hệ Thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0
  * **Môn học:** Học máy tiên tiến và ứng dụng | Báo cáo nhanh Hội đồng (Khung 5 - 10 Phút)
  * **Thành viên thực hiện:**
    * **Ngô Trí Huy**
    * **Huỳnh Công Lương**
    * **Trương Hoàng Duy**
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô trong Hội đồng! Hôm nay, em xin đại diện nhóm báo cáo kết quả thực hiện đồ án môn Học máy tiên tiến và ứng dụng: 'Hệ thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0'.
  > Nhóm gồm 3 thành viên: em Ngô Trí Huy, bạn Huỳnh Công Lương và bạn Trương Hoàng Duy.
  > Động lực của đề tài xuất phát từ thực tế: các hệ thống đọc hiểu hiện nay chủ yếu tương tác qua văn bản gõ phím, gây bất tiện trong các tình huống rảnh tay hoặc với người khiếm thị. Mục tiêu của nhóm là xây dựng một chu trình khép kín: người dùng hỏi bằng giọng nói, hệ thống tự động tìm ngữ cảnh, đọc hiểu suy luận và trả lời lại bằng giọng nói trên máy tính cá nhân."

---

### SLIDE 2: CHU TRÌNH HỎI - ĐÁP 4 CHẶNG & CƠ CHẾ DỰ PHÒNG ĐA TẦNG
* **Thời lượng dự kiến:** 1:00 - 2:15 (75s)
* **Nội dung hiển thị trên Slide:**
  * **Chặng 1 - STT (Whisper-small LoRA 50h):** CTranslate2 + INT8; VAD cắt khoảng lặng; WER 13,77% | CER 6,67% (VietSpeech).
  * **Chặng 2 - Retrieval (BM25 + Dense + Reranker):** Kho 5.869 đoạn + Wikipedia; `bge-reranker-v2-m3`; F1 kiến thức mở: 15,4 → 24,3.
  * **Chặng 3 - MRC (ViT5-base fine-tune):** Sinh câu trả lời tự do; Train ViMMRC + ViQuAD2.0; Test: EM 41,05% | F1 66,55%.
  * **Chặng 4 - TTS (Matcha-TTS OT-CFM):** 10 bước ODE trên CPU; Frontend `vi_tone_v2`; RTF: 0,52 | CER: 1,9%.
  * **Chiến lược dự phòng & vận hành cục bộ trên CPU:**
    * STT: Thread-safe Lazy Loading giúp server khởi động nhanh (~0,45s); model Whisper-small LoRA 50h chạy int8 trên CPU.
    * MRC & TTS: ViT5 chạy trên CPU, dự phòng bằng bộ trích câu khớp nhất (lexical); TTS ưu tiên Matcha → VITS → Edge-TTS → gTTS.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Để thực hiện mục tiêu trên, nhóm thiết kế kiến trúc pipeline gồm 4 chặng nối tiếp:
  > Chặng 1, STT: Nhận âm thanh từ micro người dùng, mô hình Whisper-small fine-tune LoRA 50h VietSpeech chuyển thành văn bản, chạy bằng CTranslate2 INT8 với bộ lọc VAD cắt khoảng lặng, đạt WER 13,77% so với 36,76% của bản gốc chưa fine-tune.
  > Chặng 2, Retrieval: Tìm kiếm trên kho tri thức hai tầng gồm 5.869 đoạn văn ViMMRC và ViQuAD kết hợp 1,48 triệu đoạn Wikipedia tiếng Việt bằng BM25 và vector dense, sau đó reranker bge-reranker-v2-m3 chấm lại để chọn đoạn văn phù hợp nhất.
  > Chặng 3, MRC: Mô hình ViT5-base đọc đoạn văn và sinh câu trả lời tự do ngắn gọn, không cần các phương án lựa chọn sẵn.
  > Chặng 4, TTS: Mô hình Matcha-TTS dựa trên Conditional Flow Matching tổng hợp câu trả lời thành giọng đọc qua loa.
  > Mỗi chặng đều có cơ chế dự phòng tự động: nếu chưa nạp checkpoint ViT5 thì dùng bộ trích câu khớp nhất, nếu Matcha-TTS gặp lỗi thì chuyển sang VITS, Edge-TTS hoặc gTTS."

---

### SLIDE 3: BA ĐIỂM NHẤN KỸ THUẬT: RETRIEVAL HAI TẦNG, ViT5 & MATCHA-TTS
* **Thời lượng dự kiến:** 2:15 - 3:30 (75s)
* **Nội dung hiển thị trên Slide:**
  * **1. BM25 Tinh Chỉnh & Kho Hai Tầng:**
    * Kho tri thức hai tầng: 5.869 đoạn ViMMRC + ViQuAD và 1,48 triệu đoạn Wikipedia tiếng Việt (BM25 `bm25s` chia shard + vector dense `multilingual-e5-small`).
    * Tinh chỉnh siêu tham số: $k_1 = 2.1$ (độ bão hòa tần suất từ), $b = 1.0$ (chuẩn hóa theo độ dài văn bản).
    * Bigram Phrase Boost (+0,4): Nhận diện cặp từ ghép liền kề tiếng Việt ('Điện Biên', 'Văn Miếu'), cộng điểm thưởng theo IDF.
    * Top-3 mỗi nguồn (≤9 ứng viên) được reranker `bge-reranker-v2-m3` chấm chung, đoạn tầng 1 cộng +0,25.
    * BM25 hai tầng (trước reranker, test 2.545 câu): Recall@1 71,1%, Recall@5 85,9%. Answer F1 kiến thức mở: 15,4 → 24,3.
  * **2. Đọc Hiểu Sinh Câu Trả Lời: ViT5:**
    * Hỏi đáp tự do: người dùng đặt câu hỏi bằng lời tự nhiên, không cần các phương án lựa chọn A/B/C/D.
    * Dữ liệu: 27.164 câu hỏi gộp ViMMRC 2.0 + UIT-ViQuAD2.0, chia theo bài đọc để tránh rò rỉ (21.733 / 2.715 / 2.716).
    * ViT5-base (VietAI) fine-tune seq2seq; lưu checkpoint định kỳ, hỗ trợ tiếp tục huấn luyện (resume) khi ngắt quãng.
    * Kết quả test (2.716 câu): Exact Match 41,05%, token F1 66,55%; toàn chuỗi BM25 → ViT5 đạt F1 53,9% (đoạn đúng: 68,6%).
  * **3. Matcha-TTS & Frontend `vi_tone_v2`:**
    * Kiến trúc Flow Matching: Optimal-Transport Conditional Flow Matching (OT-CFM, ICASSP 2024) kết hợp vocoder HiFi-GAN.
    * Suy luận hiệu quả: Quỹ đạo vận chuyển thẳng giúp giải ODE nhanh trên CPU (10 bước trong benchmark đạt RTF 0,52).
    * Frontend `vi_tone_v2`: Tách 6 thanh điệu tiếng Việt thành token riêng cuối âm tiết (ví dụ: `hồ` → `h ô 2`), thu gọn bộ từ vựng còn 41 ký hiệu.
    * Text Normalizer: Chuẩn hóa ngày tháng, số liệu, tiền tệ, đơn vị đo, nhãn đáp án và chèn khoảng nghỉ theo dấu câu.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Đề tài tập trung vào 3 điểm nhấn kỹ thuật chính:
  > Thứ nhất, ở khâu Truy xuất, nhóm tinh chỉnh tham số BM25 với k1=2.1, b=1.0 và bổ sung Bigram Phrase Boost cộng điểm cho cụm từ ghép liền kề trong tiếng Việt. Đồng thời, nhóm xây dựng kho tri thức hai tầng kết hợp Wikipedia tiếng Việt và reranker bge-reranker-v2-m3, giúp F1 câu trả lời cho câu hỏi kiến thức mở tăng từ 15,4% lên 24,3%.
  > Thứ hai, ở phân hệ Đọc hiểu, nhóm chuyển bài toán sang hỏi đáp tự do bằng cách fine-tune mô hình ViT5-base trên 27.164 câu hỏi gộp từ ViMMRC 2.0 và UIT-ViQuAD2.0, chia theo bài đọc để không rò rỉ dữ liệu. Mô hình sinh câu trả lời ngắn gọn, đạt F1 66,55% và Exact Match 41,05% trên tập test.
  > Thứ ba, ở phân hệ TTS, nhóm huấn luyện mô hình Matcha-TTS theo hướng Flow Matching với frontend vi_tone_v2 tách 6 thanh điệu thành token độc lập ở cuối âm tiết, kết hợp bộ chuẩn hóa văn bản tiếng Việt."

---

### SLIDE 4: BẢNG SỐ LIỆU BENCHMARK GIỮA CÁC PHÂN HỆ & BASELINE
* **Thời lượng dự kiến:** 3:30 - 4:30 (60s)
* **Nội dung hiển thị trên Slide:**
  * **STT (Whisper-small LoRA 50h CT2 int8):** WER 13,77% / CER 6,67% (Test 1.802 mẫu VietSpeech) vs Whisper gốc 36,76% / 19,43%.
  * **Retrieval (BM25 tinh chỉnh, kho 2 tầng):** Recall@1 71,1% / Recall@5 85,9% (Test 2.545 câu); Ablation kho 552 đoạn: R@1 71,45% (cũ 64,2%).
  * **Pipeline cuối (BM25 + dense + reranker):** Answer F1 (200 câu trong kho / 200 câu mở): 60,7% / 24,3% vs BM25 thuần 58,0% / 15,4%.
  * **Toàn chuỗi (BM25 → ViT5):** EM 32,3% / token F1 53,9% (Test 2.545 câu) vs đưa đúng đoạn văn (Gold): F1 68,6%.
  * **MRC (ViT5-base fine-tune):** EM 41,05% / token F1 66,55% (Test 2.716 câu) vs trích câu khớp nhất (dự phòng khi thiếu model).
  * **TTS (Matcha-TTS nhóm huấn luyện):** CER 1,9% (ASR PhoWhisper, 10 câu InfoRe1) vs VITS MMS 4,3% | Người thật 0,7%.
  * **TTS (Cao độ & Phổ):** log-F0 RMSE 2,86 bán cung / MCD 5,35 dB vs VITS 4,31 bán cung | Edge-TTS 2,69 bán cung.
  * **Tốc độ & Độ trễ (Docker CPU):** RTF 0,52 / Tổng thời gian ~12s/câu (tắt reranker ~6s).
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô, bảng số liệu trên slide tổng hợp kết quả thực nghiệm của các phân hệ:
  > Ở phân hệ STT, fine-tune LoRA 50 giờ giúp giảm WER từ 36,76% xuống 13,77% và CER xuống 6,67% trên 1.802 mẫu test VietSpeech.
  > Ở phân hệ Retrieval, trên 2.545 câu test với kho tri thức hai tầng, BM25 đạt Recall@1 71,1% và Recall@5 85,9%. Khi kết hợp dense và reranker, F1 câu trả lời trên câu kiến thức mở tăng từ 15,4% lên 24,3%, và trên câu có đoạn trong kho tăng từ 58,0% lên 60,7%.
  > Ở phân hệ MRC, ViT5 fine-tune đạt Exact Match 41,05% và token F1 66,55% trên 2.716 câu test; khi chạy toàn chuỗi từ BM25 sang ViT5 đạt F1 53,9%.
  > Ở phân hệ TTS, Matcha-TTS đạt tỷ lệ lỗi ký tự CER 1,9% qua PhoWhisper, gần mức trần giọng người thật 0,7% và thấp hơn VITS MMS (4,3%). Sai số cao độ log-F0 đạt 2,86 bán cung, gần với Edge-TTS (2,69), với tốc độ RTF 0,52 trên CPU."

---

### SLIDE 5: QUÁ TRÌNH HUẤN LUYỆN & BIỂU ĐỒ HỘI TỤ ĐA PHÂN HỆ
* **Thời lượng dự kiến:** 4:30 - 5:30 (60s)
* **Nội dung hiển thị trên Slide:**
  * **Biểu đồ minh họa:** `chart_01_training_curves.png` (4 đồ thị trực quan: Loss STT Whisper LoRA 50h, Dò tham số BM25 & Recall, Đường cong hội tụ ViT5-base EM/F1, và Hàm mất mát Matcha-TTS OT-CFM).
  * **Điểm Nhấn Hội Tụ Mô Hình:**
    * **STT LoRA 50h:** Hàm mất mát Cross-Entropy giảm đều đặn từ ~1.85 xuống 0.42 tại bước 2.750, mô hình học tốt đặc trưng âm vị tiếng Việt mà không bị overfit.
    * **Retrieval Tuning:** Lưới tham số xác lập điểm cực đại tại $k_1 = 2.1, b = 1.0$, kết hợp Bigram boost nâng Recall@1 thêm 7.27% tuyệt đối.
    * **MRC ViT5-base:** Hội tụ sau 2 epoch trên 21.733 mẫu train; validation F1 đạt 66.55% và Exact Match đạt 41.05% trên tập test 2.716 câu.
    * **Matcha-TTS Flow Matching:** Loss vận chuyển tối ưu OT-CFM giảm nhanh dưới 1.0, kết hợp vocoder HiFi-GAN tái tạo âm thanh trong trẻo, tự nhiên.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Kính thưa Thầy Cô, slide số 5 minh họa trực quan quá trình huấn luyện và các đường cong hội tụ thực nghiệm của cả 4 phân hệ.
  > Ở góc trên bên trái là quá trình fine-tune STT Whisper-small LoRA trên 50 giờ dữ liệu VietSpeech: hàm mất mát giảm ổn định từ 1,85 xuống 0,42 tại checkpoint 2.750 bước, khẳng định mô hình thích ứng sâu với âm vị học tiếng Việt.
  > Ở góc trên bên phải là đồ thị quét tham số BM25: đường cong phản ánh rõ việc tăng k1 lên 2.1 và b lên 1.0 giúp Recall@1 tăng từ 64,18% lên 68,79%, và khi cộng thêm Bigram Boost thì bứt phá lên 71,45%.
  > Ở góc dưới bên trái, mô hình đọc hiểu ViT5-base hội tụ vững chắc sau 2 epoch huấn luyện, đạt điểm F1 66,55% và Exact Match 41,05% trên 2.716 mẫu test độc lập.
  > Cuối cùng ở góc dưới bên phải, đường cong hàm mất mát Flow Matching của Matcha-TTS và Mel-loss của vocoder HiFi-GAN giảm mượt mà, đảm bảo việc tổng hợp giọng đọc vừa chuẩn cao độ vừa tự nhiên như giọng người thật."

---

### SLIDE 6: SẢN PHẨM ĐÓNG GÓI DOCKER & KỊCH BẢN DEMO END-TO-END
* **Thời lượng dự kiến:** 5:30 - 6:30 (60s)
* **Nội dung hiển thị trên Slide:**
  * **Kỹ Nghệ Phần Mềm & Đóng Gói:**
    * Kiến trúc Full-Stack: Backend FastAPI bất đồng bộ + Frontend Angular 22 Standalone hiển thị trực quan.
    * Giao diện Trực quan: Hiển thị Pipeline Flow Indicator theo thời gian thực (Thu âm → STT → Retrieval → MRC → TTS → Nghe).
    * Docker Multi-Stage: Stage 1 (Node 22) biên dịch web; Stage 2 (Python 3.11-slim) cài đặt API và PyTorch CPU wheel.
    * Khởi chạy 1 Lệnh: `docker compose up -d` ánh xạ cổng 8090 → 8000, tích hợp sẵn Docker Healthcheck.
    * Kiểm thử Tự động: 54 bài kiểm thử tự động (53 passed, 1 skipped trên CPU) bao phủ từ xử lý dữ liệu đến REST API.
  * **Kịch Bản Demo Thực Tế (Live Flow):**
    * 1. Giọng nói Đầu vào: Người dùng bấm mic hỏi: *"Ai là tác giả của Truyện Kiều?"*.
    * 2. STT (~3s): Whisper-small LoRA 50h (CTranslate2 int8) nhận dạng văn bản tiếng Việt có dấu.
    * 3. Retrieval + reranker (~6s): BM25 + dense lấy ứng viên, reranker chọn đoạn Wikipedia "Truyện Kiều".
    * 4. MRC (~1,4s): ViT5 đọc đoạn Wikipedia về Truyện Kiều và sinh câu trả lời *"Nguyễn Du"*.
    * 5. TTS (~1,3s): Matcha-TTS chuẩn hóa văn bản và tổng hợp giọng đọc câu trả lời.
    * 6. Tổng Độ trễ: Khoảng 12 giây trên CPU Docker (STT ~3s, truy xuất + reranker ~6s, ViT5 ~1,4s, TTS ~1,3s); tắt reranker còn ~6 giây.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Về mặt kỹ nghệ phần mềm, nhóm đã tích hợp hệ thống thành ứng dụng Full-stack gồm Backend FastAPI và Frontend Angular 22, hiển thị trực quan trạng thái xử lý qua từng chặng. Toàn bộ dự án được đóng gói bằng Docker multi-stage, khởi chạy bằng một lệnh docker compose và có 54 bài kiểm thử tự động.
  > Trong kịch bản demo thực tế: khi người dùng bấm micro hỏi 'Ai là tác giả của Truyện Kiều?', phân hệ STT nhận dạng câu hỏi trong khoảng 3 giây; bộ truy xuất lấy ứng viên và reranker chọn đoạn Wikipedia về Truyện Kiều trong khoảng 6 giây; ViT5 sinh câu trả lời 'Nguyễn Du' trong 1,4 giây; và Matcha-TTS tổng hợp giọng đọc trong 1,3 giây. Tổng thời gian phản hồi khoảng 12 giây trên CPU Docker, hoặc khoảng 6 giây nếu tắt reranker."

---

### SLIDE 7: TỔNG KẾT ĐÓNG GÓP, GIỚI HẠN THỰC TẾ & HƯỚNG PHÁT TRIỂN
* **Thời lượng dự kiến:** 6:30 - 7:15 (45s)
* **Nội dung hiển thị trên Slide:**
  * **Kết Quả Đạt Được:**
    * Hoàn thiện chu trình Voice Q&A tiếng Việt dựa trên ViMMRC 2.0 và UIT-ViQuAD2.0 (27.164 câu hỏi).
    * Huấn luyện mô hình Matcha-TTS (ICASSP 2024) với frontend `vi_tone_v2` tách thanh điệu, đạt CER 1,9% và RTF 0,52.
    * Vận hành cục bộ trên CPU thông thường (Edge-TTS/gTTS dự phòng cần Internet), độ trễ ~12s/câu (~6s khi tắt reranker).
    * Đóng gói ứng dụng Full-stack (FastAPI + Angular) qua Docker multi-stage, đạt 54 bài kiểm thử tự động.
  * **Giới Hạn Hiện Tại & Hướng Mở Rộng:**
    * Chạy trên GPU: Giảm thời gian chờ (hiện ~12 giây/câu trên CPU Docker do reranker chiếm ~6 giây).
    * Tinh chỉnh định tuyến & reranker: Khắc phục hiện tượng câu hỏi kiến thức mở bị đoạn tầng 1 lấn át (hiện F1 mở đạt 24,3%).
    * Thử nghiệm LLM tiếng Việt: Đánh giá thêm các mô hình lớn hơn hoặc kết hợp xếp hạng nhiều câu trả lời ứng viên.
    * Hội thoại Đa lượt (Multi-Turn): Bổ sung bộ nhớ ngữ cảnh phiên làm việc để người dùng hỏi nối tiếp tự nhiên.
    * Ứng dụng thực tế: Thử nghiệm tích hợp vào kiosk tra cứu thông tin học đường và công cụ hỗ trợ người khiếm thị.
* **Kịch bản thuyết trình (Speaker Script):**
  > "Tóm lại, nhóm đã xây dựng hoàn chỉnh hệ thống Voice Q&A tiếng Việt dựa trên ViMMRC 2.0 và UIT-ViQuAD2.0, kết hợp từ nhận dạng giọng nói, truy xuất hai tầng, đọc hiểu sinh câu trả lời tự do đến tổng hợp giọng nói Matcha-TTS chạy cục bộ trên CPU.
  > Về hạn chế và hướng phát triển: hiện tại độ trễ trên CPU khoảng 12 giây mỗi câu do reranker chiếm 6 giây, và một số câu hỏi kiến thức mở vẫn còn nhầm lẫn khi đoạn văn tầng 1 được cộng điểm ưu tiên. Trong thời gian tới, nhóm dự kiến triển khai trên GPU để giảm độ trễ, tinh chỉnh bộ định tuyến cho câu hỏi kiến thức chung, và thử nghiệm các mô hình ngôn ngữ lớn tiếng Việt để hỗ trợ hội thoại đa lượt.
  > Nhóm chúng em xin chân thành cảm ơn Thầy Cô đã lắng nghe và rất mong nhận được ý kiến đóng góp của Hội đồng!"
