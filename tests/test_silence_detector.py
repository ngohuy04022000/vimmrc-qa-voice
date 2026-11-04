"""Logic tự dừng ghi âm của web (web-interface_Luong/src/app/utils/silence-detector.ts):
biên dịch bằng TypeScript của dự án rồi chạy tình huống mẫu bằng Node."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web-interface_Luong"
TSC = WEB / "node_modules" / "typescript" / "bin" / "tsc"


@unittest.skipUnless(shutil.which("node") and TSC.exists(), "cần Node và web-interface_Luong/node_modules")
class SilenceDetectorTests(unittest.TestCase):
    def test_scenarios(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            subprocess.run(["node", str(TSC), "--ignoreConfig", str(WEB / "src/app/utils/silence-detector.ts"),
                            "--outDir", tmp, "--module", "esnext", "--target", "es2022"], check=True, timeout=120)
            (out / "package.json").write_text('{"type":"module"}')
            shutil.copy(ROOT / "tests/web/silence_detector.test.mjs", out)
            res = subprocess.run(["node", str(out / "silence_detector.test.mjs")], capture_output=True, text=True, timeout=60)
            self.assertEqual(res.returncode, 0, res.stderr[-1500:])
            self.assertIn("VAD ok", res.stdout)


if __name__ == "__main__":
    unittest.main()
