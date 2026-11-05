"""Evaluation of Complex Reasoning (Hard Questions) and Multi-Turn Long Dialogues.

Evaluates:
Part 1: 35 Hard Questions (Multi-hop, Comparative, Cause-and-Effect, Technical Depth)
Part 2: 4 Multi-Turn Long Conversational Scenarios (30 continuous dialogue turns)
Audio: TTS Voice Synthesis & STT Loopback Transcription on representative turns.
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
for folder in ("scripts", "retrieval-model_Huy", "mrc-model_Huy", "dialogue-manager_Huy", "text-to-speech_Duy", "text-to-speech_Duy/src", "speech-to-text_Luong"):
    path_str = str(ROOT / folder)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from intent_router import ConversationalIntentRouter, polish_answer, rerank_hits, remove_accents
from retrieval_client import Retriever
from mrc_client import MRCClient, LexicalBaselineClient
from dialogue import DialogueManager
from synthesize import synthesize as tts_synthesize
import stt_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("eval_hard_multiturn")


def normalize_tokens(text: str) -> list[str]:
    text = remove_accents(text).lower()
    return re.findall(r"\w+", text)


def compute_token_f1(pred: str, ref: str) -> float:
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
    r = list(re.sub(r"\s+", " ", ref.strip().lower()))
    h = list(re.sub(r"\s+", " ", hyp.strip().lower()))
    if not r:
        return 0.0 if not h else 1.0

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
                d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + 1)
    return d[len(r)][len(h)] / len(r)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=ROOT / "data" / "hard_and_multiturn_suite.json")
    parser.add_argument("--index", type=Path, default=ROOT / "data" / "kb_index.json")
    parser.add_argument("--model", type=Path, default=ROOT / "mrc-model_Huy" / "checkpoints" / "vit5-combined-cont")
    parser.add_argument("--tts-engine", default="gtts", choices=["gtts", "matcha", "edge", "vits"])
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "hard_and_multiturn_evaluation.json")
    args = parser.parse_args()

    logger.info("Loading suite from: %s", args.suite)
    with open(args.suite, "r", encoding="utf-8") as f:
        suite = json.load(f)

    hard_questions = suite["hard_questions"]
    multiturn_scenarios = suite["multiturn_scenarios"]

    logger.info("Loading knowledge index from: %s", args.index)
    retriever = Retriever.load(args.index)

    if args.model and args.model.is_dir():
        logger.info("Loading fine-tuned ViT5 reader from: %s", args.model)
        reader = MRCClient(str(args.model), context_strategy="question_chunks")
    else:
        logger.warning("No checkpoint found at %s. Falling back to LexicalBaselineClient.", args.model)
        reader = LexicalBaselineClient()

    dialogue_manager = DialogueManager(retriever, reader)

    # =========================================================================
    # Part 1: Evaluate Hard Questions
    # =========================================================================
    logger.info("--- PART 1: Evaluating %d Hard Questions ---", len(hard_questions))
    hard_results = []
    reasoning_stats = {}
    hard_latencies = []

    for idx, item in enumerate(hard_questions, 1):
        q_id = item["id"]
        category = item["category"]
        reasoning_type = item["reasoning_type"]
        question = item["question"]
        ref_ans = item["reference_answer"]

        t0 = time.perf_counter()
        raw_hits = retriever.search(question, top_k=5)
        reranked = rerank_hits(question, raw_hits, top_k=1)

        if reranked and reranked[0]["score"] > 0:
            top_hit = reranked[0]
            raw_ans = reader.answer_question(question, top_hit["passage"])
            pred_ans = polish_answer(raw_ans, question)
            passage_id = top_hit["id"]
            retrieval_score = top_hit["score"]
        else:
            pred_ans = "Xin lỗi, tôi chưa tìm thấy thông tin phù hợp cho câu hỏi này trong kho tri thức."
            passage_id = None
            retrieval_score = 0.0

        dur_ms = (time.perf_counter() - t0) * 1000
        hard_latencies.append(dur_ms)

        f1 = compute_token_f1(pred_ans, ref_ans)
        is_complete = bool(pred_ans and pred_ans.strip() and pred_ans.strip()[-1] in ".!?")

        rec = {
            "id": q_id,
            "category": category,
            "reasoning_type": reasoning_type,
            "question": question,
            "reference_answer": ref_ans,
            "predicted_answer": pred_ans,
            "passage_id": passage_id,
            "retrieval_score": round(retrieval_score, 2),
            "qa_latency_ms": round(dur_ms, 1),
            "is_complete": is_complete,
            "token_f1": round(f1, 4),
        }
        hard_results.append(rec)

        if reasoning_type not in reasoning_stats:
            reasoning_stats[reasoning_type] = {"count": 0, "complete": 0, "f1_sum": 0.0, "latency_sum": 0.0}
        reasoning_stats[reasoning_type]["count"] += 1
        if is_complete:
            reasoning_stats[reasoning_type]["complete"] += 1
        reasoning_stats[reasoning_type]["f1_sum"] += f1
        reasoning_stats[reasoning_type]["latency_sum"] += dur_ms

    logger.info("Completed Part 1: %d hard questions evaluated.", len(hard_questions))

    # =========================================================================
    # Part 2: Evaluate Multi-Turn Long Dialogues
    # =========================================================================
    logger.info("--- PART 2: Evaluating %d Multi-Turn Scenarios ---", len(multiturn_scenarios))
    scenario_results = []
    total_turns_count = 0
    reformulated_count = 0
    dialogue_latencies = []
    audio_evaluations = []

    for sc_idx, sc in enumerate(multiturn_scenarios, 1):
        sc_id = sc["scenario_id"]
        title = sc["title"]
        domain = sc["domain"]
        turns = sc["turns"]

        sess_id = f"eval_sess_{sc_id}"
        dialogue_manager.reset(sess_id)
        sc_turn_results = []

        logger.info("Running Scenario %d/%d: %s (%d turns)...", sc_idx, len(multiturn_scenarios), title, len(turns))

        for turn_data in turns:
            turn_no = turn_data["turn"]
            user_q = turn_data["question"]
            ref_ans = turn_data["reference_answer"]

            t0 = time.perf_counter()
            chat_res = dialogue_manager.respond(user_q, sess_id)
            chat_res["was_reformulated"] = bool(chat_res.get("rewritten"))
            chat_res["is_conversational"] = chat_res["kind"] in ("smalltalk", "math")
            chat_res["reformulated_query"] = chat_res.get("resolved_question", user_q)
            chat_res["passage_id"] = (chat_res.get("passage") or {}).get("id")
            chat_res["active_topic"] = dialogue_manager.session(sess_id)[1].topic
            turn_dur_ms = (time.perf_counter() - t0) * 1000
            dialogue_latencies.append(turn_dur_ms)
            total_turns_count += 1

            if chat_res["was_reformulated"]:
                reformulated_count += 1

            pred_ans = chat_res["answer"]
            f1 = compute_token_f1(pred_ans, ref_ans)
            is_complete = bool(pred_ans and pred_ans.strip() and pred_ans.strip()[-1] in ".!?")

            turn_rec = {
                "turn": turn_no,
                "question": user_q,
                "reference_answer": ref_ans,
                "predicted_answer": pred_ans,
                "is_conversational": chat_res["is_conversational"],
                "was_reformulated": chat_res["was_reformulated"],
                "reformulated_query": chat_res["reformulated_query"],
                "active_topic": chat_res["active_topic"],
                "passage_id": chat_res["passage_id"],
                "turn_latency_ms": round(turn_dur_ms, 1),
                "is_complete": is_complete,
                "token_f1": round(f1, 4),
            }

            # Run TTS & STT Loopback on selected representative turns (turn 2 and turn 4 of each scenario)
            if turn_no in (2, 4):
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
                    tmp_audio_path = tmp_audio.name
                try:
                    t_tts0 = time.perf_counter()
                    audio_path = tts_synthesize(
                        text=pred_ans,
                        output_path=tmp_audio_path,
                        engine=args.tts_engine,
                        voice="vi-VN-HoaiMyNeural" if args.tts_engine == "edge" else "nu",
                    )
                    tts_dur_ms = (time.perf_counter() - t_tts0) * 1000
                    stt_text = stt_server.transcribe(audio_path)
                    cer = compute_cer(pred_ans, stt_text)

                    turn_rec["tts_ms"] = round(tts_dur_ms, 1)
                    turn_rec["stt_transcription"] = stt_text
                    turn_rec["stt_cer"] = round(cer, 4)

                    audio_evaluations.append({
                        "scenario_id": sc_id,
                        "turn": turn_no,
                        "tts_ms": round(tts_dur_ms, 1),
                        "cer": round(cer, 4),
                        "answer": pred_ans,
                        "transcription": stt_text,
                    })
                except Exception as e:
                    logger.warning("TTS/STT failed for turn %d in %s: %s", turn_no, sc_id, e)
                    turn_rec["tts_error"] = str(e)
                finally:
                    if os.path.exists(tmp_audio_path):
                        try:
                            os.unlink(tmp_audio_path)
                        except OSError:
                            pass

            sc_turn_results.append(turn_rec)

        scenario_results.append({
            "scenario_id": sc_id,
            "title": title,
            "domain": domain,
            "total_turns": len(turns),
            "turns": sc_turn_results,
        })

    # Summary metrics calculation
    hard_total = len(hard_results)
    hard_complete = sum(1 for r in hard_results if r["is_complete"])
    hard_avg_f1 = sum(r["token_f1"] for r in hard_results) / hard_total if hard_total else 0.0
    hard_avg_lat = sum(hard_latencies) / hard_total if hard_total else 0.0

    reasoning_summary = {}
    for r_type, s in reasoning_stats.items():
        c = s["count"]
        reasoning_summary[r_type] = {
            "count": c,
            "completion_rate_pct": round((s["complete"] / c) * 100, 1) if c else 0.0,
            "avg_token_f1": round(s["f1_sum"] / c, 4) if c else 0.0,
            "avg_latency_ms": round(s["latency_sum"] / c, 1) if c else 0.0,
        }

    dialogue_avg_lat = sum(dialogue_latencies) / len(dialogue_latencies) if dialogue_latencies else 0.0
    avg_audio_tts_ms = sum(a["tts_ms"] for a in audio_evaluations) / len(audio_evaluations) if audio_evaluations else 0.0
    avg_audio_cer = sum(a["cer"] for a in audio_evaluations) / len(audio_evaluations) if audio_evaluations else 0.0

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hard_questions_evaluation": {
            "total_questions": hard_total,
            "completion_rate_pct": round((hard_complete / hard_total) * 100, 2),
            "avg_token_f1": round(hard_avg_f1, 4),
            "avg_qa_latency_ms": round(hard_avg_lat, 1),
            "reasoning_type_breakdown": reasoning_summary,
            "items": hard_results,
        },
        "multiturn_dialogue_evaluation": {
            "total_scenarios": len(multiturn_scenarios),
            "total_dialogue_turns": total_turns_count,
            "turns_reformulated_with_context": reformulated_count,
            "avg_turn_latency_ms": round(dialogue_avg_lat, 1),
            "tts_speech_evaluation": {
                "turns_evaluated": len(audio_evaluations),
                "avg_tts_latency_ms": round(avg_audio_tts_ms, 1),
                "avg_cer": round(avg_audio_cer, 4),
                "speech_intelligibility_rate_pct": round((1.0 - min(avg_audio_cer, 1.0)) * 100, 2),
            },
            "scenarios": scenario_results,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logger.info("Report saved to: %s", args.output)

    print("\n" + "=" * 70)
    print("VIMMRC HARD QUESTIONS & MULTI-TURN LONG DIALOGUE EVALUATION SUMMARY")
    print("=" * 70)
    print(f"PART 1: HARD & COMPLEX QUESTIONS ({hard_total} items)")
    print(f" - Completion & Polishing Rate: {(hard_complete / hard_total) * 100:.1f}%")
    print(f" - Average Token F1:            {hard_avg_f1:.4f}")
    print(f" - Average QA Latency:          {hard_avg_lat:.1f} ms")
    for r_type, info in reasoning_summary.items():
        print(f"   * {r_type:20s}: {info['count']:2d} items | F1: {info['avg_token_f1']:.4f} | Latency: {info['avg_latency_ms']:.1f}ms")
    print("-" * 70)
    print(f"PART 2: MULTI-TURN LONG CONVERSATIONS ({len(multiturn_scenarios)} scenarios, {total_turns_count} turns)")
    print(f" - Contextual Query Reformulations: {reformulated_count}/{total_turns_count} turns")
    print(f" - Average Turn Latency:            {dialogue_avg_lat:.1f} ms")
    print(f" - TTS Voice Synthesis Latency:     {avg_audio_tts_ms:.1f} ms")
    print(f" - STT Loopback Intelligibility:    {(1.0 - min(avg_audio_cer, 1.0)) * 100:.1f}% (CER: {avg_audio_cer:.4f})")
    print("=" * 70)


if __name__ == "__main__":
    main()
