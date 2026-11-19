# NOTICE - thành phần bên thứ ba

Mã nguồn của dự án: MIT (xem `LICENSE`). Các thành phần dưới đây có giấy phép riêng.
Cột "Nguồn xác nhận" cho biết giấy phép được kiểm chứng ở đâu trong repo; mục ghi
"cần xác minh tại nguồn" là chưa kiểm chứng được từ repo, KHÔNG được suy ra.

| Thành phần | Giấy phép | Nguồn xác nhận |
|---|---|---|
| `nguyenvulebinh/vi-mrc-large` (bộ đọc mặc định) | **CC-BY-NC-4.0, chỉ phi thương mại** | STATUS.md, README.md |
| Matcha-TTS (`text-to-speech_Duy/Matcha-TTS`, tác giả Shivam Mehta) | MIT, (c) 2023 Shivam Mehta | `text-to-speech_Duy/Matcha-TTS/LICENSE` |
| Whisper / faster-whisper (STT; checkpoint fine-tune whisper-small-vi-50h) | cần xác minh tại nguồn | repo không chứa văn bản giấy phép |
| `BAAI/bge-reranker-v2-m3` | cần xác minh tại nguồn | repo không chứa văn bản giấy phép |
| `intfloat/multilingual-e5-small` | cần xác minh tại nguồn | repo không chứa văn bản giấy phép |
| ViT5 (bộ đọc thay thế, fine-tune trong dự án) | cần xác minh tại nguồn | README.md nói là lựa chọn nếu dùng thương mại, nhưng không nêu giấy phép của mô hình gốc |
| UIT-ViQuAD2.0 | cần xác minh tại nguồn | repo không chứa văn bản giấy phép |
| ViMMRC 2.0 (`uitnlp/vimmrc2.0`, dataset gated) | cần xác minh tại nguồn; dữ liệu có điều kiện truy cập riêng, không phân phối lại | STATUS.md (data không commit) |
| Wikipedia tiếng Việt (KB `kb_wiki_full`) | CC-BY-SA (theo yêu cầu của nhóm; cần ghi nguồn và chia sẻ tương tự cho phần trích) | chưa có văn bản trong repo; cần xác minh phiên bản cụ thể tại nguồn |

## Hệ quả cho việc triển khai

Do bộ đọc mặc định `vi-mrc-large` là CC-BY-NC-4.0, **bản triển khai mặc định (Docker) chỉ dùng phi thương mại**.
Muốn dùng thương mại phải đổi `MRC_CHECKPOINT` sang bộ đọc có giấy phép phù hợp và xác minh giấy phép
của mọi mục "cần xác minh" ở trên trước khi phân phối.

Checkpoint và dữ liệu không nằm trong git; người dùng tải về tuân theo điều khoản của từng nguồn.