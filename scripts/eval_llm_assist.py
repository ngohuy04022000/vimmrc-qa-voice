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

from metrics import best_f1, token_f1_multiset, token_f1_set_noaccent  # noqa: E402
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

# Bộ held-out (viết 2026-11-09, SAU khi đã chọn ngưỡng 1,0 trên UNANSWERABLE ở trên và không xem điểm của chúng):
# câu về dữ liệu cá nhân, thời gian thực, tương lai, ý kiến và lệnh điều khiển; không câu nào Wikipedia trả lời được.
HELDOUT_UNANSWERABLE = [
    "Số dư tài khoản ngân hàng của tôi là bao nhiêu?", "Mật khẩu email của tôi là gì?", "Hôm nay có mưa ở Đà Nẵng không?",
    "Ai sẽ thắng cuộc bầu cử tổng thống Mỹ năm 2040?", "Cổ phiếu nào sẽ tăng giá trong tuần sau?",
    "Phim nào đang đứng đầu phòng vé tuần này?", "Ai đang dẫn đầu giải ngoại hạng Anh hiện nay?",
    "Tỷ lệ lạm phát tháng này là bao nhiêu?", "Bài hát nào đang đứng đầu bảng xếp hạng hôm nay?",
    "Kết quả trận chung kết năm 2041 là gì?", "Tôi bị đau đầu thì nên uống thuốc gì?", "Hôm qua tôi đã ăn gì?",
    "Hãy đặt báo thức lúc sáu giờ sáng.", "Bật đèn phòng khách giúp tôi.", "Tôi có nên chia tay người yêu không?",
    "Thời gian chờ ở bệnh viện Chợ Rẫy lúc này là bao lâu?", "Máy chủ của công ty tôi có đang bị lỗi không?",
    "Chiếc xe của tôi đang đỗ ở đâu?", "Địa chỉ nhà của hàng xóm tôi ở đâu?", "Điểm thi môn Toán của con tôi là bao nhiêu?",
    "Giá vé máy bay đi Đà Lạt ngày mai là bao nhiêu?", "Ai sẽ làm thủ tướng sau nhiệm kỳ tới?",
    "Khi nào công ty tôi trả lương?", "Con mèo nhà tôi tên là gì?", "Tôi đang nghĩ đến con số nào?",
    "Quán cà phê nào gần tôi mở cửa lúc ba giờ sáng?", "Chuyến bay VN123 hạ cánh lúc mấy giờ?",
    "Hãy kể cho tôi nghe bí mật của bạn.", "Tôi nên học ngành nào để giàu nhanh?", "Giá nhà đất Hà Nội tháng sau tăng hay giảm?",
]


def answerable_set(sample: int, offset: int = 0, suites: bool = True) -> list[dict]:
    """suites=False bỏ ood+hard (đã dùng để chọn tham số); offset chọn lát cắt của test đã xáo (seed 7)."""
    items = []
    for name, key in (("out_of_dataset_evaluation", None), ("hard_and_multiturn_evaluation", "hard_questions_evaluation") ) if suites else ():
        data = json.loads((ROOT / "reports" / f"{name}.json").read_text(encoding="utf-8"))
        rows = data[key]["items"] if key else data["items"]
        for r in rows:
            if r.get("type") == "conversation" or r.get("is_conversational") in (True, "True"):
                continue
            items.append({"src": "hard" if key else "ood", "q": r["question"], "refs": [r["reference_answer"]]})
    test = load_examples(ROOT / "data" / "combined" / "test_vimmrc.json")
    random.Random(7).shuffle(test)
    items += [{"src": "test", "q": e["question"], "refs": [e["answer"]]} for e in test[offset:offset + sample]]
    return items


def run(name: str, manager: DialogueManager, ans: list[dict], unans: list[str]) -> dict:
    rows, t0 = [], time.time()
    per_src: dict[str, list[float]] = {}
    refused_ok = 0
    for it in ans:
        r = manager.respond(it["q"], None)
        f1 = best_f1(r["answer"], it["refs"], token_f1_multiset)  # F1 chuẩn (multiset, giữ dấu), max theo tham chiếu
        f1_old = best_f1(r["answer"], it["refs"], token_f1_set_noaccent)  # bản cũ, để đối chiếu báo cáo trước 2026-11-09
        # recall: phần token của đáp án chuẩn có mặt trong câu trả lời; không phạt câu dài như token F1
        ans_toks = set(r["answer"].casefold().split())
        rec = max((sum(t in ans_toks for t in ref.casefold().split()) / max(1, len(ref.split()))) for ref in it["refs"])
        ptxt = ((r.get("passage") or {}).get("text") or "").casefold()
        raw = (r.get("raw_answer") or "").casefold().strip(" .")
        p_toks = set(ptxt.split())
        gold_in_p = max((sum(t in p_toks for t in ref.casefold().split()) / max(1, len(ref.split()))) for ref in it["refs"]) if ptxt else 0.0
        rows.append({"src": it["src"], "q": it["q"], "kind": r["kind"], "f1": round(f1, 4), "f1_set_noaccent": round(f1_old, 4), "recall": round(rec, 4),
                     "n_words": len(r["answer"].split()), "raw_in_cited_passage": bool(raw and raw in ptxt),
                     "gold_recall_in_cited_passage": round(gold_in_p, 4), "source": (r.get("source") or {}).get("label"),
                     "rerank_score": (r.get("passage") or {}).get("score"), "answer": r["answer"][:160], "full_answer": r["answer"], "raw_answer": r.get("raw_answer", "")})
        per_src.setdefault(it["src"], []).append(f1)
    t_ans = time.time() - t0
    false_refuse = sum(r["kind"] == "unknown" for r in rows)
    answered_f1 = [r["f1"] for r in rows if r["kind"] != "unknown"]
    urows = []
    for q in unans:
        r = manager.respond(q, None)
        urows.append({"q": q, "kind": r["kind"], "rerank_score": (r.get("passage") or {}).get("score"), "answer": r["answer"][:120]})
        refused_ok += r["kind"] == "unknown"
    mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else 0.0
    return {
        "name": name,
        "f1_definition": "multiset token F1, giữ dấu, max theo tham chiếu (scripts/metrics.py)",
        "f1_all": mean([r["f1"] for r in rows]),
        "f1_set_noaccent_all": mean([r["f1_set_noaccent"] for r in rows]),
        "f1_by_src": {k: mean(v) for k, v in per_src.items()},
        "f1_when_answered": mean(answered_f1),
        "recall_all": mean([r["recall"] for r in rows]),
        "raw_in_cited_passage": mean([float(r["raw_in_cited_passage"]) for r in rows if r["kind"] in ("qa",)]),
        "gold_recall_in_cited_passage": mean([r["gold_recall_in_cited_passage"] for r in rows if r["kind"] in ("qa",)]),
        "mean_words": mean([r["n_words"] for r in rows if r["kind"] != "unknown"]),
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
    ap.add_argument("--detail", action="store_true", help="chế độ câu dài kèm nguồn (DialogueManager.detail)")
    ap.add_argument("--heldout", action="store_true", help="bộ held-out: test[100:100+sample] + HELDOUT_UNANSWERABLE, không ood/hard")
    ap.add_argument("--min-rerank", type=float, default=None, help="cổng điểm reranker (DialogueManager.min_rerank)")
    args = ap.parse_args()

    retriever, reader = get_qa_services()
    assist = LLMAssist()
    if args.configs != "off" and not assist.available():  # cấu hình 'off' không gọi LLM
        sys.exit(f"Ollama không dùng được ({assist.base}, model {assist.model})")
    ans = answerable_set(args.sample, offset=100, suites=False) if args.heldout else answerable_set(args.sample)
    unans = HELDOUT_UNANSWERABLE if args.heldout else UNANSWERABLE
    print(f"answerable={len(ans)} unanswerable={len(unans)} heldout={args.heldout} model={assist.model}", flush=True)
    cfgs = {"off": dict(assist=None), "gate": dict(assist=assist, assist_verify=False),
            "verify": dict(assist=assist, assist_gate=False), "both": dict(assist=assist)}
    results = []
    for name in args.configs.split(","):
        res = run(name, DialogueManager(retriever, reader, min_rerank=args.min_rerank, detail=args.detail, **cfgs[name]), ans, unans)
        results.append(res)
        print({k: v for k, v in res.items() if k not in ("answerable", "unanswerable")}, flush=True)
    Path(args.out).write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
