# MRC tiếng Việt — ViT5 và ViMMRC 2.0

Module nhận một câu hỏi và một đoạn văn, rồi sinh câu trả lời dạng chữ để dùng sau bước retrieval/STT và trước TTS. `MRCClient` chỉ hoạt động khi đã có checkpoint fine-tune. `LexicalBaselineClient` là bộ chọn câu theo từ khóa để thử pipeline offline; nó không phải mô hình ViT5 và không đo được chất lượng MRC.

## Dữ liệu và quyền truy cập

[ViMMRC 2.0 trên Hugging Face](https://huggingface.co/datasets/uitnlp/vimmrc2.0) là dữ liệu có kiểm soát truy cập, dùng cho nghiên cứu theo thỏa thuận của tác giả. Sau khi được cấp quyền, đặt ba tệp `train_vimmrc.json`, `dev_vimmrc.json`, `test_vimmrc.json` trong `../data/`. Dự án hiện có các tệp này cục bộ; module không tải hoặc phân phối lại chúng. Có thể xem [repo gốc](https://github.com/sonlam1102/vimmrc2) để biết điều kiện sử dụng.

Mỗi JSON là một mảng bài đọc. Mỗi bài có `article` (chuỗi), `questions` (mảng câu hỏi), `options` (mỗi câu hỏi có bốn phương án) và `answers` (ký tự A–D). `mrc_data.py` kiểm tra độ dài các mảng và đổi nhãn thành **văn bản phương án đúng**, ví dụ `B` → `Hà Nội`. Một số phương án sai trong dữ liệu thật rỗng; nhãn đúng phải trỏ tới phương án có nội dung. Train, dev và test giữ nguyên theo nguồn. `train.py` xác nhận không có bài đọc trùng giữa các split trước khi tải mô hình.

### Mở rộng dữ liệu: gộp thêm UIT-ViQuAD2.0

ViMMRC 2.0 chỉ có 5.273 câu hỏi (trắc nghiệm 4 đáp án, văn sách giáo khoa). Để model ViT5 trả lời được
nhiều dạng câu hỏi hơn và phù hợp với domain rộng hơn, `build_combined_dataset.py` gộp thêm
[UIT-ViQuAD2.0](https://huggingface.co/datasets/taidng/UIT-ViQuAD2.0) (28.454 câu hỏi tự luận trích xuất,
174 bài Wikipedia tiếng Việt, dataset công khai không cần xin quyền) rồi **chia lại từ đầu** thành
train/dev/test theo tỷ lệ 80/10/10 trên toàn bộ pool đã gộp — không giữ ranh giới split gốc của từng
nguồn. Việc chia luôn theo **đơn vị passage/article** (không theo câu hỏi riêng lẻ), nên một đoạn văn chỉ
rơi vào đúng một split, tránh model "học vẹt" passage đã thấy ở train khi được đánh giá ở dev/test.

Article lấy từ ViQuAD không có `options`/`answers` (không phải trắc nghiệm) — thay vào đó có
`answer_texts`: danh sách các câu trả lời tự luận được chấp nhận cho mỗi câu hỏi. `mrc_data.flatten_articles`
đọc được cả hai dạng và đều trả về hàng `{question, passage, answer}` dạng văn bản tự do.
Câu hỏi không có đáp án (`is_impossible=True`) trong ViQuAD2.0 bị loại: 28.454 câu gốc → 21.891 câu còn lại (cộng 5.273 câu ViMMRC = 27.164 câu).

Chạy (cần `huggingface_hub`, `pandas`, `pyarrow` — đã có trong `requirements.txt`):

```powershell
python build_combined_dataset.py --out-dir ../data/combined
python train.py --data-dir ../data/combined --output-dir checkpoints/vit5-combined
```

**So sánh kết quả với bộ ViMMRC thuần không còn trực tiếp được** vì dev/test giờ là hỗn hợp hai nguồn,
domain rộng hơn — số liệu cũ (dev/test 100% ViMMRC) và số liệu mới không nằm trên cùng một thước đo.
`--seed` (mặc định 42) quyết định cách xáo trộn và chia article; giữ cố định để tái lập được đúng 3 split.

Kết quả lần fine-tune đầu (ViT5-base, 3 epoch, batch 1 × gradient accumulation 16, seed 42) trên
27.164 câu hỏi (21.733 train / 2.715 dev / 2.716 test, chia theo passage): **Exact Match 41,05%, token F1
66,02%** trên test. Checkpoint tại `checkpoints/vit5-combined/` (không commit, tự chạy lại để tái tạo).
Còn khiêm tốn vì chưa tăng epoch hoặc dò hyperparameter; `train.py` tự chọn checkpoint tốt nhất theo
Exact Match trên dev (`load_best_model_at_end`), không phải checkpoint cuối cùng.

Train tiếp 2 epoch từ checkpoint trên (learning rate 1e-5, lưu checkpoint mỗi 450 bước, resume được khi
máy tắt đột ngột) → `checkpoints/vit5-combined-cont/`: **Exact Match 41,05%, token F1 66,55%** trên test.
Dev loss tăng (0,69 → 0,84) nên train thêm cùng cấu hình không còn giúp:

```powershell
$env:TRANSFORMERS_NO_TF='1'
python train.py --data-dir ../data/combined --model-name checkpoints/vit5-combined `
  --output-dir checkpoints/vit5-combined-cont --epochs 2 --learning-rate 1e-5 --save-steps 450 --resume
```

## Chạy demo offline và kiểm tra dữ liệu

Từ thư mục gốc repository:

```powershell
cd mrc-model_Huy
pip install -r requirements.txt pytest
python -m pytest -q tests
python train.py --dry-run
```

Notebook [01_vimmrc_training.ipynb](01_vimmrc_training.ipynb) chạy từ đầu đến cuối với dữ liệu mẫu tự tạo ở `examples/sample_vimmrc.json`. Mặc định `RUN_TRAINING = False`, nên notebook không tải ViT5 và không cần GPU. Để mở notebook qua Jupyter, cài thêm `jupyterlab`; để tạo lại notebook từ `make_notebook.py`, cài `nbformat`. Giữ nguyên notebook cũ `mrc_vimmrc.ipynb` để tham khảo.

## Fine-tune trên GPU/Colab (bộ gộp ViMMRC 2.0 + UIT-ViQuAD2.0, 27.164 câu; train 21.733)

```powershell
cd mrc-model_Huy
pip install -r requirements.txt
python train.py --data-dir ../data/combined --output-dir checkpoints/vit5-combined
```

Mặc định: `VietAI/vit5-base`, seed 42, ba epoch, batch 1, tích lũy gradient 16, đầu vào tối đa 512 token, đầu ra 64 token. Script báo số đầu vào/đáp án sẽ bị cắt token trước khi huấn luyện. Trainer chọn checkpoint bằng Exact Match trên **dev**; sau đó mới dự đoán **test** và ghi `test_metrics.json`. `DataCollatorForSeq2Seq` đệm nhãn bằng `-100`, nên padding không tham gia loss. Script yêu cầu CUDA, dùng BF16 khi GPU hỗ trợ và FP32 nếu không; không thực hiện full training trên CPU. Có thể đổi các tham số bằng `python train.py --help`.

Đánh giá gồm Exact Match và token F1 sau chuẩn hóa chữ thường, dấu câu và khoảng trắng.

Passage dài hơn 512 token sẽ bị cắt, nên thông tin cần thiết ở cuối bài có thể mất. Đây là giới hạn quan trọng khi diễn giải kết quả.

Để train trên bộ dữ liệu đã mở rộng (ViMMRC + UIT-ViQuAD2.0, xem mục trên), đổi `--data-dir`:

```powershell
python build_combined_dataset.py --out-dir ../data/combined
python train.py --data-dir ../data/combined --output-dir checkpoints/vit5-combined
```

## Tích hợp

```python
from mrc_client import MRCClient, LexicalBaselineClient

client = MRCClient("checkpoints/vit5-combined-cont")  # chỉ sau khi fine-tune xong
answer = client.answer_question("Thủ đô của Việt Nam là gì?", "Hà Nội là thủ đô của Việt Nam.")

demo = LexicalBaselineClient()  # chỉ để thử pipeline offline
demo_answer = demo.answer_question("Thủ đô của Việt Nam là gì?", "Hà Nội là thủ đô của Việt Nam.")
```

Thứ tự tham số API là `(question, passage)`. `MRCClient` đọc giới hạn token đã lưu cùng checkpoint; có thể truyền `device`, `max_input_tokens` và `max_new_tokens` để ghi đè khi cần.
