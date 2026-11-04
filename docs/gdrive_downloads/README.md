# THƯ MỤC TÀI LIỆU THUYẾT TRÌNH VÀ BÁO CÁO NHÓM 09 (TẢI TỪ GOOGLE DRIVE)

**Nguồn:** Google Drive Folder Nhóm 09: `https://drive.google.com/drive/folders/1bgbQJ5EbuziZGWjN-IQtV1oYLbw7xOHS?usp=drive_link`  
**Ngày đồng bộ:** 01/11/2026  
**Thành viên nhóm:**
- **Ngô Trí Huy**
- **Huỳnh Công Lương**
- **Trương Hoàng Duy**

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

Dựa trên việc đối sánh chéo giữa Báo cáo cuối kỳ của Lương (`Nhom09_BaocaoCK_ML.docx`), Báo cáo TTS của Duy (`Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx`), mã nguồn Docker thực tế và nhật ký trạng thái `STATUS.md`:

1. **Phân hệ STT (Whisper-small LoRA 50h):**
   - Bộ dữ liệu: VietSpeech 50 giờ (41.212 mẫu Train, 1.797 mẫu Validation, 1.802 mẫu Test cố định).
   - Huấn luyện: Mixed precision BF16 trên GPU NVIDIA RTX 5060 Ti (16 GB VRAM), LoRA $r=16, \alpha=32$, learning rate $1\times 10^{-4}$, best step 2.750.
   - Kết quả test: **WER 13,77%** (giảm 23,00 điểm % / 62,56% tương đối so với Whisper gốc 36,76%); **CER 6,67%** (giảm 12,76 điểm % / 65,65% tương đối so với Whisper gốc 19,43%). So với bản 20h (WER 15,20%, CER 7,29%), bản 50h giảm thêm 9,46% WER tương đối.
   - Triển khai: `faster-whisper` / `CTranslate2` INT8 trên CPU, nhanh gấp **4,1 lần** so với PyTorch FP32, RAM khoảng 450–540 MB; tích hợp bộ lọc `vad_filter=True` giúp cắt khoảng lặng và giảm hiện tượng lặp từ.

2. **Phân hệ Retrieval (Kho tri thức hai tầng RAG):**
   - Kho tài liệu: **Tầng 1** gồm 5.879 đoạn văn (552 ViMMRC + 5.317 ViQuAD + 10 thẻ tri thức); **Tầng 2** gồm 1,48 triệu đoạn văn Wikipedia tiếng Việt.
   - BM25 Tinh chỉnh: $k_1 = 2.1, b = 1.0$ kết hợp Bigram Phrase Boost (+0,4). Trên ablation kho ViMMRC 552 đoạn (564 câu dev), đạt **Recall@1: 71,45%** (so với cấu hình mặc định Lucene 64,18%).
   - RAG hai tầng trên 2.545 câu test (trước reranker): **Recall@1: 71,1%**, **Recall@5: 85,9%**.
   - Pipeline cuối với `bge-reranker-v2-m3` (+0,25 ưu tiên tầng 1): Answer F1 trên 200 câu trong kho đạt **60,7%**; trên 200 câu kiến thức mở Wikipedia đạt **24,3%** (so với BM25 thuần 58,0% / 15,4%).

3. **Phân hệ Đọc hiểu Máy MRC (ViT5-base Seq2Seq sinh câu trả lời tự do):**
   - Bộ dữ liệu gộp: ViMMRC 2.0 (5.273 câu) + UIT-ViQuAD2.0 (21.891 câu có đáp án từ 28.454 câu gốc) = **27.164 câu hỏi**.
   - Phân chia theo bài đọc (không trùng bài đọc giữa các tập): Train 21.733 câu (~80%), Dev 2.715 câu (~10%), Test 2.716 câu (~10%).
   - Cơ chế: Sinh câu trả lời tự do ngắn gọn trực tiếp từ ngữ cảnh, không cần các phương án lựa chọn trắc nghiệm.
   - Kết quả test (2.716 câu): **Exact Match (EM): 41,05%**, **Token F1: 66,55%**. Toàn chuỗi BM25 → ViT5 (test 2.545 câu): **EM 32,3%, F1 53,9%** (đưa đoạn văn đúng: **F1 68,6%**).

4. **Phân hệ Tổng hợp Tiếng nói TTS (Matcha-TTS Flow Matching OT-CFM):**
   - Kiến trúc: 1D CNN + Transformer + Optimal-Transport Conditional Flow Matching (OT-CFM) + Vocoder HiFi-GAN tinh chỉnh 50.000 bước.
   - Cải tiến: Frontend tách thanh điệu `vi_tone_v2` (từ điển 41 ký hiệu gồm chữ cái và token thanh điệu 0–5); thuật toán Monotonic Alignment Search (MAS) viết bằng Numba.
   - Kết quả benchmark chuẩn trong kho mã nguồn (`text-to-speech_Duy/scripts/benchmark.py`, đối sánh trên câu tham chiếu giọng người thật InfoRe1):
     - **Matcha-TTS:** **MCD: 3,05 dB**, **F0 RMSE: 21,6 Hz**, **log-F0 RMSE: 0,88 bán cung**, **CER (ASR PhoWhisper): 0,8%**, **RTF: 0,64** trên CPU.
     - **So sánh:** VITS MMS đạt MCD 4,40 dB, F0 RMSE 82,7 Hz, log-F0 4,29 bán cung, CER 4,7%, RTF 0,29 (Edge-TTS là dịch vụ đám mây, không nằm trong bảng đo mới); Giọng người thật đạt CER trần 0,7%.

5. **Hiệu năng Triển khai Hệ thống (Docker CPU):**
   - Đo đạc thực tế trên Docker CPU (`OMP_NUM_THREADS=4`):
     - STT Faster-Whisper: ~3,0 giây.
     - Retrieval RAG + Reranker: ~6,0 giây.
     - ViT5 Reader sinh đáp án: ~1,4 giây.
     - TTS Matcha tổng hợp âm thanh: ~1,3 giây.
     - **Tổng thời gian toàn chu trình:** **khoảng 12 giây/câu**; nếu tắt reranker (`KB_RERANKER=`) còn **khoảng 6 giây/câu**.
   - Đảm bảo chất lượng: **115 bài kiểm thử tự động**.
