# Đối chiếu số liệu slide với nguồn

Tự động bởi `verify_deck.py`: tính chuỗi kỳ vọng từ file nguồn rồi tìm trong slide/ghi chú. 38/38 khớp; số cũ còn sót: không.

| Slide | Điều khẳng định | Giá trị từ nguồn | Nguồn | Kết quả |
|---|---|---|---|---|
| 2 | Recall@5 BM25 hai tầng, test | 85,9% | e2e_test_kb_*.json | ĐÚNG |
| 6 | Recall@1 test | 71,1% | e2e_test_kb_*.json | ĐÚNG |
| 6 | Số câu test truy xuất | 2.545 | e2e_test_kb_*.json | ĐÚNG |
| 2 | Token F1 ViT5 | 66,55% | test_metrics.json | ĐÚNG |
| 2 | EM ViT5 | 41,05% | test_metrics.json | ĐÚNG |
| 6 | Số câu test MRC | 2.716 | data/combined/test_vimmrc.json | ĐÚNG |
| 3 | Tổng số câu huấn luyện | 27.164 | data/combined/*.json | ĐÚNG |
| 3 | Chia train/dev/test | 21.733 / 2.715 / 2.716 | data/combined/*.json | ĐÚNG |
| 3 | Toàn chuỗi F1 | 53,9 | e2e_test_kb_*.json | ĐÚNG |
| 6 | Reader đoạn đúng F1 | 68,6 | e2e_test_kb_*.json | ĐÚNG |
| 6 | Toàn chuỗi F1 (ghi chú) | 53,9 | e2e_test_kb_*.json | ĐÚNG |
| 3 | F1 câu mở trước | 15,4 | rerank_routing_e2e.json | ĐÚNG |
| 3 | F1 câu mở sau reranker | 24,3 | rerank_routing_e2e.json | ĐÚNG |
| 6 | Chênh F1 câu mở | +8,9 | rerank_routing_e2e.json | ĐÚNG |
| 6 | F1 câu trong kho trước | 58,0 | rerank_routing_e2e.json | ĐÚNG |
| 6 | F1 câu trong kho sau | 60,7 | rerank_routing_e2e.json | ĐÚNG |
| 3 | Số đoạn kho chọn lọc | 5.879 | data/kb_index.json | ĐÚNG |
| 3 | Số đoạn Wikipedia (1,48 triệu) | 1,48 triệu | data/kb_wiki_full/*/passages.jsonl | ĐÚNG |
| 7 | Recall@1 dev BM25 cũ | 71,45 | lexical_benchmark.json | ĐÚNG |
| 7 | Recall@1 dev đã chọn | 77,48 | lexical_benchmark.json | ĐÚNG |
| 7 | Recall@1 train kém nhất | 44,1 | lexical_benchmark.json | ĐÚNG |
| 7 | Recall@1 train đã chọn | 64,1 | lexical_benchmark.json | ĐÚNG |
| 4 | Dev R@5 chênh | +2,83 | lexical_benchmark.json (86,52 − 83,69) | ĐÚNG |
| 5 | LLM-judge LLM 9B | 54,0 | llm_generate_judge_test.json | ĐÚNG |
| 5 | EM LLM 9B | 32,0 | llm_generate_judge_test.json | ĐÚNG |
| 5 | F1 LLM 9B | 61,7 | llm_generate_judge_test.json | ĐÚNG |
| 2 | WER Whisper gốc | 36,76% | speech-to-text_Luong/README.md | ĐÚNG |
| 2 | WER LoRA 50h | 13,77 | speech-to-text_Luong/README.md | ĐÚNG |
| 6 | WER LoRA 20h | 15,2 | speech-to-text_Luong/README.md | ĐÚNG |
| 6 | Giảm WER tương đối | 62,5% | tính từ WER | ĐÚNG |
| 6 | Số mẫu test STT | 1.802 | speech-to-text_Luong/README.md | ĐÚNG |
| 2 | TTS CER Matcha (docx Duy) | 0,8% | Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx | ĐÚNG |
| 2 | TTS RTF 20 bước (docx Duy) | RTF 0,64 | Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx | ĐÚNG |
| 6 | log-F0 Matcha (docx Duy) | log-F0 0,88 | Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx | ĐÚNG |
| 6 | CER VITS (docx Duy, dữ liệu biểu đồ) | 4,7 | Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx | ĐÚNG |
| 6 | MCD Matcha (docx Duy) | 3,05 dB | Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx | ĐÚNG |
| 8 | Số test tự động | 124 | pytest --collect-only | ĐÚNG |
| 9 | Số test tự động | 124 | pytest --collect-only | ĐÚNG |

## Chưa đối chiếu được (không có nguồn trong repo, hoặc nguồn mâu thuẫn)

- **TTS**: đối chiếu với số trong `Duy_1_TT15-20p_Bao_Cao_Matcha_TTS.docx` (Matcha 20 bước, CER 0,8%, log-F0 0,88, MCD 3,05, RTF 0,64; VITS CER 4,7%). Docx không có tệp đo kèm trong repo nên chỉ đối chiếu được với chính docx.
- Độ trễ ~3 s / ~6 s / 1,4 s / 1,3 s, tổng ~12 s (tắt reranker ~6 s): chỉ có trong `STATUS.md` (đo trên Docker CPU 4 luồng), không có tệp báo cáo.
- ViT5 + LLM chấm theo ý nghĩa (61,0 / 50,0): chỉ có trong `STATUS.md`; `llm_eval.py` không lưu kết quả thành tệp.
- 'Lazy loading ~0,45 s' (STT) trên slide: chưa có nguồn tệp.
- Câu 'Tinh chỉnh BM25: 44,1% → 64,1%' trên slide 7 là tập train 800 câu; dev là 71,45% → 77,48% (đã ghi cả hai).
