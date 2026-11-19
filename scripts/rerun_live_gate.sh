#!/usr/bin/env bash
# Lượt đo CÓ cổng thật (DIALOGUE_MIN_RERANK=1,0), cấu hình triển khai, đáp án đầy đủ. INT8 ~16 phút, FP32 ~50 phút CPU.
# Dùng cho bảng đầu cuối; scripts/simulate_gate.py chỉ phát lại cổng cho câu đơn (câu ghép `multi` có cổng riêng từng vế, lệch tối đa ~1 câu).
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8 TRANSFORMERS_NO_TF=1 OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
export QA_INDEX=data/kb_index.json KB_WIKI=data/kb_wiki_full KB_WIKI_RATIO=0.4
export KB_RERANKER=BAAI/bge-reranker-v2-m3 MRC_CHECKPOINT=mrc-model_Huy/checkpoints/vi-mrc-large
PY=.venv/Scripts/python.exe
KB_RERANKER_INT8=1 $PY scripts/eval_llm_assist.py --configs off --min-rerank 1.0 --out reports/e2e_gate1_int8_main.json
KB_RERANKER_INT8=1 $PY scripts/eval_llm_assist.py --configs off --min-rerank 1.0 --heldout --out reports/e2e_gate1_int8_heldout.json
KB_RERANKER_INT8=0 $PY scripts/eval_llm_assist.py --configs off --min-rerank 1.0 --out reports/e2e_gate1_fp32_main.json
echo DONE_LIVE
