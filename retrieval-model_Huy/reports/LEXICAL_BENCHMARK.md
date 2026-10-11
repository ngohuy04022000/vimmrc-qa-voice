# Thử nghiệm cải thiện truy xuất BM25

Chạy `python benchmark_retrieval.py` trong `retrieval-model_Huy/` để tái lập. Script dùng 800/3.600 câu hỏi train lấy mẫu cố định (`seed=42`) và 482 bài đọc train để chọn cấu hình trong 16 ứng viên. Thứ tự chọn: Recall@1, rồi MRR@5, rồi Recall@5. Sau khi khóa cấu hình, script mới đọc 70 bài đọc và 564 câu hỏi dev để so sánh một lần. Không dùng test, đáp án A–D hay phương án trả lời. [Dữ liệu số đầy đủ](lexical_benchmark.json) không chứa văn bản bài đọc.

| Corpus/cấu hình | Recall@1 | Recall@5 | MRR@5 | Thời gian truy vấn |
|---|---:|---:|---:|---:|
| Train 800, BM25 cũ | 0.5325 | 0.6738 | 0.5894 | 0.251 s |
| Train 800, cấu hình được chọn | 0.6413 | 0.7562 | 0.6865 | 0.223 s |
| Dev 564, BM25 cũ | 0.7145 | 0.8369 | 0.7624 | 0.0264 s |
| Dev 564, cấu hình được chọn | 0.7748 | 0.8652 | 0.8123 | 0.0253 s |

Cấu hình cũ là `k1=1.5, b=0.75, query_stopwords=False, bigram_boost=0.0`. Cấu hình được chọn là `k1=2.1, b=1.0, query_stopwords=True, bigram_boost=0.4`. Điểm bigram thưởng nhẹ các cặp từ đứng cạnh nhau; danh sách stopword chỉ tác động lên unigram trong câu hỏi. Các đoạn văn được giữ nguyên.

Chỉ số dev cải thiện nên `Retriever(passages)` hiện dùng cấu hình được chọn. `BASELINE_CONFIG` và `OPTIMIZED_CONFIG` cho phép tái lập hai cấu hình tường minh. `Retriever.load()` vẫn dùng tham số BM25 cũ khi mở index JSON cũ chưa lưu các trường mới.

Kiểm tra hiệu suất dùng 200 câu hỏi train: quét toàn bộ corpus với document frequency tính sẵn mất 0.1420 giây, truy vấn bằng postings 0.0518 giây (nhanh 2.74 lần); hai cách cho cùng top-5 trên 200 câu. Số đo thời gian phụ thuộc máy. Đây là bài toán truy xuất **closed corpus**: bài đọc đích đã nằm trong tập ứng viên. Với bài đọc vắng khỏi index, không thể truy xuất ID đích; cần xem `corpus_coverage` khi đánh giá các tập khác nhau.
