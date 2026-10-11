# Bàn giao phần Ngô Trí Huy

Phạm vi: Retrieval và MRC. Hai module chạy riêng, không cần mã STT, TTS hoặc giao diện của thành viên khác. `scripts/qa_pipeline.py` nối hai module để kiểm tra trước khi ghép toàn nhóm.

## Thứ tự thực hiện

1. Mở `retrieval-model_Huy/01_bm25_retrieval.ipynb`: chuẩn bị kho đoạn văn, xây BM25, tìm kiếm, lưu/nạp index, đánh giá Recall@k và MRR.
2. Đọc `mrc-model_Huy/README.md` và chạy `mrc-model_Huy/01_vimmrc_training.ipynb`: kiểm tra dữ liệu, baseline, tiền xử lý, fine-tune, đánh giá và lưu/nạp checkpoint.
3. Mở `notebooks/03_integration_demo.ipynb`: ghép hai module bằng dữ liệu mẫu. Bật dùng checkpoint chỉ sau khi đã huấn luyện thành công.
4. Bàn giao interface bên dưới cùng index và thư mục checkpoint. Không cần thành viên khác chạy notebook huấn luyện lại để dùng mô hình.

## Chạy thử ngay

Tại thư mục gốc dự án, dùng Python 3.11 trở lên:

```powershell
python -X utf8 scripts/qa_pipeline.py --demo
python -X utf8 scripts/qa_pipeline.py --demo --question "Cà phê trồng ở đâu?"
python -m unittest discover -s tests -v
```

Lệnh demo dùng kho nhỏ tự tạo, không chứa dữ liệu ViMMRC. Baseline chỉ chọn câu có từ trùng, không phải mô hình đã fine-tune. Câu hỏi ngoài kho có thể không tìm thấy đoạn hoặc chọn nhầm đoạn; điểm BM25 không phải độ tin cậy.

Chạy checkpoint thật với index đã lưu:

```powershell
python -X utf8 scripts/qa_pipeline.py --index "path/to/index.json" --model "path/to/checkpoint" --question "Câu hỏi tiếng Việt"
```

## Hợp đồng ghép nối

| Module | Đầu vào | Đầu ra |
|---|---|---|
| `Retriever.retrieve(question)` | Câu hỏi `str` | Đoạn văn `str` |
| `Retriever.search(question, top_k)` | Câu hỏi và số kết quả | Danh sách `{id, passage, score}` |
| `MRCClient.answer_question(question, passage)` | Hai chuỗi văn bản | Câu trả lời `str` |
| `QAPipeline.answer_question(question)` | Văn bản từ STT/web | Chuỗi trả cho TTS/web |
| `QAPipeline.predict(question)` | Câu hỏi `str` | Đáp án, đoạn nguồn, ID và điểm truy xuất |

Khởi tạo retriever và reader một lần khi ứng dụng khởi động. Tên thư mục có dấu gạch nối nên ví dụ tích hợp thêm thư mục vào `sys.path`; không dùng câu lệnh `import mrc-model_Huy`.

```python
import sys
from pathlib import Path

root = Path(r"D:\Tai Lieu Hoc Tap Cao Hoc\Học máy tiên tiến và ứng dụng\vimmrc-qa-voice")
sys.path.insert(0, str(root / "scripts"))
from qa_pipeline import QAPipeline, Retriever, MRCClient

qa = QAPipeline(Retriever.load("path/to/index.json"), MRCClient("path/to/checkpoint"))
answer_text = qa.answer_question("Câu hỏi từ STT hoặc ô nhập liệu")
# Thành viên phụ trách TTS dùng answer_text làm đầu vào synthesize().
```

Chuỗi rỗng gây `ValueError`; giao diện nên yêu cầu người dùng nhập lại. Không tìm được từ khớp thì pipeline trả thông báo, không gọi reader. Với truy vấn có từ trùng nhưng không liên quan, BM25 vẫn có thể trả đoạn sai; chưa có bộ phát hiện câu hỏi ngoài miền đã hiệu chỉnh.

## Dữ liệu và cách báo cáo kết quả

Dữ liệu hiện có trong `data/` là 482/70/147 bài đọc và 3.600/564/1.109 câu hỏi tương ứng train/dev/test. Kiểm tra tại thời điểm triển khai không thấy bài đọc trùng sau chuẩn hóa khoảng trắng và chữ thường giữa các split. Có phương án nhiễu rỗng; đáp án đúng không rỗng. Giữ cách chia theo bài đọc, không trộn lại theo từng câu hỏi.

ViMMRC là dữ liệu đọc hiểu trắc nghiệm. Chuyển đáp án đúng thành văn bản để fine-tune mô hình sinh câu trả lời là một biến thể tác vụ; EM/F1 của biến thể đó không tương đương accuracy trắc nghiệm. Đánh giá cần ghi rõ mô hình có nhận các lựa chọn hay không.

Với Retrieval, không đưa câu hỏi, phương án hay đáp án vào kho tìm kiếm. Kho chỉ chứa bài đọc. Nếu đánh giá câu hỏi dev trên kho gồm bài đọc dev, gọi rõ đây là đánh giá trên kho đã biết; không tuyên bố đó là truy xuất tài liệu mới ngoài kho. Kho train không chứa bài đọc dev nên phải báo coverage khi đánh giá dev.

Báo cáo riêng ba mức: Recall@k/MRR của Retrieval; EM/F1 của reader với đoạn đúng; EM/F1 toàn pipeline với đoạn truy xuất. Chỉ dùng dev để chọn tham số, giữ test cho đánh giá cuối. Điểm dữ liệu tự tạo chỉ kiểm tra phần mềm, không dùng làm kết quả nghiên cứu.

## Môi trường và giới hạn kiểm chứng

Kiểm chứng ngày 29/09/2026: 23 kiểm thử đạt; cả ba notebook chạy hết từ thư mục gốc ở chế độ offline; một bước `Seq2SeqTrainer` với T5 rất nhỏ khởi tạo ngẫu nhiên chạy thành công trên CPU và xác nhận masking nhãn padding. Đây là kiểm chứng phần mềm, không phải fine-tune ViT5. Chạy toàn bộ kiểm thử sau khi cài môi trường MRC và `pytest`:

```powershell
python -m pip install pytest
python -m pytest -q tests retrieval-model_Huy/test_retrieval.py mrc-model_Huy/tests
```

Muốn mở notebook trên máy khác, cài `jupyterlab ipykernel` rồi chạy `python -m jupyterlab` tại thư mục gốc. Demo CLI chỉ cần Python; các kiểm thử huấn luyện cần thư viện trong `mrc-model_Huy/requirements.txt`.

Kết quả baseline đã chạy trên 564 câu hỏi dev, với kho gồm đúng 70 bài đọc dev:

| Chỉ số | Kết quả |
|---|---:|
| Retrieval Recall@1 | 71,45% |
| Retrieval Recall@5 | 83,69% |
| Retrieval MRR@5 | 0,7624 |
| Baseline đọc với đoạn đúng: token F1 | 11,59% |
| Baseline toàn pipeline: token F1 | 10,41% |
| Baseline EM ở cả hai chế độ | 0% |

Đây là kết quả BM25 và bộ chọn câu theo từ trùng, chưa phải ViT5. Các con số cho thấy baseline chạy được nhưng chất lượng trả lời còn thấp. Báo cáo có hash dữ liệu tại `reports/dev_baseline.json`; chạy lại bằng:

```powershell
python -X utf8 scripts/evaluate_pipeline.py --data data/dev_vimmrc.json --split dev --baseline --output reports/dev_baseline.json
```

Thay `--baseline` bằng `--model "path/to/checkpoint"` để đánh giá reader đã huấn luyện theo cùng quy trình. Script không ghi nội dung dữ liệu gốc vào báo cáo.

Máy hiện có GPU NVIDIA nhưng bản PyTorch được phát hiện là `2.12.1+cpu`, `torch.cuda.is_available()` trả `False`. Muốn huấn luyện GPU cần môi trường PyTorch hỗ trợ CUDA phù hợp hoặc Colab. Không bật `fp16` vô điều kiện.

Mã và notebook huấn luyện không đồng nghĩa đã có checkpoint tốt. Cần hoàn tất fine-tune và đánh giá trên ViMMRC trước khi báo cáo chất lượng mô hình. Notebook gốc `mrc_vimmrc.ipynb` được giữ để tham khảo; dùng notebook mới cho quy trình hiện tại.

Nguồn dữ liệu: [ViMMRC 2.0 của UITNLP](https://huggingface.co/datasets/uitnlp/vimmrc2.0). Máy khác cần quyền truy cập hợp lệ hoặc bản dữ liệu đã được cấp. Không commit dữ liệu, token, audio hay checkpoint lên Git.
