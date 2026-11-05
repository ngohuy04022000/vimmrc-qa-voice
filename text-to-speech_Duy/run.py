#!/usr/bin/env python3
"""Cross-platform Task Runner cho module Text-to-Speech (TTS) và toàn bộ hệ thống ViMMRC.

Chạy tương thích hoàn toàn trên: Windows, macOS và Linux.
Cách dùng:
    python run.py                     # Mở menu tương tác trực quan
    python run.py -t "Xin chào bạn"   # Tổng hợp câu bất kỳ
    python run.py -f test_sentence.txt
    python run.py --app               # Khởi động cả Backend và Frontend
    python run.py --benchmark         # Chạy đo đạc benchmark (MCD, F0, CER, RTF)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Thiết lập UTF-8 cho terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT_DIR.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


def play_audio(audio_path: str | Path) -> None:
    """Mở file âm thanh bằng trình phát mặc định của hệ điều hành."""
    path_obj = Path(audio_path)
    if not path_obj.exists():
        print(f"[Cảnh báo] File audio không tồn tại: {path_obj}")
        return

    abs_path = str(path_obj.resolve())
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", abs_path], check=False)
        elif sys.platform == "win32":  # Windows
            os.startfile(abs_path)
        else:  # Linux
            subprocess.run(["xdg-open", abs_path], check=False)
        print(f"[Audio] Đang phát file: {abs_path}")
    except Exception as exc:
        print(f"[Thông báo] Không thể tự mở phát audio ({exc}). Đường dẫn file: {abs_path}")


def run_synthesize(
    text: str | None = None,
    file_path: str | Path | None = None,
    engine: str = "matcha",
    voice: str = "nu",
    rate: str = "+0%",
    output: str | Path | None = None,
    auto_play: bool = True,
) -> str | None:
    """Gọi engine tổng hợp giọng nói."""
    # Đảm bảo đường dẫn import hoạt động
    sys.path.insert(0, str(ROOT_DIR))
    sys.path.insert(0, str(ROOT_DIR / "src"))

    from synthesize import synthesize

    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()
    elif text:
        raw_text = text.strip()
    else:
        raw_text = "Đáp án đúng là câu C: Quá trình quang hợp diễn ra chủ yếu ở bào quan lục lạp của tế bào thực vật."

    if not output:
        ext = ".wav" if engine in ("matcha", "vits") else ".mp3"
        output = OUTPUTS_DIR / f"test_{engine}_{voice}{ext}"

    print(f"\n[Đang tổng hợp] Engine: {engine} | Voice: {voice} | Rate: {rate}")
    print(f"[Văn bản] {raw_text}")

    try:
        audio_path = synthesize(
            text=raw_text,
            output_path=str(output),
            voice=voice,
            engine=engine,
            rate=rate,
        )
        print(f"[Thành công] Âm thanh đã lưu tại: {audio_path}")
        if auto_play:
            play_audio(audio_path)
        return audio_path
    except Exception as exc:
        print(f"[Lỗi tổng hợp] {exc}")
        return None


def run_benchmark() -> None:
    """Chạy kịch bản đo đạc định lượng benchmark."""
    benchmark_script = ROOT_DIR / "scripts" / "benchmark.py"
    if not benchmark_script.exists():
        print(f"[Lỗi] Không tìm thấy script benchmark tại: {benchmark_script}")
        return
    print("\n[Benchmark] Đang đo đạc các chỉ số MCD, F0 RMSE, CER, RTF (Matcha & VITS)...")
    cmd = [sys.executable, str(benchmark_script), "--engines", "matcha", "vits"]
    subprocess.run(cmd, cwd=str(ROOT_DIR))


def launch_full_stack() -> None:
    """Khởi chạy cả Backend FastAPI (:8000) và Frontend Angular (:4200) tương thích đa nền tảng."""
    print("\n" + "=" * 60)
    print("  KHỞI ĐỘNG HỆ THỐNG ViMMRC VOICE Q&A (BACKEND + FRONTEND)")
    print("=" * 60)

    be_cmd = [sys.executable, "-m", "uvicorn", "scripts.api_server:app", "--host", "127.0.0.1", "--port", "8000"]
    fe_dir = PROJECT_ROOT / "web-interface_Luong"

    # Nhận diện lệnh npm theo hệ điều hành
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    print("\n[1/2] Đang khởi động Backend FastAPI (cổng 8000)...")
    if sys.platform == "darwin":
        # Trên macOS: mở qua Terminal tab mới hoặc chạy ngầm
        be_proc = subprocess.Popen(be_cmd, cwd=str(PROJECT_ROOT))
    elif sys.platform == "win32":
        # Trên Windows: tạo cửa sổ mới
        subprocess.Popen(f'start "ViMMRC Backend API (:8000)" {" ".join(be_cmd)}', cwd=str(PROJECT_ROOT), shell=True)
    else:
        be_proc = subprocess.Popen(be_cmd, cwd=str(PROJECT_ROOT))

    print("[2/2] Đang khởi động Frontend Angular Dev Server (cổng 4200)...")
    if sys.platform == "win32":
        subprocess.Popen(f'start "ViMMRC Frontend UI (:4200)" {npm_cmd} start', cwd=str(fe_dir), shell=True)
    else:
        fe_proc = subprocess.Popen([npm_cmd, "start"], cwd=str(fe_dir))

    print("\n[OK] Cả Backend và Frontend đã được gửi lệnh khởi động!")
    print("👉 Mở trình duyệt tại: http://localhost:4200/ (Frontend UI)")
    print("👉 Swagger API Docs tại: http://127.0.0.1:8000/docs (Backend API)")
    print("=" * 60 + "\n")


def interactive_menu() -> None:
    """Menu chọn lệnh tương tác trên terminal."""
    os_name = "macOS" if sys.platform == "darwin" else ("Windows" if sys.platform == "win32" else "Linux")
    test_file = ROOT_DIR / "test_sentence.txt"

    while True:
        print("\n" + "=" * 62)
        print(f"  HỆ THỐNG TỔNG HỢP TIẾNG NÓI MATCHA-TTS [Hệ điều hành: {os_name}]")
        print("=" * 62)
        print(" [1] Đọc câu trắc nghiệm mẫu từ test_sentence.txt (Matcha-TTS)")
        print(" [2] Nhập câu văn bản tiếng Việt bất kỳ để đọc")
        print(" [3] Đọc bằng giọng nơ-ron Edge-TTS Nữ (Hoài My)")
        print(" [4] Đọc bằng giọng nơ-ron Edge-TTS Nam (Nam Minh)")
        print(" [5] Khởi động cả dự án (Backend :8000 + Frontend :4200)")
        print(" [6] Chạy đo đạc Benchmark định lượng (MCD, F0, CER, RTF)")
        print(" [0] Thoát")
        print("=" * 62)

        try:
            choice = input("Chọn tùy chọn [0-6] (Mặc định: 1): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nĐã thoát.")
            break

        if not choice:
            choice = "1"

        if choice == "1":
            run_synthesize(file_path=test_file, engine="matcha")
        elif choice == "2":
            txt = input("\nNhập câu văn bản cần đọc: ").strip()
            if txt:
                run_synthesize(text=txt, engine="matcha")
        elif choice == "3":
            run_synthesize(file_path=test_file, engine="edge", voice="vi-VN-HoaiMyNeural")
        elif choice == "4":
            run_synthesize(file_path=test_file, engine="edge", voice="vi-VN-NamMinhNeural")
        elif choice == "5":
            launch_full_stack()
        elif choice == "6":
            run_benchmark()
        elif choice == "0":
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn từ 0 đến 6.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-platform Task Runner for ViMMRC TTS")
    parser.add_argument("-t", "--text", default=None, help="Văn bản tiếng Việt cần đọc")
    parser.add_argument("-f", "--file", default=None, help="Đường dẫn file .txt chứa văn bản")
    parser.add_argument("-e", "--engine", default="matcha", choices=["matcha", "vits", "edge", "gtts"], help="Engine")
    parser.add_argument("-v", "--voice", default="nu", help="Giọng đọc: nu / nam / vi-VN-HoaiMyNeural / vi-VN-NamMinhNeural")
    parser.add_argument("-o", "--output", default=None, help="Đường dẫn lưu file audio đầu ra")
    parser.add_argument("--rate", default="+0%", help="Tốc độ nói (+10%%, -10%%)")
    parser.add_argument("--no-play", action="store_true", help="Không tự động mở file audio sau khi sinh")
    parser.add_argument("--app", action="store_true", help="Khởi động cả Backend và Frontend Web UI")
    parser.add_argument("--benchmark", action="store_true", help="Chạy đánh giá benchmark")

    args = parser.parse_args()

    if args.app:
        launch_full_stack()
        return

    if args.benchmark:
        run_benchmark()
        return

    # Nếu có tham số text hoặc file -> chạy trực tiếp
    if args.text or args.file:
        run_synthesize(
            text=args.text,
            file_path=args.file,
            engine=args.engine,
            voice=args.voice,
            rate=args.rate,
            output=args.output,
            auto_play=not args.no_play,
        )
        return

    # Nếu không truyền tham số nào -> mở Menu tương tác
    interactive_menu()


if __name__ == "__main__":
    main()

