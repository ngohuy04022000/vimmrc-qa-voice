"""A/B: DialogueManager có / không có LLM (Ollama) kiểm tra đoạn và đáp án.

Ba nhóm câu hỏi, cùng một retriever + ViT5 cho mọi cấu hình:
  - answerable: 85 câu ngoài tập huấn luyện + 35 câu khó (reports/*.json) + N câu mẫu từ tập test
  - unanswerable: câu ngoài kho tri thức; đúng khi hệ thống từ chối (kind == "unknown")
Chỉ số: token F1 trên câu trả lời được, tỷ lệ từ chối nhầm, tỷ lệ từ chối đúng, độ trễ.

Dùng: python scripts/eval_llm_assist.py [--sample 100] [--out reports/llm_assist_ab.json]
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
for folder in ("", "scripts", "retrieval-model_Huy", "mrc-model_Huy", "dialogue-manager_Huy"):
    sys.path.insert(0, str(ROOT / folder))

from eval_hard_and_multiturn import compute_token_f1  # noqa: E402
from llm_assist import LLMAssist  # noqa: E402
from mrc_data import load_examples  # noqa: E402
from api_server import get_qa_services  # noqa: E402
from dialogue import DialogueManager  # noqa: E402

UNANSWERABLE = [
    "Giá vàng hôm nay là bao nhiêu?", "Thời tiết Hà Nội ngày mai thế nào?", "Tỷ số trận bóng đá tối qua là bao nhiêu?",
    "Cách nấu món phở bò ngon nhất là gì?", "Giá cổ phiếu Vinamilk hiện nay là bao nhiêu?",
    "Iphone 17 có những tính năng gì?", "Hôm nay là thứ mấy trong tuần?", "Ai là người giàu nhất hành tinh năm nay?",
    "Lịch chiếu phim rạp CGV tối nay thế nào?", "Làm sao để sửa lỗi màn hình xanh trên Windows?",
    "Bitcoin đang giao dịch ở mức giá nào?", "Kết quả xổ số miền Bắc hôm nay là gì?",
    "Mật khẩu wifi nhà tôi là gì?", "Tôi nên mua laptop hãng nào?", "Chiều cao của tháp Eiffel là bao nhiêu mét?",
    "Ai vô địch World Cup 2030?", "Công thức hóa học của axit sunfuric là gì?", "Sao Hỏa có bao nhiêu mặt trăng?",
    "Giá xăng RON 95 hôm nay là bao nhiêu?", "Tên con chó của thủ tướng là gì?", "Giải Nobel Hòa bình năm ngoái trao cho ai?",
    "Chạy thử mã Python này giúp tôi: print('hi')", "Dịch câu Hello world sang tiếng Pháp.", "Bạn thích màu gì nhất?",
    "Địa chỉ nhà hàng ngon gần đây là ở đâu?", "Điểm chuẩn đại học Bách khoa năm nay là bao nhiêu?",
    "Số điện thoại của công an quận 1 là gì?", "Tỷ giá đô la so với đồng hôm nay?", "Ca sĩ nào hát bài Hãy trao cho anh?",
    "Phiên bản Python mới nhất hiện nay là gì?",
]


def answerable_set(sample: int) -> list[dict]:
    items = []
    for name, key in (("out_of_dataset_evaluation", None), ("hard_and_multiturn_evaluation", "hard_questions_evaluation")):
        data = json.loads((ROOT / "reports" / f"{name}.json").read_text(encoding="utf-8"))
        rows = data[key]["items"] if key else data["items"]
        for r in rows:
            if r.get("type") == "conversation" or r.get("is_conversational") in (True, "True"):
                continue
            items.append({"src": "hard" if key else "ood", "q": r["question"], "refs": [r["reference_answer"]]})
    test = load_examples(ROOT / "data" / "combined" / "test_vimmrc.json")
    random.Random(7).shuffle(test)
    items += [{"src": "test", "q": e["question"], "refs": [e["answer"]]} for e in test[:sample]]
    return items


def run(name: str, manager: DialogueManager, ans: list[dict], unans: list[str]) -> dict:
    rows, t0 = [], time.time()
    per_src: dict[str, list[float]] = {}
    refused_ok = 0
    for it in ans:
        r = manager.respond(it["q"], None)
        f1 = max(compute_token_f1(r["answer"], ref) for ref in it["refs"])
        rows.append({"src": it["src"], "q": it["q"], "kind": r["kind"], "f1": round(f1, 4), "answer": r["answer"][:160]})
        per_src.setdefault(it["src"], []).append(f1)
    t_ans = time.time() - t0
    false_refuse = sum(r["kind"] == "unknown" for r in rows)
    answered_f1 = [r["f1"] for r in rows if r["kind"] != "unknown"]
    urows = []
    for q in unans:
        r = manager.respond(q, None)
        urows.append({"q": q, "kind": r["kind"], "answer": r["answer"][:120]})
        refused_ok += r["kind"] == "unknown"
    mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else 0.0
    return {
        "name": name,
        "f1_all": mean([r["f1"] for r in rows]),
        "f1_by_src": {k: mean(v) for k, v in per_src.items()},
        "f1_when_answered": mean(answered_f1),
        "false_refusal": f"{false_refuse}/{len(rows)}",
        "correct_refusal": f"{refused_ok}/{len(unans)}",
        "seconds_per_answerable": round(t_ans / len(ans), 2),
        "answerable": rows, "unanswerable": urows,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=100)
    ap.add_argument("--configs", default="off,gate,verify,both")
    ap.add_argument("--out", default=str(ROOT / "reports" / "llm_assist_ab.json"))
    ap.add_argument("--min-rerank", type=float, default=None, help="cổng điểm reranker (DialogueManager.min_rerank)")
    args = ap.parse_args()

    retriever, reader = get_qa_services()
    assist = LLMAssist()
    if not assist.available():
        sys.exit(f"Ollama không dùng được ({assist.base}, model {assist.model})")
    ans = answerable_set(args.sample)
    print(f"answerable={len(ans)} unanswerable={len(UNANSWERABLE)} model={assist.model}", flush=True)
    cfgs = {"off": dict(assist=None), "gate": dict(assist=assist, assist_verify=False),
            "verify": dict(assist=assist, assist_gate=False), "both": dict(assist=assist)}
    results = []
    for name in args.configs.split(","):
        res = run(name, DialogueManager(retriever, reader, min_rerank=args.min_rerank, **cfgs[name]), ans, UNANSWERABLE)
        results.append(res)
        print({k: v for k, v in res.items() if k not in ("answerable", "unanswerable")}, flush=True)
    Path(args.out).write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
