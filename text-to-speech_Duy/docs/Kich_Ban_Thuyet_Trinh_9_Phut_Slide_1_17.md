# KỊCH BẢN THUYẾT TRÌNH 9 PHÚT (SLIDE 1 → SLIDE 17 + DEMO)
**Tài liệu gốc:** [`ViMMRC_Voice_QA_Slides.pdf`](ViMMRC_Voice_QA_Slides.pdf)  
**Người trình bày:** Trương Hoàng Duy (Mở đầu chung cả nhóm + Phần I: Tổng hợp tiếng nói Matcha-TTS & HiFi-GAN + Demo)  
**Tổng thời lượng:** **09 phút 00 giây** (~1.250 chữ – tốc độ nói chuẩn học thuật ~135–140 âm tiết/phút, đã tính thời gian chuyển slide, bấm video minh họa ở Slide 11, 13 và chạy Demo thực tế).

---

## BẢNG PHÂN BỔ THỜI GIAN TỔNG QUAN (TIMELINE 9 PHÚT)

| Mốc thời gian | Thời lượng | Slide | Nội dung chính |
| :---: | :---: | :---: | :--- |
| `00:00 – 00:25` | 25 giây | **Slide 1** | Chào Thầy, giới thiệu đề tài & phân công 3 thành viên trong nhóm |
| `00:25 – 00:50` | 25 giây | **Slide 2** | Bối cảnh & Bài toán: Hỏi bằng giọng nói, nghe câu trả lời có căn cứ |
| `00:50 – 01:15` | 25 giây | **Slide 3** | Khảo sát nghiên cứu: Các nền tảng kế thừa ở 4 chặng |
| `01:15 – 01:45` | 30 giây | **Slide 4** | Giải pháp đề xuất & Kiến trúc tổng thể 4 chặng chạy trên CPU |
| `01:45 – 02:00` | 15 giây | **Slide 5** | Chuyển sang Phần I: Tổng hợp tiếng nói Matcha-TTS & HiFi-GAN |
| `02:00 – 02:30` | 30 giây | **Slide 6** | Bối cảnh & Khảo sát 4 hướng tiếp cận TTS cho tiếng Việt |
| `02:30 – 03:00` | 30 giây | **Slide 7** | Giải pháp đề xuất: 5 Thách thức & 5 Giải pháp kỹ thuật của nhóm |
| `03:00 – 03:25` | 25 giây | **Slide 8** | 4 Mục tiêu thiết kế & 6 Đóng góp chính của phân hệ TTS |
| `03:25 – 03:50` | 25 giây | **Slide 9** | Luồng xử lý tổng thể: 6 giai đoạn từ văn bản thô đến tệp âm thanh |
| `03:50 – 04:20` | 30 giây | **Slide 10** | Ví dụ thực tế: Một câu trả lời đi qua 6 bước biến đổi trong pipeline |
| `04:20 – 04:55` | 35 giây | **Slide 11** | Mô hình âm học Matcha-TTS (OT-CFM): Đi đường thẳng 10–20 bước *(kèm bấm Video)* |
| `04:55 – 05:25` | 30 giây | **Slide 12** | Đóng góp ngữ âm: Tách thanh điệu thành token riêng (`98 → 41 ký hiệu`) |
| `05:25 – 05:50` | 25 giây | **Slide 13** | Căn chỉnh thời gian MAS viết lại bằng Numba JIT *(kèm bấm Video)* |
| `05:50 – 06:15` | 25 giây | **Slide 14** | Hậu xử lý khoảng lặng theo dấu câu & Điều phối 4 engine dự phòng |
| `06:15 – 06:45` | 30 giây | **Slide 15** | Huấn luyện 2 giai đoạn trên InfoRe1 (25 giờ) & Chọn checkpoint bằng ASR |
| `06:45 – 07:20` | 35 giây | **Slide 16** | Kết quả thực nghiệm: MCD `3,05 dB`, log-F0 `0,88`, CER `0,8%`, RTF `< 0,7` |
| `07:20 – 07:45` | 25 giây | **Slide 17** | Đối sánh Cục bộ vs Đám mây: Đánh đổi chất giọng lấy quyền kiểm soát |
| `07:45 – 09:00` | 75 giây | **DEMO** | **Demo trực tiếp:** Nghe đối chiếu giọng đọc Matcha-TTS chuẩn hóa câu trả lời thực tế & chạy luồng hỏi đáp giọng nói trên giao diện Web, trước khi chuyển lời sang Phần II |

---

## NỘI DUNG KỊCH BẢN CHI TIẾT TỪNG SLIDE

### PHẦN MỞ ĐẦU: TỔNG QUAN HỆ THỐNG (SLIDE 1 – SLIDE 4 | `00:00 – 01:45`)

#### **Slide 1: Trang bìa – Giới thiệu Đề tài & Nhóm thực hiện** (`00:00 – 00:25` | *25 giây*)
- **[Thao tác]:** Mở Slide 1, đứng thẳng, hướng mắt về phía giảng viên.
- **[Lời nói]:**
  > "Em chào Thầy ạ. Hôm nay nhóm chúng em xin báo cáo đồ án môn học **Học máy tiên tiến và ứng dụng** với đề tài: **Hệ thống Hỏi – Đáp Đọc hiểu Văn bản bằng Giọng nói Tiếng Việt (ViMMRC Voice Q&A)**.
  > Nhóm gồm 3 thành viên: bạn **Ngô Trí Huy** (Nhóm trưởng) phụ trách Truy xuất ngữ cảnh, Đọc hiểu, Hội thoại và API; bạn **Huỳnh Công Lương** phụ trách Nhận dạng giọng nói STT, Giao diện Web và Docker; và em là **Trương Hoàng Duy**, phụ trách Tổng hợp giọng nói TTS và Đánh giá âm học. Em xin phép mở đầu bằng phần tổng quan toàn hệ thống và trình bày sâu vào phân hệ đầu tiên là Tổng hợp tiếng nói."

---

#### **Slide 2: Bối cảnh & Bài toán – Hỏi bằng giọng nói, nghe câu trả lời có căn cứ** (`00:25 – 00:50` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 2, chỉ tay theo luồng *Đầu vào $\rightarrow$ Hệ thống $\rightarrow$ Đầu ra* ở nửa trên slide.
- **[Lời nói]:**
  > "Về bài toán đặt ra: các bộ dữ liệu đọc hiểu tiếng Việt hiện nay như **ViMMRC 2.0** hay **UIT-ViQuAD** vốn chỉ tương tác bằng văn bản và yêu cầu người dùng phải đưa sẵn đoạn văn.
  > Nhóm chúng em mở rộng thành bài toán thực tế hơn: **Đầu vào** là câu hỏi nói tự nhiên bằng tiếng Việt, không kèm đoạn văn; **Hệ thống** tự động tìm đoạn văn liên quan trong kho tri thức, đọc hiểu và soạn câu trả lời hoàn chỉnh; **Đầu ra** là câu trả lời trọn câu bằng giọng nói kèm theo đoạn văn làm bằng chứng.
  > Giải pháp này hướng tới người khiếm thị, kiosk học đường hoặc khi không tiện nhìn màn hình, với **3 ràng buộc kỹ thuật nghiêm ngặt**: phải chạy hoàn toàn trên **CPU**, hoạt động được **offline**, và **chủ động từ chối trả lời khi thiếu căn cứ**."

---

#### **Slide 3: Khảo sát nghiên cứu – Các nền tảng mà đề tài kế thừa ở từng chặng** (`00:50 – 01:15` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 3, quét nhẹ qua 4 cột *STT – Truy xuất – Đọc hiểu – TTS*.
- **[Lời nói]:**
  > "Để giải quyết bài toán này, nhóm đã khảo sát và kế thừa các nền tảng học máy tiêu biểu ở từng chặng:
  > - Ở **chặng STT**, nhóm kế thừa kiến trúc **Whisper** của Radford, kỹ thuật tinh chỉnh hạng thấp **LoRA** trên bộ dữ liệu **VietSpeech** và động cơ suy luận **CTranslate2**.
  > - Ở **chặng Truy xuất**, nhóm kết hợp **BM25**, truy xuất vector dày **Multilingual E5** và bộ xếp hạng chéo **BGE-M3**.
  > - Ở **chặng Đọc hiểu**, nhóm khai thác mô hình **ViT5**, các bộ đọc trích span trên hai tập **ViMMRC 2.0** và **UIT-ViQuAD 2.0**.
  > - Và ở **chặng TTS**, nhóm ứng dụng lý thuyết **Flow Matching** qua kiến trúc **Matcha-TTS**, thuật toán căn chỉnh **MAS** của Glow-TTS và mạng sinh sóng âm **HiFi-GAN**."

---

#### **Slide 4: Giải pháp đề xuất & Kiến trúc tổng thể – Chu trình hỏi đáp 4 chặng** (`01:15 – 01:45` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 4, chỉ vào 4 con số lớn trên 4 thẻ và thanh độ trễ màu đen ở dưới cùng.
- **[Lời nói]:**
  > "Ghép nối 4 thành phần trên, kiến trúc tổng thể của hệ thống gồm 4 chặng tuần tự kèm cơ chế dự phòng đa tầng:
  > - **Chặng 1 (STT):** Mô hình `Whisper-small LoRA` tinh chỉnh trên 50 giờ VietSpeech, lượng tử hóa INT8, kéo tỷ lệ lỗi từ **WER từ 36,76% xuống còn 13,77%**.
  > - **Chặng 2 (Retrieval):** Kết hợp BM25, Dense vector và Reranker trên kho **5.879 đoạn chọn lọc** cộng với **1,48 triệu đoạn Wikipedia**, đạt **Recall@5 là 85,9%** (Recall@1 đạt 71,1%).
  > - **Chặng 3 (MRC):** Sau khi đối sánh 8 ứng viên, bộ đọc trích span `vi-mrc-large` đạt **F1 câu nói 0,468** (so với ViT5 là 0,446).
  > - **Chặng 4 (TTS):** Mô hình `Matcha-TTS` giải ODE trong 10 đến 20 bước Euler trên CPU, đạt tỷ lệ lỗi ký tự **CER chỉ 0,8%**, sát với giọng thật 0,7%.
  > Tổng độ trễ toàn chuỗi khi chạy trên Docker CPU 4 luồng là khoảng **10,6 giây mỗi câu**, và giảm xuống còn **5,1 giây** ở chế độ nhanh khi tắt reranker."

---

### PHẦN I: TỔNG HỢP TIẾNG NÓI MATCHA-TTS & HIFI-GAN (SLIDE 5 – SLIDE 17 | `01:45 – 07:45`)

#### **Slide 5: Bìa Phần I – Tổng hợp tiếng nói Matcha-TTS và HiFi-GAN** (`01:45 – 02:00` | *15 giây*)
- **[Thao tác]:** Chuyển sang Slide 5.
- **[Lời nói]:**
  > "Tiếp theo, em xin đi sâu vào **Phần I: Phân hệ Tổng hợp tiếng nói với Matcha-TTS và HiFi-GAN**. Bốn con số tóm tắt kết quả nổi bật nhất của phân hệ này là: **CER đạt 0,8%**, sai số cao độ **log-F0 RMSE đạt 0,88 bán cung**, hệ số thời gian thực **RTF từ 0,53 đến 0,64 trên CPU 8 luồng**, và bộ từ điển ngữ âm tối ưu chỉ còn **41 token (giảm 58,2%)**."

---

#### **Slide 6: Bối cảnh & Khảo sát nghiên cứu TTS** (`02:00 – 02:30` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 6, chỉ vào cột Bối cảnh bên trái rồi đối chiếu bảng 4 dòng bên phải.
- **[Lời nói]:**
  > "Khi xây dựng TTS cho hệ thống đọc hiểu tiếng Việt, nhóm đối mặt với 3 đặc thù: tiếng Việt có **6 thanh điệu** quyết định trực tiếp nghĩa của từ; câu trả lời đọc hiểu chứa nhiều **nhãn đáp án, con số, ngày tháng, đơn vị đo**; và hệ thống bắt buộc phải **chạy nhanh trên CPU, hoàn toàn offline**.
  > Qua khảo sát 4 hướng tiếp cận:
  > - **VITS MMS** của Meta chạy cục bộ nhanh nhưng thanh điệu tiếng Việt còn gượng, dẫn tới **CER lên tới 4,7%**.
  > - Các mô hình **Diffusion TTS** truyền thống cho chất lượng cao nhưng cần hàng trăm bước giải khử nhiễu nên rất chậm trên CPU.
  > - **Glow-TTS với MAS** tự căn chỉnh tốt nhưng bản cài đặt gốc yêu cầu biên dịch Cython/C++ rất dễ lỗi môi trường.
  > - Vì vậy, nhóm lựa chọn hướng thứ 4 là kết hợp **Matcha-TTS (chỉ cần 10–20 bước giải, ~20 triệu tham số) cùng HiFi-GAN**, và tự thiết kế bộ xử lý ngữ âm đầu vào chuyên biệt cho tiếng Việt."

---

#### **Slide 7: Giải pháp đề xuất – Matcha-TTS tiếng Việt với frontend tách thanh điệu** (`02:30 – 03:00` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 7, điểm qua 5 mũi tên *Thách thức $\rightarrow$ Giải pháp*.
- **[Lời nói]:**
  > "Từ các thách thức trên, nhóm đề xuất 5 giải pháp kỹ thuật tương ứng:
  > 1. Để chạy nhanh hơn thời gian thực trên CPU: nhóm áp dụng **Matcha-TTS (OT-CFM)** kết hợp học chuyển giao từ checkpoint tiếng Anh.
  > 2. Để khắc phục lỗi sai thanh điệu và dữ liệu thưa: nhóm **tách dấu thanh thành 6 token riêng biệt**, thu gọn bảng ký hiệu còn đúng **41 token**.
  > 3. Để khử tiếng rè kim loại khi ghép vocoder tổng quát: nhóm **tinh chỉnh trực tiếp HiFi-GAN trên phổ Mel nhân tạo do chính Matcha-TTS sinh ra**.
  > 4. Với văn bản chứa nhãn, số, ngày tháng: nhóm xây dựng bộ **chuẩn hóa văn bản và chèn khoảng nghỉ động theo dấu câu**.
  > 5. Để dễ đóng gói và không bao giờ đứt dịch vụ: nhóm **viết lại MAS bằng Numba JIT** và thiết kế **4 engine dự phòng**."

---

#### **Slide 8: Mục tiêu & 6 Đóng góp chính của phân hệ TTS** (`03:00 – 03:25` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 8.
- **[Lời nói]:**
  > "Slide 8 hệ thống hóa lại **4 mục tiêu cốt lõi** (Ngữ âm chính xác 6 thanh, Tài nguyên thấp `RTF < 1` trên CPU, Xử lý văn bản đặc thù, và Tự chủ offline) cùng **6 đóng góp kỹ thuật** của em trong đề tài: từ việc huấn luyện Matcha-TTS trên 25 giờ dữ liệu InfoRe1, thiết kế bộ tách thanh 41 token, viết lại MAS bằng Numba JIT, tinh chỉnh HiFi-GAN 50.000 bước, xây dựng bộ điều phối 4 engine, cho đến thiết lập quy trình đo kiểm khách quan bằng `MCD, F0, log-F0, CER` và `RTF`."

---

#### **Slide 9: Luồng xử lý – Sáu giai đoạn từ văn bản đến tệp âm thanh** (`03:25 – 03:50` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 9, chỉ theo thứ tự từ khối 1 đến khối 6.
- **[Lời nói]:**
  > "Về kiến trúc vận hành, mỗi khi nhận một câu trả lời thô từ khâu đọc hiểu, luồng xử lý của TTS đi qua **6 giai đoạn nối tiếp**:
  > - **Bước 1 (Chuẩn hóa):** Xóa Markdown, đổi ký hiệu `(B)` thành `'Đáp án B:'`, chuyển toàn bộ số, ngày tháng, đơn vị sang chữ tiếng Việt.
  > - **Bước 2 (Phân cụm):** Cắt câu dài theo các dấu phẩy, chấm phẩy, hai chấm, chấm câu.
  > - **Bước 3 (Token + thanh):** Tách dấu thanh ra cuối âm tiết và ánh xạ vào bảng mã 41 token.
  > - **Bước 4 (Matcha-TTS):** Giải phương trình dòng chảy OT-CFM trong 10–20 bước để sinh phổ Mel 80 kênh.
  > - **Bước 5 (HiFi-GAN):** Tái tạo sóng âm 22,05 kHz kết hợp bộ lọc khử nhiễu `Denoiser`.
  > - **Bước 6 (Hậu xử lý):** Cắt khoảng lặng thừa dưới `-30 dB`, làm mượt biên `fade 10 ms` và ghép thành tệp WAV hoàn chỉnh."

---

#### **Slide 10: Ví dụ thực – Một câu trả lời đi qua pipeline** (`03:50 – 04:20` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 10, chỉ vào từng dòng biến đổi cụ thể.
- **[Lời nói]:**
  > "Để thấy rõ từng bước biến đổi số, giả sử đầu vào từ bộ đọc là chuỗi: `'Đáp án: (B) Chiến thắng Điện Biên Phủ ngày 07/05/1954.'`
  > - Qua **Bước 1**, ngày `'07/05/1954'` được bung hoàn toàn thành chữ `'ngày bảy tháng năm năm một nghìn chín trăm năm mươi tư'`.
  > - Qua **Bước 2**, câu được tách thành 2 cụm ngữ nghĩa kèm khoảng nghỉ `0,25 giây` sau dấu hai chấm và `0,40 giây` ở cuối câu.
  > - Qua **Bước 3**, từ `'Chiến thắng'` được tách thành các chữ cái cơ sở `c-h-i-ê-n` cộng với token thanh sắc ở cuối âm tiết.
  > - Qua **Bước 4**, Matcha-TTS chạy 20 bước Euler tạo ra ma trận phổ Mel kích thước **80 kênh nhân 412 khung** (tương ứng khoảng 4,78 giây).
  > - Và ở **Bước 5 & Bước 6**, HiFi-GAN chuyển ma trận này thành mảng sóng âm **105.472 mẫu ở tần số 22.050 Hz**, làm mượt điểm nối và xuất ra file WAV."

---

#### **Slide 11: Mô hình âm học – Matcha-TTS đi đường thẳng nên chỉ cần 10–20 bước** (`04:20 – 04:55` | *35 giây*)
- **[Thao tác]:** Chuyển sang Slide 11. **Bấm phát Video minh họa** ở khung bên trái để hội đồng thấy quỹ đạo đường thẳng của OT-CFM so với đường cong của Diffusion.
- **[Lời nói]:**
  > "Câu hỏi đặt ra là: *Vì sao Matcha-TTS có thể chạy nhanh hơn thời gian thực trên CPU?*
  > Mời Thầy quan sát hình động minh họa bên trái: Các mô hình khuếch tán **Diffusion** truyền thống biến đổi từ nhiễu Gaussian sang phổ Mel theo những **quỹ đạo đường cong phức tạp**, nên phải chia nhỏ thành hàng trăm bước giải để không bị lệch hướng.
  > Ngược lại, **Matcha-TTS** sử dụng **Optimal-Transport Conditional Flow Matching (OT-CFM)** — ép trường vận tốc học một **đường đi thẳng trực tiếp** nối từ nhiễu trắng đến phổ Mel đích. Nhờ quỹ đạo là đường thẳng, phương pháp giải ODE Euler chỉ cần từ **10 đến 20 bước nhảy** là hội tụ chính xác về phổ Mel, giúp giảm số phép tính đi hàng chục lần và chạy mượt ngay trên CPU."

---

#### **Slide 12: Đóng góp ngữ âm – Tách thanh điệu thành token riêng (`98 → 41 ký hiệu`)** (`04:55 – 05:25` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 12, chỉ vào biểu đồ cột `98 -> 41`, biểu đồ tròn ở giữa và bảng tách dấu bên phải.
- **[Lời nói]:**
  > "Đóng góp cốt lõi thứ hai của em nằm ở việc xử lý chữ Quốc ngữ tiếng Việt.
  > Nếu giữ nguyên dấu thanh gắn liền trên từng nguyên âm như cách truyền thống, bảng từ điển sẽ phình lên tới **98 ký hiệu**. Những nguyên âm mang dấu hiếm gặp như `'ẵ'`, `'ự'`, `'ỵ'` xuất hiện rất ít trong tập huấn luyện, gây ra hiện tượng **dữ liệu thưa (data sparsity)** khiến mô hình đọc sai thanh điệu.
  > Giải pháp của nhóm là dùng chuẩn phân rã Unicode để **tách hoàn toàn dấu thanh ra khỏi nguyên âm gốc thành 6 token thanh điệu từ `0` đến `5` đặt ở cuối mỗi âm tiết** — ví dụ chữ `'hồ'` thành `h - ô - 2`, chữ `'nội'` thành `n - ô - i - 5`.
  > Cách làm này giúp thu gọn từ điển từ **98 xuống chỉ còn 41 ký hiệu (giảm 58,2%)**, bao gồm 29 chữ cái cơ sở, 6 thanh điệu, 4 dấu câu và 2 ký tự khoảng trắng/blank. Quan trọng nhất là **mọi nguyên âm trong tập dữ liệu đều cùng đóng góp gradient để học 6 token thanh điệu**, giúp đường cong cao độ F0 vững chắc hơn hẳn."

---

#### **Slide 13: Căn chỉnh thời gian – MAS viết lại bằng Numba, không cần trình biên dịch C++** (`05:25 – 05:50` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 13. **Bấm phát Video minh họa** ma trận quy hoạch động MAS.
- **[Lời nói]:**
  > "Trong quá trình huấn luyện, để biết mỗi âm vị kéo dài bao nhiêu khung phổ Mel mà không cần nhãn thời lượng gán tay, Matcha-TTS dùng thuật toán quy hoạch động **MAS (Monotonic Alignment Search)** như minh họa trên màn hình.
  > Tuy nhiên, bản cài đặt gốc của tác giả viết bằng Cython yêu cầu trình biên dịch C++ (`gcc` hoặc `MSVC`), rất hay lỗi khi đóng gói đa nền tảng. Em đã **viết lại toàn bộ hàm quy hoạch động này trên Python thuần kết hợp trình biên dịch tức thời Numba JIT (`@numba.jit(nopython=True)`)**, đạt tốc độ chạy tương đương mã C++ nhưng cài đặt và đóng gói trơn tru 100% trên cả Windows, macOS, Linux và Docker."

---

#### **Slide 14: Hậu xử lý & Điều phối – Chèn khoảng lặng theo dấu câu, 4 engine dự phòng** (`05:50 – 06:15` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 14, chỉ vào biểu đồ ngang bên trái và 4 tầng engine bên phải.
- **[Lời nói]:**
  > "Ở khâu hậu xử lý âm học, để giọng đọc câu trả lời dài có nhịp điệu tự nhiên như người thật, hệ thống tự động giữ lại **50 ms biên phụ âm cuối** (tránh nuốt âm cuối `-p, -t, -c, -m, -n`), làm mượt biên nối **10 ms**, và chèn khoảng nghỉ linh hoạt: **150 ms** cho dấu phẩy, **250 ms** cho dấu hai chấm, **400 ms** khi kết thúc câu và **450 ms** khi xuống dòng.
  > Đồng thời, hệ thống có kiến trúc **dự phòng 2 cấp với 4 engine**: ưu tiên mô hình tự huấn luyện **Matcha-TTS**, đối sánh cục bộ với **VITS MMS**, và tự động lùi về **Edge-TTS** hoặc **gTTS** nếu thiếu tài nguyên phần cứng, đảm bảo hệ thống không bao giờ bị câm."

---

#### **Slide 15: Huấn luyện – Hai giai đoạn trên InfoRe1 (~25 giờ, một giọng nữ miền Bắc)** (`06:15 – 06:45` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 15, chỉ vào thẻ GĐ 1, GĐ 2 và khung Chọn checkpoint bằng ASR.
- **[Lời nói]:**
  > "Về quy trình huấn luyện trên tập dữ liệu **InfoRe1 (25 giờ, đơn giọng nữ miền Bắc)**, em thực hiện **2 giai đoạn nối tiếp**:
  > - **Giai đoạn 1 (Acoustic):** Huấn luyện chuyển giao `Matcha-TTS` suốt **150.000 bước (tương đương 327 epoch)** với bộ tối ưu Adam và trung bình trượt hàm mũ `EMA 0,9999`. Một kinh nghiệm thực tế rất quan trọng là hàm Loss hội tụ khá sớm, nhưng độ rõ của dấu thanh vẫn tiếp tục tốt lên rất lâu sau đó; vì vậy nhóm đã dùng mô hình nhận dạng **PhoWhisper** để chấm CER tự động qua các mốc và chọn ra checkpoint tốt nhất tại bước 150.000.
  > - **Giai đoạn 2 (Vocoder):** Nếu ghép trực tiếp Matcha-TTS với HiFi-GAN đa ngôn ngữ có sẵn thì âm thanh bị rè kim loại do lệch phân phối phổ Mel. Do đó, em đóng băng Matcha-TTS, xuất ra **4.000 cặp phổ Mel nhân tạo** và **tinh chỉnh đối kháng HiFi-GAN thêm 50.000 bước**, triệt tiêu hoàn toàn hiện tượng rè âm."

---

#### **Slide 16: Kết quả – CER 0,8% sát giọng thật, RTF dưới 0,7 trên CPU** (`06:45 – 07:20` | *35 giây*)
- **[Thao tác]:** Chuyển sang Slide 16, chỉ lần lượt vào 4 biểu đồ cột *MCD – log-F0 RMSE – CER – RTF*.
- **[Lời nói]:**
  > "Slide 16 trình bày kết quả đánh giá định lượng trên tập test độc lập (từ mẫu 14.800 trở đi), đối sánh giữa **Matcha 20 bước**, **Matcha 10 bước** và mô hình nền **VITS MMS của Meta**:
  > 1. Về độ méo phổ **MCD**: Matcha đạt **3,05 dB** (bản 10 bước là 3,12 dB), tốt hơn rõ rệt so với mức **4,40 dB** của VITS MMS.
  > 2. Về sai số cao độ thanh điệu **log-F0 RMSE**: Matcha chỉ lệch **0,88 bán cung**, thấp hơn **gần 5 lần** so với mức **4,29 bán cung** của VITS MMS — phản ánh hiệu quả trực tiếp của cơ chế tách 6 token thanh điệu.
  > 3. Về độ rõ nội dung khi chấm chéo qua PhoWhisper: **CER của Matcha đạt 0,80%**, tiệm cận sát giọng thu âm thật của con người là **0,70%**, và thấp hơn gần 6 lần so với mức **4,70%** của VITS.
  > 4. Về tốc độ trên **CPU 8 luồng**: Matcha đạt **RTF 0,64 ở 20 bước** và **0,53 ở 10 bước** — tức là tổng hợp 1 giây tiếng nói chỉ mất hơn nửa giây CPU."

---

#### **Slide 17: Đối sánh – Cục bộ hay đám mây: đánh đổi chất giọng lấy quyền kiểm soát** (`07:20 – 07:45` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 17, đối chiếu cột *Matcha-TTS (cam)* với *VITS MMS* và *Azure/Edge-TTS*.
- **[Lời nói]:**
  > "Cuối cùng, khi đặt cạnh các dịch vụ đám mây thương mại như **Azure / Edge-TTS**: dù dịch vụ đám mây có chất giọng xuất sắc nhờ mô hình hàng trăm triệu tham số, nhưng bắt buộc phải có Internet và phải gửi dữ liệu văn bản ra máy chủ bên ngoài.
  > Trong khi đó, **Matcha-TTS tự huấn luyện của nhóm** chỉ nặng khoảng **20 triệu tham số**, vượt trội hoàn toàn so với VITS MMS ở độ chuẩn thanh điệu tiếng Việt, mà vẫn đảm bảo **100% chạy cục bộ offline, bảo mật dữ liệu tại chỗ và hoàn toàn miễn phí**."

---

### PHẦN DEMO TRỰC TIẾP (LIVE DEMO TTS & TOÀN CHUỖI | `07:45 – 09:00` | *1 phút 15 giây*)

- **[Thao tác chuẩn bị trước giờ báo cáo]:**
  - Mở sẵn trình duyệt tại giao diện Web của nhóm (`http://localhost:8090`) **hoặc** cửa sổ phát âm thanh / video demo ở Slide 49 để bấm phát ngay không tốn thời gian chờ nạp.
- **[Lời nói & Thao tác Demo (`07:45 – 09:00`)]:**
  > "Trước khi nhường lời cho bạn Ngô Trí Huy trình bày sâu về khâu Truy xuất và Đọc hiểu, em xin phép **Demo trực tiếp trong 1 phút** để Thầy nghe thử chất giọng thực tế của mô hình **Matcha-TTS + HiFi-GAN** cũng như cách hệ thống vận hành toàn chuỗi:
  >
  > *(Thao tác 1 – `07:55`: Bấm phát mẫu âm thanh câu trả lời chuẩn hóa hoặc chạy trên giao diện Web)*  
  > Đầu tiên, đây là âm thanh đầu ra thực tế từ câu trả lời có chứa cả ký hiệu đáp án trắc nghiệm, số liệu và ngày tháng: *'Đáp án B: Chiến thắng Điện Biên Phủ ngày 07/05/1954'*.  
  > *(Cho phát âm thanh ~5 giây)*  
  > Như Thầy vừa nghe, toàn bộ ngày tháng được đọc thành chữ rõ ràng, khoảng nghỉ sau dấu hai chấm rất tự nhiên, giữ trọn vẹn cả 6 thanh điệu tiếng Việt và hoàn toàn không còn tiếng rè kim loại nhờ HiFi-GAN đã được tinh chỉnh 50.000 bước.
  >
  > *(Thao tác 2 – `08:25`: Chuyển sang màn hình Giao diện Web `VietRead Voice` của nhóm)*  
  > Trên giao diện Web thực tế của nhóm, khi người dùng nhấn nút **Thu âm** và hỏi bằng giọng nói — ví dụ: *'Chiến dịch đại phá quân Thanh năm 1789 do ai chỉ huy?'* — thanh trạng thái bên phải sẽ sáng dần qua đúng 5 bước: từ **Thu âm** $\rightarrow$ **Speech-to-Text** $\rightarrow$ **Retrieval** $\rightarrow$ **MRC** $\rightarrow$ và cuối cùng là **Text-to-Speech** phát ra câu trả lời hoàn chỉnh kèm đoạn văn bằng chứng trích xuất ngay bên dưới. Thậm chí ở lượt sau, khi hỏi nối tiếp *'Ông ấy lên ngôi ở đâu?'*, hệ thống vẫn hiểu *'ông ấy'* chính là Quang Trung.
  >
  > Vậy làm thế nào để từ một câu hỏi tự do như vậy, hệ thống có thể tìm đúng đoạn văn trong hơn **1,48 triệu đoạn Wikipedia** và trích xuất chính xác câu trả lời trên CPU? Em xin nhường lời lại cho bạn **Ngô Trí Huy** trình bày tiếp **Phần II từ Slide 18** ạ!"

