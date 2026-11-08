"""So sánh bộ đọc (reader) trên cùng đoạn văn đã truy xuất: ViT5 cục bộ, mô hình trích span, LLM nhỏ.

Bước 1 (--stage passages): truy xuất top-1 một lần cho 220 câu answerable của eval_llm_assist, lưu lại.
Bước 2 (--stage readers): mỗi reader đọc cùng đoạn; token F1 của câu trả lời thô và câu đã soạn (compose_answer),
tách riêng nhóm câu mà đoạn văn chứa đáp án (đo đúng phần reader, không lẫn lỗi truy xuất). Chạy trên CPU.

Dùng: python scripts/eval_readers.py --stage passages
      python scripts/eval_readers.py --stage readers --readers vit5-combined-cont,nguyenvulebinh/vi-mrc-large
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
for folder in ("", "scripts", "retrieval-model_Huy", "mrc-model_Huy", "dialogue-manager_Huy"):
    sys.path.insert(0, str(ROOT / folder))

PASSAGES = ROOT / "reports" / "reader_bench_passages.json"
OUT = ROOT / "reports" / "reader_bench.json"
LLM_PROMPT = ("Đọc đoạn văn và trả lời câu hỏi bằng tiếng Việt. Chỉ ghi cụm từ trả lời ngắn nhất lấy từ đoạn văn, "
              "không giải thích.\n\nĐoạn văn: {p}\n\nCâu hỏi: {q}")


def stage_passages() -> None:
    from eval_llm_assist import answerable_set
    from api_server import get_qa_services
    retriever, _ = get_qa_services()
    rows = []
    for i, it in enumerate(answerable_set(100)):
        hits = retriever.search(it["q"], 1)
        p = hits[0]["passage"] if hits else ""
        rows.append(dict(it, passage=p, gold_in_passage=any(r.casefold() in p.casefold() for r in it["refs"])))
        if i % 20 == 0:
            print(i, flush=True)
    PASSAGES.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved", len(rows), "gold_in_passage", sum(r["gold_in_passage"] for r in rows))


class Extractive:
    def __init__(self, name: str):
        from transformers import pipeline
        self.qa = pipeline("question-answering", model=name, tokenizer=name, device=-1)

    def answer_question(self, q: str, p: str) -> str:
        out = self.qa(question=q, context=p, max_seq_len=512, doc_stride=128, max_answer_len=48)
        return out["answer"].strip() if out else ""


class ChatLLM:
    def __init__(self, name: str):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(name)
        self.device = os.getenv("READER_DEVICE", "cpu")  # cuda chỉ để đo độ chính xác; thời gian/câu khi đó không so được
        self.model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.bfloat16).eval().to(self.device)
        self.torch = torch

    def answer_question(self, q: str, p: str) -> str:
        msgs = [{"role": "user", "content": LLM_PROMPT.format(p=p[:2400], q=q)}]
        ids = self.tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            out = self.model.generate(ids, max_new_tokens=48, do_sample=False)
        return self.tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True).strip().split("\n")[0]


def load_reader(name: str):
    local = ROOT / "mrc-model_Huy" / "checkpoints" / name
    if not Path(name).is_absolute() and local.is_dir():
        from mrc_client import MRCClient
        return MRCClient(local)
    if "qwen" in name.lower() or "phogpt" in name.lower():
        return ChatLLM(name)
    return Extractive(name)


def stage_readers(names: list[str]) -> None:
    from answer_composer import compose_answer
    from eval_hard_and_multiturn import compute_token_f1
    rows = json.loads(PASSAGES.read_text(encoding="utf-8"))
    results = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for name in names:
        t0 = time.time()
        reader = load_reader(name)
        load_s = time.time() - t0
        items, t1 = [], time.time()
        for r in rows:
            try:
                raw = reader.answer_question(r["q"], r["passage"]) if r["passage"] else ""
            except Exception as e:  # một câu lỗi không làm hỏng cả lượt đo
                raw = ""
                print("ERR", name, type(e).__name__, e)
            composed = compose_answer(r["q"], raw, r["passage"]) if raw else ""
            items.append({"src": r["src"], "q": r["q"], "gold_in_passage": r["gold_in_passage"], "raw": raw,
                          "f1_raw": round(max(compute_token_f1(raw, g) for g in r["refs"]), 4),
                          "f1_composed": round(max(compute_token_f1(composed, g) for g in r["refs"]), 4)})
        sec = (time.time() - t1) / len(rows)

        def mean(xs):
            return round(sum(xs) / len(xs), 4) if xs else 0.0
        covered = [i for i in items if i["gold_in_passage"]]
        summary = {"f1_raw": mean([i["f1_raw"] for i in items]), "f1_composed": mean([i["f1_composed"] for i in items]),
                   "f1_raw_gold_in_passage": mean([i["f1_raw"] for i in covered]),
                   "f1_composed_gold_in_passage": mean([i["f1_composed"] for i in covered]),
                   "by_src_composed": {s: mean([i["f1_composed"] for i in items if i["src"] == s])
                                       for s in ("ood", "hard", "test")},
                   "n": len(items), "n_gold_in_passage": len(covered),
                   "seconds_per_q_cpu": round(sec, 2), "load_s": round(load_s, 1)}
        print(name, json.dumps(summary, ensure_ascii=False), flush=True)
        results[name] = {"summary": summary, "items": items}
        OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
        del reader


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["passages", "readers"], required=True)
    ap.add_argument("--readers", default="vit5-combined-cont")
    args = ap.parse_args()
    if args.stage == "passages":
        stage_passages()
    else:
        stage_readers([n.strip() for n in args.readers.split(",") if n.strip()])
