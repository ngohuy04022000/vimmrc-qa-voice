# Đề Cương & Kế Hoạch Nghiên Cứu Luận Văn Thạc Sĩ

**Đề tài:** Nghiên cứu kiến trúc Optimal-Transport Conditional Flow Matching (Matcha-TTS) và xây dựng mô hình tổng hợp tiếng nói tiếng Việt chất lượng cao  
**Lĩnh vực:** Xử lý tiếng nói & Ngôn ngữ tự nhiên (Speech & Natural Language Processing)  
**Thời gian thực hiện dự kiến:** 6 - 8 tuần  

---

## 1. Giới Thiệu & Tính Cấp Thiết Của Đề Tài

Tổng hợp tiếng nói từ văn bản (Text-to-Speech - TTS) là một nhánh quan trọng trong lĩnh vực Trí tuệ Nhân tạo. Trong giai đoạn 2021–2023, các mô hình học sâu như **VITS (ICML 2021)** chiếm vị trí thống trị nhờ kiến trúc End-to-End kết hợp VAE và GAN. Tuy nhiên, kiến trúc này bộc lộ những hạn chế lớn:
- Quá trình huấn luyện GAN dễ mất ổn định (mode collapse).
- Chất lượng âm thanh thường bị mờ (oversmoothed) và bị giới hạn ở tần số lấy mẫu thấp.
- Khó mô hình hóa chính xác các biến thiên cao độ phức tạp trong các ngôn ngữ có thanh điệu như tiếng Việt.

Gần đây (2024–2026), sự ra đời của **Conditional Flow Matching (CFM)** — tiêu biểu là công trình **Matcha-TTS (ICASSP 2024)** — đã tạo nên bước chuyển dịch mang tính cách mạng:
- Thay vì quá trình khuếch tán ngẫu nhiên chậm chạp của Diffusion truyền thống (DDPM), CFM xây dựng đường truyền xác suất thẳng dựa trên Lý thuyết Vận chuyển Tối ưu (Optimal Transport).
- Chỉ cần từ **4 đến 10 bước lấy mẫu ODE** để sinh ra âm thanh chất lượng phòng thu với tốc độ vượt thời gian thực (RTF $< 0.2$).

**Mục tiêu nghiên cứu:**
1. Nghiên cứu sâu cơ sở toán học của kiến trúc **Optimal-Transport Conditional Flow Matching (Matcha-TTS, ICASSP 2024)**.
2. Xây dựng và thích nghi mô hình cho tiếng Việt (**Vietnamese Matcha-TTS**), giải quyết bài toán biểu diễn thanh điệu tiếng Việt (Tone-Aware Modeling) và chuẩn hóa ngôn ngữ.
3. Huấn luyện mô hình trên bộ dữ liệu tiếng Việt chuẩn học thuật (**VIVOS Dataset**).
4. Thiết lập quy trình đánh giá đối sánh khoa học với Baseline qua các chỉ số khách quan (**MCD, F0 RMSE, RTF**) và chủ quan (**MOS**).

---

## 2. Thiết Kế Nghiên Cứu & Phương Pháp Luận (Methodology)

### 2.1. Cặp Mô Hình Đối Sánh
- **Mô hình Cơ sở (Baseline Model):** Kiến trúc **Matcha-TTS nguyên bản (Mehta et al., ICASSP 2024)** kết hợp Vocoder HiFi-GAN tiêu chuẩn.
- **Mô hình Đề xuất (Proposed Model - Vietnamese Matcha-TTS):**
  - Tích hợp bộ **Vietnamese Linguistic Front-End**: Chuẩn hóa số, ngày tháng, từ viết tắt và quy tắc ngữ âm.
  - Tích hợp cơ chế **Tone-Aware Conditioning**: Bổ sung vector đặc trưng thanh điệu tiếng Việt (6 thanh) vào bộ mã hóa văn bản để hướng dẫn trường vector vận chuyển tối ưu $v_t(x)$.
  - Huấn luyện thích nghi sâu (Domain Adaptation / Fine-tuning) trên tập dữ liệu tiếng Việt chuẩn.

### 2.2. Dữ Liệu Thực Nghiệm (Dataset)
- **Tập dữ liệu:** **VIVOS Dataset** (AILab - Trường ĐH Khoa học Tự nhiên ĐHQG-HCM).
  - Quy mô: Khoảng 15 giờ âm thanh sạch của 65 người nói tiếng Việt.
  - Phân chia thực nghiệm cố định:
    - **Tập Huấn luyện (Train set):** $90\%$ dữ liệu.
    - **Tập Thẩm định (Validation set):** $5\%$ dữ liệu (dùng để chọn checkpoint tốt nhất theo validation loss).
    - **Tập Kiểm thử (Test set):** $5\%$ dữ liệu (được giữ nguyên để so sánh giữa Baseline và Mô hình đề xuất).

### 2.3. Quy Trình Tính Toán Kết Hợp (Hybrid Compute Workflow)
- **Môi trường phát triển cục bộ (Local PC - Intel i7, 16GB RAM):**
  - Xử lý và chuẩn hóa dữ liệu âm thanh.
  - Xây dựng mã nguồn kiến trúc mô hình, pipeline huấn luyện và bộ đánh giá.
  - Chạy suy luận (Inference), phân tích tensor và tính toán độ đo.
- **Môi trường huấn luyện đám mây (Cloud GPU - Google Colab / Kaggle 16GB T4/A100):**
  - Chạy huấn luyện mô hình với Mixed Precision (`fp16`).
  - Tự động lưu trữ và đồng bộ checkpoints qua Google Drive / Hugging Face Hub.

---

## 3. Hệ Thống Tiêu Chí Đánh Giá Thực Nghiệm

Để đảm bảo tính khoa học của luận văn Thạc sĩ, việc đánh giá sẽ kết hợp cả đo lường định lượng bằng máy và khảo sát cảm thụ âm thanh từ người nghe:

### 3.1. Đánh Giá Khách Quan (Objective Metrics)
1. **MCD (Mel-Cepstral Distortion) [dB]:**  
   Đo khoảng cách giữa chuỗi phổ Mel-cepstral của âm thanh sinh ra $\hat{y}$ và âm thanh người thật đọc $y$:
   $$\text{MCD} = \frac{10\sqrt{2}}{\ln 10} \frac{1}{T} \sum_{t=1}^T \sqrt{\sum_{d=1}^D (c_{t,d} - \hat{c}_{t,d})^2}$$
   *(MCD càng nhỏ biểu thị âm thanh càng giống giọng thật, mục tiêu $< 5.5\text{ dB}$).*
2. **F0 RMSE [Hz]:**  
   Sai số toàn phương trung bình của tần số cơ bản $F_0$ (thước đo độ chuẩn xác của thanh điệu tiếng Việt).
3. **RTF (Real-Time Factor):**  
   Tỷ lệ giữa thời gian sinh âm thanh và thời lượng thực tế của đoạn âm thanh:
   $$\text{RTF} = \frac{T_{\text{sinh}}}{T_{\text{âm thanh}}}$$
   *(RTF $< 1.0$ cho biết mô hình đáp ứng thời gian thực).*

### 3.2. Đánh Giá Chủ Quan (Subjective Metrics)
- **MOS (Mean Opinion Score):**  
  Tổ chức khảo sát kiểm thử mù (Blind Test) với tối thiểu $20$ người nghe, đánh giá trên thang điểm từ 1 (kém nhất) đến 5 (tuyệt vời nhất) theo 2 tiêu chí:
  - **Độ tự nhiên (Naturalness):** Ngữ điệu có giống con người đọc hay không.
  - **Độ rõ ràng (Intelligibility):** Các âm vị và dấu thanh tiếng Việt có phát âm chuẩn xác, không bị dính chữ hay không.

---

## 4. Kế Hoạch & Tiến Độ Thực Hiện Rút Gọn (2 Tuần Sprint)

| Thời gian | Giai đoạn & Công việc cụ thể | Sản phẩm đầu ra (Deliverables) |
|:---:|---|---|
| **Ngày 1 – 2** | • Chuẩn bị và phân chia tập dữ liệu VIVOS (Train 90%, Val 5%, Test 5%).<br>• Chạy kiểm thử pipeline tiền xử lý `src/vivos_preprocessor.py`. | 3 file manifest chuẩn (`train`, `val`, `test`). |
| **Ngày 3 – 4** | • Thiết lập Baseline Matcha-TTS nguyên bản (ICASSP 2024).<br>• Sinh âm thanh mẫu Baseline và chuẩn bị bộ đo `src/evaluator.py`. | Mẫu âm thanh Baseline, script đo MCD/F0 sẵn sàng. |
| **Ngày 5 – 7** | • Mở `notebooks/02_train_matcha_colab.ipynb` trên Google Colab (GPU T4).<br>• Chạy huấn luyện/fine-tuning trên dữ liệu tiếng Việt, lưu checkpoint tự động lên Google Drive. | Checkpoint mô hình tối ưu: `best_model.pt`. |
| **Ngày 8 – 9** | • Tải `best_model.pt` từ Google Drive về thư mục `checkpoints/` local.<br>• Chạy suy luận (Inference) trên máy cá nhân cho toàn bộ tập Test set. | 2 thư mục âm thanh kiểm thử: `baseline_test/` và `proposed_test/`. |
| **Ngày 10 – 11** | • Chạy `src/evaluator.py` đo định lượng: MCD (dB), F0 RMSE (Hz), RTF.<br>• Làm Google Form khảo sát cảm thụ âm thanh MOS (15–20 người đánh giá). | Bảng số liệu thực nghiệm đối kháng hoàn chỉnh. |
| **Ngày 12 – 14** | • Đưa bảng số liệu, phổ âm và kết quả vào báo cáo / slide luận văn.<br>• Đóng gói tích hợp vào entrypoint `synthesize.py`. | Báo cáo hoàn chỉnh nộp Thầy & Demo hoạt động mượt mà. |

---

## 5. Tài Liệu Tham Khảo Cốt Lõi

1. **Shivam Mehta, Ruibo Tu, Jonas Beskow, Éva Székely, Gustav Eje Henter.** *"Matcha-TTS: A fast TTS architecture with conditional flow matching"*, **ICASSP 2024**.
2. **Yaron Lipman, Ricky T. Q. Chen, Heli Ben-Hamu, Maximilian Nickel, Matthew Le.** *"Flow Matching for Generative Modeling"*, **ICLR 2023**.
3. **Jaehyeon Kim, Jungil Kong, Juhee Son.** *"Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech"*, **ICML 2021** (VITS Paper).
4. **Jungil Kong, Jaehyeon Kim, Jaekyoung Bae.** *"HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis"*, **NeurIPS 2020**.
5. **Hi-Ngan Nguyen, Xuan-Bao Luong, et al.** *"VIVOS: A free Vietnamese speech corpus for speech recognition and synthesis"*, **AILab, VNU-HCM, 2016**.
