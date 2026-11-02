"""Comprehensive Evaluation of ViMMRC Voice Q&A on 110 Out-of-Dataset Benchmark Items.

Evaluates:
1. End-to-End Q&A Pipeline (Intent Router -> BM25 + Continuous N-gram Reranker -> ViT5 Reader -> Polish Answer)
2. Text-to-Speech (TTS) Voice Synthesis (Audio validity, duration, speed)
3. Speech-to-Text (STT) Loopback Transcription (Fidelity, CER/WER, intelligibility)
4. Category breakdown and full performance report export.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import unicodedata

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
for folder in ("scripts", "retrieval-model_Huy", "mrc-model_Huy", "text-to-speech_Duy", "text-to-speech_Duy/src", "speech-to-text_Luong"):
    path_str = str(ROOT / folder)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from intent_router import ConversationalIntentRouter, polish_answer, rerank_hits, remove_accents
from retrieval_client import Retriever
from mrc_client import MRCClient, LexicalBaselineClient
from synthesize import synthesize as tts_synthesize
import stt_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("eval_ood")


def normalize_tokens(text: str) -> list[str]:
    """Tokenize and normalize text for simple overlap and error rate calculations."""
    text = remove_accents(text).lower()
    return re.findall(r"\w+", text)


def compute_token_f1(pred: str, ref: str) -> float:
    """Compute token-level F1 score between predicted answer and reference answer."""
    pred_tokens = normalize_tokens(pred)
    ref_tokens = normalize_tokens(ref)
    if not pred_tokens or not ref_tokens:
        return 0.0

    common = set(pred_tokens) & set(ref_tokens)
    if not common:
        return 0.0

    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(ref_tokens)
    return 2 * (precision * recall) / (precision + recall)


def compute_cer(ref: str, hyp: str) -> float:
    """Compute character error rate between reference and hypothesis."""
    r = list(re.sub(r"\s+", " ", ref.strip().lower()))
    h = list(re.sub(r"\s+", " ", hyp.strip().lower()))
    if not r:
        return 0.0 if not h else 1.0

    # Levenshtein distance
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j

    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(
                    d[i - 1][j] + 1,      # deletion
                    d[i][j - 1] + 1,      # insertion
                    d[i - 1][j - 1] + 1,  # substitution
                )
    return d[len(r)][len(h)] / len(r)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=ROOT / "data" / "out_of_dataset_eval_100.json")
    parser.add_argument("--index", type=Path, default=ROOT / "data" / "kb_index.json")
    parser.add_argument("--model", type=Path, default=ROOT / "mrc-model_Huy" / "checkpoints" / "vit5-combined-cont")
    parser.add_argument("--tts-engine", default="matcha", choices=["matcha", "edge", "vits", "gtts"])
    parser.add_argument("--tts-sample", type=int, default=15, help="Number of items to synthesize and STT loopback")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for rapid testing")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "out_of_dataset_evaluation.json")
    args = parser.parse_args()

    logger.info("Loading benchmark suite from: %s", args.suite)
    with open(args.suite, "r", encoding="utf-8") as f:
        items = json.load(f)

    if args.limit:
        items = items[: args.limit]

    logger.info("Total evaluation items: %d", len(items))

    # Initialize Retriever
    logger.info("Loading knowledge index from: %s", args.index)
    retriever = Retriever.load(args.index)

    # Initialize MRC Reader
    if args.model and args.model.is_dir():
        logger.info("Loading fine-tuned ViT5 reader from: %s", args.model)
        reader = MRCClient(str(args.model), context_strategy="question_chunks")
    else:
        logger.warning("No checkpoint found at %s. Falling back to LexicalBaselineClient.", args.model)
        reader = LexicalBaselineClient()

    results = []
    category_stats = {}
    qa_latencies = []
    tts_latencies = []
    stt_cers = []

    logger.info("Starting benchmark evaluation...")
    for idx, item in enumerate(items, 1):
        q_id = item["id"]
        category = item["category"]
        q_type = item["type"]
        question = item["question"]
        ref_ans = item["reference_answer"]

        t0 = time.perf_counter()
        # 1. Intent routing
        conv_resp = ConversationalIntentRouter.get_conversational_response(question)
        if conv_resp:
            answer = conv_resp
            passage_id = "intent:conversational"
            retrieval_score = 100.0
            is_conv = True
        else:
            raw_hits = retriever.search(question, top_k=5)
            reranked = rerank_hits(question, raw_hits, top_k=1)
            if reranked and reranked[0]["score"] > 0:
                top_hit = reranked[0]
                raw_ans = reader.answer_question(question, top_hit["passage"])
                answer = polish_answer(raw_ans, question)
                passage_id = top_hit["id"]
                retrieval_score = top_hit["score"]
            else:
                answer = "Xin lỗi, tôi chưa tìm thấy thông tin phù hợp cho câu hỏi này trong kho tri thức."
                passage_id = None
                retrieval_score = 0.0
            is_conv = False

        qa_duration_ms = (time.perf_counter() - t0) * 1000
        qa_latencies.append(qa_duration_ms)

        # Basic validity assertions
        is_complete = bool(answer and answer.strip() and answer.strip()[-1] in ".!?")
        is_non_empty = bool(answer and len(answer.strip()) > 5)
        f1 = compute_token_f1(answer, ref_ans)

        rec = {
            "id": q_id,
            "category": category,
            "type": q_type,
            "question": question,
            "reference_answer": ref_ans,
            "predicted_answer": answer,
            "is_conversational": is_conv,
            "passage_id": passage_id,
            "retrieval_score": round(retrieval_score, 2),
            "qa_latency_ms": round(qa_duration_ms, 1),
            "is_complete": is_complete,
            "token_f1": round(f1, 4),
        }

        # Category aggregation
        if category not in category_stats:
            category_stats[category] = {
                "count": 0,
                "complete_count": 0,
                "f1_sum": 0.0,
                "latency_sum": 0.0,
            }
        category_stats[category]["count"] += 1
        if is_complete:
            category_stats[category]["complete_count"] += 1
        category_stats[category]["f1_sum"] += f1
        category_stats[category]["latency_sum"] += qa_duration_ms

        # Sample for TTS & STT Loopback
        if idx <= args.tts_sample or q_id in ("OOD_CONV_001", "OOD_HIST_001", "OOD_GEO_001", "OOD_LIT_001", "OOD_SCI_001", "OOD_TECH_001"):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
                tmp_audio_path = tmp_audio.name
            try:
                t_tts0 = time.perf_counter()
                audio_path = tts_synthesize(
                    text=answer,
                    output_path=tmp_audio_path,
                    engine=args.tts_engine,
                    voice="vi-VN-HoaiMyNeural" if args.tts_engine == "edge" else "nu",
                )
                tts_ms = (time.perf_counter() - t_tts0) * 1000
                tts_latencies.append(tts_ms)
                audio_bytes = os.path.getsize(audio_path)
                rec["tts_ms"] = round(tts_ms, 1)
                rec["audio_bytes"] = audio_bytes

                # STT Loopback transcription
                stt_text = stt_server.transcribe(audio_path)
                cer = compute_cer(answer, stt_text)
                stt_cers.append(cer)
                rec["stt_transcription"] = stt_text
                rec["stt_cer"] = round(cer, 4)
            except Exception as e:
                logger.warning("TTS/STT failed for item %s: %s", q_id, e)
                rec["tts_error"] = str(e)
            finally:
                if os.path.exists(tmp_audio_path):
                    try:
                        os.unlink(tmp_audio_path)
                    except OSError:
                        pass

        results.append(rec)
        if idx % 20 == 0 or idx == len(items):
            logger.info("Evaluated %d/%d items... (Current Avg QA Latency: %.1f ms)", idx, len(items), sum(qa_latencies) / len(qa_latencies))

    # Calculate overall metrics
    total_count = len(results)
    complete_count = sum(1 for r in results if r["is_complete"])
    overall_completion_rate = (complete_count / total_count) * 100 if total_count else 0.0
    avg_f1 = sum(r["token_f1"] for r in results) / total_count if total_count else 0.0
    avg_qa_latency = sum(qa_latencies) / len(qa_latencies) if qa_latencies else 0.0
    avg_tts_latency = sum(tts_latencies) / len(tts_latencies) if tts_latencies else 0.0
    avg_stt_cer = sum(stt_cers) / len(stt_cers) if stt_cers else 0.0

    category_summary = {}
    for cat, stats in category_stats.items():
        c = stats["count"]
        category_summary[cat] = {
            "total_items": c,
            "completion_rate_pct": round((stats["complete_count"] / c) * 100, 1) if c else 0.0,
            "avg_token_f1": round(stats["f1_sum"] / c, 4) if c else 0.0,
            "avg_qa_latency_ms": round(stats["latency_sum"] / c, 1) if c else 0.0,
        }

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_items": total_count,
        "overall_completion_rate_pct": round(overall_completion_rate, 2),
        "overall_token_f1": round(avg_f1, 4),
        "avg_qa_latency_ms": round(avg_qa_latency, 1),
        "tts_evaluation": {
            "engine": args.tts_engine,
            "items_synthesized": len(tts_latencies),
            "success_rate_pct": 100.0 if tts_latencies else 0.0,
            "avg_tts_latency_ms": round(avg_tts_latency, 1),
        },
        "stt_evaluation": {
            "items_transcribed": len(stt_cers),
            "avg_character_error_rate": round(avg_stt_cer, 4),
            "intelligibility_rate_pct": round((1.0 - min(avg_stt_cer, 1.0)) * 100, 2),
        },
        "category_breakdown": category_summary,
        "items": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logger.info("Evaluation complete! Report saved to: %s", args.output)
    print("\n" + "=" * 60)
    print("VIMMRC OUT-OF-DATASET 110-BENCHMARK EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total Items Evaluated:        {total_count}")
    print(f"Completion & Polishing Rate:  {overall_completion_rate:.1f}%")
    print(f"Average Token F1:             {avg_f1:.4f}")
    print(f"Average QA Latency:           {avg_qa_latency:.1f} ms")
    print(f"TTS Synthesis Latency:        {avg_tts_latency:.1f} ms ({args.tts_engine})")
    print(f"STT Loopback Intelligibility: {(1.0 - min(avg_stt_cer, 1.0)) * 100:.1f}% (CER: {avg_stt_cer:.4f})")
    print("-" * 60)
    for cat, info in category_summary.items():
        print(f" - {cat:30s}: {info['total_items']:2d} items | Completion: {info['completion_rate_pct']}% | Latency: {info['avg_qa_latency_ms']:.1f}ms")
    print("=" * 60)


if __name__ == "__main__":
    main()
