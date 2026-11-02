"""Đánh giá tầng hội thoại trên bộ hội thoại tự viết (eval/conversations.json).

Mặc định chạy offline: kho kiến thức mẫu eval/seed_kb.json + HeuristicReader (không cần
mô hình). Trên máy có dữ liệu/checkpoint thật, trỏ tới kho và reader thật:

    python -X utf8 dialogue-manager_Huy/eval_dialogue.py \
        --index data/kb_index.json --wiki data/kb_wiki_full --reranker BAAI/bge-reranker-v2-m3 \
        --mrc mrc-model_Huy/checkpoints/vit5-combined-cont

--tts-check: chuẩn hóa mọi câu trả lời qua normalizer của TTS, báo câu còn chữ số/ký hiệu
            mà TTS sẽ đọc sai.
--voice ENGINE: vòng giọng nói đầy đủ cho các câu hỏi một lượt: TTS(ENGINE) đọc câu hỏi ->
            Whisper (speech-to-text_Luong) chép lại -> hệ thống trả lời bản chép (cần mô hình).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for folder in (HERE, ROOT / "retrieval-model_Huy", ROOT / "mrc-model_Huy", ROOT / "text-to-speech_Duy" / "src"):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from dialogue import DialogueManager  # noqa: E402
from utterance import fold  # noqa: E402


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def check_turn(answer: str, kind: str, turn: dict) -> list[str]:
    problems = []
    if turn.get("kind") and turn["kind"] != kind:
        problems.append(f"kind={kind}, mong đợi {turn['kind']}")
    a = _norm(answer)
    for group in turn.get("expect", []):
        options = [_norm(o) for o in group.split("|")]
        if not any(o in a for o in options):
            problems.append(f"thiếu '{group}'")
    return problems


def tts_problems(answer: str) -> list[str]:
    from normalizer import normalize_vietnamese_text
    spoken = normalize_vietnamese_text(answer)
    leftovers = re.findall(r"\d+|[%$€£²³°&@#*_=<>/\\|~^]", spoken)
    return [f"TTS còn '{x}'" for x in dict.fromkeys(leftovers)]


def build_system(args):
    if args.index:
        from kb_retriever import load_any
        retriever = load_any(args.index, args.wiki, args.wiki_ratio, args.reranker)
    else:
        from retrieval_client import Retriever
        retriever = Retriever(json.loads((HERE / "eval" / "seed_kb.json").read_text(encoding="utf-8")))
    reader = None
    if args.mrc:
        from mrc_client import MRCClient
        reader = MRCClient(args.mrc)
    return DialogueManager(retriever, reader, seed=0)


def voice_roundtrip(text: str, engine: str, workdir: Path) -> str:
    sys.path.insert(0, str(ROOT / "text-to-speech_Duy"))
    sys.path.insert(0, str(ROOT / "speech-to-text_Luong"))
    from synthesize import synthesize
    import stt_server
    audio = synthesize(text=text, output_path=str(workdir / f"q_{abs(hash(text))}.{'wav' if engine in ('matcha', 'vits') else 'mp3'}"),
                       engine=engine, voice="nu")
    try:
        return stt_server.transcribe(audio)
    finally:
        Path(audio).unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, default=HERE / "eval" / "conversations.json")
    ap.add_argument("--index", help="QA_INDEX: data/kb_index.json hoặc thư mục KB")
    ap.add_argument("--wiki", help="thư mục Wikipedia KB (data/kb_wiki_full)")
    ap.add_argument("--wiki-ratio", type=float, default=0.4)
    ap.add_argument("--reranker", default=None)
    ap.add_argument("--mrc", help="checkpoint ViT5")
    ap.add_argument("--tts-check", action="store_true")
    ap.add_argument("--voice", choices=["matcha", "vits", "edge", "gtts"], help="vòng TTS -> STT cho câu một lượt")
    ap.add_argument("--category", action="append", help="chỉ chạy các nhóm này")
    ap.add_argument("--out", type=Path, help="ghi báo cáo JSON")
    ap.add_argument("-v", "--verbose", action="store_true", help="in mọi lượt, không chỉ lượt sai")
    args = ap.parse_args()

    items = json.loads(args.data.read_text(encoding="utf-8"))["items"]
    if args.category:
        items = [it for it in items if it["category"] in args.category]
    dm = build_system(args)
    workdir = Path(__file__).parent / "eval" / "_voice_tmp"
    if args.voice:
        workdir.mkdir(exist_ok=True)

    per_cat = defaultdict(lambda: [0, 0])
    turns_ok = turns_total = 0
    tts_bad = 0
    records = []
    t0 = time.time()
    for item in items:
        sid = f"eval-{item['id']}"
        dm.reset(sid)
        item_ok = True
        for ti, turn in enumerate(item["turns"]):
            user = turn["user"]
            heard = user
            if args.voice and len(item["turns"]) == 1 and item["category"] not in {"math"}:
                heard = voice_roundtrip(user, args.voice, workdir)
            res = dm.respond(heard, sid, item.get("passage"))
            problems = check_turn(res["answer"], res["kind"], turn)
            if args.tts_check:
                tp = tts_problems(res["answer"])
                tts_bad += bool(tp)
                problems += tp
            ok = not problems
            item_ok &= ok
            turns_ok += ok
            turns_total += 1
            rec = {"id": item["id"], "turn": ti, "category": item["category"], "user": user, "heard": heard,
                   "resolved": res.get("resolved_question"), "kind": res["kind"], "answer": res["answer"],
                   "passage_id": (res.get("passage") or {}).get("id"), "ok": ok, "problems": problems}
            records.append(rec)
            if args.verbose or not ok:
                mark = "OK " if ok else "SAI"
                extra = f" [nghe: {heard}]" if heard != user else ""
                print(f"{mark} {item['id']}#{ti} {user}{extra}\n     -> ({res['kind']}) {res.get('resolved_question')}\n     => {res['answer']}"
                      + ("" if ok else f"\n     !! {'; '.join(problems)}"))
        per_cat[item["category"]][0] += item_ok
        per_cat[item["category"]][1] += 1

    n_items = sum(v[1] for v in per_cat.values())
    n_ok = sum(v[0] for v in per_cat.values())
    print("\n=== Kết quả theo nhóm (một mục đạt khi mọi lượt đạt) ===")
    for cat, (ok, tot) in sorted(per_cat.items()):
        print(f"{cat:14s} {ok:3d}/{tot:<3d} {100 * ok / tot:5.1f}%")
    print(f"{'TỔNG mục':14s} {n_ok:3d}/{n_items:<3d} {100 * n_ok / n_items:5.1f}%")
    print(f"{'TỔNG lượt':14s} {turns_ok:3d}/{turns_total:<3d} {100 * turns_ok / turns_total:5.1f}%")
    if args.tts_check:
        print(f"Câu trả lời TTS còn chữ số/ký hiệu: {tts_bad}/{turns_total}")
    print(f"Thời gian: {time.time() - t0:.1f}s")
    if args.out:
        args.out.write_text(json.dumps({
            "config": {k: (str(v.resolve().relative_to(ROOT)) if isinstance(v, Path) and v.resolve().is_relative_to(ROOT)
                           else str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()},
            "items": n_items, "items_ok": n_ok, "turns": turns_total, "turns_ok": turns_ok,
            "per_category": {c: {"ok": v[0], "total": v[1]} for c, v in per_cat.items()},
            "records": records}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
