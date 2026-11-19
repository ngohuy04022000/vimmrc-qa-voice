# Tái lập số liệu

Mỗi mục: lệnh sinh ra file trong `reports/` và trạng thái. **[chạy lại được]** = lệnh dưới đây đủ để sinh lại;
**[giao thức]** = script có, nhưng lệnh gốc không được lưu nên đây là lệnh suy ra từ STATUS.md và mã nguồn (chưa chạy lại để so);
**[ad-hoc]** = không có script, chỉ có mô tả.

Chạy từ thư mục gốc dự án bằng `.venv\Scripts\python.exe` (PowerShell; trong Git Bash dùng `PYTHONIOENCODING=utf-8`).
CPU trừ khi ghi khác; số giây tuyệt đối phụ thuộc máy.

## 0. Chuẩn bị (không commit data và checkpoint)
```powershell
python mrc-model_Huy\build_combined_dataset.py          # data\combined\{train,dev,test}_vimmrc.json (seed 42)
python retrieval-model_Huy\build_kb.py --wiki --wiki-full --wiki-output data\kb_wiki_full
                                                        # data\kb_index.json (tầng 1) + data\kb_wiki_full (tầng 2, cần mạng:
                                                        # wikimedia/wikipedia 20231101.vi); cờ --wiki-full suy từ tên thư mục [giao thức]
python retrieval-model_Huy\build_dense.py data\kb_wiki_full   # shard_*\embeddings.npy (multilingual-e5-small, ~1,1 GB)
python -m pytest -q -p no:cacheprovider                 # 166 test trên máy dev (~2 phút); checkout sạch: 4 test cần data/dist/checkpoint tự bỏ qua
```
Checkpoint: `mrc-model_Huy\checkpoints\vi-mrc-large` (bộ đọc triển khai), `vit5-combined-cont`;
`speech-to-text_Luong\models\whisper-small-vi-50h-ct2`; `text-to-speech_Duy\checkpoints\matcha_vi.pt`.

## 1. Đầu cuối triển khai (bảng chính của bài báo)  **[chạy lại được]**
```bash
bash scripts/rerun_e2e_gate.sh      # 3 lượt KHÔNG cổng (INT8 chính, INT8 held-out, FP32 chính), ghi điểm reranker từng câu (+ lượt 4 ViT5)
bash scripts/rerun_live_gate.sh     # 3 lượt CÓ cổng thật τ=1,0: INT8 chính, INT8 held-out, FP32 chính (dùng cho bảng đầu cuối)
bash scripts/rerun_vit5.sh          # chỉ lượt ViT5 (bộ đọc dự phòng) không cổng; đã nằm trong rerun_e2e_gate.sh
# thời gian thực tế ngày 2026-11-09 trên máy dự án (CPU, OMP_NUM_THREADS=4): INT8 chính ~16 phút, held-out ~11 phút, FP32 chính ~40–50 phút (tuỳ máy đang rảnh hay không)
python scripts/simulate_gate.py reports/e2e_nogate_int8_main.json --check reports/llm_assist_off_int8_gate1.json --out reports/gate_sim_int8_main.json
python scripts/simulate_gate.py reports/e2e_nogate_int8_heldout.json --heldout --out reports/gate_sim_int8_heldout.json
python scripts/simulate_gate.py reports/e2e_nogate_fp32_main.json --out reports/gate_sim_fp32_main.json
python scripts/bootstrap_ci.py      # reports/bootstrap_ci.json (paired bootstrap 10.000 lần, seed 0)
python scripts/recompute_f1.py      # F1 chuẩn tính lại từ báo cáo cũ (reports/f1_recomputed.json)
```
- Bộ chính: 220 câu trả lời được (ood 85 + hard 35 + test 100, `eval_llm_assist.answerable_set`) và 30 câu không trả lời được
  (`UNANSWERABLE`, viết tay). **Ngưỡng 1,0 và β đã được chọn trên bộ này**, nên số trên bộ này lạc quan.
- Bộ held-out (`--heldout`): 100 câu `test_vimmrc.json` chưa dùng (lát cắt [100:200] của danh sách xáo seed 7) và 30 câu
  `HELDOUT_UNANSWERABLE` viết sau khi đã chọn ngưỡng. Held-out đối với ngưỡng cổng, **không** đối với β (β chọn trên mẫu 500 câu
  seed 0 của `eval_dense.py`, có thể giao với lát cắt này).
- `reports/rerank_confidence_gate.json` là phép mô phỏng ad-hoc ban đầu (không có script); `simulate_gate.py` thay thế nó.
- `llm_assist_off_*.json` cũ: câu trả lời lưu bị cắt ở 160 ký tự (trừ `detail_v3`), F1 tính lại từ chúng sai số cỡ ±0,001.

## 2. F1: một định nghĩa duy nhất
`scripts/metrics.py`: `token_f1_multiset` (chuẩn SQuAD, giữ dấu tiếng Việt, đếm lặp) là thước đo chính; `token_f1_set_noaccent`
là bản cũ của `eval_hard_and_multiturn` / `eval_out_of_dataset` (tập hợp, bỏ dấu) chỉ để đối chiếu. Báo cáo trước 2026-11-09 trong
`reports/llm_assist_*.json`, `reader_bench.json`, `hard_and_multiturn_evaluation.json`, `out_of_dataset_evaluation.json`,
`stt_fix_ab.json` dùng bản cũ; `reader_gold_*.json`, `*routing*`, `dense_*` dùng bản multiset từ đầu.

## 3. Các phép đo khác
| File | Lệnh | Trạng thái |
|---|---|---|
| `reader_gold_<tên>.json` | `python scripts\eval_reader_gold.py --checkpoint mrc-model_Huy\checkpoints\<tên> --out reports\reader_gold_<tên>.json` | chạy lại được |
| `reader_bench*.json` | `python scripts\eval_readers.py --stage passages` rồi `--stage readers --readers <danh sách>` | giao thức |
| `*routing_e2e*.json` (tier, β) | `$env:RERANK_DEVICE="cuda"; python scripts\eval_dense.py --n 500 [--offset 500] --reranker BAAI/bge-reranker-v2-m3 --output reports\<tên>.json` | giao thức |
| `kb_threshold*.json` | `python scripts\tune_kb_threshold.py --wiki data\kb_wiki_full --output reports\kb_threshold_full.json` | giao thức |
| `tier_ratio_dev.json` | `python scripts\tune_tier_ratio.py` | chạy lại được |
| `e2e_{dev,test}_kb_*.json` (ViT5) | `python scripts\eval_e2e.py --split dev --wiki data\kb_wiki_full --output reports\e2e_dev_kb_vit5-combined-cont.json` | giao thức; harness của thời ViT5, mặc định pool 10 / tỉ lệ 0,5 |
| `reader_signals.json`, `reader_signal_analysis.json` | `collect_reader_signals.py`, `tune_reader_signals.py` (chỉ in ra màn hình; `reader_signal_analysis.json` không có script ghi) | một phần |
| `stt_int8_infore1*.json` | `python scripts\eval_stt_int8.py --dataset doof-ferb/infore1_25hours --n 135 --out reports\stt_int8_infore1.json` (và `--model` Whisper-small gốc) | giao thức |
| `speech-to-text_Luong\training\results_{20,50}h.json` | `python speech-to-text_Luong\training\evaluate_models.py` | cần VietSpeech (dataset có điều kiện truy cập) |
| `latency_docker*.json`, `ood_latency_docker.json` | `python scripts\measure_latency.py --out ...`, `python scripts\measure_ood_latency.py` (cần container chạy ở cổng 8090) | chạy lại được |
| `reranker_speed.json` | không có script (đo xoay vòng FP32/INT8 trên 100 câu test) | ad-hoc |
| Số TTS (CER 0,8 %, log-F0 0,88, MCD 3,05 dB, RTF 0,53–0,64) | bảng ở `text-to-speech_Duy\docs\tts.md` (dòng 202–208), sinh bởi `python text-to-speech_Duy\scripts\benchmark.py`; CER qua PhoWhisper-base. Lưu ý trong `tts.md`: giọng tham chiếu cùng người nói với dữ liệu huấn luyện (InfoRe1), nên MCD/F0 gồm cả khác biệt chất giọng và CER chưa phải đo độc lập người nói. Không có file JSON trong `reports/` | giao thức |
| `human_eval_sheet.csv` | `python scripts\make_human_eval_sheet.py --per-src 20 --seed 0`; quy trình `docs\human_eval_protocol.md` | chưa có người chấm |

## 4. Giới hạn đã biết của phép đo
- Bộ 30 câu "không trả lời được" do nhóm viết; một vài câu Wikipedia trả lời được (xem STATUS.md). Không có nhãn độc lập.
- Tập A của tier là câu có đoạn đúng trong KB (kho đóng); 459/466 bài của `test_vimmrc.json` nằm trong `kb_index.json` theo thiết kế.
- Một số chênh lệch nhỏ không có ý nghĩa thống kê: xem `reports/bootstrap_ci.json` trước khi diễn giải.

## 5. Docker và gói nén
- `docker compose up -d --build` (cổng 127.0.0.1:8090). Image chạy bằng người dùng không root (uid 10001); `data/` gắn chỉ đọc, `outputs/` ghi được. Bảo mật tuỳ chọn (API_KEY, CORS_ORIGINS, RATE_LIMIT_PER_MIN) mặc định tắt, xem `docker-compose.yml`.
- Gói nén `vimmrc-qa-voice.zip` (thư mục mẹ) là ảnh chụp ổ đĩa kèm `.git/`; loại `checkpoint-*/`, `Video demo/`, `.venv/`, `node_modules/`. Hướng dẫn giải nén và SHA-256 nằm ở `ViMMRC_Tai_Lap_Va_Git.md` (thư mục mẹ).
