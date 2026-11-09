# KỊCH BẢN THUYẾT TRÌNH (SLIDE 1 → SLIDE 17)
**Tài liệu gốc:** [`ViMMRC_Voice_QA_Slides.pptx.pdf`](file:///d:/Project/vimmrc-qa-voice/docs/ViMMRC_Voice_QA_Slides.pptx.pdf) (Bản cập nhật mới nhất, 52 slide)  
**Người trình bày:** Trương Hoàng Duy (Mở đầu chung cả nhóm + Phần I: Tổng hợp tiếng nói Matcha-TTS & HiFi-GAN)  
**Tổng thời lượng:** **07 phút 45 giây** (~1.100 chữ – tốc độ nói chuẩn học thuật ~135–140 âm tiết/phút, đã tính thời gian chuyển slide và bấm các video/mô phỏng ở Slide 11, 13; phần Demo toàn chuỗi sẽ do nhóm thực hiện ở cuối buổi báo cáo tại Slide 50).

---

## BẢNG PHÂN BỔ THỜI GIAN TỔNG QUAN (TIMELINE ~7 PHÚT 45 GIÂY)

| Mốc thời gian | Thời lượng | Slide | Nội dung chính |
| :---: | :---: | :---: | :--- |
| `00:00 – 00:25` | 25 giây | **Slide 1** | Chào Thầy, giới thiệu đề tài & phân công 3 thành viên trong nhóm |
| `00:25 – 00:50` | 25 giây | **Slide 2** | Bối cảnh & Bài toán: Hỏi bằng giọng nói, tiếp nhận câu trả lời có bằng chứng xác thực |
| `00:50 – 01:15` | 25 giây | **Slide 3** | Khảo sát nghiên cứu: Các nền tảng học máy kế thừa ở 4 chặng |
| `01:15 – 01:45` | 30 giây | **Slide 4** | Giải pháp đề xuất & Kiến trúc tổng thể: Chu trình 4 chặng vận hành trên CPU |
| `01:45 – 02:00` | 15 giây | **Slide 5** | Chuyển sang Phần I: Tổng hợp tiếng nói Matcha-TTS & HiFi-GAN |
| `02:00 – 02:30` | 30 giây | **Slide 6** | Bối cảnh & Khảo sát 4 hướng tiếp cận TTS cho tiếng Việt |
| `02:30 – 03:00` | 30 giây | **Slide 7** | Giải pháp đề xuất: 5 Thách thức & 5 Giải pháp kỹ thuật của nhóm |
| `03:00 – 03:25` | 25 giây | **Slide 8** | 4 Mục tiêu thiết kế & 6 Đóng góp kỹ thuật chính của phân hệ TTS |
| `03:25 – 03:50` | 25 giây | **Slide 9** | Luồng xử lý tổng thể: 6 giai đoạn từ văn bản thô đến tệp âm thanh |
| `03:50 – 04:20` | 30 giây | **Slide 10** | Ví dụ thực tế: Một câu trả lời đi qua 6 bước biến đổi trong pipeline |
| `04:20 – 04:55` | 35 giây | **Slide 11** | Mô hình âm học Matcha-TTS (OT-CFM): Quỹ đạo thẳng 10–20 bước *(kèm bấm Video)* |
| `04:55 – 05:25` | 30 giây | **Slide 12** | Đóng góp ngữ âm: Tách thanh điệu thành token riêng (`98 → 41 ký hiệu`) |
| `05:25 – 05:50` | 25 giây | **Slide 13** | Căn chỉnh thời gian MAS tái lập trình bằng Numba JIT *(kèm bấm Video)* |
| `05:50 – 06:15` | 25 giây | **Slide 14** | Hậu xử lý khoảng lặng thích ứng theo dấu câu & Điều phối 4 engine dự phòng |
| `06:15 – 06:45` | 30 giây | **Slide 15** | Huấn luyện 2 giai đoạn trên InfoRe1 (25 giờ) & Chọn checkpoint bằng ASR |
| `06:45 – 07:20` | 35 giây | **Slide 16** | Kết quả thực nghiệm: MCD `3,05 dB`, log-F0 `0,88`, CER `0,8%`, RTF `< 0,7` |
| `07:20 – 07:45` | 25 giây | **Slide 17** | Đối sánh Cục bộ vs Đám mây & Chuyển lời sang bạn Ngô Trí Huy (Phần II) |

---

## NỘI DUNG KỊCH BẢN CHI TIẾT TỪNG SLIDE

### PHẦN MỞ ĐẦU: TỔNG QUAN HỆ THỐNG (SLIDE 1 – SLIDE 4 | `00:00 – 01:45`)

#### **Slide 1: Trang bìa – Giới thiệu Đề tài & Nhóm thực hiện** (`00:00 – 00:25` | *25 giây*)
- **[Thao tác]:** Mở Slide 1, đứng thẳng, hướng mắt về phía giảng viên.
- **[Lời nói]:**
  > "Em chào Thầy ạ. Hôm nay nhóm chúng em xin báo cáo đồ án môn học **Học máy tiên tiến và ứng dụng** với đề tài: **Hệ thống Hỏi – Đáp Đọc hiểu Văn bản bằng Giọng nói Tiếng Việt (ViMMRC Voice Q&A)**, với chuỗi xử lý hoàn chỉnh: **STT $\rightarrow$ Truy xuất 2 tầng $\rightarrow$ vi-mrc-large $\rightarrow$ Matcha-TTS, chạy hoàn toàn trên CPU**.
  > Nhóm gồm 3 thành viên: bạn **Ngô Trí Huy** (Nhóm trưởng) phụ trách Truy xuất ngữ cảnh, Đọc hiểu, Quản lý hội thoại và API; bạn **Huỳnh Công Lương** phụ trách Nhận dạng giọng nói STT, Giao diện Web và Đóng gói Docker; và em là **Trương Hoàng Duy**, phụ trách Tổng hợp tiếng nói TTS và Đánh giá âm học. Em xin phép mở đầu bằng phần tổng quan toàn hệ thống và trình bày chi tiết phân hệ đầu tiên là Tổng hợp tiếng nói."

---

#### **Slide 2: Bối cảnh & Bài toán – Hỏi bằng giọng nói, tiếp nhận câu trả lời có bằng chứng xác thực** (`00:25 – 00:50` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 2, chỉ tay theo luồng *Đầu vào $\rightarrow$ Hệ thống $\rightarrow$ Đầu ra* ở nửa trên slide.
- **[Lời nói]:**
  > "Về bài toán đặt ra: các bộ dữ liệu đọc hiểu máy tiếng Việt hiện nay như **ViMMRC 2.0** hay **UIT-ViQuAD** chủ yếu tương tác qua văn bản và yêu cầu người dùng phải cung cấp sẵn đoạn văn ngữ cảnh.
  > Đề tài mở rộng bài toán sang ngữ cảnh tương tác tự nhiên: **Đầu vào** là câu hỏi thoại tự nhiên bằng tiếng Việt, không kèm ngữ cảnh; **Hệ thống** tự động tìm kiếm đoạn văn liên quan trong kho tri thức, đọc hiểu và xây dựng câu trả lời hoàn chỉnh; **Đầu ra** là câu trả lời trọn câu bằng giọng nói kèm theo đoạn văn làm bằng chứng xác thực.
  > Hệ thống hướng tới ứng dụng hỗ trợ người khiếm thị, kiosk tra cứu tự động và môi trường rảnh tay, với **3 ràng buộc thiết kế kỹ thuật**: vận hành hoàn toàn trên **CPU**, hỗ trợ chạy **offline**, và **chủ động từ chối trả lời khi thiếu căn cứ xác thực**."

---

#### **Slide 3: Khảo sát nghiên cứu – Các nền tảng học máy kế thừa ở từng chặng** (`00:50 – 01:15` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 3, quét nhẹ qua 4 cột *STT – Truy xuất – Đọc hiểu – TTS*.
- **[Lời nói]:**
  > "Để hiện thực hóa bài toán, nhóm đã khảo sát và kế thừa các nền tảng học máy tiêu biểu ở từng chặng:
  > - Ở **chặng STT**, nhóm kế thừa kiến trúc **Whisper** của Radford, kỹ thuật tinh chỉnh tham số hiệu quả **LoRA** trên tập dữ liệu **VietSpeech** và thư viện suy luận tối ưu **CTranslate2**.
  > - Ở **chặng Truy xuất**, nhóm kết hợp thuật toán **BM25** để khớp chính xác các dữ kiện cụ thể như tên riêng, con số, mốc thời gian và thuật ngữ; cùng với mô hình biểu diễn đa ngữ **Multilingual E5** để nắm bắt ngữ nghĩa câu hỏi, và mô hình **tái xếp hạng BGE-M3** nhằm chọn lọc đoạn văn có độ tương quan cao nhất.
  > - Ở **chặng Đọc hiểu**, nhóm khảo sát kiến trúc chuỗi-sang-chuỗi **ViT5** cùng các mô hình đọc trích xuất span trên hai tập dữ liệu **ViMMRC 2.0** và **UIT-ViQuAD 2.0**.
  > - Ở **chặng TTS**, nhóm ứng dụng lý thuyết dòng chảy xác suất qua kiến trúc **Matcha-TTS**, thuật toán căn chỉnh thời gian tự động **MAS** của Glow-TTS và mạng sinh dạng sóng **HiFi-GAN**."

---

#### **Slide 4: Giải pháp đề xuất & Kiến trúc tổng thể: Chu trình 4 chặng vận hành trên CPU** (`01:15 – 01:45` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 4, chỉ vào 4 con số lớn trên 4 thẻ và thanh độ trễ ở dưới cùng.
- **[Lời nói]:**
  > "Ghép nối 4 thành phần trên, kiến trúc tổng thể của hệ thống là một đường ống 4 chặng tuần tự tích hợp cơ chế dự phòng đa tầng:
  > - **Chặng 1 (STT):** Mô hình `Whisper-small LoRA` tinh chỉnh trên 50 giờ VietSpeech, lượng tử hóa INT8, giảm tỷ lệ lỗi từ **WER 36,76% xuống còn 13,77%**.
  > - **Chặng 2 (Retrieval):** Cơ chế truy xuất kết hợp BM25 cho dữ kiện từ khóa, Dense vector cho ngữ nghĩa ngữ cảnh và mô hình tái xếp hạng BGE-M3 trên kho tri thức 2 tầng gồm **5.879 đoạn chọn lọc** và **1,48 triệu đoạn Wikipedia**; chỉ số **Recall@5 BM25 2 tầng đạt 85,9%** (trong khi Recall@1 đạt 71,1%).
  > - **Chặng 3 (MRC):** Qua đối sánh **9 mô hình ứng viên**, bộ đọc trích xuất span `vi-mrc-large` đạt **F1 câu nói 0,468** (vượt trội hơn ViT5 ở mức 0,446).
  > - **Chặng 4 (TTS):** Mô hình `Matcha-TTS` chuyển đổi nhiễu sang phổ âm thanh bằng cách giải phương trình vi phân (ODE) chỉ trong 10 đến 20 bước Euler trên CPU, đạt tỷ lệ lỗi ký tự **CER 0,8%**, tiệm cận mức của giọng người thu âm thật (0,7%).
  > Tổng thời gian đáp ứng trung bình trên môi trường Docker CPU 4 luồng đạt khoảng **10,6 giây mỗi truy vấn**, và có thể rút ngắn xuống **5,1 giây** ở chế độ suy luận nhanh khi lược bớt tầng tái xếp hạng."

---

### PHẦN I: TỔNG HỢP TIẾNG NÓI MATCHA-TTS & HIFI-GAN (SLIDE 5 – SLIDE 17 | `01:45 – 07:45`)

#### **Slide 5: Bìa Phần I – Tổng hợp tiếng nói Matcha-TTS và HiFi-GAN** (`01:45 – 02:00` | *15 giây*)
- **[Thao tác]:** Chuyển sang Slide 5.
- **[Lời nói]:**
  > "Tiếp theo, em xin đi sâu vào **Phần I: Phân hệ Tổng hợp tiếng nói với Matcha-TTS và HiFi-GAN**. Bốn chỉ số kỹ thuật chính phản ánh hiệu năng của phân hệ gồm: tỷ lệ lỗi ký tự **CER đạt 0,8%** (đo độ rõ ràng của từ ngữ khi nhận dạng lại), sai số cao độ **log-F0 RMSE ở mức 0,88 bán cung** (đo độ chuẩn xác của 6 thanh điệu), hệ số thời gian thực **RTF từ 0,53 đến 0,64 trên CPU 8 luồng** (nghĩa là tổng hợp 1 giây âm thanh chỉ mất hơn nửa giây CPU), và bảng ký hiệu ngữ âm được tinh giản còn **41 token (giảm 58,2% so với biểu diễn nguyên âm ghép dấu)**."

---

#### **Slide 6: Bối cảnh & Khảo sát nghiên cứu TTS** (`02:00 – 02:30` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 6, chỉ vào cột Bối cảnh bên trái rồi đối chiếu bảng 4 dòng bên phải.
- **[Lời nói]:**
  > "Khi xây dựng phân hệ TTS cho hệ thống đọc hiểu tiếng Việt, nhóm đối mặt với 3 đặc thù ngôn ngữ và hệ thống: tiếng Việt có **6 thanh điệu** đóng vai trò phân biệt ngữ nghĩa; câu trả lời đọc hiểu chứa nhiều **ký hiệu đáp án, số liệu, mốc thời gian, đơn vị đo**; và hệ thống đặt mục tiêu **vận hành cục bộ trên CPU, không phụ thuộc kết nối ngoài**.
  > Qua khảo sát 4 hướng tiếp cận tiêu biểu:
  > - **VITS MMS** của Meta có tốc độ suy luận nhanh nhưng đường cong thanh điệu tiếng Việt chưa mượt, dẫn tới **CER ở mức 4,7%**.
  > - Các mô hình **Diffusion TTS** truyền thống cho chất lượng âm thanh tốt nhưng đòi hỏi hàng trăm bước giải khử nhiễu, chi phí tính toán cao trên CPU.
  > - **Glow-TTS với thuật toán MAS** có khả năng tự động căn chỉnh thời gian giữa âm vị và âm thanh mà không cần nhãn thủ công, nhưng cài đặt gốc phụ thuộc thư viện Cython/C++, dễ phát sinh lỗi khi triển khai đa môi trường.
  > - Do đó, nhóm lựa chọn giải pháp kết hợp **Matcha-TTS (mô hình dòng chảy xác suất giải phương trình vi phân ODE tối ưu trong 10–20 bước, quy mô 18,2 triệu tham số) cùng HiFi-GAN**, đồng thời tự phát triển bộ tiền xử lý ngữ âm tách thanh điệu chuyên biệt cho tiếng Việt."

---

#### **Slide 7: Giải pháp đề xuất – Matcha-TTS tiếng Việt kết hợp cơ chế tách thanh điệu độc lập** (`02:30 – 03:00` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 7, điểm qua 5 mũi tên *Thách thức $\rightarrow$ Giải pháp*.
- **[Lời nói]:**
  > "Từ các thách thức trên, nhóm đề xuất 5 giải pháp kỹ thuật tương ứng:
  > 1. Để đạt tốc độ nhanh hơn thời gian thực trên CPU: nhóm áp dụng **Matcha-TTS với lý thuyết dòng chảy tối ưu (OT-CFM)** kết hợp kỹ thuật học chuyển giao từ mô hình tiếng Anh tiền huấn luyện.
  > 2. Để giải quyết hiện tượng dữ liệu thưa và cải thiện độ chuẩn xác thanh điệu: nhóm phát triển **cơ chế tách dấu thanh độc lập thành 6 token riêng biệt**, tinh giản bảng ký hiệu ngữ âm về đúng **41 token**.
  > 3. Để xử lý hiện tượng méo và rè âm tần số cao khi ghép vocoder tổng quát: nhóm **tinh chỉnh mạng HiFi-GAN trực tiếp trên phổ Mel nhân tạo do chính Matcha-TTS sinh ra**.
  > 4. Đối với văn bản chứa ký hiệu đáp án, số liệu, ngày tháng: nhóm xây dựng bộ **chuẩn hóa văn bản chuyên biệt và chèn khoảng lặng thích ứng theo cấu trúc cú pháp**.
  > 5. Để chuẩn hóa triển khai và đảm bảo tính sẵn sàng cao: nhóm **tái lập trình thuật toán căn chỉnh thời gian MAS bằng Numba JIT** và thiết lập cơ chế chuyển đổi qua **4 engine dự phòng**."

---

#### **Slide 8: Mục tiêu & 6 Đóng góp chính của phân hệ TTS** (`03:00 – 03:25` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 8.
- **[Lời nói]:**
  > "Slide 8 tổng hợp **4 mục tiêu thiết kế** (Tái tạo chính xác 6 thanh điệu; Giữ `RTF < 1` trên CPU tiêu chuẩn; Chuẩn hóa cấu trúc văn bản đặc thù; và Vận hành cục bộ tự chủ) cùng **6 đóng góp kỹ thuật chính** của phân hệ: huấn luyện Matcha-TTS trên 25 giờ dữ liệu InfoRe1, xây dựng bộ tách thanh 41 token, viết lại thuật toán căn chỉnh thời gian MAS bằng Numba JIT, tinh chỉnh mạng HiFi-GAN qua 50.000 bước, phát triển bộ điều phối 4 engine dự phòng, và thiết lập quy trình đo kiểm khách quan dựa trên độ sai lệch âm sắc `MCD`, sai số cao độ `log-F0 RMSE`, độ rõ chữ `CER` và tốc độ `RTF`."

---

#### **Slide 9: Luồng xử lý – Sáu giai đoạn từ văn bản đến tệp âm thanh** (`03:25 – 03:50` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 9, chỉ theo thứ tự từ khối 1 đến khối 6.
- **[Lời nói]:**
  > "Về kiến trúc vận hành, mỗi khi tiếp nhận câu trả lời thô từ khâu đọc hiểu, luồng xử lý của TTS đi qua **6 giai đoạn nối tiếp**:
  > - **Bước 1 (Chuẩn hóa):** Loại bỏ cú pháp Markdown, chuyển đổi ký hiệu `(B)` thành `'Đáp án B:'`, quy đổi toàn bộ số liệu, mốc thời gian, ký hiệu đo lường sang dạng văn bản chữ tiếng Việt.
  > - **Bước 2 (Phân đoạn):** Chia câu dài thành các cụm ngữ nghĩa dựa trên dấu phẩy, chấm phẩy, hai chấm và dấu kết thúc câu.
  > - **Bước 3 (Token hóa & Tách thanh):** Tách dấu thanh điệu ra cuối âm tiết và ánh xạ vào bảng mã 41 token.
  > - **Bước 4 (Matcha-TTS):** Giải phương trình vi phân dòng chảy (ODE) trong 10 đến 20 bước Euler để sinh ma trận phổ Mel 80 kênh.
  > - **Bước 5 (HiFi-GAN):** Chuyển đổi phổ Mel thành tín hiệu âm thanh 22,05 kHz kết hợp bộ lọc làm sạch `Denoiser`.
  > - **Bước 6 (Hậu xử lý):** Khử khoảng lặng thừa dưới ngưỡng `-30 dB`, áp dụng biên làm mượt `fade 10 ms` và ghép nối thành tệp WAV hoàn chỉnh."

---

#### **Slide 10: Ví dụ thực – Một câu trả lời đi qua pipeline** (`03:50 – 04:20` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 10, chỉ vào từng dòng biến đổi cụ thể.
- **[Lời nói]:**
  > "Để minh họa cụ thể sự biến đổi dữ liệu qua từng bước, xét chuỗi đầu vào từ bộ đọc hiểu: `'Đáp án: (B) Chiến thắng Điện Biên Phủ ngày 07/05/1954.'`
  > - Qua **Bước 1**, chuỗi ngày `'07/05/1954'` được quy đổi hoàn chỉnh thành `'ngày bảy tháng năm năm một nghìn chín trăm năm mươi tư'`.
  > - Qua **Bước 2**, câu được phân thành 2 cụm ngữ nghĩa kèm thời lượng nghỉ được gán nhãn: `0,25 giây` sau dấu hai chấm và `0,40 giây` tại vị trí kết câu.
  > - Qua **Bước 3**, từ `'Chiến thắng'` được phân rã thành chuỗi ký tự cơ sở `c-h-i-ê-n` cùng token thanh sắc ở cuối âm tiết, và `t-h-ă-n-g` cùng token thanh sắc.
  > - Qua **Bước 4**, Matcha-TTS giải 20 bước Euler để tạo ra ma trận phổ Mel kích thước **80 kênh nhân 412 khung** (tương ứng khoảng 4,78 giây âm thanh).
  > - Ở **Bước 5 & Bước 6**, HiFi-GAN chuyển ma trận này thành dạng sóng âm **105.472 mẫu ở tần số 22.050 Hz**, xử lý làm mượt điểm nối và xuất ra tệp WAV hoàn chỉnh."

---

#### **Slide 11: Mô hình âm học – Matcha-TTS quỹ đạo thẳng chỉ cần 10–20 bước** (`04:20 – 04:55` | *35 giây*)
- **[Thao tác]:** Chuyển sang Slide 11. **Bấm phát Video mô phỏng quỹ đạo giải ODE** ở khung bên trái để hội đồng theo dõi sự khác biệt giữa OT-CFM và Diffusion.
- **[Lời nói]:**
  > "Cơ sở để Matcha-TTS đạt tốc độ nhanh hơn thời gian thực trên CPU nằm ở mô hình dòng chảy xác suất:
  > Kính mời Thầy theo dõi **mô phỏng so sánh quỹ đạo chuyển đổi ở khung bên trái**:
  > Trong mô hình này, **ODE (phương trình vi phân thường)** chính là quy luật toán học mô tả sự biến đổi liên tục từ một đám nhiễu ngẫu nhiên ban đầu thành ma trận phổ âm thanh Mel có nghĩa:
  > - Với các mô hình khuếch tán **Diffusion** truyền thống, quá trình biến đổi từ nhiễu sang âm thanh đi theo những **quỹ đạo cong phi tuyến phức tạp**, do đó máy tính bắt buộc phải chia nhỏ thành 50 đến hàng trăm bước giải lặp thì mới tái tạo được âm thanh chuẩn.
  > - Ngược lại, **Matcha-TTS** ứng dụng lý thuyết **Optimal-Transport Conditional Flow Matching (OT-CFM)** — tức là ép trường vận tốc phải học một **quỹ đạo đi thẳng trực tiếp**, là con đường ngắn nhất nối từ đám nhiễu tới phổ Mel mục tiêu. Nhờ quỹ đạo là đường thẳng, phương pháp giải tích phân số học Euler chỉ cần từ **10 đến 20 bước nhảy đơn giản** là đã hội tụ chính xác, giúp mô hình giảm thiểu tối đa phép tính và vận hành mượt mà trực tiếp trên CPU."

---

#### **Slide 12: Đóng góp ngữ âm – Tách thanh điệu thành token riêng (`98 → 41 ký hiệu`)** (`04:55 – 05:25` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 12, chỉ vào biểu đồ cột `98 -> 41`, biểu đồ tròn phân bố và bảng phân rã dấu bên phải.
- **[Lời nói]:**
  > "Đóng góp kỹ thuật thứ hai của phân hệ nằm ở việc tối ưu hóa biểu diễn ngữ âm cho chữ Quốc ngữ tiếng Việt.
  > Nếu giữ nguyên cách biểu diễn dấu thanh gắn liền trên từng nguyên âm, từ điển ký hiệu sẽ mở rộng lên tới **98 ký hiệu**. Những nguyên âm mang dấu hiếm gặp như `'ẵ'`, `'ự'`, `'ỵ'` có tần suất xuất hiện rất thấp trong tập huấn luyện, dẫn tới hiện tượng **dữ liệu thưa (data sparsity)** và làm giảm độ chuẩn xác khi học đường nét cao độ thanh điệu.
  > Giải pháp của nhóm là áp dụng chuẩn phân rã ký tự, **tách độc lập dấu thanh ra khỏi nguyên âm gốc thành 6 token thanh điệu cố định (từ `0` đến `5`) đặt ở cuối mỗi âm tiết** — ví dụ chữ `'hồ'` được biểu diễn thành `h - ô - 2`, chữ `'nội'` thành `n - ô - i - 5`.
  > Phương pháp này giúp tinh giản bảng ký hiệu từ **98 xuống còn 41 token (giảm 58,2%)**, bao gồm 29 chữ cái cơ sở, 6 token thanh điệu, 4 dấu ngắt câu và 2 token điều khiển. Về mặt học máy, **tất cả nguyên âm trong toàn bộ tập dữ liệu đều đóng góp gradient vào quá trình cập nhật 6 token thanh điệu**, giúp mô hình học đường cong cao độ F0 ổn định và chuẩn xác hơn."

---

#### **Slide 13: Căn chỉnh thời gian – MAS tái lập trình bằng Numba, loại bỏ phụ thuộc C++** (`05:25 – 05:50` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 13. **Bấm phát Video mô phỏng ma trận căn chỉnh MAS**.
- **[Lời nói]:**
  > "Trong quá trình huấn luyện mô hình tổng hợp tiếng nói, một thách thức lớn là: làm sao máy tính biết mỗi âm vị hay mỗi từ được nói kéo dài bao nhiêu mili-giây, mà không cần con người phải ngồi cắt và gắn nhãn thời lượng thủ công?
  > Matcha-TTS giải quyết bài toán này nhờ thuật toán **MAS (Monotonic Alignment Search) — tức là Tìm kiếm căn chỉnh thời gian đơn điệu**:
  > Thuật toán áp dụng quy hoạch động trên ma trận tương đồng để tự động tìm ra đường đi tối ưu nhất, khớp từng ký hiệu âm vị với một chuỗi khung phổ âm thanh liên tiếp từ trái qua phải như mô phỏng trên màn hình. Nhờ vậy, mô hình tự động sinh ra nhãn thời lượng chuẩn xác cho từng âm vị.
  > Tuy nhiên, cài đặt gốc của tác giả viết bằng Cython đòi hỏi bộ biên dịch C++ (`gcc` hoặc `MSVC`), rất dễ gây lỗi không tương thích môi trường khi triển khai trên các hệ điều hành khác nhau hoặc đóng gói Docker. Em đã **tái lập trình hoàn toàn thuật toán quy hoạch động MAS này bằng Python thuần kết hợp bộ biên dịch tức thời Numba JIT**, đạt tốc độ xử lý tương đương mã C++ biên dịch sẵn nhưng đảm bảo khả năng cài đặt và đóng gói đồng nhất trên Windows, macOS, Linux và Docker."

---

#### **Slide 14: Hậu xử lý & Điều phối – Khoảng lặng thích ứng theo dấu câu & 4 engine dự phòng** (`05:50 – 06:15` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 14, chỉ vào biểu đồ ngang bên trái và sơ đồ 4 tầng engine bên phải.
- **[Lời nói]:**
  > "Ở khâu hậu xử lý âm học, nhằm đảm bảo câu trả lời duy trì nhịp điệu tự nhiên, hệ thống thiết lập cơ chế giữ lại **50 ms biên phụ âm cuối** (tránh hiện tượng mất âm đối với các phụ âm khép `-p, -t, -c, -m, -n`), áp dụng đoạn làm mượt chuyển tiếp **10 ms**, và bố trí khoảng lặng thích ứng theo cấu trúc cú pháp: **150 ms** cho dấu phẩy, **250 ms** cho dấu hai chấm, **400 ms** khi kết thúc câu và **450 ms** khi chuyển dòng.
  > Đồng thời, kiến trúc phân hệ được thiết kế **dự phòng đa tầng với 4 engine**: ưu tiên mô hình nội bộ **Matcha-TTS**, hỗ trợ đối sánh cục bộ với **VITS MMS**, và tự động kích hoạt chuyển tiếp sang **Edge-TTS** hoặc **gTTS** khi môi trường hạn chế tài nguyên tính toán, đảm bảo tính sẵn sàng liên tục của chuỗi dịch vụ."

---

#### **Slide 15: Huấn luyện – Hai giai đoạn trên InfoRe1 (~25 giờ, một giọng nữ miền Bắc)** (`06:15 – 06:45` | *30 giây*)
- **[Thao tác]:** Chuyển sang Slide 15, chỉ vào thẻ GĐ 1, GĐ 2 và khung Chọn checkpoint bằng ASR.
- **[Lời nói]:**
  > "Về quy trình huấn luyện trên tập dữ liệu **InfoRe1 (25 giờ, đơn giọng nữ miền Bắc)**, quy trình gồm **2 giai đoạn nối tiếp**:
  > - **Giai đoạn 1 (Acoustic):** Nhóm chuyển giao trọng số mô hình `Matcha-TTS` qua **150.000 bước cập nhật (tương đương 327 epoch)** với bộ tối ưu Adam và hệ số trung bình trượt `EMA 0,9999`. Quan sát thực nghiệm cho thấy giá trị hàm mất mát (loss) đạt trạng thái hội tụ tương đối sớm, nhưng độ phân biệt thanh điệu vẫn tiếp tục được cải thiện ở các bước huấn luyện sâu; do đó nhóm sử dụng mô hình nhận dạng **PhoWhisper** để đo lường chỉ số CER định kỳ trên tập kiểm thử, từ đó xác định checkpoint tối ưu tại bước 150.000.
  > - **Giai đoạn 2 (Vocoder):** Khi ghép trực tiếp Matcha-TTS với HiFi-GAN đa ngôn ngữ tổng quát, tín hiệu phát sinh hiện tượng méo và rè âm do lệch phân phối phổ Mel. Để giải quyết, nhóm đóng băng Matcha-TTS, kết xuất **4.000 cặp phổ Mel nhân tạo** từ tập huấn luyện và **tinh chỉnh đối kháng mạng HiFi-GAN thêm 50.000 bước**, xử lý triệt để hiện tượng rè âm ở các dải tần số cao."

---

#### **Slide 16: Kết quả – CER 0,8% tiệm cận giọng thật, RTF dưới 0,7 trên CPU** (`06:45 – 07:20` | *35 giây*)
- **[Thao tác]:** Chuyển sang Slide 16, chỉ lần lượt vào 4 biểu đồ cột *MCD – log-F0 RMSE – CER – RTF*.
- **[Lời nói]:**
  > "Slide 16 trình bày kết quả đánh giá định lượng trên tập kiểm thử độc lập (từ mẫu 14.800 trở đi), đối chiếu giữa **Matcha 20 bước**, **Matcha 10 bước** và mô hình nền **VITS MMS của Meta** qua 4 thước đo thực nghiệm:
  > 1. Về độ méo phổ **MCD (Mel Cepstral Distortion)**: Thước đo này đánh giá độ sai lệch âm sắc so với giọng người thật tính bằng đơn vị decibel (càng thấp càng tự nhiên). Matcha đạt **3,05 dB** ở cấu hình 20 bước (3,12 dB ở 10 bước), cải thiện rõ rệt so với mức **4,40 dB** của VITS MMS.
  > 2. Về sai số cao độ thanh điệu **log-F0 RMSE**: Đo bằng đơn vị bán cung âm nhạc để đánh giá độ chuẩn xác của ngữ điệu trầm bổng tiếng Việt. Matcha ghi nhận mức lệch chỉ **0,88 bán cung**, thấp hơn gần 5 lần so với mức **4,29 bán cung** của VITS MMS — phản ánh trực tiếp hiệu quả định lượng của cơ chế tách 6 token thanh điệu.
  > 3. Về độ rõ nội dung qua chỉ số **CER (Character Error Rate)**: Đánh giá khách quan bằng cách cho mô hình nhận dạng giọng nói độc lập PhoWhisper nghe và đo tỷ lệ nhận dạng sai ký tự. CER của Matcha đạt **0,80%**, tiệm cận sát mức của giọng người thu âm thật là **0,70%**, và tốt hơn hẳn mức **4,70%** của VITS MMS.
  > 4. Về tốc độ xử lý qua hệ số thời gian thực **RTF (Real-Time Factor)**: Matcha đạt **RTF 0,64 ở 20 bước** và **0,53 ở 10 bước** trên CPU 8 luồng — nghĩa là để tạo ra 1 giây âm thanh tiếng nói, CPU chỉ mất khoảng hơn nửa giây tính toán, nhanh gấp đôi thời gian thực."

---

#### **Slide 17: Đối sánh – Cục bộ và Đám mây & Chuyển lời sang bạn Ngô Trí Huy (Phần II)** (`07:20 – 07:45` | *25 giây*)
- **[Thao tác]:** Chuyển sang Slide 17, đối chiếu cột *Matcha-TTS (cam)* với *VITS MMS* và *Azure/Edge-TTS*, sau đó hướng tay về phía bạn Ngô Trí Huy.
- **[Lời nói]:**
  > "Khi so sánh với các dịch vụ đám mây thương mại như **Azure TTS hay Edge-TTS**: các giải pháp thương mại sở hữu mô hình quy mô lớn hàng trăm triệu đến hàng tỷ tham số nên có ưu thế về độ tự nhiên ngữ điệu, nhưng phụ thuộc hoàn toàn vào đường truyền Internet và gửi dữ liệu văn bản ra máy chủ bên ngoài.
  > Trong khi đó, **mô hình Matcha-TTS tự huấn luyện của đề tài** có quy mô tối ưu chỉ **18,2 triệu tham số** (đếm trực tiếp từ checkpoint thực tế, so với mức 36,3 triệu tham số của VITS MMS), mang lại độ chuẩn xác thanh điệu tiếng Việt vượt trội hơn trong môi trường cục bộ, đồng thời đáp ứng trọn vẹn yêu cầu **vận hành 100% offline, xử lý dữ liệu tại chỗ và hoàn toàn miễn phí**.
  > 
  > Đó là toàn bộ giải pháp thiết kế và kết quả thực nghiệm của phân hệ Tổng hợp tiếng nói TTS. Tiếp theo, làm thế nào để từ một câu hỏi thoại tự do, hệ thống có thể truy xuất chính xác đoạn văn ngữ cảnh trong kho dữ liệu hơn **1,48 triệu đoạn Wikipedia** và trích xuất câu trả lời chuẩn xác trên CPU? Em xin trân trọng nhường phần trình bày tiếp theo cho bạn **Ngô Trí Huy** với **Phần II: Truy xuất ngữ cảnh và Đọc hiểu từ Slide 18** ạ!"
