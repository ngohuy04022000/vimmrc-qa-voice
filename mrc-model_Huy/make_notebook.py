"""Rebuild the staged tutorial notebook from small, reviewable cells."""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent
nb = nbf.read(ROOT / "01_vimmrc_training.ipynb", as_version=4)
nb.cells = [
    nbf.v4.new_markdown_cell(
        "# ViMMRC 2.0: MRC sinh câu trả lời với ViT5\n\n"
        "Mục tiêu: chuyển nhãn A–D thành văn bản của đáp án đúng, fine-tune ViT5, "
        "đánh giá trên dev/test và gọi API `answer_question(question, passage)`. "
        "Notebook này chạy được demo offline mà không tải mô hình. "
        "Dữ liệu ViMMRC 2.0 có điều kiện truy cập; xem README trước khi huấn luyện."
    ),
    nbf.v4.new_markdown_cell(
        "## 1. Thiết lập\n\nChạy từ thư mục `mrc-model_Huy` hoặc thư mục gốc của dự án. "
        "Để huấn luyện trên GPU/Colab, cài `pip install -r requirements.txt` trước khi bật công tắc ở bước 4."
    ),
    nbf.v4.new_code_cell(
        "from pathlib import Path\nimport json, sys, subprocess\n\n"
        "candidates = [Path.cwd(), Path.cwd() / 'mrc-model_Huy',\n"
        "              Path.cwd() / 'vimmrc-qa-voice' / 'mrc-model_Huy']\n"
        "WORK_DIR = next((path for path in candidates if (path / 'mrc_data.py').exists()), None)\n"
        "assert (WORK_DIR / 'mrc_data.py').exists(), 'Run from the repository or mrc-model_Huy folder'\n"
        "sys.path.insert(0, str(WORK_DIR.resolve()))\n"
        "from mrc_data import load_examples, evaluate_predictions\n"
        "from mrc_client import LexicalBaselineClient, MRCClient\n"
        "print('MRC workspace:', WORK_DIR.resolve())"
    ),
    nbf.v4.new_markdown_cell(
        "## 2. Kiểm tra schema\n\nMỗi bài đọc có `article`, `questions`, `options`, `answers`. "
        "Các mảng song song theo câu hỏi; đáp án A–D được đổi thành văn bản lựa chọn tương ứng. "
        "Ví dụ nhỏ bên dưới là dữ liệu tự tạo, không thuộc ViMMRC."
    ),
    nbf.v4.new_code_cell(
        "sample = load_examples(WORK_DIR / 'examples' / 'sample_vimmrc.json')\n"
        "assert len(sample) == 2 and sample[0]['answer'] == 'Hà Nội'\n"
        "for row in sample:\n"
        "    print({'question': row['question'], 'answer': row['answer']})"
    ),
    nbf.v4.new_code_cell(
        "DATA_DIR = WORK_DIR.parent / 'data'\n"
        "paths = {name: DATA_DIR / f'{name}_vimmrc.json' for name in ('train', 'dev', 'test')}\n"
        "if all(path.exists() for path in paths.values()):\n"
        "    from train import validate_split_disjoint\n"
        "    validate_split_disjoint(paths)\n"
        "    print('Licensed split counts:', {name: len(load_examples(path)) for name, path in paths.items()})\n"
        "else:\n"
        "    print('Licensed ViMMRC files unavailable; offline demo remains runnable.')"
    ),
    nbf.v4.new_markdown_cell(
        "## 3. Baseline offline để thử giao diện\n\n"
        "Baseline chỉ chọn câu trong passage có nhiều từ trùng với câu hỏi. "
        "Đây **không phải** mô hình được huấn luyện và không đại diện cho chất lượng ViT5."
    ),
    nbf.v4.new_code_cell(
        "baseline = LexicalBaselineClient()\n"
        "demo_answer = baseline.answer_question('Thành phố nằm ở miền nào?', sample[0]['passage'])\n"
        "print('Lexical baseline:', demo_answer)\n"
        "baseline_predictions = [baseline.answer_question(row['question'], row['passage']) for row in sample]\n"
        "print('Baseline on synthetic sample:', evaluate_predictions(baseline_predictions, sample))"
    ),
    nbf.v4.new_markdown_cell(
        "## 4. Fine-tune ViT5 (chỉ khi đã có GPU và quyền truy cập dữ liệu)\n\n"
        "`train.py` kiểm tra schema và rò rỉ bài đọc giữa split, đặt seed, dùng dev chọn checkpoint, "
        "và chỉ đánh giá test sau huấn luyện. Mặc định batch 1 + tích lũy gradient 16 để giảm bộ nhớ. "
        "Các passage dài hơn 512 token bị cắt; đây là giới hạn cần đo và cải thiện trong thí nghiệm tiếp theo. "
        "Kết quả sẽ thay đổi theo phần cứng và seed."
    ),
    nbf.v4.new_code_cell(
        "RUN_TRAINING = False  # Đổi thành True sau khi cài requirements, có CUDA và dữ liệu hợp lệ\n"
        "CHECKPOINT = WORK_DIR / 'checkpoints' / 'vit5-vimmrc'\n"
        "if RUN_TRAINING:\n"
        "    subprocess.run([sys.executable, str(WORK_DIR / 'train.py'),\n"
        "                    '--data-dir', str(DATA_DIR), '--output-dir', str(CHECKPOINT)], check=True)\n"
        "else:\n"
        "    print('Training disabled. Set RUN_TRAINING=True on GPU/Colab to fine-tune ViT5.')"
    ),
    nbf.v4.new_markdown_cell(
        "## 5. Suy luận và đánh giá\n\nCheckpoint do bước 4 tạo mới có thể khởi tạo `MRCClient`. "
        "Metric test được ghi vào `test_metrics.json`: Exact Match và token F1."
    ),
    nbf.v4.new_code_cell(
        "if (CHECKPOINT / 'config.json').exists():\n"
        "    client = MRCClient(CHECKPOINT)\n"
        "    print('ViT5:', client.answer_question(sample[0]['question'], sample[0]['passage']))\n"
        "    metrics_file = CHECKPOINT / 'test_metrics.json'\n"
        "    if metrics_file.exists():\n"
        "        print('Held-out test metrics:', json.loads(metrics_file.read_text(encoding='utf-8')))\n"
        "else:\n"
        "    print('No fine-tuned checkpoint yet; run step 4 on GPU to test MRCClient.')"
    ),
    nbf.v4.new_markdown_cell(
        "## 6. Ghi chú thí nghiệm\n\n"
        "Ghi lại phiên bản dữ liệu/model, seed, số epoch và ba metric sau khi chạy GPU. "
        "ViMMRC là bài toán trắc nghiệm; chuyển đáp án thành văn bản giúp API trả lời tự do, "
        "nhưng Exact Match ở đây đo mức khớp với lựa chọn đúng, chưa đo mọi cách diễn đạt hợp nghĩa."
    ),
]
nb.metadata.setdefault("kernelspec", {"display_name": "Python 3", "language": "python", "name": "python3"})
nbf.write(nb, ROOT / "01_vimmrc_training.ipynb")
