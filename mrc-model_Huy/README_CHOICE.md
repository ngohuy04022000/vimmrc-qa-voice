# Xếp hạng lựa chọn ViMMRC trên CPU

`ChoiceRanker` là mô hình **trắc nghiệm bốn lựa chọn**. Nó nhận câu hỏi, passage và đúng bốn phương án A–D, rồi trả về văn bản của phương án được chọn. Nó không trả lời câu hỏi tự do khi không có lựa chọn. Nhánh này độc lập với ViT5 trong `train.py`.

Mô hình dùng TF‑IDF ký tự cho passage, câu liên quan câu hỏi và từng lựa chọn; thêm đặc trưng khớp từ, cụm chính xác và độ dài lựa chọn. Logistic regression học cách chấm điểm từng phương án. Phương án rỗng được phép trong dữ liệu ViMMRC nhưng không bao giờ được chọn.

## Huấn luyện và đánh giá

Sau khi có quyền truy cập [ViMMRC 2.0](https://huggingface.co/datasets/uitnlp/vimmrc2.0), đặt `train_vimmrc.json` và `dev_vimmrc.json` trong `../data/`, rồi chạy tại thư mục này:

```powershell
pip install -r requirements_choice.txt
python train_choice_ranker.py
```

Script chỉ mở **train** và **dev**, không mở test. Từ train, chia theo nhóm bài đọc với seed 42 thành inner train/validation, chọn hệ số `C` trên tập {0.1, 1, 10}, rồi huấn luyện lại trên toàn train. Dev được dùng một lần để đánh giá checkpoint đã chọn. `checkpoints/choice_ranker/` chứa `ranker.joblib`, `report.json` và `model_card.md`; checkpoint cục bộ này không được đưa vào Git. Chỉ nạp tệp joblib đáng tin cậy vì định dạng này dùng pickle.

Lần chạy hiện tại trên dữ liệu cục bộ (3.600 câu train, 564 câu dev) cho **51,95%** độ chính xác dev (293/564), so với baseline lexical **43,62%** (246/564) và chọn ngẫu nhiên có seed **25,18%**. C trên inner validation là 10, đạt **53,94%**. Chênh lệch ranker–lexical là **8,33 điểm phần trăm** trên cùng dev. Đây là kết quả của bài toán bốn lựa chọn với passage gốc; retrieval thực tế có thể hạ độ chính xác. Test chưa được đánh giá. [Notebook thí nghiệm](02_choice_ranker.ipynb) trình bày các bước và đọc report được tạo tại máy chạy.

## API

```python
from choice_ranker import ChoiceRanker

ranker = ChoiceRanker.load("checkpoints/choice_ranker")
prediction = ranker.predict(question, passage, options)
# {'label': 'B', 'answer': 'Hà Nội', 'scores': {'A': 0.1, 'B': 0.8, ...}}
answer = ranker.answer_question(question, passage, options)
```

`options` là danh sách đúng bốn chuỗi theo thứ tự A–D. `scores` là xác suất dự đoán theo từng lựa chọn, **không chuẩn hóa để tổng bốn lựa chọn bằng 1**. Phương án rỗng có điểm `-inf`. Để chạy test module: `pip install pytest` rồi chuyển vào thư mục `cd mrc-model_Huy` và chạy `python -m pytest -q tests/test_choice_ranker.py` (hoặc từ thư mục gốc: `python -m pytest -q mrc-model_Huy/tests/test_choice_ranker.py`).
