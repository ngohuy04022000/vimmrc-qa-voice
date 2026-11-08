# Quy trình chấm tay câu trả lời dài kèm nguồn

Mục đích: token F1 phạt câu dài (F1 0,4421 → 0,2945 khi câu dài từ 21,6 lên 52,4 từ) nên không đo được chất lượng
thật của chế độ `DIALOGUE_DETAIL`. Cần đánh giá người trên một mẫu nhỏ, độc lập với đáp án tham chiếu.

## Chuẩn bị
```powershell
.venv\Scripts\python.exe scripts\make_human_eval_sheet.py --per-src 20 --seed 0
```
Tạo `reports/human_eval_sheet.csv` (60 dòng nếu mỗi nhóm đủ 20). Hai cột `_hidden_*` chỉ để phân tích sau, che đi khi chấm.
Tối thiểu hai người chấm độc lập, mỗi người một bản sao của tệp; không trao đổi trước khi chấm xong.

## Các cột cần điền
| Cột | Thang | Cách chấm |
|---|---|---|
| `correct` | 0/1 | Câu trả lời đầu (trước câu bằng chứng) trả lời đúng câu hỏi, đối chiếu kiến thức hoặc nguồn gốc. |
| `evidence_relevant` | 0/1/2 | 0 = câu thêm vào lạc đề hoặc sai; 1 = liên quan nhưng thừa; 2 = bổ sung thông tin hữu ích cho câu hỏi. |
| `source_supports_answer` | 0/1 | Mở nguồn được ghi ("Wikipedia, bài X" hay bài đọc ViMMRC) và xác nhận nguồn đó chứa thông tin của câu trả lời. |
| `natural_to_hear` | 1–5 | Đọc to hoặc nghe qua TTS: có tự nhiên, không lặp, không chứa ký tự khó đọc không. |

## Phân tích
- Độ đồng thuận: Cohen's kappa cho `correct`, `source_supports_answer`; trọng số bậc cho `evidence_relevant`.
- Báo cáo tỷ lệ theo nhóm câu hỏi (`_hidden_src`) với khoảng tin cậy Wilson 95 %; mẫu 20 câu mỗi nhóm cho khoảng rộng khoảng ±20 điểm,
  nên chỉ kết luận được các khác biệt lớn.
- So sánh với chế độ ngắn: cùng danh sách câu hỏi, chỉ chấm `correct`; chế độ dài không được làm giảm `correct`.

## Giới hạn
Mẫu nhỏ; câu hỏi `hard` và `ood` do nhóm tự viết; người chấm biết dự án nên có thiên lệch; nguồn Wikipedia nên kiểm tra theo bản cục bộ của kho (`data/kb_wiki_full`),
không phải bản trực tuyến hiện tại.
