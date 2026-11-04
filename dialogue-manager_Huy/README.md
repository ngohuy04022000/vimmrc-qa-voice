# dialogue-manager_Huy — tầng hội thoại

Nằm giữa STT và retrieval/MRC. Mục tiêu: hệ thống trả lời được câu nói tự nhiên **không có trong
bộ dữ liệu** — câu xã giao, câu hỏi nối tiếp nhiều lượt, câu hỏi phức tạp (so sánh, câu ghép,
đúng/sai, tại sao/như thế nào) — và luôn trả lời bằng **câu trọn vẹn** để TTS đọc tự nhiên.

Không thêm thư viện nào: chỉ regex và heuristic, dùng chung hợp đồng có sẵn
`retriever.search(q, top_k)` và `reader.answer_question(q, passage)`, nên chạy được cả với
BM25 + reranker + ViT5 thật lẫn bản offline không cần mô hình.

## Luồng một lượt nói

```
câu nói (STT/gõ)
  └─ utterance.clean_utterance   bỏ "ừm", "cho mình hỏi là", "vậy bạn", "... không" bao ngoài
  ├─ smalltalk.detect_intent      chào, cảm ơn, bạn là ai, giờ/ngày, kể chuyện cười, nhắc lại,
  │                               "giải thích rõ hơn", "tôi tên là ..." -> trả lời ngay
  ├─ smalltalk.try_arithmetic     "12 nhân 12 bằng mấy", "một trăm trừ ba mươi lăm"
  ├─ dialogue.resolve_followup    "còn Hàn Quốc thì sao?" -> "Thủ đô của Hàn Quốc là gì"
  │                               "ông ấy sinh năm nào?" -> "Thomas Edison sinh năm nào"
  │                               "vào năm nào?" -> ghép vào câu hỏi trước
  ├─ dialogue.parse_comparison    "A hay B dài hơn", "so sánh diện tích của A và B",
  │                               "A và B, ai sinh trước", "A có cao hơn B không"
  ├─ dialogue.split_multi_question "X cao bao nhiêu và nằm ở tỉnh nào?" -> 2 câu, vế 2 mượn chủ ngữ
  ├─ dialogue._yesno              so mệnh đề với câu bằng chứng: tên riêng, con số, phủ định,
  │                               hướng (miền Bắc/miền Nam)
  └─ câu hỏi đơn: retrieve -> chọn đoạn -> reader -> answer_composer.compose_answer
                  (từ chối "chưa tìm thấy" khi đoạn văn không chứa tên riêng/từ khóa của câu hỏi)
```

`answer_composer.compose_answer` biến cụm ngắn của reader thành câu: `"Tokyo"` →
`"Thủ đô của Nhật Bản là Tokyo."`; câu hỏi tại sao/như thế nào/giới thiệu thì thêm câu bằng
chứng (ViT5 được huấn luyện để trả lời cụm ngắn). `HeuristicReader` là reader dự phòng khi chưa
có checkpoint ViT5 (trích số + đơn vị, năm/ngày gần vị ngữ nhất, tên người, nơi chốn, vế sau "là").

## Dùng

API (đã gắn vào `scripts/api_server.py`):

```
POST /api/ask        {question, session_id?, passage?}
  -> {answer, kind, intent, session_id, resolved_question, passage{id,text,score}|null, parts[]}
POST /api/ask/reset  {session_id}
```

`kind` ∈ `qa, multi, compare, yesno, summary, expand, smalltalk, math, unknown`. Gửi lại
`session_id` của lượt trước để hệ thống hiểu câu nối tiếp. Có `passage` thì đọc đoạn đó thay vì
truy xuất (tóm tắt, hỏi đáp trên đoạn người dùng dán vào).

Terminal:

```bash
python -X utf8 dialogue-manager_Huy/chat_cli.py --debug
```

## Đánh giá

Bộ câu hỏi tự viết, diễn đạt khác đoạn văn, **không lấy từ ViMMRC/ViQuAD**:

- `eval/conversations.json` — bộ phát triển: 157 mục / 190 lượt (20 câu xã giao, 50 câu kiến thức,
  17 tại sao/như thế nào, 12 đúng/sai, 11 so sánh, 8 câu ghép, 16 hội thoại nhiều lượt, 3 đoạn văn
  người dùng dán vào, 8 câu kiểu STT có từ đệm/viết thường, 6 phép tính/ngày giờ, 6 câu ngoài kho
  phải từ chối).
- `eval/conversations_heldout.json` — bộ held-out: 72 mục / 79 lượt, viết **sau** khi đã chỉnh hệ
  thống trên bộ phát triển.
- `eval/seed_kb.json` — 75 đoạn kiến thức phổ thông (địa lý, lịch sử, khoa học, văn hóa) làm kho
  khi chạy offline; cũng là kho mặc định của server khi chưa có `data/`.

```bash
python -X utf8 dialogue-manager_Huy/eval_dialogue.py --tts-check
python -X utf8 dialogue-manager_Huy/eval_dialogue.py --data dialogue-manager_Huy/eval/conversations_heldout.json --tts-check
```

Kết quả offline (kho mẫu + `HeuristicReader`, không mô hình), một mục đạt khi mọi lượt đều chứa
từ khóa mong đợi và đúng loại phản hồi:

| Bộ | Lần đầu | Sau khi sửa |
|---|---|---|
| Phát triển (157 mục) | 130/157 = 82,8% | 156/157 = 99,4% (đã chỉnh trên chính bộ này, lạc quan) |
| **Held-out (72 mục)** | **59/72 = 81,9%** (`reports/dialogue_heldout_first_run.json`) | 70/72 = 97,2% (sau khi sửa các lỗi chung mà lần chạy đầu lộ ra) |

Con số đáng tin nhất là **81,9% của lần chạy held-out đầu tiên**; hai con số "sau khi sửa" đã
nhìn thấy lỗi nên lạc quan hơn thực tế. `--tts-check`: 0 câu trả lời còn chữ số/ký hiệu mà TTS sẽ
đọc sai (sau khi bổ sung `normalizer.py`: đơn vị sau "triệu/tỷ", `H2O`, khoảng số, số La Mã,
`TP.HCM`).

Giới hạn cần biết:

- Các con số trên đo **offline trên kho 75 đoạn tự viết**, không phải trên KB thật (5.879 đoạn
  ViMMRC/ViQuAD + 1,48 triệu đoạn Wikipedia) với ViT5. Trên máy có dữ liệu, chạy:
  ```bash
  python -X utf8 dialogue-manager_Huy/eval_dialogue.py --index data/kb_index.json --wiki data/kb_wiki_full \
      --reranker BAAI/bge-reranker-v2-m3 --mrc mrc-model_Huy/checkpoints/vit5-combined-cont --out reports/dialogue_eval_full.json
  ```
  Kho lớn có nhiều đoạn gây nhiễu hơn, nên điểm câu kiến thức có thể thấp hơn; phần xã giao,
  phép tính, viết lại câu nối tiếp và tách câu hỏi không phụ thuộc kho.
- Vòng giọng nói đầy đủ (TTS đọc câu hỏi → Whisper chép lại → trả lời): `--voice gtts` (hoặc
  `edge`/`matcha`), cần mạng hoặc checkpoint; chưa chạy được trong sandbox (không có mạng ra
  HuggingFace/Google).
- Heuristic tiếng Việt: câu gõ **không dấu** chỉ hiểu được phần xã giao, không truy xuất được
  (kho có dấu); Whisper luôn chép có dấu nên không ảnh hưởng đường giọng nói.
- Đúng/sai chỉ kết luận khi câu bằng chứng mâu thuẫn rõ (khác tên riêng, khác số, phủ định,
  ngược hướng); còn lại trả lời "chưa chắc chắn" kèm bằng chứng (ví dụ "Có phải Edison phát minh
  ra điện thoại không?" — kho không có câu nào nói thẳng điều đó).

## Test

```bash
python -m pytest dialogue-manager_Huy/tests -q
```

Gồm test đơn vị từng bước và chốt chất lượng (bộ phát triển ≥ 95%, held-out ≥ 90%) để sửa đổi
sau này không làm tụt điểm mà không ai biết.
