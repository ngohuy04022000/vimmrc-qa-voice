"""`uvicorn scripts.api_server:app` (và Docker CMD) phải import được mà không nhờ pytest.ini.

pytest.ini thêm `scripts` vào sys.path trong tiến trình test nên mọi test khác che mất lỗi
thiếu đường dẫn; ở đây chạy một tiến trình mới từ thư mục gốc, giống lúc triển khai."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ApiImportTests(unittest.TestCase):
    def test_import_from_repo_root_in_fresh_process(self):
        result = subprocess.run([sys.executable, "-c", "import scripts.api_server"], cwd=ROOT,
                                capture_output=True, text=True, timeout=180,
                                env={**__import__("os").environ, "PYTHONPATH": "", "TRANSFORMERS_NO_TF": "1"})
        self.assertEqual(result.returncode, 0, result.stderr[-1500:])


if __name__ == "__main__":
    unittest.main()
