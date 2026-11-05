#!/usr/bin/env python3
"""Script khởi chạy đồng thời Backend và Frontend cho dự án ViMMRC.

Hoạt động trên cả macOS, Windows và Linux:
    python run_web.py      (Windows)
    python3 run_web.py     (macOS / Linux)
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FE_DIR = ROOT / "web-interface_Luong"

# Thiết lập UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    print("=" * 60)
    print("  KHỞI ĐỘNG HỆ THỐNG ViMMRC VOICE Q&A (BE + FE)")
    print("  Hệ điều hành:", "macOS" if sys.platform == "darwin" else ("Windows" if sys.platform == "win32" else "Linux"))
    print("=" * 60)

    # 1. Khởi động Backend FastAPI (:8000)
    print("\n[1/2] Đang khởi động Backend FastAPI (cổng 8000)...")
    be_cmd = [sys.executable, "-m", "uvicorn", "scripts.api_server:app", "--host", "127.0.0.1", "--port", "8000"]
    be_proc = subprocess.Popen(be_cmd, cwd=str(ROOT))

    # 2. Khởi động Frontend Angular (:4200)
    print("[2/2] Đang khởi động Frontend Angular (cổng 4200)...")
    fe_cmd = [npm_cmd, "start"]
    fe_proc = subprocess.Popen(fe_cmd, cwd=str(FE_DIR))

    print("\n" + "-" * 60)
    print("👉 Frontend: http://localhost:4200/")
    print("👉 Backend API: http://127.0.0.1:8000/docs")
    print("👉 Nhấn Ctrl+C để dừng cả 2 máy chủ bất cứ lúc nào.")
    print("-" * 60 + "\n")

    # Mở trình duyệt sau 3 giây
    time.sleep(3)
    try:
        webbrowser.open("http://localhost:4200/")
    except Exception:
        pass

    try:
        # Chờ đợi tiến trình hoạt động
        while True:
            time.sleep(1)
            if be_proc.poll() is not None:
                print("\n[Cảnh báo] Backend đã dừng.")
                break
            if fe_proc.poll() is not None:
                print("\n[Cảnh báo] Frontend đã dừng.")
                break
    except KeyboardInterrupt:
        print("\n[Đang tắt] Dừng cả Backend và Frontend...")
    finally:
        for proc in (be_proc, fe_proc):
            try:
                if proc.poll() is None:
                    if sys.platform == "win32":
                        proc.terminate()
                    else:
                        os.kill(proc.pid, signal.SIGTERM)
            except Exception:
                pass
        print("[Xong] Đã dừng tất cả dịch vụ.")


if __name__ == "__main__":
    main()

