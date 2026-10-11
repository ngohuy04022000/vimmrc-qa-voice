# Truy xuất đoạn văn bằng BM25

Module của Huy chọn đoạn văn tiếng Việt liên quan tới câu hỏi để đưa cho MRC. Chạy bằng Python 3.10+ và thư viện chuẩn, không cần tải mô hình. BM25 chỉ so khớp từ; kết quả là ngữ cảnh, không phải đáp án. Mặc định hiện dùng cấu hình được chọn bằng câu hỏi train; [báo cáo thử nghiệm](reports/LEXICAL_BENCHMARK.md) ghi rõ phép đo và giới hạn.

## Chạy nhanh với dữ liệu tổng hợp

Từ thư mục `retrieval-model_Huy/`:

```powershell
python retrieval_cli.py demo "Hành tinh nào gần Mặt Trời nhất?"
python retrieval_cli.py index --input synthetic_passages.json --output sample_index.json
python retrieval_cli.py query --index sample_index.json --question "Mưa hình thành từ đâu?" --top-k 2
python retrieval_cli.py evaluate --index sample_index.json --queries synthetic_queries.json --top-k 1
python -m unittest -v test_retrieval.py
```

`sample_index.json` là file tạo ra để thử, không cần commit. `synthetic_passages.json` và `synthetic_queries.json` là ví dụ **tự tạo**, không thuộc ViMMRC.

## Giao diện tích hợp

```python
from retrieval_client import BASELINE_CONFIG, OPTIMIZED_CONFIG, Retriever

retriever = Retriever([{"id": "p1", "passage": "Nội dung đoạn văn."}])
context: str = retriever.retrieve("Nội dung gì?")
hits = retriever.search("Nội dung gì?", top_k=5)
retriever.save("corpus_index.json")
retriever = Retriever.load("corpus_index.json")
old_retriever = Retriever([{"id": "p1", "passage": "Nội dung đoạn văn."}], **BASELINE_CONFIG)
```

`retrieve(question)` trả về **chuỗi passage** tốt nhất, hoặc `""` nếu câu hỏi không có từ nào trùng với corpus. `search(question, top_k)` trả danh sách `{id, passage, score}` xếp theo BM25; nếu đồng điểm giữ thứ tự corpus. Corpus đầu vào là danh sách `{id: str, passage: str}` với ID duy nhất. Index JSON lưu corpus và tham số BM25; chỉ dùng từ nguồn đáng tin cậy. `OPTIMIZED_CONFIG` là cấu hình mặc định; `BASELINE_CONFIG` tái lập BM25 cũ. Tokenizer chuẩn hóa Unicode NFC, không tách từ tiếng Việt theo âm tiết ghép hoặc xử lý đồng nghĩa.

## Chuẩn bị và đánh giá ViMMRC

Từ gốc repository, sau khi đã có các file dữ liệu cục bộ:

```powershell
python retrieval-model_Huy/retrieval_cli.py prepare-vimmrc --input data/dev_vimmrc.json --output retrieval-model_Huy/dev_index.json --split dev
python retrieval-model_Huy/retrieval_cli.py evaluate-vimmrc --index retrieval-model_Huy/dev_index.json --data data/dev_vimmrc.json --split dev --top-k 5
python retrieval-model_Huy/retrieval_cli.py prepare-vimmrc --input data/train_vimmrc.json --output retrieval-model_Huy/train_index.json --split train
python retrieval-model_Huy/retrieval_cli.py evaluate-vimmrc --index retrieval-model_Huy/train_index.json --data data/dev_vimmrc.json --split dev --top-k 5
```

`prepare-vimmrc` chỉ lấy trường `article`; ID có dạng `dev:0000` hoặc `train:0000`. Trường `questions`, `options`, `answers` không được đưa vào index. `evaluate-vimmrc` lấy mỗi câu hỏi làm truy vấn, tìm **bài đọc trùng sau chuẩn hóa Unicode NFC và khoảng trắng** trong index làm nhãn liên quan; **không dùng nhãn đáp án A–D**. Các chỉ số là trung bình Recall@k và MRR@k, tính cả câu hỏi có bài đọc gốc vắng trong corpus. `corpus_coverage` cho biết tỷ lệ câu hỏi có bài đọc gốc trong corpus. Dev-on-dev là kiểm tra **closed corpus** (bài đọc đích có sẵn); train-on-dev thường thiếu bài đọc đích, nên coverage thấp và Recall@k bị chặn bởi coverage. Không nên diễn giải dev-on-dev là kết quả tổng quát hóa sang tài liệu chưa thấy.

Notebook [01_bm25_retrieval.ipynb](01_bm25_retrieval.ipynb) trình bày từng bước và chạy độc lập với dữ liệu tổng hợp. Dữ liệu ViMMRC là tùy chọn cho CLI; không có dữ liệu thật vẫn chạy được demo, test và notebook.

## Tái lập phép chọn cấu hình

Từ `retrieval-model_Huy/`, chạy `python benchmark_retrieval.py` khi đã có `../data/train_vimmrc.json` và `../data/dev_vimmrc.json`. Script chọn trong 16 cấu hình trên tối đa 800 câu hỏi train lấy mẫu cố định rồi mới đánh giá cấu hình thắng trên dev; ghi chỉ số và thời gian vào `reports/lexical_benchmark.json`. Không đọc test. Truy vấn dùng postings để chỉ chấm điểm tài liệu chứa từ của câu hỏi, thay vì quét mọi tài liệu.
