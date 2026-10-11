# MRC tiếng Việt — ViT5 và ViMMRC 2.0

Module nhận một câu hỏi và một đoạn văn, rồi sinh câu trả lời dạng chữ để dùng sau bước retrieval/STT và trước TTS. `MRCClient` chỉ hoạt động khi đã có checkpoint fine-tune. `LexicalBaselineClient` là bộ chọn câu theo từ khóa để thử pipeline offline; nó không phải mô hình ViT5 và không đo được chất lượng MRC.

## Dữ liệu và quyền truy cập

[ViMMRC 2.0 trên Hugging Face](https://huggingface.co/datasets/uitnlp/vimmrc2.0) là dữ liệu có kiểm soát truy cập, dùng cho nghiên cứu theo thỏa thuận của tác giả. Sau khi được cấp quyền, đặt ba tệp `train_vimmrc.json`, `dev_vimmrc.json`, `test_vimmrc.json` trong `../data/`. Dự án hiện có các tệp này cục bộ; module không tải hoặc phân phối lại chúng. Có thể xem [repo gốc](https://github.com/sonlam1102/vimmrc2) để biết điều kiện sử dụng.

Mỗi JSON là một mảng bài đọc. Mỗi bài có `article` (chuỗi), `questions` (mảng câu hỏi), `options` (mỗi câu hỏi có bốn phương án) và `answers` (ký tự A–D). `mrc_data.py` kiểm tra độ dài các mảng và đổi nhãn thành **văn bản phương án đúng**, ví dụ `B` → `Hà Nội`. Một số phương án sai trong dữ liệu thật rỗng; nhãn đúng phải trỏ tới phương án có nội dung. Train, dev và test giữ nguyên theo nguồn. `train.py` xác nhận không có bài đọc trùng giữa các split trước khi tải mô hình.

## Chạy demo offline và kiểm tra dữ liệu

Trong thư mục này:

```powershell
pip install -r requirements.txt pytest
python -m pytest -q tests
python train.py --dry-run
```

Notebook [01_vimmrc_training.ipynb](01_vimmrc_training.ipynb) chạy từ đầu đến cuối với dữ liệu mẫu tự tạo ở `examples/sample_vimmrc.json`. Mặc định `RUN_TRAINING = False`, nên notebook không tải ViT5 và không cần GPU. Để mở notebook qua Jupyter, cài thêm `jupyterlab`; để tạo lại notebook từ `make_notebook.py`, cài `nbformat`. Giữ nguyên notebook cũ `mrc_vimmrc.ipynb` để tham khảo.

## Fine-tune trên GPU/Colab

```powershell
pip install -r requirements.txt
python train.py --data-dir ../data --output-dir checkpoints/vit5-vimmrc
```

Mặc định: `VietAI/vit5-base`, seed 42, ba epoch, batch 1, tích lũy gradient 16, đầu vào tối đa 512 token, đầu ra 64 token. Script báo số đầu vào/đáp án sẽ bị cắt token trước khi huấn luyện. Trainer chọn checkpoint bằng Exact Match trên **dev**; sau đó mới dự đoán **test** và ghi `test_metrics.json`. `DataCollatorForSeq2Seq` đệm nhãn bằng `-100`, nên padding không tham gia loss. Script yêu cầu CUDA, dùng BF16 khi GPU hỗ trợ và FP32 nếu không; không thực hiện full training trên CPU. Có thể đổi các tham số bằng `python train.py --help`.

Đánh giá gồm Exact Match và token F1 sau chuẩn hóa chữ thường, dấu câu và khoảng trắng. `choice_accuracy` là phép ghép **heuristic**: chọn lựa chọn có token F1 cao nhất so với câu sinh, rồi kiểm tra nhãn A–D. Nếu mọi lựa chọn đều có điểm 0, dự đoán được tính là sai; khi hòa điểm dương, lựa chọn xuất hiện trước thắng. Đây là cách đánh giá thêm cho bài toán trắc nghiệm, không phải điểm xác suất của mô hình cho từng lựa chọn. API thực tế vẫn trả lời tự do khi không có danh sách lựa chọn.

Passage dài hơn 512 token sẽ bị cắt, nên thông tin cần thiết ở cuối bài có thể mất. Đây là giới hạn quan trọng khi diễn giải kết quả. Chưa có checkpoint huấn luyện trong repository, vì vậy chưa có số liệu test của ViT5 để báo cáo.

## Tích hợp

```python
from mrc_client import MRCClient, LexicalBaselineClient

client = MRCClient("checkpoints/vit5-vimmrc")  # chỉ sau khi fine-tune
answer = client.answer_question("Thủ đô của Việt Nam là gì?", "Hà Nội là thủ đô của Việt Nam.")

demo = LexicalBaselineClient()  # chỉ để thử pipeline offline
demo_answer = demo.answer_question("Thủ đô của Việt Nam là gì?", "Hà Nội là thủ đô của Việt Nam.")
```

Thứ tự tham số API là `(question, passage)`. `MRCClient` đọc giới hạn token đã lưu cùng checkpoint; có thể truyền `device`, `max_input_tokens` và `max_new_tokens` để ghi đè khi cần.
