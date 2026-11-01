# THƯ MỤC TÀI LIỆU THUYẾT TRÌNH VÀ BÁO CÁO NHÓM 09 (TẢI TỪ GOOGLE DRIVE)

**Nguồn:** Google Drive Folder Nhóm 09: `https://drive.google.com/drive/folders/1bgbQJ5EbuziZGWjN-IQtV1oYLbw7xOHS?usp=drive_link`  
**Ngày đồng bộ:** 01/11/2026  
**Thành viên nhóm:**
- **Ngô Trí Huy (Nhóm trưởng):** Phân hệ Retrieval (BM25 + Dense + Reranker), Kho tri thức hai tầng RAG, Mô hình MRC (ViT5-base Seq2Seq sinh câu trả lời tự do), Tích hợp hệ thống.
- **Huỳnh Công Lương:** Phân hệ STT (Whisper-small LoRA 50h, CTranslate2 INT8, VAD), Giao diện Web (Angular 22 SPA), Đóng gói Docker Container.
- **Trương Hoàng Duy:** Phân hệ TTS (Matcha-TTS Flow Matching OT-CFM, Vocoder HiFi-GAN), Frontend tách thanh điệu `vi_tone_v2`, Text Normalizer & Benchmark Âm học.

---

## 1. Danh mục các tệp tải về từ Google Drive

| Tên tệp | Thư mục nguồn trên Drive | Dung lượng | Mô tả nội dung |
| :--- | :--- | :--- | :--- |
| `Tai_Lieu_Thuyet_Trinh_5_Phut.docx` | Thư mục `New/` | 1,8 MB | Bản thảo kịch bản 5 phút của nhóm (~997 từ, 6 slide). Chứa văn phong thuyết minh của Huy, nhưng còn mang số liệu cũ (ChoiceRanker, 1.8s, kho 552 bài). |
| `Tai_Lieu_Thuyet_Trinh_25p_TTS_9phut.docx` | Thư mục `New/` | 3,2 MB | Bản thảo kịch bản 25 phút của nhóm (~16 slide), tập trung sâu vào phân hệ TTS (9 phút). |
| `Nhom09_BaocaoCK_ML.docx` | Thư mục gốc | 1,3 MB | Báo cáo khoa học cuối kỳ hoàn chỉnh của Huỳnh Công Lương về Phân hệ STT (Whisper-small LoRA 20h & 50h, CTranslate2, VAD, 15 bảng số liệu đối sánh). |
| `Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx` | Thư mục gốc | 2,3 MB | Báo cáo khoa học chuyên sâu của Trương Hoàng Duy về Phân hệ TTS (Matcha-TTS, OT-CFM, MAS Numba JIT, HiFi-GAN, MCD, F0 RMSE, RTF). |
| `Tai_Lieu_Thuyet_Trinh_GDocs.docx` | Tệp Google Docs gốc | 237 KB | Tài liệu Google Docs "Tài liệu thuyết trình" (ID `15qQz8BvQH8GLv0RpLbBkqRMSDTad9_9zh7jxrPvprsE`). |
| `ViMMRC_Presentation_5min_gdrive.pptx` | Thư mục gốc | 55 KB | File slide PowerPoint 5 phút bản gốc của nhóm trên Drive (6 slide). |
| `ViMMRC_Presentation_30min_gdrive.pptx` | Thư mục gốc | 128 KB | File slide PowerPoint 30 phút bản gốc của nhóm trên Drive (24 slide, chưa cân chỉnh thời lượng, ~4.500 từ). |
| `ViMMRC_KichBan_5phut_gdrive.docx` | Thư mục gốc | 43 KB | File Word kịch bản 5 phút bản lưu trên Drive. |
| `Huy_model_card.md` | Thư mục `Huy_MRC/` | 899 B | Model card thử nghiệm ban đầu của Huy về 4-choice TF-IDF ranker. |
| `Huy_report.json` | Thư mục `Huy_MRC/` | 742 B | Báo cáo JSON ban đầu của Huy về phân hệ MRC cũ. |

---

## 2. Kết quả đối soát số liệu thực nghiệm chuẩn xác nhất

Dựa trên việc đối sánh chéo giữa Báo cáo cuối kỳ của Lương (`Nhom09_BaocaoCK_ML.docx`), Báo cáo TTS của Duy (`Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx`), mã nguồn Docker thực tế và nhật ký nghiệm thu `STATUS.md`:

1. **Phân hệ STT (Whisper-small LoRA 50h):**
   - Bộ dữ liệu: VietSpeech 50 giờ (41.212 mẫu Train, 1.797 mẫu Validation, 1.802 mẫu Test cố định).
   - Huấn luyện: Mixed precision BF16 trên GPU NVIDIA RTX 5060 Ti (16 GB VRAM), LoRA $r=16, \alpha=32$, learning rate $1\times 10^{-4}$, best step 2.750.
   - Kết quả test: **WER 13,77%** (giảm 23,00 điểm % / 62,56% tương đối so với Whisper gốc 36,76%); **CER 6,67%** (giảm 12,76 điểm % / 65,65% tương đối so với Whisper gốc 19,43%). So với bản 20h (WER 15,20%, CER 7,29%), bản 50h giảm thêm 9,47% WER.
   - Triển khai: `faster-whisper` / `CTranslate2` INT8 trên CPU, nhanh gấp **4,1 lần** so với PyTorch FP32, RAM chỉ ~450 MB; tích hợp bộ lọc `vad_filter=True` cắt hoàn toàn khoảng lặng vô nghĩa và hiện tượng lặp hallucination.

2. **Phân hệ Retrieval (Kho tri thức hai tầng RAG):**
   - Kho tài liệu: **Tầng 1** gồm 5.869 đoạn văn (ViMMRC 2.0 + UIT-ViQuAD2.0); **Tầng 2** gồm 1.481.873 đoạn văn Wikipedia tiếng Việt.
   - BM25 Tinh chỉnh: $k_1 = 2.1, b = 1.0$ kết hợp Bigram Phrase Boost (+0.4) đạt **Recall@1: 71,45%**, **Recall@5: 86,88%**, **MRR: 0,7719** trên 564 câu dev ViMMRC (vượt trội so với BM25 mặc định 64,18% / 79,96%).
   - RAG hai tầng trên 2.545 câu test: **Recall@1: 71,1%**, **Recall@5: 85,9%**.
   - Pipeline cuối với `bge-reranker-v2-m3` (+0,25 ưu tiên tầng 1): Answer F1 trên 200 câu trong kho đạt **60,7%**; trên 200 câu kiến thức mở Wikipedia đạt **24,3%** (vượt xa BM25 thuần 15,4%).

3. **Phân hệ Đọc hiểu Máy MRC (ViT5-base Seq2Seq sinh câu trả lời tự do):**
   - Bộ dữ liệu gộp: ViMMRC 2.0 (5.273 câu) + UIT-ViQuAD2.0 (21.891 câu) = **27.164 câu hỏi**.
   - Phân chia zero-leakage theo bài đọc: Train 21.733 câu (~80%), Dev 2.715 câu (~10%), Test 2.716 câu (~10%).
   - Cơ chế: Sinh câu trả lời tự do ngắn gọn, đúng trọng tâm trực tiếp từ ngữ cảnh, **loại bỏ hoàn toàn giả định trắc nghiệm 4 lựa chọn (ChoiceRanker)**.
   - Kết quả test: **Exact Match (EM): 41,05%**, **Token F1: 66,55%** (Dev: EM 42,62%, F1 67,92%).

4. **Phân hệ Tổng hợp Tiếng nói TTS (Matcha-TTS Flow Matching OT-CFM):**
   - Kiến trúc: 1D CNN + Transformer + Optimal-Transport Conditional Flow Matching (OT-CFM) + Vocoder HiFi-GAN tinh chỉnh 50.000 bước.
   - Cải tiến: Frontend tách thanh điệu `vi_tone_v2` (từ điển 41 âm vị + token thanh điệu 0–5); thuật toán Monotonic Alignment Search (MAS) tối ưu hóa bằng Numba JIT.
   - Kết quả âm học:
     - 10 bước Euler ODE: **CER: 0,85%** (hoặc 1,9% qua PhoWhisper), **log-F0 RMSE: 0,91 bán cung** (F0 RMSE 22,1 Hz), **MCD: 3,12 dB**, **RTF: 0,52 – 0,53** trên CPU (nhanh gấp 2 lần thời gian thực).
     - 20 bước Euler ODE: CER: 0,80%, log-F0 RMSE: 0,88 bán cung, MCD: 3,05 dB, RTF: 0,64.
     - So sánh: VITS MMS đạt CER 4,7%, log-F0 4,29 bán cung, MCD 4,40 dB. Mức trần người thật đạt CER 0,7%.

5. **Hiệu năng Triển khai Hệ thống (Docker CPU):**
   - Đo đạc thực tế trên Docker CPU (`OMP_NUM_THREADS=4`):
     - STT Faster-Whisper: ~3,0 giây.
     - Retrieval RAG + Reranker: ~6,0 giây.
     - ViT5 Reader sinh đáp án: ~1,4 giây.
     - TTS Matcha tổng hợp âm thanh: ~1,3 giây.
     - **Tổng thời gian toàn chu trình:** **khoảng 12 giây/câu**; nếu tắt reranker còn **khoảng 6 giây/câu**.
   - Đảm bảo chất lượng: **54/54 automated test cases passed** (1 test CPU accelerate skipped).
