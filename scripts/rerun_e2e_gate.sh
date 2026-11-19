#!/usr/bin/env bash
# Chạy lại phép đo đầu cuối KHÔNG cổng (để ghi điểm reranker từng câu) rồi mô phỏng mọi ngưỡng bằng scripts/simulate_gate.py.
# Cấu hình khớp docker-compose.yml (bộ đọc vi-mrc-large, KB 2 tầng, tỉ lệ 0,4, reranker bge-reranker-v2-m3). ~90 phút CPU.
#   1) bộ chính 220+30 câu, INT8 (mặc định triển khai)   -> reports/e2e_nogate_int8_main.json
#   2) bộ held-out 100+30 câu mới, INT8                  -> reports/e2e_nogate_int8_heldout.json
#   3) bộ chính, FP32 (KB_RERANKER_INT8=0)               -> reports/e2e_nogate_fp32_main.json
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8 TRANSFORMERS_NO_TF=1 OMP_NUM_THREADS=${OMP_NUM_THREADS:-4}
export QA_INDEX=data/kb_index.json KB_WIKI=data/kb_wiki_full KB_WIKI_RATIO=0.4
export KB_RERANKER=BAAI/bge-reranker-v2-m3 MRC_CHECKPOINT=mrc-model_Huy/checkpoints/vi-mrc-large
PY=.venv/Scripts/python.exe
KB_RERANKER_INT8=1 $PY scripts/eval_llm_assist.py --configs off --out reports/e2e_nogate_int8_main.json
KB_RERANKER_INT8=1 $PY scripts/eval_llm_assist.py --configs off --heldout --out reports/e2e_nogate_int8_heldout.json
KB_RERANKER_INT8=0 $PY scripts/eval_llm_assist.py --configs off --out reports/e2e_nogate_fp32_main.json
echo DONE_MAIN
# 4) bộ đọc ViT5 (bản dự phòng) để so với bộ đọc span trên cùng mã và cùng định nghĩa F1
MRC_CHECKPOINT=mrc-model_Huy/checkpoints/vit5-combined-cont KB_RERANKER_INT8=0 $PY scripts/eval_llm_assist.py --configs off --out reports/e2e_nogate_vit5_fp32_main.json
echo DONE_VIT5
