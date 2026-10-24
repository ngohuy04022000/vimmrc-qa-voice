"""So sánh 2 hướng dùng LLM (Ollama local) để cải thiện độ chính xác MRC tự luận:

A. --mode judge   : chấm lại dự đoán của ViT5 (checkpoint đã fine-tune) bằng LLM
                     theo khớp ý nghĩa (semantic match), thay cho so khớp ký tự
                     tuyệt đối (Exact Match) — EM ký tự không thể cao với câu trả
                     lời dài, diễn giải khác cách nhưng đúng ý.
B. --mode generate : bỏ ViT5, dùng LLM sinh câu trả lời trực tiếp từ (passage,
                     câu hỏi), rồi chấm bằng cùng judge để so sánh công bằng.

Chạy (cần Ollama server chạy local, xem OLLAMA_MODEL):
    python llm_eval.py --mode judge --split test --n 200
    python llm_eval.py --mode generate --split test --n 200
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

from mrc_data import load_examples

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ornith-1.5:9b")


def ollama_generate(prompt: str, *, max_tokens: int = 200, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            resp = requests.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                      "options": {"temperature": 0, "num_predict": max_tokens}},
                timeout=180,
            )
            resp.raise_for_status()
            return resp.json()["response"].strip()
        except (requests.RequestException, KeyError) as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"Ollama request failed after {retries} tries: {exc}") from exc
            time.sleep(2 * (attempt + 1))
    raise AssertionError("unreachable")


def extract_final_answer(reply: str) -> str:
    """Model này luôn "nghĩ" (chain-of-thought) trước khi trả lời, đóng khung bằng
    </think>; nếu thiếu thẻ đóng (bị cắt do max_tokens quá ngắn), coi toàn bộ phần
    trước </think> là rác và trả chuỗi rỗng — một câu trả lời rỗng còn đúng hơn
    một đoạn suy luận tiếng Anh bị tính nhầm là câu trả lời tiếng Việt."""
    if "</think>" in reply:
        return reply.rsplit("</think>", 1)[1].strip()
    return ""


JUDGE_PROMPT = """Bạn là giám khảo chấm câu trả lời đọc hiểu văn bản tiếng Việt.
Câu hỏi: {question}
Đáp án chuẩn: {gold}
Câu trả lời của học sinh: {prediction}

Câu trả lời của học sinh có đúng về Ý NGHĨA so với đáp án chuẩn không? Diễn đạt
khác, viết tắt, thiếu/thừa vài từ không quan trọng vẫn tính là ĐÚNG nếu ý chính
khớp. Chỉ tính SAI nếu ý nghĩa thực sự khác hoặc trả lời nhầm nội dung khác.

Không giải thích. Dòng cuối cùng của câu trả lời PHẢI là đúng một từ: DUNG hoặc SAI."""


def judge_matches(question: str, gold: str, prediction: str) -> bool:
    if not prediction.strip():
        return False
    # Model có thể "nghĩ" dài dòng trước khi kết luận; num_predict đủ lớn để nó
    # kết luận xong, rồi đọc kết luận DUNG/SAI xuất hiện SAU CÙNG trong chuỗi
    # (không phải token đầu) để không bắt nhầm lúc model mới liệt kê đề bài.
    reply = ollama_generate(JUDGE_PROMPT.format(question=question, gold=gold, prediction=prediction),
                            max_tokens=200)
    matches = list(re.finditer(r"\b(DUNG|SAI)\b", reply.upper()))
    if not matches:
        return False
    return matches[-1].group(1) == "DUNG"


GENERATE_PROMPT = """Đọc đoạn văn sau và trả lời câu hỏi bằng một câu ngắn gọn,
trích hoặc diễn giải trực tiếp từ đoạn văn. Không giải thích thêm, không lặp lại
câu hỏi, chỉ đưa ra câu trả lời.

Đoạn văn:
{passage}

Câu hỏi: {question}

Trả lời:"""


def llm_answer(question: str, passage: str) -> str:
    reply = ollama_generate(GENERATE_PROMPT.format(passage=passage, question=question), max_tokens=400)
    return extract_final_answer(reply)


def run_judge_on_predictions(examples: list[dict], predictions: list[str]) -> dict:
    correct = 0
    details = []
    for row, pred in zip(examples, predictions):
        ok = judge_matches(row["question"], row["answer"], pred)
        correct += ok
        details.append({"question": row["question"], "gold": row["answer"], "prediction": pred, "llm_judge_correct": ok})
    return {"llm_judge_accuracy": correct / len(examples), "n": len(examples), "details": details}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["judge", "generate"], required=True)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "combined")
    parser.add_argument("--split", default="test")
    parser.add_argument("--n", type=int, default=200, help="Số câu hỏi lấy mẫu (toàn bộ test tốn nhiều giờ với LLM local)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--checkpoint", type=Path, default=Path(__file__).resolve().parent / "checkpoints" / "vit5-combined",
                        help="Checkpoint ViT5 để sinh dự đoán, chỉ dùng ở --mode judge")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    examples = load_examples(args.data_dir / f"{args.split}_vimmrc.json")
    import random
    random.Random(args.seed).shuffle(examples)
    examples = examples[:args.n]
    print(f"Đánh giá {len(examples)} câu hỏi ({args.mode}) với model Ollama {OLLAMA_MODEL}")

    if args.mode == "judge":
        from mrc_client import MRCClient
        client = MRCClient(args.checkpoint)
        predictions = [client.answer_question(row["question"], row["passage"]) for row in examples]
        label = "vit5_judge"
    else:
        predictions = [llm_answer(row["question"], row["passage"]) for row in examples]
        label = "llm_generate_judge"

    result = run_judge_on_predictions(examples, predictions)
    from mrc_data import evaluate_predictions
    char_metrics = evaluate_predictions(predictions, examples)
    result["char_level_metrics"] = char_metrics
    print(f"{label}: LLM-judge accuracy = {result['llm_judge_accuracy']:.4f} "
          f"(EM ký tự = {char_metrics['exact_match']:.4f}, token F1 = {char_metrics['token_f1']:.4f})")

    out_path = args.out or (Path(__file__).resolve().parent / f"{label}_{args.split}.json")
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Chi tiết ghi tại {out_path}")


if __name__ == "__main__":
    main()
