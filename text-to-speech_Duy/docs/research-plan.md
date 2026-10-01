# Tài Liệu Thiết Kế Phương Pháp Luận & Kiến Trúc Hệ Thống Tổng Hợp Tiếng Nói (Vietnamese TTS)

**Đề tài:** Nghiên cứu kiến trúc Optimal-Transport Conditional Flow Matching (Matcha-TTS) và xây dựng mô hình tổng hợp tiếng nói tiếng Việt chất lượng cao  
**Lĩnh vực:** Xử lý tiếng nói & Ngôn ngữ tự nhiên (Speech & Natural Language Processing)  

---

## 1. Giới Thiệu & Đặt Vấn Đề Khoa Học

Tổng hợp tiếng nói từ văn bản (Text-to-Speech - TTS) là bài toán chuyển đổi chuỗi văn bản $L = [w_1, w_2, \dots, w_N]$ thành dạng sóng âm thanh liên tục $y(t) \in \mathbb{R}^T$. Trong giai đoạn 2021–2023, các mô hình học sâu như **VITS (ICML 2021)** chiếm vị trí thống trị nhờ kiến trúc End-to-End kết hợp VAE và GAN. Tuy nhiên, kiến trúc này bộc lộ những hạn chế kỹ thuật:
- Quá trình huấn luyện hàm mục tiêu đối kháng (Adversarial Minimax Loss) dễ mất ổn định và rơi vào hiện tượng sụp đổ mode (mode collapse).
- Chất lượng âm thanh thường bị hiện tượng làm mờ phổ (oversmoothing) trong các đoạn biến thiên cao độ nhanh.
- Khó mô hình hóa chính xác các biến thiên cao độ phức tạp trong các ngôn ngữ có thanh điệu như tiếng Việt (6 thanh điệu đặc thù).

Gần đây (2024–2026), sự ra đời của **Conditional Flow Matching (CFM)** — tiêu biểu là công trình **Matcha-TTS (ICASSP 2024)** — đã tạo nên bước chuyển dịch mang tính đột phá:
- Thay vì quá trình khuếch tán ngẫu nhiên nhiều bước (chậm) của Diffusion truyền thống (DDPM/Grad-TTS), CFM xây dựng đường truyền xác suất thẳng dựa trên Lý thuyết Vận chuyển Tối ưu (Optimal Transport).
- Chỉ cần từ **4 đến 10 bước giải phương trình vi phân thường (ODE Solver)** để sinh ra âm thanh chất lượng cao với tốc độ thực thi vượt trội (RTF $< 0.2$).

**Mục tiêu nghiên cứu:**
1. Nghiên cứu sâu cơ sở toán học của kiến trúc **Optimal-Transport Conditional Flow Matching (Matcha-TTS, ICASSP 2024)** và mô hình nền tảng **VITS (ICML 2021)**.
2. Xây dựng và thích nghi mô hình cho tiếng Việt (**Vietnamese Matcha-TTS**), giải quyết bài toán biểu diễn thanh điệu tiếng Việt (Tone-Aware Modeling) và chuẩn hóa ngôn ngữ.
3. Huấn luyện mô hình trên bộ dữ liệu tiếng Việt chuẩn học thuật (**VIVOS Dataset**).
4. Thiết lập quy trình đánh giá đối sánh khoa học định lượng (**MCD, F0 RMSE, RTF**) và định tính (**MOS**).

---

## 2. Thiết Kế Nghiên Cứu & Phương Pháp Luận (Methodology)

### 2.1. Cặp Mô Hình Đối Sánh
- **Mô hình Cơ sở (Baseline Model - VITS / Matcha gốc):** 
  - VITS (Kim et al., ICML 2021) trên trọng số pretrained tiếng Việt (Meta MMS-TTS).
  - Matcha-TTS nguyên bản (Mehta et al., ICASSP 2024) kết hợp Vocoder HiFi-GAN tiêu chuẩn.
- **Mô hình Đề xuất (Proposed Model - Vietnamese Matcha-TTS):**
  - **Vietnamese Linguistic Front-End**: Chuẩn hóa số, ngày tháng, từ viết tắt, ký hiệu trắc nghiệm MRC và quy tắc ngữ âm tiếng Việt.
  - **Tone-Aware Conditioning**: Tách rời và nhúng đặc trưng thanh điệu tiếng Việt (6 thanh) vào bộ mã hóa văn bản để dẫn dắt trường vector vận chuyển tối ưu $v_t(x)$.
  - **OT-CFM Training**: Huấn luyện hồi quy trường vector xác suất trên tập dữ liệu tiếng Việt chuẩn.

### 2.2. Dữ Liệu Thực Nghiệm (Dataset)
- **Tập dữ liệu:** **VIVOS Dataset** (AILab - Trường ĐH Khoa học Tự nhiên ĐHQG-HCM, 2016).
  - Quy mô: ~15 giờ âm thanh chất lượng phòng thu từ 65 người nói bản xứ tiếng Việt.
  - Phân chia thực nghiệm cố định (Deterministic Split):
    - **Tập Huấn luyện (Train set):** $90\%$ dữ liệu.
    - **Tập Thẩm định (Validation set):** $5\%$ dữ liệu (dùng để chọn checkpoint tối ưu theo Validation Loss).
    - **Tập Kiểm thử (Test set):** $5\%$ dữ liệu (giữ độc lập hoàn toàn để so sánh giữa Baseline và Mô hình đề xuất).

---

## 3. Hệ Thống Tiêu Chí Đánh Giá Thực Nghiệm

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
   Khảo sát kiểm thử mù (Blind Test) với tối thiểu $20$ người nghe, đánh giá trên thang điểm từ 1 (kém nhất) đến 5 (tuyệt vời nhất) theo 2 tiêu chí:
  - **Độ tự nhiên (Naturalness):** Ngữ điệu có giống con người đọc hay không.
  - **Độ rõ ràng (Intelligibility):** Các âm vị và dấu thanh tiếng Việt có phát âm chuẩn xác, không bị dính chữ hay không.

---

## 4. Cơ Chế Hoạt Động Của Hệ Thống (System Execution Pipeline)

Toàn bộ hệ thống được phân rã thành 3 giai đoạn hoạt động độc lập và khép kín:

### Giai đoạn A: Tiền xử lý & Trích xuất Đặc trưng (Preprocessing & Feature Extraction)
1. **Chuẩn hóa văn bản (`src/normalizer.py`):**
   - Loại bỏ nhiễu ký tự, chuẩn hóa chữ hoa/thường, giải mã các định dạng đặc thù tiếng Việt: số nguyên, số thực, ngày/tháng/năm, tiền tệ VNĐ, tỷ lệ phần trăm và tiền tố trắc nghiệm `[A-D].`.
2. **Ngữ âm hóa & Gán nhãn thanh điệu (`src/vivos_preprocessor.py`):**
   - Chuyển đổi chuỗi từ tiếng Việt sang chuỗi âm vị (Phoneme Sequence) kèm chỉ số thanh điệu (Tone ID: $0$ đến $5$).
   - Sinh ra các file manifest chuẩn hóa `train.jsonl`, `val.jsonl`, `test.jsonl`.
3. **Trích xuất Mel-Spectrogram:**
   - Đọc tín hiệu âm thanh với tần số mẫu $22,050\text{ Hz}$, áp dụng STFT với bước trượt (hop size) 256 mẫu, kích thước cửa sổ 1024 mẫu để tạo ma trận 80 kênh Mel-spectrogram.

### Giai đoạn B: Huấn luyện Mô hình trên Đám mây (`notebooks/02_train_matcha_colab.ipynb`)
1. **Kiến trúc mạng:**
   - **Text Encoder:** Mạng 1D Convolution kết hợp Transformer Block mã hóa chuỗi âm vị thành biểu diễn ngữ cảnh $\mu_x$.
   - **Duration Predictor / MAS:** Căn chỉnh độ dài thời gian giữa chuỗi âm vị và chuỗi khung Mel.
   - **CFM Vector Field Estimator:** Mạng 2D U-Net / DiT (Diffusion Transformer) dự đoán trường vận tốc $v_\theta(x_t, t, \mu_x)$.
2. **Hàm mất mát hồi quy trường vector (Optimal-Transport CFM Loss):**
   $$\mathcal{L}_{\text{CFM}}(\theta) = \mathbb{E}_{t, q(x_1), p(x_0)} \left[ \| v_\theta(\psi_t(x_0), t, \mu_x) - (x_1 - x_0) \|^2 \right]$$
   Trong đó $x_0 \sim \mathcal{N}(0, I)$ là nhiễu Gaussian ban đầu, $x_1$ là Mel-spectrogram mục tiêu, và $\psi_t(x_0) = (1 - t)x_0 + t x_1$ là quỹ đạo đường thẳng tối ưu.
3. **Lưu trữ Checkpoint:** Trọng số tối ưu theo Validation Loss được xuất thành file `checkpoints/best_model.pt`.

### Giai đoạn C: Suy luận & Đánh giá Thực nghiệm Cục bộ (`synthesize.py` & `src/evaluator.py`)
1. **Suy luận (Inference Pipeline):**
   - Bộ giải vi phân (ODE Solver: Euler hoặc Midpoint) giải tích phân từ $t=0$ (nhiễu ngẫu nhiên) đến $t=1$ theo trường vector $v_\theta$ đã học trong $N = 4 \div 10$ bước để tái tạo Mel-spectrogram $\hat{x}_1$.
   - Bộ giải mã âm học (Neural Vocoder - HiFi-GAN) chuyển $\hat{x}_1$ thành dạng sóng âm thanh PCM $16\text{-bit}$ `.wav`.
2. **Đo đạc & Lập bảng thực nghiệm (`src/evaluator.py`):**
   - Đọc các cặp file âm thanh kiểm thử (Ground Truth vs Sinh bởi Baseline vs Sinh bởi Mô hình đề xuất).
   - Tự động tính toán Dynamic Time Warping (DTW) cho phổ Mel-cepstral để trích xuất MCD (dB), dùng thuật toán YIN để đo F0 RMSE (Hz) và tính RTF thời gian thực.

---

## 5. Danh Mục Bài Báo Khoa Học & Tài Liệu Tham Khảo (Academic References)

Dưới đây là các công trình khoa học nền tảng định hình cơ sở lý thuyết và phương pháp luận của đề tài:

### 5.1. Nhóm Công Trình Cốt Lõi Về Flow Matching & Generative Modeling
1. **Shivam Mehta, Ruibo Tu, Jonas Beskow, Éva Székely, Gustav Eje Henter.** (2024).  
   *"Matcha-TTS: A fast TTS architecture with conditional flow matching"*.  
   **IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP 2024)**.  
   *Đóng góp:* Đề xuất kiến trúc Flow Matching với giải thuật vận chuyển tối ưu giúp giảm số bước lấy mẫu xuống 4-10 bước, vượt trội so với Diffusion truyền thống.  
   *Liên kết:* [arXiv:2309.03199](https://arxiv.org/abs/2309.03199)

2. **Yaron Lipman, Ricky T. Q. Chen, Heli Ben-Hamu, Maximilian Nickel, Matthew Le.** (2023).  
   *"Flow Matching for Generative Modeling"*.  
   **International Conference on Learning Representations (ICLR 2023)**.  
   *Đóng góp:* Đặt nền móng toán học cho phương pháp Flow Matching không phụ thuộc vào mô phỏng ngẫu nhiên (simulation-free training) trên các đường truyền xác suất thẳng (OT paths).  
   *Liên kết:* [arXiv:2210.02747](https://arxiv.org/abs/2210.02747)

### 5.2. Nhóm Công Trình Về Kiến Trúc Baseline & End-to-End TTS
3. **Jaehyeon Kim, Jungil Kong, Juhee Son.** (2021).  
   *"Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech"*.  
   **International Conference on Machine Learning (ICML 2021)** (VITS Paper).  
   *Đóng góp:* Mô hình Baseline nền tảng kết hợp VAE, Normalizing Flows và học đối kháng GAN cùng thuật toán căn chỉnh Monotonic Alignment Search (MAS).  
   *Liên kết:* [arXiv:2106.06103](https://arxiv.org/abs/2106.06103)

4. **Vineel Pratap, Andros Tjandra, Bowen Shi, et al.** (2023).  
   *"Scaling Speech Technology to 1,000+ Languages"*.  
   **Advances in Neural Information Processing Systems (NeurIPS 2023)** (Meta MMS Project).  
   *Đóng góp:* Cung cấp mô hình pretrained VITS cho tiếng Việt (`facebook/mms-tts-vie`), được dùng làm chuẩn so sánh Baseline trong đề tài.  
   *Liên kết:* [arXiv:2305.13516](https://arxiv.org/abs/2305.13516)

### 5.3. Nhóm Công Trình Về Vocoder & Âm Học
5. **Jungil Kong, Jaehyeon Kim, Jaekyoung Bae.** (2020).  
   *"HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis"*.  
   **Advances in Neural Information Processing Systems (NeurIPS 2020)**.  
   *Đóng góp:* Kiến trúc Neural Vocoder chuyển đổi phổ Mel thành tín hiệu sóng âm với cấu trúc Multi-Period Discriminator (MPD) và Multi-Scale Discriminator (MSD).  
   *Liên kết:* [arXiv:2010.05646](https://arxiv.org/abs/2010.05646)

### 5.4. Tập Dữ Liệu Thực Nghiệm Tiếng Việt
6. **Hi-Ngan Nguyen, Xuan-Bao Luong, Quoc-Bao Nguyen, Tat-Thang Vu, Mai-Chi Luong.** (2016).  
   *"VIVOS: A free Vietnamese speech corpus for speech recognition and synthesis"*.  
   **AILab, University of Science, VNU-HCM**.  
   *Đóng góp:* Tập dữ liệu chuẩn học thuật tiếng Việt với 15 giờ ghi âm phát âm chuẩn xác, cung cấp ground-truth cho huấn luyện và kiểm thử đối sánh.  
   *Liên kết chính thức:* [Zenodo DOI 10.5281/zenodo.7068130](https://doi.org/10.5281/zenodo.7068130) | [Hugging Face AILAB-VNUHCM/vivos](https://huggingface.co/datasets/AILAB-VNUHCM/vivos)

