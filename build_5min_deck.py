# -*- coding: utf-8 -*-
"""
Script to rebuild docs/ViMMRC_Presentation_5min.pptx
Duration: 5 - 10 Minutes (Calibrated ~7 - 8 minutes, 980 words @ 125 wpm)
All numbers strictly reconciled with STATUS.md and final reports.
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
# SLIDE 1: BÌA & GIỚI THIỆU NHANH (0:00 - 1:15)
# ==========================================
s1_notes = """Kính thưa Thầy Cô trong Hội đồng! Hôm nay, em xin đại diện nhóm báo cáo kết quả thực hiện đồ án môn Học máy tiên tiến và ứng dụng: 'Hệ thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0'.
Nhóm gồm 3 thành viên: em Ngô Trí Huy, nhóm trưởng, phụ trách Phân hệ Truy xuất ngữ cảnh và Mô hình Đọc hiểu MRC; bạn Huỳnh Công Lương phụ trách Nhận dạng giọng nói STT, Giao diện Web và Docker; bạn Trương Hoàng Duy phụ trách Tổng hợp tiếng nói TTS và Đánh giá âm học.
Động lực lớn nhất của đề tài xuất phát từ việc: phần lớn các hệ thống đọc hiểu hiện nay chỉ tương tác qua văn bản gõ phím, rất hạn chế trong các tình huống rảnh tay như đang lái xe hay hỗ trợ người khiếm thị. Mục tiêu của nhóm là xây dựng một chu trình hoàn chỉnh khép kín: người dùng hỏi trực tiếp bằng giọng nói, hệ thống tự động tìm kiếm ngữ cảnh, đọc hiểu suy luận và phát âm thanh câu trả lời tự nhiên ngay trên máy tính thông thường."""

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
    duration_tag="Thuyết trình 5 - 10 Phút (Briefing Deck) | Thời lượng: ~7 - 8 Phút",
    notes_text=s1_notes
)

# ==========================================
# SLIDE 2: KIẾN TRÚC PIPELINE 4 CHẶNG (1:15 - 2:45)
# ==========================================
s2_notes = """Để hiện thực hóa mục tiêu trên, nhóm đã thiết kế kiến trúc pipeline 4 chặng đồng bộ:
Chặng 1, STT: Nhận âm thanh từ micro người dùng, mô hình Whisper-small fine-tune LoRA 50h VietSpeech chuyển thành văn bản, chạy trên engine CTranslate2 INT8 với bộ lọc VAD cắt khoảng lặng, đạt WER 13,77% so với 36,76% của bản gốc.
Chặng 2, Retrieval: Quét trên kho tri thức hai tầng gồm 5.869 đoạn văn ViMMRC và ViQuAD kết hợp 1,48 triệu đoạn Wikipedia tiếng Việt bằng BM25 và dense, sau đó reranker bge-reranker-v2-m3 chấm lại để chọn đoạn văn chính xác nhất.
Chặng 3, MRC: Mô hình ViT5-base đọc ngữ cảnh và sinh câu trả lời tự do ngắn gọn, không cần các phương án trắc nghiệm sẵn.
Chặng 4, TTS: Mô hình Matcha-TTS dựa trên Conditional Flow Matching tổng hợp câu trả lời thành giọng đọc truyền cảm qua loa.
Hệ thống có cơ chế dự phòng tự động ở từng chặng, chạy cục bộ 100% trên CPU thông thường với độ trễ đo thực tế khoảng 12 giây mỗi câu, và khoảng 6 giây khi tắt reranker."""

s2 = builder.add_content_slide(
    category="Kiến trúc Tổng thể",
    title="Chu Trình Hỏi - Đáp 4 Chặng & Cơ Chế Chịu Lỗi Đa Tầng",
    presenter="Ngô Trí Huy (Nhóm trưởng)",
    time_str="1:15 - 2:45 (90s)",
    notes_text=s2_notes
)

steps = [
    ("CHẶNG 1: STT", "Whisper-small LoRA 50h", "CTranslate2 + INT8", "VAD cắt khoảng lặng", "WER 13,77% | CER 6,67% (VietSpeech)", PRIMARY_BLUE),
    ("CHẶNG 2: RETRIEVAL", "BM25 + Dense + Reranker", "Kho 5.869 đoạn + Wikipedia", "bge-reranker-v2-m3", "F1 kiến thức mở: 15,4 → 24,3", TEAL),
    ("CHẶNG 3: MRC", "ViT5-base fine-tune", "Sinh câu trả lời tự do", "Train gộp 27.164 câu hỏi", "Test: EM 41.05% | F1 66.55%", TECH_BLUE),
    ("CHẶNG 4: TTS", "Matcha-TTS (OT-CFM)", "10 bước ODE trên CPU", "Frontend vi_tone_v2", "RTF: 0.52 | CER: 0.85% / 1.9%", GREEN)
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

    for line in [d1, d2, d3]:
        p = ctf.add_paragraph()
        p.text = f"• {line}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

card_bot, tf_bot = builder.add_card(s2, Inches(0.8), Inches(5.4), Inches(11.7), Inches(1.1), title="CƠ CHẾ DỰ PHÒNG & TỰ PHỤC HỒI (FAIL-SAFE PIPELINE)", border_color=PRIMARY_BLUE)
p_bot = tf_bot.add_paragraph()
p_bot.text = "Hệ thống thiết kế chịu lỗi đa tầng: Khâu STT có Lazy Loading tự nạp mô hình; khâu MRC tự động chuyển sang trích xuất đoạn nếu checkpoint ViT5 chưa tải; khâu TTS thiết lập chuỗi Fallback ưu tiên Matcha-TTS -> VITS -> Edge-TTS -> gTTS, đảm bảo phản hồi liên tục."
p_bot.font.size = Pt(10)
p_bot.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 3: BA ĐÓNG GÓP KỸ THUẬT NỔI BẬT (2:45 - 4:15)
# ==========================================
s3_notes = """Đề tài đạt được 3 đóng góp kỹ thuật trọng tâm:
Thứ nhất, ở phân hệ Truy xuất, nhóm tinh chỉnh siêu tham số BM25 đạt k1=2.1, b=1.0 và đề xuất cơ chế Bigram Phrase Boost cộng điểm cho cụm từ ghép tiếng Việt, giúp tăng Recall@1 thêm 7,27%. Đồng thời nhóm xây dựng kho tri thức hai tầng kết hợp Wikipedia tiếng Việt và cơ chế reranking tăng F1 câu hỏi kiến thức mở từ 15,4% lên 24,3%.
Thứ hai, ở phân hệ Đọc hiểu, nhóm chuyển đổi toàn diện từ bài toán trắc nghiệm sang hỏi đáp tự do, kết hợp bộ dữ liệu ViMMRC 2.0 và UIT-ViQuAD2.0 với 27.164 câu, phân tách nghiêm ngặt zero-leakage theo bài đọc. ViT5-base sinh câu trả lời tự nhiên, đạt F1 66,55% và EM 41,05% trên tập test.
Thứ ba, ở phân hệ TTS, nhóm ứng dụng thành công kỹ thuật Flow Matching tiên tiến với frontend vi_tone_v2 tách dấu thanh độc lập và tối ưu thuật toán căn chỉnh MAS bằng Numba JIT, giúp mô hình phát âm chuẩn xác cả 6 thanh điệu tiếng Việt."""

s3 = builder.add_content_slide(
    category="Đóng Góp Khoa Học & Kỹ Thuật",
    title="Ba Cải Tiến Kỹ Thuật Đột Phá Trong Toàn Hệ Thống",
    presenter="Ngô Trí Huy (Nhóm trưởng)",
    time_str="2:45 - 4:15 (90s)",
    notes_text=s3_notes
)

contributions = [
    (
        "1. RETRIEVAL: BM25 + DENSE + RERANKER",
        "Truy xuất kho hai tầng & Bigram Boost",
        [
            ("k1 = 2.1, b = 1.0:", "Tinh chỉnh thực nghiệm tối ưu độ dài đoạn văn."),
            ("Bigram Phrase Boost (+0.4):", "Cộng điểm cụm từ ghép tiếng Việt, tăng mạnh Recall@1."),
            ("Kho hai tầng:", "5.869 đoạn chuyên biệt + 1,48 triệu đoạn Wikipedia."),
            ("Reranker v2-m3:", "Chọn đoạn tốt nhất, F1 câu kiến thức mở tăng 15,4 -> 24,3.")
        ],
        PRIMARY_BLUE
    ),
    (
        "2. MRC: ViT5 SINH CÂU TRẢ LỜI TỰ DO",
        "Mở rộng hỏi đáp không cần trắc nghiệm",
        [
            ("Tập dữ liệu gộp 27.164 câu:", "ViMMRC 2.0 kết hợp UIT-ViQuAD2.0."),
            ("Zero Data Leakage:", "Tách Train / Dev / Test nghiêm ngặt theo bài đọc."),
            ("Sinh chuỗi Seq2Seq:", "ViT5-base sinh câu trả lời tự do ngắn gọn, đúng trọng tâm."),
            ("Vượt trội:", "Đạt EM 41.05%, token F1 66.55% trên tập Test.")
        ],
        TEAL
    ),
    (
        "3. TTS: MATCHA FLOW MATCHING & VI_TONE",
        "Tổng hợp giọng nói thanh điệu cao cấp",
        [
            ("OT-CFM tiên tiến:", "10 bước ODE trên CPU đạt RTF 0.52 (nhanh gấp đôi thời gian thực)."),
            ("Frontend vi_tone_v2:", "Bóc tách thanh điệu 0-5 riêng biệt, khắc phục lỗi dấu hỏi/ngã/nặng."),
            ("MAS Numba JIT:", "Căn chỉnh thời gian âm vị tốc độ cao, loại bỏ lỗi Cython."),
            ("Vocoder HiFi-GAN:", "Tinh chỉnh 50k bước khử rè kim loại, chất lượng tự nhiên.")
        ],
        GREEN
    )
]

for idx, (title, sub, bullets, col) in enumerate(contributions):
    bx = Inches(0.8) + idx * Inches(3.98)
    card, ctf = builder.add_card(s3, bx, Inches(1.5), Inches(3.8), Inches(5.0), title="", border_color=col)
    
    p0 = ctf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = col
    
    p_sub = ctf.add_paragraph()
    p_sub.text = sub
    p_sub.font.size = Pt(12)
    p_sub.font.bold = True
    p_sub.font.color.rgb = TEXT_DARK
    
    for bold_txt, norm_txt in bullets:
        p = ctf.add_paragraph()
        r1 = p.add_run()
        r1.text = f"• {bold_txt} "
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = TEXT_DARK
        
        r2 = p.add_run()
        r2.text = norm_txt
        r2.font.size = Pt(9)
        r2.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 4: KẾT QUẢ THỰC NGHIỆM & BENCHMARK (4:15 - 5:45)
# ==========================================
s4_notes = """Kính thưa Thầy Cô, các kết quả thực nghiệm trên bảng là minh chứng định lượng cho hiệu quả của hệ thống:
Ở phân hệ STT, fine-tune LoRA 50 giờ giúp giảm hơn 22,9 điểm WER trên tập test VietSpeech 1.802 mẫu, đưa WER xuống 13,77% và CER xuống 6,67%; lượng hóa INT8 giúp tăng tốc 4,1 lần trên CPU.
Ở phân hệ Retrieval, trên 2.545 câu test với kho tri thức hai tầng, BM25 đạt Recall@1 71,1% và Recall@5 85,9%.
Ở phân hệ MRC, mô hình ViT5 đạt Exact Match 41,05% và token F1 66,55% trên 2.716 câu test độc lập.
Ở phân hệ TTS, Matcha-TTS 10 bước đạt CER chỉ 0,85%, sai số cao độ log-F0 chỉ 0,91 bán cung, vượt trội hoàn toàn so với VITS MMS có CER 4,7% và log-F0 4,29 bán cung. Tốc độ RTF đạt 0,52 trên CPU, tức là nhanh gấp đôi thời gian thực."""

s4 = builder.add_content_slide(
    category="Đánh Giá Thực Nghiệm",
    title="Bảng Benchmark Tổng Hợp Đối Sánh Các Phân Hệ & Baseline",
    presenter="Ngô Trí Huy (Nhóm trưởng)",
    time_str="4:15 - 5:45 (90s)",
    notes_text=s4_notes
)

headers = ["Phân hệ / Mô hình", "Chỉ số then chốt", "Giá trị đạt được", "Đối sánh Baseline", "Ý nghĩa thực tiễn & Bối cảnh"]
rows_data = [
    ["Retrieval (BM25 hai tầng)", "Recall@1 / Recall@5 (Test 2.545 câu)", "71.1% / 85.9%", "Kho đơn tầng (không wiki)", "Tìm đúng đoạn văn trả lời ngay ở top 1 và top 5"],
    ["Pipeline cuối (dense + reranker)", "Answer F1: kho / mở", "60.7% / 24.3%", "BM25 thuần: 58.0% / 15.4%", "Reranker cải thiện rõ rệt câu kiến thức mở (+8.9% F1)"],
    ["STT (Whisper LoRA 50h)", "WER / CER (VietSpeech)", "13.77% / 6.67%", "Whisper gốc: 36.76% / 19.43%", "Giảm 62.6% WER tương đối; CTranslate2 nhanh gấp 4.1x CPU"],
    ["MRC (ViT5-base Seq2Seq)", "Exact Match / Token F1", "41.05% / 66.55%", "Extractive Baseline: ~21.5% / ~43.2%", "Sinh câu trả lời tự do ngắn gọn, đúng trọng tâm"],
    ["TTS (Matcha-TTS Flow Matching)", "Lỗi ký tự (CER qua ASR)", "0.85% (1.9% PhoWhisper)", "VITS: 4.7% (Người thật: 0.7%)", "Phát âm rõ chữ, tiệm cận mức trần giọng người thật"],
    ["TTS (Matcha-TTS cao độ F0)", "Sai số cao độ (log-F0)", "0.91 bán cung (22.1 Hz)", "VITS: 4.29 bán cung / Edge: 2.69", "Thanh điệu chuẩn xác, tự nhiên tiệm cận dịch vụ thương mại"],
    ["Tốc độ (Matcha CPU)", "Real-Time Factor (RTF)", "0.52 - 0.53", "Ngưỡng thời gian thực: < 1.0", "Nhanh gấp đôi thời gian thực trên CPU Intel Core i5/i7"],
    ["Độ trễ toàn trình (Docker CPU)", "Voice-to-Voice Latency", "~12 giây (tắt rerank: ~6s)", "Mục tiêu CPU: hoàn toàn offline", "STT ~3s, RAG+Rerank ~6s, ViT5 ~1.4s, TTS ~1.3s"],
    ["Kiểm thử tự động (Quality)", "Automated Test Suite", "54/54 tests passed (100%)", "Không có kiểm thử tự động", "Bao phủ toàn diện REST API, VAD, Normalizer, Fallback"]
]

col_widths = [Inches(2.5), Inches(2.2), Inches(1.8), Inches(2.3), Inches(2.9)]
builder.add_table(s4, Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.1), headers, rows_data, col_widths=col_widths)

# ==========================================
# SLIDE 5: SẢN PHẨM HOÀN CHỈNH & LIVE DEMO (5:45 - 7:00)
# ==========================================
s5_notes = """Về mặt kỹ nghệ phần mềm, nhóm đã tích hợp hoàn chỉnh hệ thống thành một ứng dụng Full-stack hoàn chỉnh: Backend FastAPI mô-đun hóa với cơ chế thread-safe lazy loading kết hợp Frontend Angular hiển thị trực quan luồng dữ liệu đang chạy qua 4 chặng. Toàn bộ giải pháp được đóng gói tự động hóa 100% bằng Docker multi-stage container và vượt qua toàn bộ 54 trên 54 ca kiểm thử tự động.
Trong kịch bản demo thực tế: khi người dùng bấm micro hỏi 'Ai là tác giả của Truyện Kiều?', phân hệ STT nhận dạng câu hỏi trong khoảng 3 giây; bộ truy xuất lấy ứng viên và reranker chọn chính xác đoạn Wikipedia về tác phẩm; ViT5 suy luận và sinh đáp án 'Nguyễn Du'; cuối cùng Matcha-TTS phát âm thanh câu trả lời ra loa chỉ sau 1,3 giây. Toàn bộ chu trình mất khoảng 12 giây trên Docker CPU và khoảng 6 giây khi tắt reranker."""

s5 = builder.add_content_slide(
    category="Kỹ Nghệ Phần Mềm & Thực Nghiệm",
    title="Sản Phẩm Hoàn Chỉnh, Đóng Gói Docker & Kịch Bản Live Demo",
    presenter="Ngô Trí Huy (Nhóm trưởng)",
    time_str="5:45 - 7:00 (75s)",
    notes_text=s5_notes
)

col1_left = Inches(0.8)
col2_left = Inches(6.8)
col_width = Inches(5.7)

card_prod, tf_prod = builder.add_card(s5, col1_left, Inches(1.5), col_width, Inches(5.0), "KIẾN TRÚC SẢN PHẨM SẴN SÀNG TRIỂN KHAI")
prod_points = [
    ("Giao diện Web SPA (Angular 22):", "Thiết kế hiện đại, responsive, có biểu đồ Pipeline Flow Status theo dõi tiến trình thời gian thực (Micro -> STT -> RAG -> MRC -> TTS -> Loa)."),
    ("Backend API (FastAPI RESTful):", "Kiến trúc module hóa cao, giao tiếp chuẩn JSON/Audio, hỗ trợ Lazy Loading nạp mô hình vào RAM theo luồng an toàn (Thread-Safe Lock)."),
    ("Đóng gói Docker Multi-Stage:", "Stage 1 (node:22-alpine) biên dịch Angular assets; Stage 2 (python:3.11-slim) triển khai PyTorch CPU, tối ưu kích thước image."),
    ("Tự động hóa & Kiểm chuẩn:", "100% tự động khởi chạy bằng docker-compose; vượt qua toàn diện 54/54 ca kiểm thử tự động (Unit Test, Integration Test, Regression Test).")
]
for bold_p, norm_p in prod_points:
    p = tf_prod.add_paragraph()
    r1 = p.add_run()
    r1.text = f"• {bold_p} "
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = PRIMARY_BLUE
    r2 = p.add_run()
    r2.text = norm_p
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = TEXT_DARK

card_demo, tf_demo = builder.add_card(s5, col2_left, Inches(1.5), col_width, Inches(5.0), "KỊCH BẢN LIVE DEMO: 'AI LÀ TÁC GIẢ CỦA TRUYỆN KIỀU?'", border_color=GREEN)
demo_steps = [
    ("1. Thu âm Micro (Client):", "Người dùng bấm giữ mic, nói tự nhiên: 'Ai là tác giả của Truyện Kiều?'. Web Audio API thu âm chuẩn PCM 16kHz."),
    ("2. Nhận dạng STT (~3s):", "Whisper LoRA 50h lọc nhiễu VAD, giải mã thành chuỗi văn bản câu hỏi tiếng Việt có dấu đầy đủ."),
    ("3. Truy xuất RAG (~6s):", "BM25 + dense quét kho hai tầng; bge-reranker-v2-m3 chọn chính xác đoạn Wikipedia 'Truyện Kiều'."),
    ("4. Đọc hiểu MRC (~1.4s):", "ViT5-base đọc hiểu ngữ cảnh và câu hỏi, sinh câu trả lời tự do chính xác: 'Nguyễn Du'."),
    ("5. Tổng hợp TTS (~1.3s):", "Text Normalizer chuẩn hóa và Matcha-TTS tổng hợp âm thanh giọng nói truyền cảm, trình duyệt tự động phát loa."),
    ("-> Tổng thời gian xử lý:", "~12 giây trên Docker CPU thông thường (~6 giây khi tắt reranker).")
]
for bold_s, norm_s in demo_steps:
    p = tf_demo.add_paragraph()
    r1 = p.add_run()
    r1.text = f"• {bold_s} "
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = GREEN
    r2 = p.add_run()
    r2.text = norm_s
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = TEXT_DARK

# ==========================================
# SLIDE 6: TỔNG KẾT & HƯỚNG PHÁT TRIỂN (7:00 - 8:00)
# ==========================================
s6_notes = """Tóm lại, đồ án của nhóm đã hiện thực hóa thành công một hệ thống Voice Q&A tiếng Việt hoàn chỉnh, khép kín chu trình đa phương thức từ âm thanh đến ngữ nghĩa rồi trở lại âm thanh. Hệ thống chạy hoàn toàn cục bộ trên CPU máy tính thông thường, bảo đảm quyền riêng tư và làm chủ các công nghệ học máy tiên tiến từ Flow Matching đến Transformer.
Trong định hướng phát triển tiếp theo, nhóm sẽ triển khai trên GPU để rút ngắn độ trễ toàn trình xuống dưới 2 giây, tiếp tục tinh chỉnh bộ reranker cho các câu hỏi mở phức tạp, và thử nghiệm tích hợp các mô hình ngôn ngữ lớn (LLMs tiếng Việt) để hỗ trợ hội thoại đàm thoại đa lượt.
Nhóm chúng em xin chân thành cảm ơn sự hướng dẫn tận tình của Thầy Cô! Rất mong nhận được những góp ý quý báu từ Hội đồng để nhóm tiếp tục hoàn thiện đề tài."""

s6 = builder.add_content_slide(
    category="Kết Luận & Định Hướng",
    title="Tổng Kết Đóng Góp, Giá Trị Thực Tiễn & Hướng Phát Triển",
    presenter="Ngô Trí Huy (Nhóm trưởng)",
    time_str="7:00 - 8:00 (60s)",
    notes_text=s6_notes
)

card_val, tf_val = builder.add_card(s6, col1_left, Inches(1.5), col_width, Inches(5.0), "CÁC GIÁ TRỊ KHOA HỌC & THỰC TIỄN ĐẠT ĐƯỢC")
val_items = [
    ("Hệ thống Voice Q&A Tiếng Việt Khép kín:", "Xây dựng trọn vẹn chu trình đa phương thức từ âm thanh micro đến câu trả lời giọng nói qua loa, chạy offline 100% trên CPU phổ thông."),
    ("Làm chủ Công nghệ Tạo sinh SOTA:", "Làm chủ thành công mô hình Flow Matching (Matcha-TTS) kết hợp frontend tách thanh điệu vi_tone_v2 giải quyết triệt để vấn đề dấu thanh tiếng Việt."),
    ("Mở rộng Đọc hiểu Tự do:", "Chuyển đổi bài toán trắc nghiệm hạn chế sang hỏi đáp tự do open-domain trên kho tri thức hai tầng với 1,48 triệu đoạn văn Wikipedia."),
    ("Kỹ nghệ Phần mềm Chuẩn mực:", "Kiến trúc micro-services module hóa, API rõ ràng, kiểm thử tự động 54/54 test cases đạt, đóng gói Docker triển khai một lệnh.")
]
for b_v, n_v in val_items:
    p = tf_val.add_paragraph()
    r1 = p.add_run()
    r1.text = f"• {b_v} "
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = PRIMARY_BLUE
    r2 = p.add_run()
    r2.text = n_v
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = TEXT_DARK

card_future, tf_future = builder.add_card(s6, col2_left, Inches(1.5), col_width, Inches(5.0), "ĐỊNH HƯỚNG PHÁT TRIỂN TRONG TƯƠNG LAI", border_color=AMBER)
future_items = [
    ("Tăng tốc phần cứng GPU:", "Triển khai trên GPU NVIDIA máy chủ (TensorRT / ONNX Runtime) để rút ngắn độ trễ toàn trình xuống dưới 2 giây, phục vụ đàm thoại tức thì."),
    ("Tối ưu hóa Reranker câu hỏi mở:", "Tiếp tục fine-tune bge-reranker-v2-m3 trên dữ liệu tiếng Việt thực tế để phân biệt tốt hơn giữa câu hỏi trong kho và kiến thức mở bách khoa."),
    ("Tích hợp Mô hình Ngôn ngữ Lớn (LLM):", "Thử nghiệm kết hợp các mô hình LLM tiếng Việt (Vistral, PhoGPT, Qwen2.5-Vi) để tổng hợp câu trả lời phong phú và hỗ trợ hội thoại đa lượt."),
    ("Mở rộng miền ứng dụng thực tiễn:", "Ứng dụng vào hệ thống tra cứu thủ tục hành chính công, cổng thông tin đào tạo trường đại học và trợ lý ảo hỗ trợ người khiếm thị.")
]
for b_f, n_f in future_items:
    p = tf_future.add_paragraph()
    r1 = p.add_run()
    r1.text = f"• {b_f} "
    r1.font.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = AMBER
    r2 = p.add_run()
    r2.text = n_f
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = TEXT_DARK

# Build and save PPTX
builder.save()
print("Saved 6 slides to docs/ViMMRC_Presentation_5min.pptx successfully!")
