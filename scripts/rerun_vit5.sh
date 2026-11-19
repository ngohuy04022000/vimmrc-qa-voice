#!/usr/bin/env bash
# Chỉ lượt 4 của rerun_e2e_gate.sh (ViT5, FP32, không cổng, bộ chính). ~35 phút CPU.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8 TRANSFORMERS_NO_TF=1 OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
export QA_INDEX=data/kb_index.json KB_WIKI=data/kb_wiki_full KB_WIKI_RATIO=0.4 KB_RERANKER=BAAI/bge-reranker-v2-m3
MRC_CHECKPOINT=mrc-model_Huy/checkpoints/vit5-combined-cont KB_RERANKER_INT8=0 .venv/Scripts/python.exe scripts/eval_llm_assist.py --configs off --out reports/e2e_nogate_vit5_fp32_main.json
echo DONE_VIT5
