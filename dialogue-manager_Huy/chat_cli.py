"""Trò chuyện với hệ thống trên terminal (gõ câu hỏi, Enter; 'thoát' để dừng).

    python -X utf8 dialogue-manager_Huy/chat_cli.py                       # kho mẫu, không cần mô hình
    python -X utf8 dialogue-manager_Huy/chat_cli.py --index data/kb_index.json --wiki data/kb_wiki_full \
        --mrc mrc-model_Huy/checkpoints/vit5-combined-cont --tts edge     # hệ thống thật + đọc câu trả lời
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for folder in (HERE, ROOT / "retrieval-model_Huy", ROOT / "mrc-model_Huy", ROOT / "text-to-speech_Duy"):
    sys.path.insert(0, str(folder))

from eval_dialogue import build_system  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index")
    ap.add_argument("--wiki")
    ap.add_argument("--wiki-ratio", type=float, default=0.4)
    ap.add_argument("--reranker")
    ap.add_argument("--mrc")
    ap.add_argument("--tts", choices=["matcha", "vits", "edge", "gtts"], help="đọc câu trả lời thành file audio")
    ap.add_argument("--debug", action="store_true", help="in câu hỏi đã viết lại và đoạn văn dùng")
    args = ap.parse_args()
    dm = build_system(args)
    sid = "cli"
    print("VietRead: Xin chào! Hãy đặt câu hỏi (gõ 'thoát' để dừng, 'mới' để bắt đầu hội thoại mới).")
    while True:
        try:
            text = input("Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text.casefold() in {"thoát", "thoat", "exit", "quit"}:
            break
        if text.casefold() in {"mới", "moi", "reset"}:
            dm.reset(sid)
            print("VietRead: Đã bắt đầu hội thoại mới.")
            continue
        res = dm.respond(text, sid)
        print(f"VietRead: {res['answer']}")
        if args.debug:
            p = res.get("passage") or {}
            print(f"   [{res['kind']}] hiểu là: {res.get('resolved_question')} | đoạn: {p.get('id')}")
        if args.tts:
            from synthesize import synthesize
            print(f"   (audio: {synthesize(text=res['answer'], engine=args.tts, voice='nu')})")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
