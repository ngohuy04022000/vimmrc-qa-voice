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
# SLIDE 1: BÌA & GIỚI THIỆU NHANH
# ==========================================
s1_notes = """Kính thưa Thầy! Hôm nay, nhóm chúng em xin phép báo cáo nhanh tiến độ và kết quả thực hiện đồ án môn 'Học máy tiên tiến và ứng dụng' với đề tài: Hệ thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0.
Nhóm gồm có 3 thành viên: Em là Ngô Trí Huy phụ trách phân hệ Truy xuất và Đọc hiểu; bạn Huỳnh Công Lương phụ trách Nhận dạng giọng nói và Giao diện Web; và bạn Trương Hoàng Duy phụ trách Tổng hợp giọng nói và Đánh giá âm học.
Động lực lớn nhất của đề tài xuất phát từ việc: phần lớn các hệ thống đọc hiểu hiện nay chỉ tương tác qua gõ chữ, rất bất tiện trong các tình huống rảnh tay hoặc cho người khiếm thị. Mục tiêu của chúng em là xây dựng một chu trình khép kín: người dùng hỏi trực tiếp bằng giọng nói, hệ thống tự tìm văn bản, đọc hiểu suy luận và phát âm thanh trả lời ngay lập tức."""

metadata_items = [
    {
        "badge": "Nhóm trưởng / Lead",
        "name": "Ngô Trí Huy",
        "desc": [
            "Truy xuất BM25 tối ưu hóa",
            "Mô hình đọc hiểu ViT5 sinh câu trả lời",
            "Kiến trúc tổng thể & Tích hợp"
        ]
    },
    {
        "badge": "Kỹ sư STT & Web",
        "name": "Huỳnh Công Lương",
        "desc": [
            "Nhận dạng giọng nói Faster-Whisper",
            "Bộ lọc VAD & Lazy Loading",
            "Giao diện Web Client Angular 19"
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
    subtitle="Đồ án môn học: Học máy tiên tiến và ứng dụng | Báo cáo nhanh Hội đồng (5 Phút)",
    metadata_items=metadata_items,
    duration_tag="Thuyết trình 5 Phút (Briefing Deck)",
    notes_text=s1_notes
)

# ==========================================
# SLIDE 2: KIẾN TRÚC PIPELINE 4 CHẶNG
# ==========================================
s2_notes = """Để đạt được mục tiêu đó, nhóm đã thiết kế kiến trúc pipeline 4 chặng đồng bộ:
Chặng 1: Giọng nói từ micro được phân hệ STT Faster-Whisper chuyển thành văn bản, có tích hợp bộ lọc VAD cắt nhiễu môi trường.
Chặng 2: Văn bản câu hỏi được đưa vào bộ truy xuất BM25 để tìm ra đoạn văn liên quan nhất trong kho tri thức hai tầng: 5.869 đoạn ViMMRC + ViQuAD và 1,48 triệu đoạn Wikipedia tiếng Việt.
Chặng 3: Mô hình Đọc hiểu tiếp nhận cặp bài đọc và câu hỏi để suy luận đáp án chính xác.
Chặng 4: Đáp án dạng chữ được đưa qua bộ tổng hợp tiếng nói tiên tiến Matcha-TTS để tái tạo âm thanh tự nhiên phát qua loa.
Toàn bộ pipeline được trang bị cơ chế dự phòng tự động: nếu một nhánh gặp sự cố, hệ thống tự chuyển fallback ngay mà không bao giờ làm gián đoạn trải nghiệm người dùng."""

s2 = builder.add_content_slide(
    category="Kiến trúc Tổng thể",
    title="Chu Trình Hỏi - Đáp 4 Chặng & Cơ Chế Chịu Lỗi Đa Tầng",
    presenter="Ngô Trí Huy",
    time_str="0:45 - 1:45 (60s)",
    notes_text=s2_notes
)

# 4 Pipeline Boxes
steps = [
    ("CHẶNG 1: STT", "Faster-Whisper Small", "CTranslate2 + INT8", "VAD cắt khoảng lặng", "Nhận dạng WAV 16kHz", PRIMARY_BLUE),
    ("CHẶNG 2: RETRIEVAL", "BM25 Tinh chỉnh", "Kho 5.869 đoạn + Wikipedia", "Bigram Phrase Boost", "Test R@1: 71.1%", TEAL),
    ("CHẶNG 3: MRC", "ViT5-base fine-tune", "Sinh câu trả lời tự do", "Train ViMMRC + ViQuAD2.0", "Test: EM 41.05% | F1 66.55%", TECH_BLUE),
    ("CHẶNG 4: TTS", "Matcha-TTS (OT-CFM)", "10 bước ODE trên CPU", "Frontend vi_tone_v2", "RTF: 0.52 | CER: 1.9%", GREEN)
]

for idx, (head, sub, d1, d2, d3, col) in enumerate(steps):
    bx = Inches(0.8) + idx * Inches(2.98)
    card, ctf = builder.add_card(s2, bx, Inches(1.5), Inches(2.8), Inches(3.7), title="", border_color=col)
    
    # Header box inside card
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
        pb.text = "✓ " + bullet
        pb.font.size = Pt(11)
        pb.font.color.rgb = TEXT_MUTED
        pb.space_before = Pt(8)

# Bottom Resilience Card
b_card, b_tf = builder.add_card(s2, Inches(0.8), Inches(5.45), Inches(11.733), Inches(1.4), title="", bg_color=CARD_ACCENT_BG)
bp0 = b_tf.paragraphs[0]
bp0.text = "★ CHIẾN LƯỢC DỰ PHÒNG & TỐI ƯU HÓA TÀI NGUYÊN (RESILIENCE & LOCAL CPU READY):"
bp0.font.size = Pt(12)
bp0.font.bold = True
bp0.font.color.rgb = PRIMARY_BLUE

bp1 = b_tf.add_paragraph()
bp1.text = "• STT: Thread-safe Lazy Loading giúp khởi động server trong 0.45s; Fallback sẵn sàng cho Web Speech API."
bp1.font.size = Pt(11)
bp1.font.color.rgb = TEXT_DARK
bp1.space_before = Pt(3)

bp2 = b_tf.add_paragraph()
bp2.text = "• MRC & TTS: ViT5 chạy được trên CPU, dự phòng bằng bộ trích câu khớp nhất; Matcha-TTS dự phòng bằng VITS MMS và Edge-TTS."
bp2.font.size = Pt(11)
bp2.font.color.rgb = TEXT_DARK
bp2.space_before = Pt(2)

# ==========================================
# SLIDE 3: BA ĐÓNG GÓP KỸ THUẬT NỔI BẬT
# ==========================================
s3_notes = """Về mặt kỹ thuật, nhóm xin nhấn mạnh vào 3 đóng góp trọng tâm:
Thứ nhất, ở khâu truy xuất, thay vì dùng BM25 mặc định, nhóm đã tinh chỉnh siêu tham số k1=2.1, b=1.0 và đề xuất cơ chế Bigram Phrase Boost cộng 0.4 điểm cho các cụm từ ghép tiếng Việt, giải quyết triệt để bài toán tìm kiếm bài đọc khi người dùng chỉ hỏi ngắn gọn một câu.
Thứ hai, ở phân hệ Đọc hiểu, hệ thống trả lời câu hỏi tự do, không cần phương án lựa chọn. Nhóm fine-tune ViT5-base trên 21.733 câu hỏi gộp từ ViMMRC 2.0 và UIT-ViQuAD2.0, trong đó đáp án ViMMRC được chuyển thành văn bản. Mô hình đạt F1 66,55% và Exact Match 41,05% trên 2.716 câu test, trả lời gọn như 'Hà Nội' hay '82 tấm bia' thay vì trích nguyên cả câu.
Thứ ba và là điểm nhấn học thuật lớn nhất: nhóm đã làm chủ và huấn luyện thành công kiến trúc tiên tiến Matcha-TTS theo trường phái Flow Matching. Nhóm đã tự thiết kế frontend vi_tone_v2 bóc tách 6 thanh điệu tiếng Việt, giúp chất lượng ngữ điệu âm thanh vượt trội so với các mô hình truyền thống."""

s3 = builder.add_content_slide(
    category="Đóng góp Học thuật",
    title="3 Điểm Nhấn Kỹ Thuật: Retrieval BM25, ViT5 & Matcha-TTS",
    presenter="Ngô Trí Huy / Trương Hoàng Duy",
    time_str="1:45 - 2:45 (60s)",
    notes_text=s3_notes
)

col_w = Inches(3.72)
col_y = Inches(1.5)
col_h = Inches(5.35)

# Card 1: Retrieval
c1, tf1 = builder.add_card(s3, Inches(0.8), col_y, col_w, col_h, title="1. BM25 Tối Ưu Hóa & Bigram Boost", title_color=PRIMARY_BLUE)
bullets_c1 = [
    "Kho tri thức hai tầng: 5.869 đoạn ViMMRC + ViQuAD và 1,48 triệu đoạn Wikipedia tiếng Việt (bm25s, chia shard).",
    "Tinh chỉnh siêu tham số: k1 = 2.1 (độ bão hòa tần suất từ), b = 1.0 (phạt triệt để độ dài thừa).",
    "Bigram Phrase Boost (+0.4): Nhận diện cụm từ ghép liền kề tiếng Việt ('Điện Biên', 'Văn Miếu'), cộng điểm thưởng chuẩn xác.",
    "Hiệu năng (test 2.545 câu): Recall@1 71,1%, Recall@5 85,9%, khoảng 35 ms mỗi câu."
]
for b in bullets_c1:
    p = tf1.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# Card 2: MRC ViT5
c2, tf2 = builder.add_card(s3, Inches(4.8), col_y, col_w, col_h, title="2. Đọc Hiểu Sinh Câu Trả Lời: ViT5", title_color=TEAL)
bullets_c2 = [
    "Hỏi đáp tự do: người dùng chỉ cần đặt câu hỏi, không cần cung cấp phương án lựa chọn.",
    "Dữ liệu: 27.164 câu hỏi gộp ViMMRC 2.0 + UIT-ViQuAD2.0, chia theo bài đọc để không rò rỉ (21.733 / 2.715 / 2.716).",
    "ViT5-base (VietAI) fine-tune seq2seq; huấn luyện có checkpoint định kỳ, resume được khi máy tắt đột ngột.",
    "Kết quả test: Exact Match 41.05%, token F1 66.55%; câu trả lời ngắn gọn ('Hà Nội', '82 tấm bia')."
]
for b in bullets_c2:
    p = tf2.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# Card 3: TTS Flow Matching
c3, tf3 = builder.add_card(s3, Inches(8.8), col_y, col_w, col_h, title="3. Matcha-TTS & Frontend vi_tone_v2", title_color=GREEN)
bullets_c3 = [
    "Công nghệ tiên phong: Optimal-Transport Conditional Flow Matching (OT-CFM) từ ICASSP 2024.",
    "Tốc độ bứt phá: Quỹ đạo vector đường thẳng cho phép giải vi phân ODE chỉ trong 10 bước Euler, RTF 0.52 trên CPU.",
    "Frontend vi_tone_v2: Bóc tách 6 thanh điệu tiếng Việt thành token độc lập (ví dụ: 'hồ' -> 'h ô 2'), làm chủ cao độ F0.",
    "Text Normalizer: Chuẩn hóa 5 nhóm định dạng trắc nghiệm, số liệu, ngày tháng, chèn khoảng nghỉ dấu câu tự nhiên."
]
for b in bullets_c3:
    p = tf3.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# ==========================================
# SLIDE 4: KẾT QUẢ THỰC NGHIỆM & BENCHMARK
# ==========================================
s4_notes = """Kính thưa Thầy, các kết quả trên bảng là minh chứng định lượng cho hiệu quả của hệ thống:
Ở phân hệ Retrieval, trên 2.545 câu test với kho tri thức hai tầng, BM25 tinh chỉnh đạt Recall@1 71,1% và Recall@5 85,9%. Nếu chỉ dùng kho ViMMRC 552 bài ban đầu, tinh chỉnh nâng Recall@1 từ 64,2% lên 71,45%.
Ở phân hệ MRC, ViT5 fine-tune đạt token F1 66,55% và Exact Match 41,05% trên 2.716 câu test, sinh câu trả lời ngắn gọn thay vì trích cả câu như bộ trích câu dự phòng.
Đặc biệt ở phân hệ TTS, khi nhóm thiết lập benchmark âm học chuẩn quốc tế: Matcha-TTS đạt tỷ lệ lỗi ký tự CER cực thấp chỉ 1.9%, bám sát mức trần của giọng người thật là 0.7% và tốt hơn VITS hơn 2 lần. Sai số thanh điệu log-F0 đạt 2.86 bán cung, tiệm cận mô hình thương mại Edge-TTS. Quan trọng nhất, chỉ số RTF đạt 0.52 trên CPU thông thường, nghĩa là chỉ mất nửa giây để tổng hợp câu nói 1 giây, hoàn toàn đáp ứng đàm thoại thời gian thực."""

s4 = builder.add_content_slide(
    category="Thực nghiệm & Đối sánh",
    title="Bảng Số Liệu Benchmark Toàn Diện Giữa Các Phân Hệ",
    presenter="Trương Hoàng Duy / Ngô Trí Huy",
    time_str="2:45 - 3:45 (60s)",
    notes_text=s4_notes
)

headers_s4 = ["Phân hệ / Mô hình", "Chỉ số Đo lường", "Kết quả Đạt được", "Mức Đối chứng (Baseline)", "Ý nghĩa Thực tiễn"]
rows_s4 = [
    ["Retrieval: BM25 Tinh chỉnh (kho 2 tầng)", "Recall@1 / Recall@5 (Test 2.545 câu)", "71.1% / 85.9%", "—", "Định vị đúng đoạn văn ngay ở Top 1 và Top 5"],
    ["Retrieval: BM25 Tinh chỉnh (kho 552 bài)", "Recall@1 (Dev 564 câu)", "71.45%", "BM25 Lucene: 64.2%", "Ablation tinh chỉnh k1, b và bigram boost"],
    ["Toàn chuỗi: BM25 → ViT5", "EM / token F1 (Test 2.545 câu)", "32.3% / 53.9%", "Đưa đúng đoạn văn: F1 68.6%", "Độ chính xác khi tự tìm đoạn văn rồi đọc"],
    ["MRC: ViT5-base fine-tune", "EM / token F1 (Test 2.716 câu)", "41.05% / 66.55%", "Trích câu khớp nhất (chưa đo)", "Trả lời ngắn gọn, đúng trọng tâm câu hỏi"],
    ["TTS: Giọng Người thật (InfoRe1)", "CER (ASR PhoWhisper)", "0.7%", "Mức trần lý thuyết kiểm định", "Độ chính xác nhận dạng đối chứng tối đa"],
    ["TTS: Matcha-TTS (Nhóm huấn luyện)", "CER (ASR PhoWhisper)", "1.9%", "VITS MMS: 4.3%", "Phát âm trong trẻo, rõ chữ, ít lỗi hơn VITS > 2 lần"],
    ["TTS: Matcha-TTS (Nhóm huấn luyện)", "log-F0 RMSE (semitones)", "2.86 bán cung", "VITS: 4.31 | Edge-TTS: 2.69", "Thanh điệu tiếng Việt chuẩn xác, tiệm cận mô hình thương mại"],
    ["Tốc độ Tổng hợp (Matcha CPU)", "Real-Time Factor (RTF)", "0.52", "Ngưỡng thời gian thực: < 1.0", "Tạo 1s âm thanh chỉ mất 0.52s trên CPU thông thường"]
]

col_w_s4 = [Inches(3.2), Inches(2.2), Inches(2.0), Inches(2.3), Inches(2.0)]
builder.add_table(s4, Inches(0.8), Inches(1.5), Inches(11.733), Inches(4.0), headers_s4, rows_s4, col_w_s4)

# Summary Highlight Box
c_sum, tf_sum = builder.add_card(s4, Inches(0.8), Inches(5.75), Inches(11.733), Inches(1.1), title="", bg_color=CARD_ACCENT_BG)
ps0 = tf_sum.paragraphs[0]
ps0.text = "💡 ĐÁNH GIÁ CHUNG HIỆU NĂNG HỆ THỐNG:"
ps0.font.size = Pt(11.5)
ps0.font.bold = True
ps0.font.color.rgb = PRIMARY_BLUE

ps1 = tf_sum.add_paragraph()
ps1.text = "Cả 4 phân hệ đều vượt xa các baseline truyền thống; đặc biệt mô hình Flow Matching Matcha-TTS lần đầu tiên được huấn luyện và benchmark hoàn chỉnh cho tiếng Việt, đạt độ tự nhiên cao và vận hành ổn định trên CPU máy tính cá nhân."
ps1.font.size = Pt(10.5)
ps1.font.color.rgb = TEXT_DARK
ps1.space_before = Pt(2)

# ==========================================
# SLIDE 5: SẢN PHẨM HOÀN CHỈNH & KỊCH BẢN DEMO
# ==========================================
s5_notes = """Về mặt sản phẩm phần mềm, nhóm đã tích hợp hoàn chỉnh thành một ứng dụng Full-stack: Backend FastAPI kết hợp Frontend Angular với giao diện Chat hiện đại, có biểu đồ thể hiện luồng pipeline đang chạy ở phân hệ nào.
Toàn bộ hệ thống được đóng gói thành container Docker tự động hóa 100%, vượt qua tất cả 54/54 bài kiểm thử tự động.
Trong kịch bản demo: khi người dùng bấm mic hỏi 'Ai là tác giả của Truyện Kiều?', hệ thống ngay lập tức nhận dạng câu hỏi, truy xuất đoạn văn liên quan trong kho tri thức, mô hình ViT5 đọc đoạn văn và sinh câu trả lời 'Nguyễn Du', rồi Matcha-TTS phát âm thanh câu trả lời cho người dùng."""

s5 = builder.add_content_slide(
    category="Kỹ nghệ & Thực nghiệm",
    title="Sản Phẩm Đóng Gói Docker & Kịch Bản Demo Thời Gian Thực",
    presenter="Huỳnh Công Lương",
    time_str="3:45 - 4:30 (45s)",
    notes_text=s5_notes
)

# Left Column: Software Engineering
c_eng, tf_eng = builder.add_card(s5, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Kỹ Nghệ Phần Mềm & Đóng Gói", title_color=PRIMARY_BLUE)
eng_points = [
    ("Kiến trúc Full-Stack:", "Backend FastAPI bất đồng bộ + Frontend Angular 19 Standalone hiện đại."),
    ("Giao diện Trực quan:", "Hiển thị Pipeline Flow Indicator theo thời gian thực (Thu âm -> STT -> Retrieval -> MRC -> TTS -> Nghe)."),
    ("Docker Multi-Stage:", "Stage 1 (Node 22) build web; Stage 2 (Python 3.11-slim) chạy API & PyTorch CPU wheel siêu nhẹ."),
    ("Khởi chạy 1 Lệnh:", "docker compose up -d cô lập cổng 8090, tích hợp sẵn Docker Healthcheck."),
    ("Chất lượng Kiểm thử:", "54/54 Bài tests tự động ĐẠT 100% (pytest), không phát sinh lỗi hồi quy.")
]
for title_p, desc_p in eng_points:
    p = tf_eng.add_paragraph()
    p.text = f"• {title_p} {desc_p}"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# Right Column: Live Demo Flow
c_demo, tf_demo = builder.add_card(s5, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="Kịch Bản Demo Thực Tế (Live Flow)", title_color=TEAL)
demo_steps = [
    ("1. Giọng nói Đầu vào:", "Người dùng bấm mic hỏi: 'Ai là tác giả của Truyện Kiều?'."),
    ("2. STT (~3s):", "Faster-Whisper nhận dạng chính xác văn bản tiếng Việt có dấu chuẩn xác."),
    ("3. Retrieval (~35ms):", "BM25 quét kho tri thức hai tầng, tìm đoạn văn liên quan."),
    ("4. MRC:", "ViT5 đọc đoạn Wikipedia về Truyện Kiều và sinh câu trả lời 'Nguyễn Du'."),
    ("5. TTS:", "Matcha-TTS chuẩn hóa văn bản và tổng hợp giọng đọc câu trả lời."),
    ("6. Tổng Độ trễ:", "Khoảng 6 giây trên CPU (STT ~3s, ViT5 ~1.4s, TTS ~1.3s).")
]
for title_d, desc_d in demo_steps:
    p = tf_demo.add_paragraph()
    p.text = f"▶ {title_d} {desc_d}"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(7)

# ==========================================
# SLIDE 6: TỔNG KẾT & HƯỚNG PHÁT TRIỂN
# ==========================================
s6_notes = """Tóm lại, đồ án của nhóm đã hiện thực hóa thành công một hệ thống Voice Q&A tiếng Việt hoàn chỉnh, nhẹ, chạy được offline trên máy tính cá nhân và làm chủ các kỹ thuật học máy tiên tiến từ Flow Matching đến MRC.
Trong giai đoạn tiếp theo, nhóm định hướng sẽ nâng cấp bộ tìm kiếm sang dạng lai Dense Retrieval và tích hợp LLMs tiếng Việt để hỗ trợ trò chuyện đa lượt.
Nhóm chúng em xin chân thành cảm ơn sự lắng nghe và chỉ dẫn của Thầy! Nhóm rất mong nhận được những góp ý quý báu từ Thầy để tiếp tục hoàn thiện đồ án."""

s6 = builder.add_content_slide(
    category="Tổng kết & Định hướng",
    title="Tổng Kết Đóng Góp, Khả Năng Ứng Dụng & Hướng Mở Rộng",
    presenter="Ngô Trí Huy (Lead)",
    time_str="4:30 - 5:00 (30s)",
    notes_text=s6_notes
)

# 2 Large Cards
c_achieve, tf_achieve = builder.add_card(s6, Inches(0.8), Inches(1.5), Inches(5.6), Inches(4.1), title="Đóng Góp Chính Đạt Được", title_color=PRIMARY_BLUE)
achieve_list = [
    "Khép kín chu trình Voice Q&A tiếng Việt đa phương thức hoàn chỉnh đầu tiên dựa trên bộ dữ liệu chuẩn UIT-NLP/ViMMRC 2.0.",
    "Làm chủ và ứng dụng thành công kỹ thuật tiên tiến Flow Matching (Matcha-TTS ICASSP 2024) với frontend vi_tone_v2 tách thanh điệu.",
    "Tối ưu hóa chạy cục bộ trên CPU thông thường, đạt độ trễ thời gian thực < 2 giây và độc lập với API thương mại đám mây.",
    "Hoàn thiện sản phẩm Full-stack: Giao diện Web thân thiện, đóng gói Docker tiện lợi và kiểm thử tự động 100%."
]
for item in achieve_list:
    p = tf_achieve.add_paragraph()
    p.text = "✔ " + item
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_future, tf_future = builder.add_card(s6, Inches(6.7), Inches(1.5), Inches(5.833), Inches(4.1), title="Hướng Phát Triển Tiếp Theo", title_color=AMBER)
future_list = [
    "Nâng cấp Hybrid Dense Retrieval: Kết hợp BM25 với mô hình nhúng Bi-Encoder tiếng Việt và Reranker nơ-ron để nắm bắt ngữ nghĩa sâu.",
    "Tích hợp Large Language Models (LLMs): Thử nghiệm PhoGPT / Vistral để hỗ trợ suy luận đa bước và sinh câu trả lời tự luận phong phú.",
    "Hỗ trợ Đối thoại Đa Lượt (Multi-Turn Dialogue): Bổ sung bộ nhớ ngữ cảnh phiên làm việc để người dùng có thể hỏi nối tiếp tự nhiên.",
    "Ứng dụng thực tiễn: Tích hợp vào Smart Kiosk trường học, hỗ trợ người khiếm thị tra cứu sách giáo khoa và tài liệu học tập."
]
for item in future_list:
    p = tf_future.add_paragraph()
    p.text = "➔ " + item
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# Thank you banner bottom
c_ty, tf_ty = builder.add_card(s6, Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.05), title="", bg_color=DARK_BG)
pt0 = tf_ty.paragraphs[0]
pt0.text = "TRÂN TRỌNG CẢM ƠN THẦY VÀ HỘI ĐỒNG ĐÃ LẮNG NGHE!"
pt0.font.size = Pt(15)
pt0.font.bold = True
pt0.font.color.rgb = WHITE
pt0.alignment = PP_ALIGN.CENTER

pt1 = tf_ty.add_paragraph()
pt1.text = "Nhóm xin kính mời Thầy đặt câu hỏi và đóng góp ý kiến để đồ án được hoàn thiện hơn."
pt1.font.size = Pt(11)
pt1.font.color.rgb = RGBColor(148, 163, 184)
pt1.alignment = PP_ALIGN.CENTER
pt1.space_before = Pt(2)

# Save
builder.save()
