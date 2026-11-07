"""Đo độ trễ từng chặng của hệ thống đang chạy (mặc định Docker ở cổng 8090): /api/ask (truy xuất + xếp hạng lại + đọc hiểu + soạn câu)
và /api/tts. STT (/api/stt) không đo ở đây. Câu hỏi đầu tiên là khởi động nguội nên bị loại khỏi thống kê.

Dùng: python scripts/measure_latency.py [--base http://localhost:8090] [--rounds 2] [--out reports/latency_docker.json]
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
import uuid
from pathlib import Path

import requests

QUESTIONS = [
    "Thủ đô của Nhật Bản là gì?", "Ai phát minh ra bóng đèn sợi đốt?", "Vì sao bầu trời có màu xanh?",
    "Fansipan cao bao nhiêu mét?", "Hành tinh nào gần Mặt Trời nhất?", "Truyện Kiều do ai sáng tác?",
    "Sông nào dài nhất Việt Nam?", "Trận Bạch Đằng năm 938 do ai chỉ huy?", "Công thức hóa học của nước là gì?",
    "Quang Trung đại phá quân Thanh vào năm nào?", "Vịnh Hạ Long nằm ở tỉnh nào?", "Whisper là mô hình của công ty nào?",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8090")
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    health = requests.get(f"{args.base}/api/health", timeout=30).json()
    ask_s, tts_s, rows = [], [], []
    for r in range(args.rounds):
        for q in QUESTIONS:
            t = time.perf_counter()
            resp = requests.post(f"{args.base}/api/ask", json={"question": q, "session_id": uuid.uuid4().hex}, timeout=600).json()
            dt_ask = time.perf_counter() - t
            answer = resp.get("answer", "")
            t = time.perf_counter()
            requests.post(f"{args.base}/api/tts", json={"text": answer}, timeout=600)
            dt_tts = time.perf_counter() - t
            rows.append({"q": q, "kind": resp.get("kind"), "ask_s": round(dt_ask, 2), "tts_s": round(dt_tts, 2)})
            if r or q != QUESTIONS[0]:  # bỏ câu đầu: khởi động nguội
                ask_s.append(dt_ask)
                tts_s.append(dt_tts)
            print(rows[-1], flush=True)
    summary = {"health": health, "n": len(ask_s),
               "ask_median_s": round(statistics.median(ask_s), 2), "ask_mean_s": round(statistics.mean(ask_s), 2),
               "tts_median_s": round(statistics.median(tts_s), 2), "tts_mean_s": round(statistics.mean(tts_s), 2)}
    print(json.dumps(summary, ensure_ascii=False))
    if args.out:
        args.out.write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
