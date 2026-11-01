# -*- coding: utf-8 -*-
"""
Script to build docs/ViMMRC_Presentation_5min.pptx
Duration: 5 - 10 Minutes (Calibrated ~6 - 7 minutes, ~840 words @ 125-130 wpm)
All numbers strictly reconciled with STATUS.md and verified benchmarks.
"""
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from slide_builder import (
    SlideDeckBuilder, DARK_BG, PRIMARY_BLUE, TECH_BLUE, TEAL, AMBER,
    TEXT_DARK, TEXT_MUTED, CARD_ACCENT_BG, GREEN, WHITE
)

builder = SlideDeckBuilder("docs/ViMMRC_Presentation_5min.pptx")

# ==========================================
# SLIDE 1: BÌA & GIỚI THIỆU NHANH (0:00 - 1:00)
# ==========================================
s1_notes = """Kính thưa Thầy Cô trong Hội đồng! Hôm nay, em xin đại diện nhóm báo cáo kết quả thực hiện đồ án môn Học máy tiên tiến và ứng dụng: 'Hệ thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0'.
Nhóm gồm 3 thành viên: em Ngô Trí Huy, nhóm trưởng, phụ trách Phân hệ Truy xuất ngữ cảnh và Mô hình Đọc hiểu MRC; bạn Huỳnh Công Lương phụ trách Nhận dạng giọng nói STT, Giao diện Web và Docker; bạn Trương Hoàng Duy phụ trách Tổng hợp tiếng nói TTS và Đánh giá âm học.
Động lực của đề tài xuất phát từ thực tế: các hệ thống đọc hiểu hiện nay chủ yếu tương tác qua văn bản gõ phím, gây bất tiện trong các tình huống rảnh tay hoặc với người khiếm thị. Mục tiêu của nhóm là xây dựng một chu trình khép kín: người dùng hỏi bằng giọng nói, hệ thống tự động tìm ngữ cảnh, đọc hiểu suy luận và trả lời lại bằng giọng nói trên máy tính cá nhân."""

metadata_items = [
    {
        "badge": "Nhóm trưởng / Lead",
        "name": "Ngô Trí Huy",
        "desc": [
            "Truy xuất BM25 + Dense + Reranker",
            "Mô hình đọc hiểu ViT5 sinh câu trả lời",
            "Tích hợp backend & kho tri thức"
        ]
    },
    {
        "badge": "Kỹ sư STT & Web",
        "name": "Huỳnh Công Lương",
        "desc": [
            "STT Whisper-small LoRA 50h (CTranslate2)",
            "Giao diện Web Angular 22 SPA",
            "Đóng gói Docker Container"
        ]
    },
    {
        "badge": "Kỹ sư TTS & Âm học",
        "name": "Trương Hoàng Duy",
        "desc": [
            "Tổng hợp giọng nói Matcha-TTS (CFM)",
            "Frontend tách thanh điệu vi_tone_v2",
            "Chuẩn hóa Text Normalizer & Benchmark"
        ]
    }
]

builder.add_title_slide(
    title="HỆ THỐNG HỎI - ĐÁP BẰNG GIỌNG NÓI TIẾNG VIỆT\nDỰA TRÊN BỘ DỮ LIỆU ViMMRC 2.0",
    subtitle="Đồ án môn học: Học máy tiên tiến và ứng dụng | Báo cáo nhanh Hội đồng (Khung 5 - 10 Phút)",
    metadata_items=metadata_items,
    duration_tag="Thuyết trình 5 - 10 Phút (Briefing Deck)",
    notes_text=s1_notes
)

# ==========================================
# SLIDE 2: KIẾN TRÚC PIPELINE 4 CHẶNG (1:00 - 2:15)
# ==========================================
s2_notes = """Để thực hiện mục tiêu trên, nhóm thiết kế kiến trúc pipeline gồm 4 chặng nối tiếp:
Chặng 1, STT: Nhận âm thanh từ micro người dùng, mô hình Whisper-small fine-tune LoRA 50h VietSpeech chuyển thành văn bản, chạy bằng CTranslate2 INT8 với bộ lọc VAD cắt khoảng lặng, đạt WER 13,77% so với 36,76% của bản gốc chưa fine-tune.
Chặng 2, Retrieval: Tìm kiếm trên kho tri thức hai tầng gồm 5.869 đoạn văn ViMMRC và ViQuAD kết hợp 1,48 triệu đoạn Wikipedia tiếng Việt bằng BM25 và vector dense, sau đó reranker bge-reranker-v2-m3 chấm lại để chọn đoạn văn phù hợp nhất.
Chặng 3, MRC: Mô hình ViT5-base đọc đoạn văn và sinh câu trả lời tự do ngắn gọn, không cần các phương án lựa chọn sẵn.
Chặng 4, TTS: Mô hình Matcha-TTS dựa trên Conditional Flow Matching tổng hợp câu trả lời thành giọng đọc qua loa.
Mỗi chặng đều có cơ chế dự phòng tự động: nếu chưa nạp checkpoint ViT5 thì dùng bộ trích câu khớp nhất, nếu Matcha-TTS gặp lỗi thì chuyển sang VITS, Edge-TTS hoặc gTTS."""

s2 = builder.add_content_slide(
    category="Kiến trúc Tổng thể",
    title="Chu Trình Hỏi - Đáp 4 Chặng & Cơ Chế Dự Phòng Đa Tầng",
    presenter="Ngô Trí Huy (Nhóm trưởng)",
    time_str="1:00 - 2:15 (75s)",
    notes_text=s2_notes
)

steps = [
    ("CHẶNG 1: STT", "Whisper-small LoRA 50h", "CTranslate2 + INT8", "VAD cắt khoảng lặng", "WER 13,77% | CER 6,67% (VietSpeech)", PRIMARY_BLUE),
    ("CHẶNG 2: RETRIEVAL", "BM25 + Dense + Reranker", "Kho 5.869 đoạn + Wikipedia", "bge-reranker-v2-m3", "F1 kiến thức mở: 15,4 → 24,3", TEAL),
    ("CHẶNG 3: MRC", "ViT5-base fine-tune", "Sinh câu trả lời tự do", "Train ViMMRC + ViQuAD2.0", "Test: EM 41.05% | F1 66.55%", TECH_BLUE),
    ("CHẶNG 4: TTS", "Matcha-TTS (OT-CFM)", "10 bước ODE trên CPU", "Frontend vi_tone_v2", "RTF: 0.52 | CER: 1.9%", GREEN)
]

for idx, (head, sub, d1, d2, d3, col) in enumerate(steps):
    bx = Inches(0.8) + idx * Inches(2.98)
    card, ctf = builder.add_card(s2, bx, Inches(1.5), Inches(2.8), Inches(3.7), title="", border_color=col)

    p0 = ctf.paragraphs[0]
    p0.text = head
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = col
    p0.alignment = PP_ALIGN.CENTER

    p_sub = ctf.add_paragraph()
    p_sub.text = sub
    p_sub.font.size = Pt(13)
    p_sub.font.bold = True
    p_sub.font.color.rgb = TEXT_DARK
    p_sub.alignment = PP_ALIGN.CENTER
    p_sub.space_before = Pt(4)

    for bullet in [d1, d2, d3]:
        pb = ctf.add_paragraph()
        pb.text = "• " + bullet
        pb.font.size = Pt(11)
        pb.font.color.rgb = TEXT_MUTED
        pb.space_before = Pt(8)

b_card, b_tf = builder.add_card(s2, Inches(0.8), Inches(5.45), Inches(11.733), Inches(1.4), title="", bg_color=CARD_ACCENT_BG)
bp0 = b_tf.paragraphs[0]
bp0.text = "CHIẾN LƯỢC DỰ PHÒNG & VẬN HÀNH CỤC BỘ TRÊN CPU (RESILIENCE & LOCAL CPU READY):"
bp0.font.size = Pt(12)
bp0.font.bold = True
bp0.font.color.rgb = PRIMARY_BLUE

bp1 = b_tf.add_paragraph()
bp1.text = "• STT: Thread-safe Lazy Loading giúp server khởi động nhanh (~0.45s); model Whisper-small LoRA 50h chạy int8 trên CPU."
bp1.font.size = Pt(11)
bp1.font.color.rgb = TEXT_DARK
bp1.space_before = Pt(3)

bp2 = b_tf.add_paragraph()
bp2.text = "• MRC & TTS: ViT5 chạy trên CPU, dự phòng bằng bộ trích câu khớp nhất (lexical); TTS ưu tiên Matcha → VITS → Edge-TTS → gTTS."
bp2.font.size = Pt(11)
bp2.font.color.rgb = TEXT_DARK
bp2.space_before = Pt(2)

# ==========================================
# SLIDE 3: BA ĐÓNG GÓP KỸ THUẬT NỔI BẬT (2:15 - 3:30)
# ==========================================
s3_notes = """Đề tài tập trung vào 3 điểm nhấn kỹ thuật chính:
Thứ nhất, ở khâu Truy xuất, nhóm tinh chỉnh tham số BM25 với k1=2.1, b=1.0 và bổ sung Bigram Phrase Boost cộng điểm cho cụm từ ghép liền kề trong tiếng Việt. Đồng thời, nhóm xây dựng kho tri thức hai tầng kết hợp Wikipedia tiếng Việt và reranker bge-reranker-v2-m3, giúp F1 câu trả lời cho câu hỏi kiến thức mở tăng từ 15,4% lên 24,3%.
Thứ hai, ở phân hệ Đọc hiểu, nhóm chuyển bài toán sang hỏi đáp tự do bằng cách fine-tune mô hình ViT5-base trên 27.164 câu hỏi gộp từ ViMMRC 2.0 và UIT-ViQuAD2.0, chia theo bài đọc để không rò rỉ dữ liệu. Mô hình sinh câu trả lời ngắn gọn, đạt F1 66,55% và Exact Match 41,05% trên tập test.
Thứ ba, ở phân hệ TTS, nhóm huấn luyện mô hình Matcha-TTS theo hướng Flow Matching với frontend vi_tone_v2 tách 6 thanh điệu thành token độc lập ở cuối âm tiết, kết hợp bộ chuẩn hóa văn bản tiếng Việt."""

s3 = builder.add_content_slide(
    category="Đóng góp Học thuật & Kỹ thuật",
    title="Ba Điểm Nhấn Kỹ Thuật: Retrieval Hai Tầng, ViT5 & Matcha-TTS",
    presenter="Ngô Trí Huy (Nhóm trưởng)",
    time_str="2:15 - 3:30 (75s)",
    notes_text=s3_notes
)

col_w = Inches(3.72)
col_y = Inches(1.5)
col_h = Inches(5.35)

c1, tf1 = builder.add_card(s3, Inches(0.8), col_y, col_w, col_h, title="1. BM25 Tinh Chỉnh & Kho Hai Tầng", title_color=PRIMARY_BLUE)
bullets_c1 = [
    "Kho tri thức hai tầng: 5.869 đoạn ViMMRC + ViQuAD và 1,48 triệu đoạn Wikipedia tiếng Việt (BM25 bm25s chia shard + vector dense multilingual-e5-small).",
    "Tinh chỉnh siêu tham số: k1 = 2.1 (độ bão hòa tần suất từ), b = 1.0 (chuẩn hóa theo độ dài văn bản).",
    "Bigram Phrase Boost (+0.4): Nhận diện cặp từ ghép liền kề tiếng Việt ('Điện Biên', 'Văn Miếu'), cộng điểm thưởng theo IDF.",
    "Top-3 mỗi nguồn (≤9 ứng viên) được reranker bge-reranker-v2-m3 chấm chung, đoạn tầng 1 cộng +0,25.",
    "BM25 hai tầng (trước reranker, test 2.545 câu): Recall@1 71,1%, Recall@5 85,9%. Answer F1 kiến thức mở: 15,4 → 24,3."
]
for b in bullets_c1:
    p = tf1.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(6)

c2, tf2 = builder.add_card(s3, Inches(4.8), col_y, col_w, col_h, title="2. Đọc Hiểu Sinh Câu Trả Lời: ViT5", title_color=TEAL)
bullets_c2 = [
    "Hỏi đáp tự do: người dùng đặt câu hỏi bằng lời tự nhiên, không cần các phương án lựa chọn A/B/C/D.",
    "Dữ liệu: 27.164 câu hỏi gộp ViMMRC 2.0 + UIT-ViQuAD2.0, chia theo bài đọc để tránh rò rỉ (21.733 / 2.715 / 2.716).",
    "ViT5-base (VietAI) fine-tune seq2seq; lưu checkpoint định kỳ, hỗ trợ tiếp tục huấn luyện (resume) khi ngắt quãng.",
    "Kết quả test (2.716 câu): Exact Match 41,05%, token F1 66,55%; toàn chuỗi BM25 → ViT5 đạt F1 53,9% (đoạn đúng: 68,6%)."
]
for b in bullets_c2:
    p = tf2.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(7)

c3, tf3 = builder.add_card(s3, Inches(8.8), col_y, col_w, col_h, title="3. Matcha-TTS & Frontend vi_tone_v2", title_color=GREEN)
bullets_c3 = [
    "Kiến trúc Flow Matching: Optimal-Transport Conditional Flow Matching (OT-CFM, ICASSP 2024) kết hợp vocoder HiFi-GAN.",
    "Suy luận hiệu quả: Quỹ đạo vận chuyển thẳng giúp giải ODE nhanh trên CPU (10 bước trong benchmark đạt RTF 0.52).",
    "Frontend vi_tone_v2: Tách 6 thanh điệu tiếng Việt thành token riêng cuối âm tiết (ví dụ: 'hồ' -> 'h ô 2'), thu gọn bộ từ vựng còn 41 ký hiệu.",
    "Text Normalizer: Chuẩn hóa ngày tháng, số liệu, tiền tệ, đơn vị đo, nhãn đáp án và chèn khoảng nghỉ theo dấu câu."
]
for b in bullets_c3:
    p = tf3.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(7)

# ==========================================
# SLIDE 4: KẾT QUẢ THỰC NGHIỆM & BENCHMARK (3:30 - 4:45)
# ==========================================
s4_notes = """Kính thưa Thầy Cô, bảng số liệu trên slide tổng hợp kết quả thực nghiệm của các phân hệ:
Ở phân hệ STT, fine-tune LoRA 50 giờ giúp giảm WER từ 36,76% xuống 13,77% và CER xuống 6,67% trên 1.802 mẫu test VietSpeech.
Ở phân hệ Retrieval, trên 2.545 câu test với kho tri thức hai tầng, BM25 đạt Recall@1 71,1% và Recall@5 85,9%. Khi kết hợp dense và reranker, F1 câu trả lời trên câu kiến thức mở tăng từ 15,4% lên 24,3%, và trên câu có đoạn trong kho tăng từ 58,0% lên 60,7%.
Ở phân hệ MRC, ViT5 fine-tune đạt Exact Match 41,05% và token F1 66,55% trên 2.716 câu test; khi chạy toàn chuỗi từ BM25 sang ViT5 đạt F1 53,9%.
Ở phân hệ TTS, Matcha-TTS đạt tỷ lệ lỗi ký tự CER 1,9% qua PhoWhisper, gần mức trần giọng người thật 0,7% và thấp hơn VITS MMS (4,3%). Sai số cao độ log-F0 đạt 2,86 bán cung, gần với Edge-TTS (2,69), với tốc độ RTF 0,52 trên CPU."""

s4 = builder.add_content_slide(
    category="Thực nghiệm & Đối sánh",
    title="Bảng Số Liệu Benchmark Giữa Các Phân Hệ & Baseline",
    presenter="Ngô Trí Huy (Nhóm trưởng)",
    time_str="3:30 - 4:45 (75s)",
    notes_text=s4_notes
)

headers_s4 = ["Phân hệ / Mô hình", "Chỉ số Đo lường", "Kết quả Đạt được", "Mức Đối chứng (Baseline)", "Ý nghĩa Thực tiễn"]
rows_s4 = [
    ["STT: Whisper-small LoRA 50h (CT2 int8)", "WER / CER (Test 1.802 mẫu VietSpeech)", "13.77% / 6.67%", "Whisper-small gốc: 36.76% / 19.43%", "Giảm 62,6% WER tương đối; nhanh gấp 4,1x trên CPU"],
    ["Retrieval: BM25 Tinh chỉnh (kho 2 tầng)", "Recall@1 / Recall@5 (Test 2.545 câu)", "71.1% / 85.9%", "Ablation kho 552 đoạn: R@1 71.45% (cũ 64.2%)", "Định vị đúng đoạn văn ngay ở Top 1 và Top 5"],
    ["Pipeline cuối: BM25 + dense + reranker", "Answer F1 (200 câu trong kho / 200 câu mở)", "60.7% / 24.3%", "BM25 thuần: 58.0% / 15.4%", "Cải thiện câu trả lời cả trong kho lẫn kiến thức mở"],
    ["Toàn chuỗi: BM25 → ViT5", "EM / token F1 (Test 2.545 câu)", "32.3% / 53.9%", "Đưa đúng đoạn văn (Gold): F1 68.6%", "Độ chính xác khi tự tìm đoạn văn rồi sinh câu trả lời"],
    ["MRC: ViT5-base fine-tune", "EM / token F1 (Test 2.716 câu)", "41.05% / 66.55%", "Trích câu khớp nhất (dự phòng khi thiếu model)", "Sinh câu trả lời ngắn gọn, đúng trọng tâm câu hỏi"],
    ["TTS: Matcha-TTS (Nhóm huấn luyện)", "CER (ASR PhoWhisper, 10 câu InfoRe1)", "1.9%", "VITS MMS: 4.3% | Người thật: 0.7%", "Phát âm rõ chữ, tỷ lệ lỗi thấp hơn VITS hơn 2 lần"],
    ["TTS: Matcha-TTS (Nhóm huấn luyện)", "log-F0 RMSE / MCD (10 câu InfoRe1)", "2.86 bán cung / 5.35 dB", "VITS: 4.31 bán cung | Edge-TTS: 2.69", "Thanh điệu ổn định, gần với dịch vụ đám mây"],
    ["Tốc độ & Độ trễ (Docker CPU)", "RTF TTS / Tổng thời gian 1 câu hỏi", "RTF 0.52 / ~12s (tắt rerank ~6s)", "Ngưỡng thời gian thực TTS: RTF < 1.0", "Chạy cục bộ trên CPU (STT ~3s, RAG ~6s, MRC ~1.4s, TTS ~1.3s)"]
]

col_w_s4 = [Inches(3.1), Inches(2.3), Inches(2.0), Inches(2.3), Inches(2.033)]
builder.add_table(s4, Inches(0.8), Inches(1.45), Inches(11.733), Inches(4.15), headers_s4, rows_s4, col_w_s4)

c_sum, tf_sum = builder.add_card(s4, Inches(0.8), Inches(5.75), Inches(11.733), Inches(1.1), title="", bg_color=CARD_ACCENT_BG)
ps0 = tf_sum.paragraphs[0]
ps0.text = "ĐÁNH GIÁ TỔNG HỢP HIỆU NĂNG HỆ THỐNG:"
ps0.font.size = Pt(11.5)
ps0.font.bold = True
ps0.font.color.rgb = PRIMARY_BLUE

ps1 = tf_sum.add_paragraph()
ps1.text = "Các phép đo thực nghiệm đều cải thiện rõ rệt so với baseline: STT giảm hơn 22,9 điểm % WER so với Whisper gốc; pipeline truy xuất có reranker tăng F1 câu hỏi mở từ 15,4% lên 24,3%; Matcha-TTS giảm hơn một nửa lỗi CER so với VITS và chạy trực tiếp trên CPU."
ps1.font.size = Pt(10.5)
ps1.font.color.rgb = TEXT_DARK
ps1.space_before = Pt(2)

# ==========================================
# SLIDE 5: SẢN PHẨM HOÀN CHỈNH & LIVE DEMO (4:45 - 5:45)
# ==========================================
s5_notes = """Về mặt kỹ nghệ phần mềm, nhóm đã tích hợp hệ thống thành ứng dụng Full-stack gồm Backend FastAPI và Frontend Angular 22, hiển thị trực quan trạng thái xử lý qua từng chặng. Toàn bộ dự án được đóng gói bằng Docker multi-stage, khởi chạy bằng một lệnh docker compose và có 54 bài kiểm thử tự động.
Trong kịch bản demo thực tế: khi người dùng bấm micro hỏi 'Ai là tác giả của Truyện Kiều?', phân hệ STT nhận dạng câu hỏi trong khoảng 3 giây; bộ truy xuất lấy ứng viên và reranker chọn đoạn Wikipedia về Truyện Kiều trong khoảng 6 giây; ViT5 sinh câu trả lời 'Nguyễn Du' trong 1,4 giây; và Matcha-TTS tổng hợp giọng đọc trong 1,3 giây. Tổng thời gian phản hồi khoảng 12 giây trên CPU Docker, hoặc khoảng 6 giây nếu tắt reranker."""

s5 = builder.add_content_slide(
    category="Kỹ nghệ & Thực nghiệm",
    title="Sản Phẩm Đóng Gói Docker & Kịch Bản Demo End-to-End",
    presenter="Ngô Trí Huy (Nhóm trưởng)",
    time_str="4:45 - 5:45 (60s)",
    notes_text=s5_notes
)

c_eng, tf_eng = builder.add_card(s5, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Kỹ Nghệ Phần Mềm & Đóng Gói", title_color=PRIMARY_BLUE)
eng_points = [
    ("Kiến trúc Full-Stack:", "Backend FastAPI bất đồng bộ + Frontend Angular 22 Standalone hiển thị trực quan."),
    ("Giao diện Trực quan:", "Hiển thị Pipeline Flow Indicator theo thời gian thực (Thu âm -> STT -> Retrieval -> MRC -> TTS -> Nghe)."),
    ("Docker Multi-Stage:", "Stage 1 (Node 22) biên dịch web; Stage 2 (Python 3.11-slim) cài đặt API và PyTorch CPU wheel."),
    ("Khởi chạy 1 Lệnh:", "docker compose up -d ánh xạ cổng 8090 -> 8000, tích hợp sẵn Docker Healthcheck."),
    ("Kiểm thử Tự động:", "54 bài kiểm thử tự động (53 passed, 1 skipped trên CPU) bao phủ từ xử lý dữ liệu đến REST API.")
]
for title_p, desc_p in eng_points:
    p = tf_eng.add_paragraph()
    p.text = f"• {title_p} {desc_p}"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_demo, tf_demo = builder.add_card(s5, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="Kịch Bản Demo Thực Tế (Live Flow)", title_color=TEAL)
demo_steps = [
    ("1. Giọng nói Đầu vào:", "Người dùng bấm mic hỏi: 'Ai là tác giả của Truyện Kiều?'."),
    ("2. STT (~3s):", "Whisper-small LoRA 50h (CTranslate2 int8) nhận dạng văn bản tiếng Việt có dấu."),
    ("3. Retrieval + reranker (~6s):", "BM25 + dense lấy ứng viên, reranker chọn đoạn Wikipedia 'Truyện Kiều'."),
    ("4. MRC (~1.4s):", "ViT5 đọc đoạn Wikipedia về Truyện Kiều và sinh câu trả lời 'Nguyễn Du'."),
    ("5. TTS (~1.3s):", "Matcha-TTS chuẩn hóa văn bản và tổng hợp giọng đọc câu trả lời."),
    ("6. Tổng Độ trễ:", "Khoảng 12 giây trên CPU Docker (STT ~3s, truy xuất + reranker ~6s, ViT5 ~1.4s, TTS ~1.3s); tắt reranker còn ~6 giây.")
]
for title_d, desc_d in demo_steps:
    p = tf_demo.add_paragraph()
    p.text = f"• {title_d} {desc_d}"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(7)

# ==========================================
# SLIDE 6: TỔNG KẾT & HƯỚNG PHÁT TRIỂN (5:45 - 6:30)
# ==========================================
s6_notes = """Tóm lại, nhóm đã xây dựng hoàn chỉnh hệ thống Voice Q&A tiếng Việt dựa trên ViMMRC 2.0 và UIT-ViQuAD2.0, kết hợp từ nhận dạng giọng nói, truy xuất hai tầng, đọc hiểu sinh câu trả lời tự do đến tổng hợp giọng nói Matcha-TTS chạy cục bộ trên CPU.
Về hạn chế và hướng phát triển: hiện tại độ trễ trên CPU khoảng 12 giây mỗi câu do reranker chiếm 6 giây, và một số câu hỏi kiến thức mở vẫn còn nhầm lẫn khi đoạn văn tầng 1 được cộng điểm ưu tiên. Trong thời gian tới, nhóm dự kiến triển khai trên GPU để giảm độ trễ, tinh chỉnh bộ định tuyến cho câu hỏi kiến thức chung, và thử nghiệm các mô hình ngôn ngữ lớn tiếng Việt để hỗ trợ hội thoại đa lượt.
Nhóm chúng em xin chân thành cảm ơn Thầy Cô đã lắng nghe và rất mong nhận được ý kiến đóng góp của Hội đồng!"""

s6 = builder.add_content_slide(
    category="Tổng kết & Định hướng",
    title="Tổng Kết Đóng Góp, Giới Hạn Thực Tế & Hướng Phát Triển",
    presenter="Ngô Trí Huy (Nhóm trưởng)",
    time_str="5:45 - 6:30 (45s)",
    notes_text=s6_notes
)

c_achieve, tf_achieve = builder.add_card(s6, Inches(0.8), Inches(1.5), Inches(5.6), Inches(4.1), title="Kết Quả Đạt Được", title_color=PRIMARY_BLUE)
achieve_list = [
    "Hoàn thiện chu trình Voice Q&A tiếng Việt dựa trên ViMMRC 2.0 và UIT-ViQuAD2.0 (27.164 câu hỏi).",
    "Huấn luyện mô hình Matcha-TTS (ICASSP 2024) với frontend vi_tone_v2 tách thanh điệu, đạt CER 1,9% và RTF 0,52.",
    "Vận hành cục bộ trên CPU thông thường (Edge-TTS/gTTS dự phòng cần Internet), độ trễ ~12s/câu (~6s khi tắt reranker).",
    "Đóng gói ứng dụng Full-stack (FastAPI + Angular) qua Docker multi-stage, đạt 54 bài kiểm thử tự động."
]
for item in achieve_list:
    p = tf_achieve.add_paragraph()
    p.text = "• " + item
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_future, tf_future = builder.add_card(s6, Inches(6.7), Inches(1.5), Inches(5.833), Inches(4.1), title="Giới Hạn Hiện Tại & Hướng Mở Rộng", title_color=AMBER)
future_list = [
    "Chạy trên GPU: Giảm thời gian chờ (hiện ~12 giây/câu trên CPU Docker do reranker chiếm ~6 giây).",
    "Tinh chỉnh định tuyến & reranker: Khắc phục hiện tượng câu hỏi kiến thức mở bị đoạn tầng 1 lấn át (hiện F1 mở đạt 24,3%).",
    "Thử nghiệm LLM tiếng Việt: Đánh giá thêm các mô hình lớn hơn hoặc kết hợp xếp hạng nhiều câu trả lời ứng viên.",
    "Hội thoại Đa lượt (Multi-Turn): Bổ sung bộ nhớ ngữ cảnh phiên làm việc để người dùng hỏi nối tiếp tự nhiên.",
    "Ứng dụng thực tế: Thử nghiệm tích hợp vào kiosk tra cứu thông tin học đường và công cụ hỗ trợ người khiếm thị."
]
for item in future_list:
    p = tf_future.add_paragraph()
    p.text = "→ " + item
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(7)

c_ty, tf_ty = builder.add_card(s6, Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.05), title="", bg_color=DARK_BG)
pt0 = tf_ty.paragraphs[0]
pt0.text = "TRÂN TRỌNG CẢM ƠN THẦY CÔ VÀ HỘI ĐỒNG ĐÃ LẮNG NGHE!"
pt0.font.size = Pt(15)
pt0.font.bold = True
pt0.font.color.rgb = WHITE
pt0.alignment = PP_ALIGN.CENTER

pt1 = tf_ty.add_paragraph()
pt1.text = "Nhóm xin kính mời Thầy Cô đặt câu hỏi và đóng góp ý kiến để đồ án được hoàn thiện hơn."
pt1.font.size = Pt(11)
pt1.font.color.rgb = RGBColor(148, 163, 184)
pt1.alignment = PP_ALIGN.CENTER
pt1.space_before = Pt(2)

builder.save()
print("Saved 6 slides to docs/ViMMRC_Presentation_5min.pptx successfully!")
