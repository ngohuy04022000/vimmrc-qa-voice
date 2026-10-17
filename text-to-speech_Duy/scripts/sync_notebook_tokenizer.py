"""Đồng bộ src/vi_tokenizer.py vào cell `%%writefile vi_tokenizer.py` của notebook huấn luyện.

Notebook trên Kaggle không import được mã nguồn dự án, nên chứa một bản sao nguyên văn của bộ tách token
để huấn luyện và suy luận token hóa giống hệt nhau. tests/test_vi_tokenizer.py báo lỗi khi hai bản lệch nhau;
chạy script này sau mỗi lần sửa src/vi_tokenizer.py.

Chạy lệnh (từ thư mục gốc repository):
    cd text-to-speech_Duy
    python scripts/sync_notebook_tokenizer.py

Hoặc chạy trực tiếp từ thư mục gốc:
    python text-to-speech_Duy/scripts/sync_notebook_tokenizer.py
"""

import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOK = os.path.join(ROOT_DIR, "notebooks", "train_matcha.ipynb")
TOKENIZER = os.path.join(ROOT_DIR, "src", "vi_tokenizer.py")
MAGIC = "%%writefile vi_tokenizer.py"


def main() -> None:
    """Thay nội dung cell tokenizer trong notebook bằng nội dung hiện tại của src/vi_tokenizer.py."""
    with open(NOTEBOOK, encoding="utf-8") as f:
        nb = json.load(f)
    with open(TOKENIZER, encoding="utf-8") as f:
        source = f"{MAGIC}\n{f.read().rstrip()}"

    cells = [c for c in nb["cells"] if "".join(c["source"]).startswith(MAGIC)]
    if len(cells) != 1:
        raise RuntimeError(f"Cần đúng 1 cell bắt đầu bằng '{MAGIC}', tìm thấy {len(cells)}")
    if "".join(cells[0]["source"]) == source:
        print("[OK] Notebook đã đồng bộ, không cần thay đổi.")
        return

    cells[0]["source"] = source.splitlines(keepends=True)
    with open(NOTEBOOK, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"[OK] Đã đồng bộ {os.path.relpath(TOKENIZER, ROOT_DIR)} -> {os.path.relpath(NOTEBOOK, ROOT_DIR)}")


if __name__ == "__main__":
    main()
