"""Cài mã nguồn Matcha-TTS vào text-to-speech_Duy/Matcha-TTS/ cho môi trường chạy cục bộ.

Matcha-TTS không được commit (đã .gitignore) vì là repo bên ngoài có .git riêng. Script này:
1. Clone đúng commit đã kiểm thử (MATCHA_COMMIT) về Matcha-TTS/.
2. Thay Monotonic Alignment Search (C-extension Cython, cần trình biên dịch) bằng bản numba thuần Python.

Matcha-TTS chỉ được dùng như mã nguồn (src/matcha_engine.py tự thêm Matcha-TTS/ vào sys.path),
không cần `pip install`. Thư viện phụ thuộc nằm trong requirements.txt.

Chạy lệnh (từ bất kỳ thư mục nào):
    python scripts/setup_matcha.py
"""

import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATCHA_DIR = os.path.join(ROOT_DIR, "Matcha-TTS")
MATCHA_REPO = "https://github.com/shivammehta25/Matcha-TTS.git"
MATCHA_COMMIT = "bd4d90d"  # commit đã kiểm thử với checkpoint của dự án

# Monotonic Alignment Search viết bằng numba (giống bản trong notebooks/02_train_matcha_colab.ipynb)
MAS_CODE = '''import numba
import numpy as np
import torch


@numba.njit(parallel=True, cache=True)
def _maximum_path_batch(paths, values, t_xs, t_ys):
    max_neg_val = -1e9
    for b in numba.prange(paths.shape[0]):
        path, value, t_x, t_y = paths[b], values[b], t_xs[b], t_ys[b]
        for y in range(t_y):
            for x in range(max(0, t_x + y - t_y), min(t_x, y + 1)):
                v_cur = max_neg_val if x == y else value[x, y - 1]
                if x == 0:
                    v_prev = 0.0 if y == 0 else max_neg_val
                else:
                    v_prev = value[x - 1, y - 1]
                value[x, y] += max(v_prev, v_cur)
        index = t_x - 1
        for y in range(t_y - 1, -1, -1):
            path[index, y] = 1
            if index != 0 and (index == y or value[index, y - 1] < value[index - 1, y - 1]):
                index -= 1


def maximum_path(value, mask):
    value = value * mask
    device, dtype = value.device, value.dtype
    value_np = value.detach().float().cpu().numpy()
    mask_np = mask.detach().cpu().numpy()
    path = np.zeros_like(value_np, dtype=np.int32)
    t_x = mask_np.sum(1)[:, 0].astype(np.int32)
    t_y = mask_np.sum(2)[:, 0].astype(np.int32)
    _maximum_path_batch(path, value_np, t_x, t_y)
    return torch.from_numpy(path).to(device=device, dtype=dtype)
'''


def main() -> None:
    """Clone Matcha-TTS (nếu chưa có), checkout commit cố định và vá Monotonic Alignment Search."""
    if not os.path.isdir(MATCHA_DIR):
        print(f"[setup] Clone {MATCHA_REPO} -> {MATCHA_DIR}")
        subprocess.run(["git", "clone", "-q", MATCHA_REPO, MATCHA_DIR], check=True)
        subprocess.run(["git", "-C", MATCHA_DIR, "checkout", "-q", MATCHA_COMMIT], check=True)
    else:
        print(f"[setup] Đã có {MATCHA_DIR}, bỏ qua bước clone.")

    mas_path = os.path.join(MATCHA_DIR, "matcha", "utils", "monotonic_align", "__init__.py")
    with open(mas_path, "w", encoding="utf-8") as f:
        f.write(MAS_CODE)
    print(f"[setup] Đã thay Monotonic Alignment Search bằng bản numba: {mas_path}")

    sys.path.insert(0, MATCHA_DIR)
    from matcha.models.matcha_tts import MatchaTTS  # noqa: F401  (kiểm tra import)

    print("[OK] Matcha-TTS sẵn sàng.")


if __name__ == "__main__":
    main()
