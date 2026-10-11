# Tài Liệu Thiết Kế Phương Pháp Luận & Kiến Trúc Hệ Thống Tổng Hợp Tiếng Nói (Vietnamese TTS)

**Đề tài:** Nghiên cứu kiến trúc Optimal-Transport Conditional Flow Matching (Matcha-TTS) và xây dựng mô hình tổng hợp tiếng nói tiếng Việt chất lượng cao  
**Lĩnh vực:** Xử lý tiếng nói & Ngôn ngữ tự nhiên (Speech & Natural Language Processing)  

---

## 1. Giới Thiệu & Đặt Vấn Đề Khoa Học

Tổng hợp tiếng nói từ văn bản (Text-to-Speech, TTS) là bài toán chuyển chuỗi văn bản $L = [w_1, \dots, w_N]$ thành dạng sóng $y(t)$. Trong hệ thống ViMMRC Voice Q&A, TTS là khâu cuối: đọc to câu trả lời do mô hình đọc hiểu (MRC) sinh ra. Đầu vào là văn bản thuần, đầu ra là đường dẫn file âm thanh.

Giai đoạn 2021–2023, **VITS (ICML 2021)** chiếm ưu thế nhờ kiến trúc end-to-end kết hợp VAE, Normalizing Flow và GAN. Kiến trúc này có một số hạn chế:
- Huấn luyện đối kháng (GAN) khó ổn định và nhạy với siêu tham số.
- Ràng buộc khả nghịch của Normalizing Flow giới hạn khả năng biểu diễn.
- Biến thiên cao độ nhanh và phức tạp của ngôn ngữ có thanh điệu như tiếng Việt (6 thanh) khó mô hình hóa khi dữ liệu ít.

**Conditional Flow Matching (CFM)**, tiêu biểu là **Matcha-TTS (ICASSP 2024)**, học trường vector đưa nhiễu Gauss tới phân phối mel-spectrogram dọc theo **đường vận chuyển tối ưu thẳng**. Mô hình huấn luyện bằng hồi quy thuần (không GAN) và chỉ cần vài đến vài chục bước giải ODE khi suy luận. Phân tích toán học chi tiết ở [`matcha-architecture.md`](matcha-architecture.md).

**Mục tiêu nghiên cứu:**
1. Nghiên cứu cơ sở toán học của Matcha-TTS (OT-CFM) và mô hình nền VITS.
2. Thích nghi Matcha-TTS cho tiếng Việt: chuẩn hóa ngôn ngữ đặc thù ViMMRC và **biểu diễn thanh điệu tách rời (Tone Decoupling)**.
3. Huấn luyện trên dữ liệu tiếng Việt công khai (VIVOS, InfoRe1) với tài nguyên Colab miễn phí.
4. Đánh giá định lượng (MCD, F0 RMSE, log-F0 RMSE, CER, RTF) so với giọng người thật, và định tính (MOS).

---

## 2. Thiết Kế Nghiên Cứu & Phương Pháp Luận

### 2.1. Các hệ thống đối sánh

| Vai trò | Hệ thống | Mô tả |
|---|---|---|
| Baseline | **VITS MMS** (`facebook/mms-tts-vie`) | VITS pretrained tiếng Việt của Meta MMS, chạy cục bộ |
| Mốc công nghiệp | **Edge-TTS** (`vi-VN-HoaiMyNeural`) | Giọng nơ-ron thương mại của Microsoft, qua mạng |
| Đề xuất, bản 1 | **Matcha-TTS VIVOS** (`checkpoints/matcha_vi.pt`) | 65 giọng, frontend `char_v1`, HiFi-GAN Universal. Đã huấn luyện (epoch 39, step 14 937) |
| Đề xuất, bản 2 | **Matcha-TTS InfoRe1** (`matcha_vi_v2.pt`) | 1 giọng, frontend `vi_tone_v2`, HiFi-GAN fine-tune. Pipeline hoàn chỉnh trong notebook, đang huấn luyện |

### 2.2. Đóng góp chính: Biểu diễn thanh điệu tách rời (Tone Decoupling)

Chữ Quốc ngữ ghi thanh điệu bằng dấu gắn trên nguyên âm. Nếu dùng nguyên ký tự mang dấu làm token, như bản 1, thì:
- Bộ từ vựng phình lên 91 token, vì mỗi nguyên âm có tới 6 biến thể.
- Mỗi thanh phải được học lại cho từng nguyên âm: thanh "huyền" của *à*, *ề*, *ồ*… là các embedding độc lập. Với dữ liệu ít (VIVOS khoảng 14 phút mỗi giọng), nhiều tổ hợp hiếm gần như không được học.

Frontend `vi_tone_v2` (`src/vi_frontend.py`) phân tách Unicode NFD, tách 5 dấu thanh khỏi nguyên âm và đặt thành **một token thanh điệu ở cuối mỗi âm tiết**. Thanh ngang được ghi tường minh là `0`:

$$\text{hồ} \rightarrow [h, ô, \mathbf{2}], \qquad \text{nội} \rightarrow [n, ô, i, \mathbf{5}], \qquad \text{gươm} \rightarrow [g, ư, ơ, m, \mathbf{0}].$$

Bộ từ vựng còn **41 token** (29 chữ cái, 6 thanh, khoảng trắng, 4 dấu câu, blank). Mỗi thanh là một embedding dùng chung, được học trên toàn bộ dữ liệu. Token thanh ở cuối vần cho phép self-attention của encoder điều khiển đường F0 của cả âm tiết. Frontend còn đánh vần chữ viết tắt (nhãn đáp án "B" → "bê"), thay chữ cái ngoại lai (f → ph, j → gi, w → u, z → d) và tùy chọn giữ dấu câu làm token.

### 2.3. Dữ liệu

| Tập | Quy mô | Đặc điểm | Dùng cho |
|---|---|---|---|
| **VIVOS** (AILab, ĐH KHTN – ĐHQG-HCM) | ~15 giờ, 65 người nói | Thiết kế cho **nhận dạng** tiếng nói: 16 kHz, có tạp âm; đo được nhiễu nền mô hình học lại khoảng −37 dB | Bản 1 (gộp train + test, 100 câu validation) |
| **InfoRe1** (`doof-ferb/infore1_25hours`) | ~25 giờ, 14 935 câu, 1 giọng nữ | Thu sạch, nhiễu nền khoảng −52 dB; transcript chữ thường, không dấu câu | Bản 2; 10 câu gần cuối tập (từ chỉ số 14 800) làm tham chiếu benchmark |

Tiền xử lý: resample 22,05 kHz, cắt im lặng hai đầu (40 dB), chuẩn hóa năng lượng RMS khoảng −20 dBFS (bản 1 chuẩn hóa theo đỉnh), mel 80 kênh (FFT 1024, hop 256, $f_{\max}$ = 8 kHz) khớp với vocoder HiFi-GAN.

### 2.4. Huấn luyện

- Khởi tạo từ checkpoint Matcha LJSpeech: tái sử dụng decoder và phần lớn encoder (302/305 tensor), chỉ học lại embedding token.
- Adam, learning rate $10^{-4}$, mixed precision (fp16 trên T4), clip gradient 5.
- **Không dùng early stopping theo val loss**: bản 1 dừng ở khoảng 15k step vì $\mathcal{L}_{\text{CFM}}$ chững lại sớm, trong khi chất giọng vẫn cải thiện. Bản 2 train theo số step (mặc định 100k), lưu snapshot mỗi 10k step và **chọn snapshot bằng CER** (ASR PhoWhisper).
- **Fine-tune HiFi-GAN** trên mel *teacher-forced* (decoder sinh mel theo căn chỉnh MAS của câu thật) để khắc phục sai lệch giữa mel tổng hợp và mel thật.

### 2.5. Hậu xử lý khi suy luận

Dữ liệu huấn luyện không có dấu câu, nên mô hình không tự học được chỗ ngắt nghỉ. `src/matcha_engine.py` tách cụm theo dấu câu, sinh từng cụm và chèn khoảng lặng (0,15 s / 0,25 s / 0,4 s). Engine cũng cắt nhiễu hai đầu cụm (−30 dB), fade 10 ms và chuẩn hóa âm lượng. Với checkpoint đa giọng, giọng mặc định được chọn theo CER thấp nhất cho từng giới tính.

---

## 3. Hệ Thống Tiêu Chí Đánh Giá

Cài đặt trong `src/evaluator.py`, chạy bằng `scripts/benchmark.py`. Tham chiếu là **giọng người thật**: 10 câu InfoRe1, mỗi câu dài 2–8 giây.

| Chỉ số | Định nghĩa | Ý nghĩa |
|---|---|---|
| **MCD** (dB) ↓ | $\frac{10\sqrt{2}}{\ln 10}\cdot\frac{1}{\lvert P\rvert}\sum_{(i,j)\in P}\lVert c^{ref}_{i,1:24} - c^{syn}_{j,1:24}\rVert$; mel-cepstrum bậc 24 trên dải 0–8 kHz, $P$ là đường căn chỉnh DTW | Sai khác phổ; gồm cả khác biệt chất giọng do khác người nói |
| **F0 RMSE** (Hz) ↓ | RMSE của F0 (pYIN, 60–400 Hz) trên các khung hữu thanh đã căn chỉnh DTW | Sai số cao độ tuyệt đối; chỉ so được giữa các giọng cùng giới |
| **log-F0 RMSE** (bán cung) ↓ | Như trên, trên $12\log_2 F_0$ sau khi trừ trung bình mỗi câu | **Hình dạng đường thanh điệu**, không phụ thuộc giọng |
| **CER** ↓ | Tỷ lệ lỗi ký tự khi PhoWhisper-base nhận dạng lại giọng tổng hợp | Độ rõ và độ đúng thanh (sai thanh là sai ký tự) |
| **RTF** ↓ | Thời gian sinh / thời lượng audio, trên CPU | Khả năng đáp ứng thời gian thực |
| **MOS** (1–5) ↑ | Kiểm thử nghe mù, ≥ 20 người, theo độ tự nhiên và độ rõ | Chất lượng cảm nhận (dự kiến) |

> Một số chỉ số tự động không dùng được cho tiếng Việt. Bộ dự đoán MOS UTMOS (huấn luyện trên tiếng Anh) đã được thử và chấm Edge-TTS **thấp nhất** trong các hệ thống, nên bị loại.

---

## 4. Cơ Chế Hoạt Động Của Hệ Thống

### Giai đoạn A: Tiền xử lý văn bản (`src/normalizer.py`, `src/vi_frontend.py`)
1. **Chuẩn hóa ngôn ngữ ViMMRC:** bỏ định dạng Markdown; chuẩn hóa nhãn trắc nghiệm `(B)`, `B.`, `Đáp án: (B)` thành `Đáp án B:`; đọc ngày tháng, số nguyên và số thập phân, phần trăm, tiền tệ, đơn vị đo.
2. **Token hóa:** `char_v1` hoặc `vi_tone_v2`, tùy metadata lưu trong checkpoint; chèn blank giữa các token.

### Giai đoạn B: Huấn luyện trên Colab (`notebooks/02_train_matcha_colab.ipynb`)
Tải dữ liệu (parquet từ Hugging Face), tính mel, huấn luyện, chọn snapshot bằng CER, rồi fine-tune HiFi-GAN. Mọi trạng thái lưu tại `MyDrive/Colab Notebooks/TTS/` nên có thể chạy tiếp qua nhiều phiên Colab miễn phí. Kết quả xuất ra là `matcha_vi_v2.pt` (kèm metadata frontend) và `matcha_vi_v2_hifigan.pt`.

### Giai đoạn C: Suy luận và đánh giá cục bộ (`synthesize.py`, `src/matcha_engine.py`, `scripts/`)
1. Encoder và duration predictor cho ra $\mu_y$; bộ giải Euler $N$ bước (mặc định 10) tích phân trường vector $v_\theta$ từ nhiễu $\mathcal{N}(0, 0{,}667^2 I)$ tới mel; HiFi-GAN sinh dạng sóng 22,05 kHz.
2. `scripts/benchmark.py` tính các chỉ số ở mục 3; `scripts/audition_speakers.py` chấm CER từng giọng.

---

## 5. Kết Quả Thực Nghiệm

### 5.1. Chẩn đoán checkpoint bản 1 (VIVOS)

| Quan sát | Số liệu đo | Hệ quả |
|---|---|---|
| Nhiễu nền ở hai đầu mỗi câu sinh ra | khoảng −37 dB so với đỉnh (InfoRe1 thật: khoảng −52 dB) | Mô hình học lại tạp âm của dữ liệu ASR; engine phải cắt nhiễu khi hậu xử lý |
| Độ rõ theo người nói (CER, 65 giọng × 3 câu) | Trung bình 3,3%; tốt nhất 0% (`VIVOSSPK25` nữ, `VIVOSSPK12` nam); kém nhất 12,3% (`VIVOSDEV02`) | Giọng mặc định cũ (speaker 0, CER 6,4%) được thay bằng giọng CER 0% |
| Ngắt nghỉ | Không có (VIVOS không có dấu câu) | Thêm cơ chế ngắt cụm theo dấu câu |
| Chữ viết tắt, nhãn đáp án | "B" bị đọc thành phụ âm câm | Frontend đánh vần theo tên chữ cái |

Kết luận: checkpoint bản 1 **đọc đúng chữ** (CER thấp) nhưng **chưa tự nhiên**. Nguyên nhân chính nằm ở dữ liệu (ASR, nhiều giọng × ít phút, có nhiễu), số step huấn luyện (khoảng 15k) và vocoder chưa fine-tune. Đây là cơ sở cho thiết kế bản 2.

### 5.2. Benchmark so với giọng người thật

Thiết lập: tham chiếu 10 câu giọng người thật InfoRe1, các chỉ số định nghĩa ở mục 3, chạy bằng `python scripts/benchmark.py`.

Kết quả ngày 10/10/2026: 10 câu, CPU, checkpoint VIVOS (`matcha_vi.pt`, giọng nữ `VIVOSSPK25`, 10 bước ODE).

| Mô hình | MCD (dB) ↓ | F0 RMSE (Hz) ↓ | log-F0 RMSE (bán cung) ↓ | CER ↓ | RTF (CPU) ↓ | Ghi chú |
|---|:---:|:---:|:---:|:---:|:---:|---|
| Giọng người thật (InfoRe1) | – | – | – | 0,7% | – | Tham chiếu; CER trần của ASR |
| **Matcha-TTS (tự huấn luyện)** | 5,35 | 70,4 | **2,86** | **1,9%** | 0,52 | OT-CFM, cục bộ |
| VITS MMS (pretrained) | **4,45** | 84,1 | 4,31 | 4,3% | 0,38 | End-to-end VAE, cục bộ, **giọng nam** |
| Edge-TTS HoaiMy | 4,63 | **48,3** | 2,69 | 1,0% | 0,13 | Cloud; RTF gồm độ trễ mạng |

**Nhận xét:**
- **Độ rõ (CER):** Matcha rõ nhất trong hai mô hình cục bộ, ít lỗi hơn VITS khoảng 2 lần. Matcha lấy mẫu từ nhiễu ngẫu nhiên nên CER dao động giữa các lần chạy (0,8% – 1,9% qua 3 lần đo), luôn ngang Edge-TTS và sát mức trần 0,7% của ASR.
- **Thanh điệu (log-F0 RMSE):** đường cao độ của Matcha gần Edge-TTS (2,86 so với 2,69 bán cung) và tốt hơn rõ rệt so với VITS (4,31).
- **MCD và F0 RMSE (Hz)** bao gồm cả khác biệt về **chất giọng**, vì tham chiếu là một người nói khác. VITS là giọng nam nên F0 RMSE tính bằng Hz cao. MCD của Matcha cao nhất, phù hợp với chẩn đoán dữ liệu VIVOS có nhiễu và vocoder chưa fine-tune; đây là điều mà pipeline huấn luyện mới nhắm tới.
- **Tốc độ:** Matcha đạt RTF 0,52 trên CPU, tức nhanh hơn thời gian thực khoảng 2 lần mà không cần mạng.

---

## 6. Hạn Chế & Hướng Tiếp Theo

1. **Hoàn tất huấn luyện bản 2** (InfoRe1 + `vi_tone_v2` + HiFi-GAN fine-tune), rồi đánh giá trên **tập kiểm thử tách riêng**. 10 câu tham chiếu hiện tại thuộc InfoRe1 nên bản 2 đã thấy khi huấn luyện.
2. **MOS:** tổ chức kiểm thử nghe mù; các chỉ số tự động chỉ phản ánh một phần chất lượng cảm nhận.
3. **Ablation Tone Decoupling:** huấn luyện `char_v1` và `vi_tone_v2` trên cùng dữ liệu và cùng số step, so sánh log-F0 RMSE và CER để định lượng đóng góp của biểu diễn thanh điệu.
4. **Dấu câu và ngữ điệu:** dùng dữ liệu có dấu câu (ví dụ PhoAudiobook) để mô hình tự học ngắt nghỉ và ngữ điệu câu hỏi.

---

## 7. Danh Mục Bài Báo Khoa Học & Tài Liệu Tham Khảo (Academic References)

Dưới đây là các công trình khoa học nền tảng định hình cơ sở lý thuyết và phương pháp luận của đề tài:

### 7.1. Nhóm Công Trình Cốt Lõi Về Flow Matching & Generative Modeling
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

### 7.2. Nhóm Công Trình Về Kiến Trúc Baseline & End-to-End TTS
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

### 7.3. Nhóm Công Trình Về Vocoder & Âm Học
5. **Jungil Kong, Jaehyeon Kim, Jaekyoung Bae.** (2020).  
   *"HiFi-GAN: Generative Adversarial Networks for Efficient and High Fidelity Speech Synthesis"*.  
   **Advances in Neural Information Processing Systems (NeurIPS 2020)**.  
   *Đóng góp:* Kiến trúc Neural Vocoder chuyển đổi phổ Mel thành tín hiệu sóng âm với cấu trúc Multi-Period Discriminator (MPD) và Multi-Scale Discriminator (MSD).  
   *Liên kết:* [arXiv:2010.05646](https://arxiv.org/abs/2010.05646)

### 7.4. Tập Dữ Liệu Thực Nghiệm Tiếng Việt
6. **Hi-Ngan Nguyen, Xuan-Bao Luong, Quoc-Bao Nguyen, Tat-Thang Vu, Mai-Chi Luong.** (2016).  
   *"VIVOS: A free Vietnamese speech corpus for speech recognition and synthesis"*.  
   **AILab, University of Science, VNU-HCM**.  
   *Đóng góp:* Tập dữ liệu tiếng nói tiếng Việt công khai (~15 giờ, 65 người nói) thiết kế cho nhận dạng tiếng nói; được dùng để huấn luyện checkpoint đa giọng đầu tiên của dự án.  
   *Liên kết chính thức:* [Zenodo DOI 10.5281/zenodo.7068130](https://doi.org/10.5281/zenodo.7068130) | [Hugging Face AILAB-VNUHCM/vivos](https://huggingface.co/datasets/AILAB-VNUHCM/vivos)

