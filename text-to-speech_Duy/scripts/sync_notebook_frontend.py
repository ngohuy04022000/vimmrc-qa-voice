"""Đồng bộ src/vi_frontend.py vào cell `%%writefile vi_frontend.py` của notebook huấn luyện.

Notebook Colab không import được mã nguồn dự án, nên chứa một bản sao nguyên văn của frontend để
huấn luyện và suy luận token hóa giống hệt nhau. tests/test_vi_frontend.py báo lỗi khi hai bản lệch nhau;
chạy script này sau mỗi lần sửa src/vi_frontend.py.

Chạy lệnh (từ bất kỳ thư mục nào):
    python scripts/sync_notebook_frontend.py
"""

import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTEBOOK = os.path.join(ROOT_DIR, "notebooks", "02_train_matcha_colab.ipynb")
FRONTEND = os.path.join(ROOT_DIR, "src", "vi_frontend.py")
MAGIC = "%%writefile vi_frontend.py"


def main() -> None:
    """Thay nội dung cell frontend trong notebook bằng nội dung hiện tại của src/vi_frontend.py."""
    with open(NOTEBOOK, encoding="utf-8") as f:
        nb = json.load(f)
    with open(FRONTEND, encoding="utf-8") as f:
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
    print(f"[OK] Đã đồng bộ {os.path.relpath(FRONTEND, ROOT_DIR)} -> {os.path.relpath(NOTEBOOK, ROOT_DIR)}")


if __name__ == "__main__":
    main()
