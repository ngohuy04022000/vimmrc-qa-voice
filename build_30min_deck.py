import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from slide_builder import (
    SlideDeckBuilder, DARK_BG, PRIMARY_BLUE, TECH_BLUE, TEAL, AMBER,
    TEXT_DARK, TEXT_MUTED, CARD_ACCENT_BG, GREEN, WHITE
)

builder = SlideDeckBuilder("docs/ViMMRC_Presentation_30min.pptx")

# ==============================================================================
# PHẦN 1: TỔNG QUAN, BÀI TOÁN & DỮ LIỆU ViMMRC 2.0 (Slides 1 - 4)
# ==============================================================================

# SLIDE 1
s1_notes = """Kính thưa Thầy Cô trong Hội đồng và các bạn học viên cao học! Hôm nay, nhóm chúng em xin báo cáo đồ án môn học 'Học máy tiên tiến và ứng dụng' với đề tài: 'Xây dựng Hệ thống Hỏi - Đáp Bằng Giọng Nói Tiếng Việt Dựa Trên Bộ Dữ Liệu ViMMRC 2.0'.
Nhóm gồm 3 thành viên: em Ngô Trí Huy, nhóm trưởng, phụ trách Phân hệ Truy xuất, Mô hình Đọc hiểu ViT5 và tích hợp backend; bạn Huỳnh Công Lương phụ trách Nhận dạng Giọng nói Whisper-small fine-tune LoRA, Giao diện Web và Docker; bạn Trương Hoàng Duy phụ trách Tổng hợp Tiếng nói Flow Matching cùng Benchmark âm học.
Trong video 30 phút này, nhóm sẽ trình bày toàn diện từ bối cảnh, dữ liệu, cơ sở toán học, tối ưu kỹ thuật, kết quả thực nghiệm đến demo thực tế. Kính mời Thầy Cô cùng theo dõi!"""

metadata_s1 = [
    {
        "badge": "Nhóm trưởng / Lead",
        "name": "Ngô Trí Huy",
        "desc": [
            "Truy xuất BM25 + dense + reranker",
            "Retrieval (RAG) & MRC (ViT5)",
            "Tích hợp backend & kho tri thức"
        ]
    },
    {
        "badge": "Kỹ sư STT & Web",
        "name": "Huỳnh Công Lương",
        "desc": [
            "STT Whisper-small LoRA 50h",
            "Tối ưu CTranslate2 & VAD filter",
            "Giao diện Web Angular 22 & Docker"
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
    subtitle="Báo cáo Đồ án Toàn diện: Kiến trúc Học máy, Mô hình Hóa Toán học & Thực nghiệm (30 Phút)",
    metadata_items=metadata_s1,
    duration_tag="Thuyết trình 30 Phút (Video Báo Cáo Chuyên Sâu)",
    notes_text=s1_notes
)

# SLIDE 2
s2_notes = """Thưa Thầy Cô, Machine Reading Comprehension là trụ cột quan trọng của Xử lý Ngôn ngữ Tự nhiên. Tuy nhiên, việc giới hạn ở bàn phím và văn bản gây bất tiện trong môi trường rảnh tay như lái xe hoặc với người khiếm thị.
Khi chuyển sang Voice Q&A tiếng Việt, nhóm đối mặt với 3 thách thức lớn:
Thứ nhất, tính chất thanh điệu: tiếng Việt có 6 thanh điệu biến thiên cao độ. Mô hình TTS thông thường dễ sai dấu hỏi, ngã, nặng hoặc mất tự nhiên.
Thứ hai, độ trễ tích lũy: pipeline gồm 4 chặng nối tiếp nhau, tổng thời gian cộng dồn lại; đo thực tế khoảng 12 giây mỗi câu trên Docker CPU.
Thứ ba, yêu cầu chạy cục bộ: hệ thống cần hoạt động ổn định trên CPU phổ thông để bảo mật dữ liệu giọng nói, không phụ thuộc API trả phí."""

s2 = builder.add_content_slide(
    category="Phần 1: Tổng quan & Bài toán",
    title="Bối Cảnh Nghiên Cứu & Ba Thách Thức Độc Thù Của Voice Q&A Tiếng Việt",
    presenter="Ngô Trí Huy (Lead)",
    time_str="1:15 - 2:30 (75s)",
    notes_text=s2_notes
)

c_s2_1, tf_s2_1 = builder.add_card(s2, Inches(0.8), Inches(1.5), Inches(3.72), Inches(5.35), title="1. Rào Cản Text-Only", title_color=PRIMARY_BLUE)
for b in [
    "Các hệ thống MRC truyền thống bị bó hẹp trong tương tác bàn phím và màn hình.",
    "Không thể sử dụng trong môi trường rảnh tay: lái xe, nấu ăn, di chuyển ngoài đường.",
    "Bỏ quên người khiếm thị, người cao tuổi mắt kém hoặc trẻ em chưa thạo đọc viết.",
    "Đòi hỏi chuyển đổi sang mô hình Voice-In / Voice-Out đa phương thức."
]:
    p = tf_s2_1.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s2_2, tf_s2_2 = builder.add_card(s2, Inches(4.8), Inches(1.5), Inches(3.72), Inches(5.35), title="2. Thách Thức Âm Học Tiếng Việt", title_color=TEAL)
for b in [
    "Tiếng Việt có 6 thanh điệu (Ngang, Huyền, Sắc, Hỏi, Ngã, Nặng) mang tính phân biệt nghĩa cao.",
    "Các mô hình TTS phương Tây áp dụng thẳng vào tiếng Việt thường nuốt thanh điệu, đọc ngang phè hoặc sai dấu hỏi/ngã.",
    "Hiện tượng từ đồng âm khác nghĩa và từ ghép đòi hỏi mô hình phải hiểu cả ngữ cảnh âm vị học.",
    "Cần giải pháp tách thanh điệu độc lập trong Text Encoder."
]:
    p = tf_s2_2.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s2_3, tf_s2_3 = builder.add_card(s2, Inches(8.8), Inches(1.5), Inches(3.72), Inches(5.35), title="3. Chạy Cục Bộ & Rào Cản Phần Cứng", title_color=AMBER)
for b in [
    "Độ trễ cộng dồn qua 4 chặng nối tiếp (STT, Retrieval, MRC, TTS).",
    "Ràng buộc GPU: Hầu hết mô hình SOTA (Whisper Large, Diffusion TTS) đòi hỏi GPU máy chủ tốn kém.",
    "Yêu cầu đồ án: Hệ thống chạy cục bộ trên CPU cá nhân phổ thông (Intel i5/i7, 8GB RAM), dữ liệu giọng nói không rời máy.",
    "Đo thực tế: ~12 giây/câu trên Docker CPU (~6 giây khi tắt reranker)."
]:
    p = tf_s2_3.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# SLIDE 3
s3_notes = """Để giải quyết các thách thức đó, nhóm đặt mục tiêu xây dựng một hệ thống Voice Q&A tiếng Việt hoàn chỉnh, khép kín từ thu âm đến phát giọng nói. Bốn nguyên lý thiết kế xuyên suốt gồm:
Một là Tính Module hóa: từng phân hệ STT, Retrieval, MRC và TTS được trừu tượng hóa qua các lớp Client riêng biệt, cho phép kiểm thử độc lập và linh hoạt nâng cấp thuật toán.
Hai là Chạy cục bộ trên CPU: tối ưu hóa kích thước mô hình và suy luận để toàn bộ pipeline chạy ổn định trên máy tính phổ thông với 8GB RAM mà không bắt buộc có GPU rời.
Ba là Tính chịu lỗi: mỗi phân hệ đều có cơ chế dự phòng tự động khi gặp dữ liệu bất thường hoặc gián đoạn mạng.
Bốn là Đo lường thực tế: nhóm đo đạc chi tiết từng thành phần trên Docker CPU, đạt khoảng 12 giây mỗi câu khi bật reranker và khoảng 6 giây khi tắt reranker."""

s3 = builder.add_content_slide(
    category="Phần 1: Tổng quan & Bài toán",
    title="Mục Tiêu Khoa Học & 4 Nguyên Lý Thiết Kế Hệ Thống Cốt Lõi",
    presenter="Ngô Trí Huy (Lead)",
    time_str="2:30 - 3:45 (75s)",
    notes_text=s3_notes
)

principles = [
    ("1. TÍNH MODULE HÓA CAO (HIGH MODULARITY)", "Kiến trúc hướng dịch vụ, trừu tượng hóa qua các BaseClient Interface.", "Cho phép hoán đổi độc lập các thuật toán (ví dụ: thay BM25 bằng Dense Retriever, thay Matcha bằng VITS) mà không ảnh hưởng toàn hệ thống.", PRIMARY_BLUE),
    ("2. KHẢ NĂNG CHẠY CỤC BỘ (LOCAL & CPU-FRIENDLY)", "Tối ưu hóa tham số để toàn bộ pipeline chạy ổn định trên CPU máy tính 8GB RAM.", "Chạy cục bộ, không dùng API đám mây trả phí (OpenAI, Google Speech); Edge-TTS/gTTS dự phòng cần Internet.", TEAL),
    ("3. TÍNH CHỊU LỖI & DỰ PHÒNG (FAULT TOLERANCE)", "Thiết kế cơ chế Multi-level Fallback ở từng phân hệ.", "Nếu chưa có checkpoint ViT5 -> Lexical baseline trích câu trả lời; Nếu Matcha-TTS lỗi -> VITS -> Edge-TTS -> gTTS tự động thay thế; có cơ chế dự phòng ở từng phân hệ.", TECH_BLUE),
    ("4. ĐO LƯỜNG THỜI GIAN PHẢN HỒI (MEASURED LATENCY)", "Giảm tải ở các khâu: VAD cắt khoảng lặng, Euler 10 bước TTS; reranker có thể tắt (KB_RERANKER=) để đổi độ chính xác lấy tốc độ.", "Chạy cục bộ trên CPU; đo thực tế ~12 giây/câu trên Docker CPU (~6 giây khi tắt reranker).", GREEN)
]

for idx, (title_p, sub_p, det_p, col_p) in enumerate(principles):
    py = Inches(1.5) + idx * Inches(1.35)
    card, tf_p = builder.add_card(s3, Inches(0.8), py, Inches(11.733), Inches(1.2), title="", border_color=col_p)
    p0 = tf_p.paragraphs[0]
    p0.text = title_p
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = col_p
    p1 = tf_p.add_paragraph()
    p1.text = "• " + sub_p
    p1.font.size = Pt(10.5)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_DARK
    p1.space_before = Pt(2)
    p2 = tf_p.add_paragraph()
    p2.text = "→ " + det_p
    p2.font.size = Pt(10)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(1)

# SLIDE 4
s4_notes = """Trọng tâm dữ liệu của đề tài bắt đầu từ bộ dữ liệu đọc hiểu ViMMRC 2.0 do UIT-NLP công bố, gồm 5.273 câu hỏi trắc nghiệm tiếng Việt dành cho học sinh. Để mở rộng cho bài toán hỏi đáp tự do, nhóm đã gộp ViMMRC 2.0 với bộ dữ liệu UIT-ViQuAD2.0 gồm 21.891 câu hỏi tự luận trên Wikipedia, tạo thành kho dữ liệu tổng cộng 27.164 câu.
Dữ liệu được phân chia theo bài đọc thành 3 tập: Train 21.733 câu, Dev 2.715 câu và Test 2.716 câu. Nhóm tuân thủ nghiêm ngặt nguyên tắc phân tách ở cấp độ bài đọc: các văn bản trong tập Dev và Test hoàn toàn chưa từng xuất hiện trong tập Train, đảm bảo zero leakage.
Về tiền xử lý, bài đọc trong dữ liệu có độ dài từ 120 đến hơn 1.200 từ. Nhóm đã chuẩn hóa Unicode NFC, loại bỏ ký tự điều khiển ẩn và lập kho tri thức hai tầng gồm 5.869 đoạn văn ViMMRC và ViQuAD kết hợp 1,48 triệu đoạn Wikipedia tiếng Việt, làm cơ sở tri thức vững chắc cho hệ thống."""

s4 = builder.add_content_slide(
    category="Phần 1: Tổng quan & Bài toán",
    title="Phân Tích Chuyên Sâu Bộ Dữ Liệu Chuẩn UIT-NLP/ViMMRC 2.0",
    presenter="Ngô Trí Huy (Lead)",
    time_str="3:45 - 5:30 (105s)",
    notes_text=s4_notes
)

headers_s4 = ["Tập Dữ Liệu (Split)", "Nguồn", "Số Câu Hỏi (Questions)", "Tỷ Lệ (%)", "Nguyên Tắc Phân Tách (Partitioning)"]
rows_s4 = [
    ["Tập Huấn luyện (Train)", "ViMMRC 2.0 + UIT-ViQuAD2.0", "21.733 câu hỏi", "80.0%", "Chia theo bài đọc để huấn luyện ViT5"],
    ["Tập Phát triển (Dev)", "ViMMRC 2.0 + UIT-ViQuAD2.0", "2.715 câu hỏi", "10.0%", "Không trùng bài đọc với Train (Disjoint)"],
    ["Tập Kiểm thử (Test)", "ViMMRC 2.0 + UIT-ViQuAD2.0", "2.716 câu hỏi", "10.0%", "Đánh giá mù năng lực tổng quát hóa (Zero Leakage)"],
    ["TỔNG CỘNG CẢ BỘ", "ViMMRC 5.273 + ViQuAD 21.891 (từ 28.454 gốc)", "27.164 câu hỏi", "100.0%", "Kho truy xuất: 5.869 đoạn + 1,48 triệu đoạn Wikipedia"]
]
col_w_s4 = [Inches(2.6), Inches(2.2), Inches(2.2), Inches(1.3), Inches(3.433)]
builder.add_table(s4, Inches(0.8), Inches(1.5), Inches(11.733), Inches(2.3), headers_s4, rows_s4, col_w_s4)

c_s4_left, tf_s4_l = builder.add_card(s4, Inches(0.8), Inches(4.0), Inches(5.6), Inches(2.85), title="Đặc Điểm & Thách Thức Ngữ Liệu", title_color=PRIMARY_BLUE)
for b in [
    "Dữ liệu dùng dạng hỏi đáp tự do: Bài đọc (Passage) + Câu hỏi (Question) + Câu trả lời dạng văn bản.",
    "Độ dài bài đọc biến thiên: Từ khoảng 120 từ đến hơn 1.200 từ (vượt giới hạn 512 subword token của Transformer).",
    "Nguồn gộp: ViMMRC 2.0 (5.273 câu, bài tập đọc phổ thông) + UIT-ViQuAD2.0 (28.454 câu gốc, còn 21.891 sau khi loại câu không có đáp án) = 27.164 câu."
]:
    p = tf_s4_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(5)

c_s4_right, tf_s4_r = builder.add_card(s4, Inches(6.7), Inches(4.0), Inches(5.833), Inches(2.85), title="Quy Trình Chuẩn Hóa & Tiền Xử Lý", title_color=TEAL)
for b in [
    "Chuẩn hóa Unicode NFC: Đồng bộ mã hóa ký tự tiếng Việt giữa các nguồn dữ liệu.",
    "Làm sạch ký tự rỗng & điều khiển ẩn: Loại bỏ các khoảng trắng zwnj, tab lỗi trong dữ liệu gốc.",
    "Kho tri thức (build_kb.py): 5.869 đoạn ViMMRC + ViQuAD (kb_index.json) và 1,48 triệu đoạn Wikipedia tiếng Việt (kb_wiki_full).",
    "Đánh giá theo Generative QA (sinh câu trả lời tự do): EM và token F1 trên 2.716 câu test."
]:
    p = tf_s4_r.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(5)

# ==============================================================================
# PHẦN 2: KIẾN TRÚC TỔNG THỂ & PHÂN HỆ STT (Slides 5 - 8)
# ==============================================================================

# SLIDE 5
s5_notes = """Kính thưa Thầy Cô, em là Huỳnh Công Lương, xin trình bày về Kiến trúc Hệ thống và Phân hệ STT.
Trên màn hình là kiến trúc 4 chặng:
Người dùng nói vào mic, âm thanh gửi tới phân hệ STT để chuyển thành văn bản câu hỏi. Câu hỏi đi vào phân hệ Retrieval tìm kiếm trên kho tri thức hai tầng và trả về đoạn văn liên quan nhất. Tiếp đó, phân hệ MRC dùng ViT5 đọc hiểu và sinh câu trả lời tự do. Cuối cùng, phân hệ TTS tổng hợp thành giọng nói tự nhiên phát qua loa.
Hệ thống có cơ chế Fallback ở từng chặng: chưa nạp checkpoint ViT5 thì dùng bộ trích xuất lexical; chuỗi TTS ưu tiên Matcha-TTS, lỗi sẽ chuyển VITS, Edge-TTS hoặc gTTS, đảm bảo không bao giờ gián đoạn."""

s5 = builder.add_content_slide(
    category="Phần 2: Kiến trúc & STT",
    title="Kiến Trúc Pipeline 4 Chặng & Chiến Lược Fallback Đa Tầng",
    presenter="Huỳnh Công Lương",
    time_str="5:30 - 6:45 (75s)",
    notes_text=s5_notes
)

steps_s5 = [
    ("CHẶNG 1: STT", "Whisper-small LoRA 50h (CT2 int8)", "Audio 16kHz -> Text Query", "WER 13,77% | CER 6,67% (VietSpeech)", PRIMARY_BLUE),
    ("CHẶNG 2: RETRIEVAL", "BM25 + Dense + Reranker", "Kho 5.869 đoạn + Wikipedia", "Đoạn khớp nhất sau rerank", TEAL),
    ("CHẶNG 3: MRC", "ViT5 (RAG)", "Đọc hiểu & Suy luận đáp án", "Fallback: Lexical Overlap", TECH_BLUE),
    ("CHẶNG 4: TTS", "Matcha-TTS (Flow Matching)", "Text Answer -> Audio 22kHz", "Fallback: VITS / Edge-TTS / gTTS", GREEN)
]

for idx, (head, eng, dat, fb, col) in enumerate(steps_s5):
    bx = Inches(0.8) + idx * Inches(2.98)
    card, ctf = builder.add_card(s5, bx, Inches(1.5), Inches(2.8), Inches(3.4), title="", border_color=col)
    p0 = ctf.paragraphs[0]
    p0.text = head
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = col
    p0.alignment = PP_ALIGN.CENTER

    p_eng = ctf.add_paragraph()
    p_eng.text = eng
    p_eng.font.size = Pt(13)
    p_eng.font.bold = True
    p_eng.font.color.rgb = TEXT_DARK
    p_eng.alignment = PP_ALIGN.CENTER
    p_eng.space_before = Pt(4)

    p_dat = ctf.add_paragraph()
    p_dat.text = "→ " + dat
    p_dat.font.size = Pt(10.5)
    p_dat.font.color.rgb = TEXT_MUTED
    p_dat.space_before = Pt(8)

    p_fb = ctf.add_paragraph()
    p_fb.text = "• " + fb
    p_fb.font.size = Pt(10)
    p_fb.font.color.rgb = PRIMARY_BLUE
    p_fb.space_before = Pt(8)

# Lower Protocol Card
c_proto, tf_proto = builder.add_card(s5, Inches(0.8), Inches(5.15), Inches(11.733), Inches(1.7), title="Giao Thức RESTful & Hợp Đồng Dữ Liệu (REST API Contracts)", title_color=PRIMARY_BLUE, bg_color=CARD_ACCENT_BG)
for b in [
    "GET /api/health -> {status, retrieval, retrieval_passages, reader, tts_engine, frontend_served}.",
    "POST /api/stt (multipart audio) -> {text}.",
    "POST /api/retrieve {question, top_k?} -> {passages:[{id,text,score}]} trên kb_index.json + kb_wiki_full.",
    "POST /api/answer {question, passage} -> {answer}.",
    "POST /api/tts {text, engine?, voice?, rate?} -> file audio."
]:
    p = tf_proto.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(2)

# SLIDE 6
s6_notes = """Ở phân hệ STT, mục tiêu là nhận dạng tiếng Việt chính xác có dấu trên CPU với mức chiếm dụng bộ nhớ hợp lý.
Nhóm triển khai mô hình Whisper-small được fine-tune LoRA trên 50 giờ dữ liệu VietSpeech, sau đó chuyển đổi sang CTranslate2 với lượng tử hóa INT8.
Kết quả đánh giá trên 1.802 mẫu test VietSpeech cho thấy: mô hình đạt tỷ lệ lỗi từ WER 13,77% và tỷ lệ lỗi ký tự CER 6,67%, giảm hơn 22,9 điểm phần trăm WER so với mô hình Whisper-small gốc chưa fine-tune có WER 36,76% và CER 19,43%.
Về tài nguyên, thư viện CTranslate2 giúp giảm đáng kể bộ nhớ RAM và tăng tốc tính toán ma trận trên CPU. Trong môi trường Docker CPU, thời gian nhận dạng thực tế mất khoảng 3 giây cho một câu hỏi đàm thoại, đáp ứng tốt yêu cầu xử lý cục bộ của đồ án."""

s6 = builder.add_content_slide(
    category="Phần 2: Kiến trúc & STT",
    title="Phân Hệ STT: Whisper-small LoRA 50h & CTranslate2",
    presenter="Huỳnh Công Lương",
    time_str="6:45 - 8:15 (90s)",
    notes_text=s6_notes
)

c_s6_l, tf_s6_l = builder.add_card(s6, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Mô Hình STT Triển Khai & Faster-Whisper", title_color=PRIMARY_BLUE)
for b in [
    "Kiến trúc Transformer Encoder-Decoder đa nhiệm, được huấn luyện trên 680.000 giờ âm thanh đa ngữ.",
    "Mô hình triển khai: Whisper-small fine-tune LoRA 50h VietSpeech -> CTranslate2 int8.",
    "WER 13,77% / CER 6,67% trên 1.802 mẫu test VietSpeech (Whisper small gốc: 36,76% / 19,43%).",
    "PyTorch Whisper gốc (một lần đo riêng): tiêu tốn ~1.8GB RAM, suy luận trên CPU ~3.8s cho câu hỏi 3s.",
    "Giải pháp CTranslate2: Thư viện C++ tối ưu hóa toán tử ma trận, tích hợp bộ cấp phát bộ nhớ tùy biến riêng.",
    "Lượng tử hóa INT8 (compute_type='int8'): Giảm kích thước trọng số 4 lần mà không suy hao độ chính xác nhận dạng từ."
]:
    p = tf_s6_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s6_r, tf_s6_r = builder.add_card(s6, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="So Sánh Hiệu Năng Thực Nghiệm Trên CPU", title_color=TEAL)
whisper_stats = [
    ("Tốc độ suy luận (Inference Speed)", "Nhanh gấp 4.1 lần so với Whisper PyTorch gốc"),
    ("Tiêu thụ bộ nhớ RAM", "Giảm 65% (Từ 1.8 GB xuống còn 540 MB)"),
    ("Kích thước mô hình (Weights)", "Model 'small': 244M tham số, điểm cân bằng vàng"),
    ("WER / CER (1.802 mẫu test VietSpeech)", "13,77% / 6,67% (Whisper small gốc: 36,76% / 19,43%)"),
    ("Độ trễ câu hỏi 3s (Docker CPU)", "Khoảng 3 giây trong Docker; khác cấu hình đo 3.8s của PyTorch ở trên")
]
for title_w, val_w in whisper_stats:
    p = tf_s6_r.add_paragraph()
    p.text = f"• {title_w}:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_before = Pt(8)
    p_v = tf_s6_r.add_paragraph()
    p_v.text = f"  → {val_w}"
    p_v.font.size = Pt(10.5)
    p_v.font.color.rgb = TEXT_DARK
    p_v.space_before = Pt(2)

# SLIDE 7
s7_notes = """Hai giải pháp tối ưu quan trọng ở phân hệ STT là bộ lọc VAD và cơ chế Lazy Loading:
Khi người dùng bấm mic thu âm, đoạn âm thanh luôn chứa khoảng lặng trước và sau câu nói. Nếu nạp toàn bộ vào Whisper, mô hình vừa tốn thời gian giải mã vừa dễ bị lặp từ. Nhóm đã bật bộ lọc VAD tích hợp trong Faster-Whisper để tự động cắt các đoạn im lặng và tạp âm nền, giúp giảm 30 đến 40% thời lượng âm thanh cần đưa vào giải mã.
Thứ hai, việc nạp mô hình AI ngay khi khởi động server thường mất 15 đến 20 giây, khiến Docker Healthcheck dễ báo timeout. Nhóm áp dụng mẫu thiết kế Thread-Safe Lazy Loading với Lock trong Python: server FastAPI khởi động nhanh trong khoảng 0,45 giây để mở cổng mạng; mô hình chỉ nạp vào RAM ở request đầu tiên và được lưu trữ tĩnh phục vụ xuyên suốt phiên làm việc."""

s7 = builder.add_content_slide(
    category="Phần 2: Kiến trúc & STT",
    title="Tối Ưu Hóa STT: Voice Activity Detection (VAD) & Lazy Loading",
    presenter="Huỳnh Công Lương",
    time_str="8:15 - 9:30 (75s)",
    notes_text=s7_notes
)

c_s7_l, tf_s7_l = builder.add_card(s7, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Bộ Lọc Voice Activity Detection (VAD)", title_color=PRIMARY_BLUE)
for b in [
    "Vấn đề thực tế: Người dùng thu âm luôn có khoảng lặng 0.5s - 1.0s ở đầu và cuối bản ghi.",
    "Nguy cơ: Đưa khoảng lặng vào Transformer tốn thời gian giải mã và dễ gây hiện tượng lặp từ (hallucination).",
    "Giải pháp: Bật bộ lọc VAD tích hợp trong Faster-Whisper (vad_filter=True, dựa trên Silero VAD).",
    "Tự động phát hiện biên độ hoạt tính tiếng nói, cắt bỏ vùng im lặng và tạp âm nền trước khi giải mã.",
    "Kết quả: Giảm 30-40% thời lượng âm thanh cần đưa vào bộ giải mã."
]:
    p = tf_s7_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s7_r, tf_s7_r = builder.add_card(s7, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="Mẫu Thiết Kế Thread-Safe Lazy Loading", title_color=TEAL)
for b in [
    "Vấn đề: Nạp mô hình lúc server khởi động làm Docker bị nghẽn (hang) 15-20s, dễ bị Healthcheck kill.",
    "Thiết kế: Áp dụng cơ chế Double-Checked Locking với threading.Lock() trong speech-to-text_Luong/stt_server.py.",
    "Server FastAPI khởi động trong 0.45s, mở cổng 8090 (Docker map 8090 -> 8000) và vượt qua bài test Docker ngay.",
    "Trọng số mô hình chỉ được nạp ở request đầu tiên khi có người dùng thực tế gọi mic.",
    "Sau khi nạp, mô hình được lưu trong bộ nhớ tĩnh và phục vụ liên tục cho toàn bộ các request sau."
]:
    p = tf_s7_r.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# SLIDE 8
s8_notes = """Khâu xử lý tín hiệu âm thanh phía client đóng vai trò then chốt cho chất lượng nhận dạng:
Trình duyệt thông thường thu âm qua micro với tần số 44.1kHz hoặc 48kHz dạng Stereo 2 kênh. Nếu tải trực tiếp dữ liệu thô này lên server, dung lượng file rất lớn và server phải mất chu kỳ CPU gọi ffmpeg để giải mã.
Nhóm đã phát triển module xử lý âm thanh trực tiếp trên Web Client bằng Web Audio API của Angular: tín hiệu từ micro được giải mã qua AudioContext, gộp thành 1 kênh mono và thực hiện hạ mẫu qua OfflineAudioContext về đúng chuẩn 16.000 Hz, 16-bit Linear PCM WAV theo yêu cầu của Whisper.
Nhờ xử lý trước tại client, kích thước file âm thanh giảm hơn 85%, chỉ còn khoảng 60KB cho một câu nói 2 giây, giúp truyền tải qua mạng gần như tức thời và giải phóng hoàn toàn gánh nặng chuyển đổi định dạng ở backend."""

s8 = builder.add_content_slide(
    category="Phần 2: Kiến trúc & STT",
    title="Xử Lý Tín Hiệu Âm Thanh Phía Client (Web Audio API & PCM 16kHz)",
    presenter="Huỳnh Công Lương",
    time_str="9:30 - 11:00 (90s)",
    notes_text=s8_notes
)

c_s8_1, tf_s8_1 = builder.add_card(s8, Inches(0.8), Inches(1.5), Inches(3.72), Inches(5.35), title="1. Thu Âm Trình Duyệt", title_color=PRIMARY_BLUE)
for b in [
    "Sử dụng navigator.mediaDevices.getUserMedia({ audio: true }).",
    "Bảo mật: Yêu cầu cấp quyền micro an toàn trên giao thức HTTP localhost và HTTPS.",
    "Khởi tạo AudioContext kết hợp ScriptProcessor / AudioWorklet để bắt chuỗi mẫu nhị phân trong lúc thu âm."
]:
    p = tf_s8_1.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s8_2, tf_s8_2 = builder.add_card(s8, Inches(4.8), Inches(1.5), Inches(3.72), Inches(5.35), title="2. Thuật Toán Downsampling", title_color=TEAL)
for b in [
    "Micro máy tính mặc định: 44.1kHz hoặc 48kHz Stereo (2 kênh âm thanh).",
    "Yêu cầu của Whisper: 16.000 Hz, Linear PCM 16-bit, Đơn kênh (Mono).",
    "Thực hiện thuật toán nội suy tuyến tính (Linear Interpolation) hạ mẫu trực tiếp trên Client.",
    "Đóng gói định dạng chuẩn RIFF WAV header hoàn chỉnh trước khi gửi đi."
]:
    p = tf_s8_2.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s8_3, tf_s8_3 = builder.add_card(s8, Inches(8.8), Inches(1.5), Inches(3.72), Inches(5.35), title="3. Lợi Ích Hiệu Năng", title_color=GREEN)
for b in [
    "Giảm tải băng thông mạng: Dung lượng file câu hỏi 2s giảm từ 400KB xuống còn ~60KB (tiết kiệm 85%).",
    "Giảm tải chu kỳ CPU Backend: Server không cần gọi lệnh chuyển đổi ffmpeg phụ trợ.",
    "Thời gian tải lên qua mạng gần như tức thì (< 20ms trên mạng nội bộ hoặc WiFi)."
]:
    p = tf_s8_3.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# ==============================================================================
# PHẦN 3: PHÂN HỆ CỐT LÕI: RETRIEVAL & ĐỌC HIỂU MRC (Slides 9 - 13)
# ==============================================================================

# SLIDE 9
s9_notes = """Kính thưa Thầy Cô, em là Ngô Trí Huy, xin tiếp tục trình bày Phân hệ Truy xuất Ngữ cảnh và Mô hình Đọc hiểu MRC.
Khác với bài toán đọc hiểu lý thuyết nơi câu hỏi luôn có sẵn bài đọc đi kèm, trong hệ thống Voice Q&A thực tế, người dùng chỉ đặt một câu hỏi ngắn gọn. Hệ thống phải tự tìm trong kho tài liệu để xác định đoạn văn chứa câu trả lời.
Thách thức lớn là sự bất đối xứng độ dài: câu hỏi người dùng chỉ có 5 đến 10 từ khóa, trong khi mỗi đoạn văn dài hàng trăm từ. Hơn nữa, việc tìm kiếm ứng viên ở tầng 1 cần diễn ra rất nhanh, chỉ khoảng 15 mili-giây, để nhường quỹ thời gian cho mô hình reranker và mô hình đọc hiểu nơ-ron phía sau. Nếu truy xuất sai đoạn văn, toàn bộ pipeline phía sau chắc chắn sẽ đưa ra câu trả lời không chính xác."""

s9 = builder.add_content_slide(
    category="Phần 3: Retrieval & MRC",
    title="Phân Hệ Retrieval: Bài Toán Tìm Kiếm Ngữ Cảnh Open-Domain",
    presenter="Ngô Trí Huy (Lead)",
    time_str="11:00 - 12:15 (75s)",
    notes_text=s9_notes
)

c_s9_l, tf_s9_l = builder.add_card(s9, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Sự Khác Biệt Giữa Closed vs Open-Domain", title_color=PRIMARY_BLUE)
for b in [
    "Bài toán MRC lý thuyết (Closed-Domain): Bài đọc luôn được cung cấp sẵn cùng câu hỏi -> Mô hình chỉ việc trích xuất hoặc xếp hạng.",
    "Hệ thống Voice Q&A thực tế (Open-Domain): Người dùng chỉ hỏi một câu ngắn bằng giọng nói, hoàn toàn không chỉ định bài đọc.",
    "Nhiệm vụ của Phân hệ Retrieval: Quét kho tri thức hai tầng (5.869 đoạn + 1,48 triệu đoạn Wikipedia), định vị chính xác bài đọc chứa bằng chứng đúng.",
    "Nếu Retrieval sai bài đọc -> Cả mô hình MRC phía sau chắc chắn sẽ trả lời sai (Garbage In, Garbage Out)."
]:
    p = tf_s9_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s9_r, tf_s9_r = builder.add_card(s9, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="Thách Thức & Ràng Buộc Kỹ Thuật", title_color=TEAL)
for b in [
    "Bất cân xứng độ dài: Câu hỏi ngắn 5 - 10 từ vs Bài đọc dài 300 - 800 từ (Query-Document Asymmetry).",
    "Hiện tượng nhiễu từ vựng: Nhiều bài đọc cùng chủ đề (ví dụ: các bài về danh nhân lịch sử) có nhiều từ vựng chung gây phân tán điểm số.",
    "Chi phí thời gian: BM25 tầng 1 ~15 ms; toàn bộ truy xuất lai + reranker ~6 giây/câu.",
    "Giải pháp: Cải tiến giải thuật BM25 kết hợp tăng trọng số từ ghép tiếng Việt (Bigram Boost)."
]:
    p = tf_s9_r.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# SLIDE 10
s10_notes = """Để tầng truy xuất BM25 vừa nhẹ vừa chính xác, em đã cải tiến thuật toán BM25 qua hai bước:
Thứ nhất, trên công thức Okapi BM25, em tinh chỉnh siêu tham số k1 lên 2,1 để tăng độ bão hòa với các từ khóa trọng tâm lặp lại, và đặt b bằng 1,0 để chuẩn hóa mạnh theo độ dài của văn bản, thay cho cấu hình mặc định của Lucene vốn chưa tối ưu cho các bài đọc chênh lệch độ dài.
Thứ hai, tiếng Việt có đặc thù từ ghép rất mạnh; nếu tách rời các từ như 'Điện' và 'Biên', điểm số sẽ bị loãng. Em đề xuất cơ chế Bigram Phrase Boost: trích xuất các cặp từ liền kề trong câu hỏi; nếu đoạn văn chứa đúng cụm từ theo đúng thứ tự, đoạn văn được cộng thêm 0,4 điểm thưởng nhân trọng số IDF. Kỹ thuật này giúp phân biệt rõ nghĩa từ ghép và tăng độ chính xác truy xuất rõ rệt."""

s10 = builder.add_content_slide(
    category="Phần 3: Retrieval & MRC",
    title="Tinh Chỉnh Thuật Toán BM25 & Cơ Chế Bigram Phrase Boost",
    presenter="Ngô Trí Huy (Lead)",
    time_str="12:15 - 13:30 (75s)",
    notes_text=s10_notes
)

c_s10_t, tf_s10_t = builder.add_card(s10, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.8), title="Công Thức Toán Học Okapi BM25 & Hai Siêu Tham Số", title_color=PRIMARY_BLUE)
p_f = tf_s10_t.add_paragraph()
p_f.text = "Score(D, Q) = ∑ [ IDF(q_i) * ( f(q_i, D) * (k1 + 1) ) / ( f(q_i, D) + k1 * (1 - b + b * (|D| / avgdl)) ) ]"
p_f.font.size = Pt(12)
p_f.font.bold = True
p_f.font.color.rgb = TECH_BLUE
p_f.alignment = PP_ALIGN.CENTER
p_f.space_before = Pt(4)

for det_line in [
    "• Tinh chỉnh k1 = 2.1 (Mặc định 1.2): Tăng độ bão hòa tần suất từ khóa, ưu tiên các bài đọc có từ khóa chuyên biệt lặp lại.",
    "• Tinh chỉnh b = 1.0 (Mặc định 0.75): Chuẩn hóa mạnh theo độ dài đoạn văn, hạn chế việc các bài đọc dài chiếm ưu thế điểm số."
]:
    p_det = tf_s10_t.add_paragraph()
    p_det.text = det_line
    p_det.font.size = Pt(10.5)
    p_det.font.color.rgb = TEXT_DARK
    p_det.space_before = Pt(3)

c_s10_l, tf_s10_l = builder.add_card(s10, Inches(0.8), Inches(3.45), Inches(5.6), Inches(3.4), title="Đặc Thù Từ Ghép Tiếng Việt", title_color=TEAL)
for b in [
    "Tiếng Việt đơn lập: Một từ có thể gồm 2 tiếng ghép lại ('Điện Biên', 'Văn Miếu', 'Quốc Tử Giám').",
    "Nếu chỉ tách từ đơn lẻ (Unigram), điểm số bị loãng vì từ 'Văn' hay 'Biên' xuất hiện khắp nơi.",
    "Cần một cơ chế nhận biết trật tự từ liền kề mà không làm tăng độ phức tạp thuật toán."
]:
    p = tf_s10_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(6)

c_s10_r, tf_s10_r = builder.add_card(s10, Inches(6.7), Inches(3.45), Inches(5.833), Inches(3.4), title="Giải Pháp Bigram Phrase Boost (+0.4)", title_color=GREEN)
for b in [
    "Trích xuất tất cả các cặp từ 2 tiếng liền kề (w_i, w_{i+1}) trong câu hỏi của người dùng.",
    "Nếu văn bản chứa chính xác cụm 2 tiếng đó theo đúng thứ tự -> Cộng thêm điểm thưởng:",
    "Score_Boost = Score_BM25 + 0.4 * IDF(Bigram).",
    "Giúp hệ thống phân biệt chính xác giữa 'nhà trường' với 'trường hợp' hoặc 'nhà cửa'."
]:
    p = tf_s10_r.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(6)

# SLIDE 11
s11_notes = """Hiệu quả của việc tinh chỉnh BM25 được chứng minh qua thực nghiệm ablation trên 564 câu hỏi Dev đối chiếu với kho ViMMRC 552 bài đọc ban đầu:
Với BM25 mặc định, Recall@1 đạt 64,18% và Recall@5 đạt 79,96%. Khi tinh chỉnh k1 và b, Recall@1 tăng lên 68,79%. Khi kết hợp thêm Bigram Phrase Boost, Recall@1 đạt 71,45% và Recall@5 đạt tới 83,69%, chỉ số MRR@5 đạt 0,7624.
Điều này khẳng định rằng trong đại đa số trường hợp, đoạn văn chứa câu trả lời đúng luôn nằm ở vị trí thứ nhất hoặc thứ hai trong danh sách xếp hạng.
Về tốc độ, thời gian quét BM25 tầng 1 chỉ mất khoảng 15 mili-giây trên CPU. Đây là tiền đề vững chắc trước khi nhóm mở rộng quy mô kho dữ liệu sang kiến trúc hai tầng toàn diện."""

s11 = builder.add_content_slide(
    category="Phần 3: Retrieval & MRC",
    title="Ablation Tinh Chỉnh BM25 (Kho ViMMRC 552 Bài, 564 Câu Dev)",
    presenter="Ngô Trí Huy (Lead)",
    time_str="13:30 - 14:45 (75s)",
    notes_text=s11_notes
)

headers_s11 = ["Cấu Hình Thuật Toán", "Recall@1 (%)", "Recall@3 (%)", "Recall@5 (%)", "MRR@5", "Thời Gian TB (ms)"]
rows_s11 = [
    ["BM25 Mặc định (k1=1.2, b=0.75)", "64.18%", "75.89%", "79.96%", "0.7042", "12.3 ms"],
    ["BM25 Tinh chỉnh (k1=2.1, b=1.0)", "68.79%", "79.43%", "82.27%", "0.7415", "12.5 ms"],
    ["BM25 Tinh chỉnh + Bigram Boost", "71.45%", "80.85%", "83.69%", "0.7624", "14.8 ms"]
]
col_w_s11 = [Inches(3.4), Inches(1.6), Inches(1.6), Inches(1.6), Inches(1.6), Inches(1.933)]
builder.add_table(s11, Inches(0.8), Inches(1.5), Inches(11.733), Inches(2.2), headers_s11, rows_s11, col_w_s11)

c_s11_bot, tf_s11_b = builder.add_card(s11, Inches(0.8), Inches(4.0), Inches(11.733), Inches(2.85), title="Phân Tích Chi Tiết Hiệu Quả Thực Nghiệm", title_color=PRIMARY_BLUE)
for b in [
    "Recall@1 đạt 71.45%: Hơn 7 trên 10 câu hỏi người dùng đặt ra được hệ thống định vị chính xác bài đọc ngay ở vị trí xếp hạng số 1.",
    "Recall@5 đạt 83.69%: Khi lấy Top 5 bài đọc đưa vào mô hình đọc hiểu, xác suất chứa bài đọc đúng lên tới gần 84%.",
    "MRR@5 đạt 0.7624: Chỉ số nghịch đảo thứ hạng trung bình rất cao, chứng minh bài đọc đúng luôn tập trung ở thứ hạng 1 và 2.",
    "BM25 tầng 1 ~15 ms; toàn bộ truy xuất lai + reranker ~6 giây/câu.",
    "Kết quả này là ablation cũ trên kho ViMMRC 552 đoạn; hệ thống hiện tại dùng kho hai tầng 5.869 đoạn + 1,48 triệu đoạn Wikipedia."
]:
    p = tf_s11_b.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(6)

# SLIDE 12
s12_notes = """Để trả lời các câu hỏi kiến thức mở, nhóm đã xây dựng kho tri thức hai tầng cho RAG:
Tầng 1 gồm 5.869 đoạn văn chọn lọc từ ViMMRC và ViQuAD. Tầng 2 gồm 1,48 triệu đoạn trích từ Wikipedia tiếng Việt, được đánh chỉ mục kép: BM25 chia shard và chỉ mục vector dense multilingual-e5-small 384 chiều lưu float16 khoảng 1,1 GB.
Với mỗi câu hỏi, hệ thống lấy top 3 từ BM25 tầng 1, top 3 từ BM25 Wikipedia và top 3 từ dense Wikipedia, tổng cộng tối đa 9 ứng viên. Reranker cross-encoder bge-reranker-v2-m3 chấm điểm chung tất cả ứng viên, trong đó đoạn tầng 1 được cộng ưu tiên 0,25 điểm.
Đánh giá trên tập test 2.545 câu, BM25 hai tầng đạt Recall@1 71,1% và Recall@5 85,9%. Khi có reranker, F1 câu trả lời trên câu kiến thức mở tăng từ 15,4 lên 24,3, và câu có trong kho tăng từ 58,0 lên 60,7, cho thấy hiệu quả rõ rệt của kiến trúc truy xuất lai hai tầng."""

s12 = builder.add_content_slide(
    category="Phần 3: Retrieval & MRC",
    title="Retrieval: Kho Tri Thức Hai Tầng Cho RAG",
    presenter="Ngô Trí Huy (Lead)",
    time_str="14:45 - 16:00 (75s)",
    notes_text=s12_notes
)

c_s12_l, tf_s12_l = builder.add_card(s12, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Kiến Trúc Kho Tri Thức", title_color=PRIMARY_BLUE)
for b in [
    "Tầng 1: 5.869 đoạn văn ViMMRC + ViQuAD (BM25, k1=2.1, b=1.0, bigram boost).",
    "Tầng 2: 1,48 triệu đoạn Wikipedia tiếng Việt (≤800 ký tự/đoạn), có cả chỉ mục BM25 (bm25s, chia shard) và vector dense (multilingual-e5-small, 384 chiều, float16 mmap ~1,1 GB).",
    "Ứng viên: top-3 BM25 tầng 1 + top-3 BM25 Wikipedia + top-3 dense Wikipedia (≤9).",
    "Reranker bge-reranker-v2-m3 (cross-encoder) chấm chung; đoạn tầng 1 được cộng +0,25, điểm cao nhất thắng.",
    "Đoạn văn đọc từ đĩa theo offset, không nạp toàn bộ kho vào RAM."
]:
    p = tf_s12_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s12_r, tf_s12_r = builder.add_card(s12, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="Kết Quả Đánh Giá Retrieval", title_color=TEAL)
mrc_stats = [
    ("Test 2.545 câu, BM25 hai tầng (trước reranker): R@1 / R@5", "71,1% / 85,9%"),
    ("Câu hỏi ViQuAD (2.156 câu)", "R@1 73,2% / R@5 88,9%"),
    ("Câu hỏi ViMMRC (389 câu)", "R@1 59,4% / R@5 69,2%"),
    ("Answer F1, 200 câu trong kho / 200 câu mở: BM25 thuần", "58,0 / 15,4"),
    ("Answer F1: reranker + ưu tiên kho +0,25 (đang dùng)", "60,7 / 24,3"),
    ("Thời gian truy xuất + reranker / câu", "~6 giây trên CPU")
]
for title_m, val_m in mrc_stats:
    p = tf_s12_r.add_paragraph()
    p.text = f"• {title_m}:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_before = Pt(8)
    p_v = tf_s12_r.add_paragraph()
    p_v.text = f"  → {val_m}"
    p_v.font.size = Pt(10.5)
    p_v.font.color.rgb = TEXT_DARK
    p_v.space_before = Pt(2)

# SLIDE 13
s13_notes = """Sau khi có đoạn văn ngữ cảnh, nhóm sử dụng mô hình ViT5-base của VietAI để đọc hiểu và sinh câu trả lời tự do, không cần các phương án trắc nghiệm sẵn có.
Về giới hạn ngữ cảnh 512 token: nhiều bài đọc dài từ 800 đến 1.200 từ. Nhóm đã thử nghiệm chọn lọc phân đoạn ngữ cảnh theo câu hỏi nhưng độ chính xác không cải thiện, do đó nhóm chọn giải pháp chuẩn hóa lấy 512 token đầu của đoạn văn.
Kết quả huấn luyện mô hình ViT5 trên bộ dữ liệu mở rộng đạt Exact Match 41,05% và token F1 66,55% trên 2.716 câu test độc lập. Khi chạy toàn chuỗi từ khâu truy xuất đến sinh câu trả lời, F1 toàn chuỗi đạt 53,9%, khẳng định mô hình sinh câu trả lời chuẩn xác và mạch lạc."""

s13 = builder.add_content_slide(
    category="Phần 3: Retrieval & MRC",
    title="Phân Hệ MRC: ViT5 Seq2Seq & Giới Hạn 512 Token",
    presenter="Ngô Trí Huy (Lead)",
    time_str="16:00 - 17:00 (60s)",
    notes_text=s13_notes
)

c_s13_l, tf_s13_l = builder.add_card(s13, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Mô Hình Sinh Chuỗi ViT5 (VietAI)", title_color=PRIMARY_BLUE)
for b in [
    "Kiến trúc Transformer Sequence-to-Sequence (Text-to-Text Transfer Transformer).",
    "Được VietAI tiền huấn luyện chuyên sâu trên kho ngữ liệu tiếng Việt quy mô lớn.",
    "Nhiệm vụ: Generative QA. Test 2.716 câu (bộ gộp): EM 41,05 / F1 66,55.",
    "Toàn chuỗi BM25 -> ViT5: F1 53,9 (đưa đúng đoạn văn: F1 68,6).",
    "Đầu vào: 'context: <ngữ cảnh> question: <câu hỏi>'.",
    "Đầu ra: Tự động sinh chuỗi câu trả lời hoàn chỉnh ngữ pháp tiếng Việt."
]:
    p = tf_s13_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s13_r, tf_s13_r = builder.add_card(s13, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="Giới Hạn 512 Token & Chọn Ngữ Cảnh", title_color=TEAL)
for b in [
    "Vấn đề 512 Token Ceiling: Bài đọc dài tới 1.200 từ; cắt ở đầu bài có thể làm mất bằng chứng ở cuối bài.",
    "Đã thử chọn ngữ cảnh theo câu hỏi (question_chunks) nhưng không cải thiện.",
    "Mặc định cắt 512 token đầu (head).",
    "Kết quả hiện tại: EM 41,05 / F1 66,55 trên 2.716 câu test; toàn chuỗi F1 53,9."
]:
    p = tf_s13_r.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# ==============================================================================
# PHẦN 4: PHÂN HỆ TỔNG HỢP TIẾNG NÓI TIÊN TIẾN TTS (Slides 14 - 18)
# ==============================================================================

# SLIDE 14
s14_notes = """Kính thưa Thầy Cô, em là Trương Hoàng Duy, xin báo cáo về Phân hệ Tổng hợp Tiếng nói (TTS) và Bộ benchmark đánh giá âm học.
Phân hệ TTS là điểm chạm trực tiếp quyết định cảm nhận của người dùng. Một câu trả lời chính xác nhưng giọng đọc khô cứng hay sai thanh điệu sẽ làm giảm trải nghiệm tương tác.
Tổng quan các thế hệ TTS: Tacotron2 hay FastSpeech2 dễ bị nhòe phổ Mel; mô hình VITS có cấu trúc tiềm ẩn phức tạp, khó kiểm soát cao độ; trong khi các mô hình Diffusion như Grad-TTS tuy hay nhưng cần 50 đến 100 bước khử nhiễu lặp lại, quá chậm để chạy trên CPU.
Nhóm đã làm chủ kiến trúc mới nhất: Matcha-TTS từ hội nghị ICASSP 2024. Dựa trên Flow Matching, Matcha-TTS cho chất lượng âm thanh tự nhiên như Diffusion nhưng giải mã cực nhanh, chỉ cần 10 bước tính toán trên CPU thông thường."""

s14 = builder.add_content_slide(
    category="Phần 4: Phân hệ TTS Tiên tiến",
    title="Phân Hệ TTS: Tiến Trình Công Nghệ & Lựa Chọn Matcha-TTS",
    presenter="Trương Hoàng Duy",
    time_str="17:00 - 18:15 (75s)",
    notes_text=s14_notes
)

c_s14_1, tf_s14_1 = builder.add_card(s14, Inches(0.8), Inches(1.5), Inches(3.72), Inches(5.35), title="1. Mô Hình Truyền Thống", title_color=PRIMARY_BLUE)
for b in [
    "Tacotron2 / FastSpeech2: Dựa trên hồi quy MSE trực tiếp trên Mel-spectrogram.",
    "Nhược điểm: Âm thanh bị mờ nhòe (over-smoothing), giọng đọc kim loại, thiếu độ rung tự nhiên.",
    "VITS (VAE + GAN): Cải thiện đáng kể nhưng cấu trúc quá cồng kềnh, khó kiểm soát thanh điệu tiếng Việt."
]:
    p = tf_s14_1.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s14_2, tf_s14_2 = builder.add_card(s14, Inches(4.8), Inches(1.5), Inches(3.72), Inches(5.35), title="2. Mô Hình Diffusion", title_color=TEAL)
for b in [
    "Grad-TTS / Diff-TTS: Dựa trên quá trình khử nhiễu ngẫu nhiên phân tán.",
    "Ưu điểm: Âm thanh trong trẻo, tự nhiên, phổ Mel sắc nét.",
    "Nhược điểm lớn: Tốc độ suy luận chậm, thường cần 50 đến 100 bước lặp SDE/ODE nên khó chạy nhanh trên CPU."
]:
    p = tf_s14_2.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s14_3, tf_s14_3 = builder.add_card(s14, Inches(8.8), Inches(1.5), Inches(3.72), Inches(5.35), title="3. Matcha-TTS (ICASSP 2024)", title_color=GREEN)
for b in [
    "Kỹ thuật Flow Matching: Kết hợp chất lượng âm thanh của Diffusion với quỹ đạo giải tích gọn nhẹ.",
    "Đường vận chuyển tối ưu: Giải ODE nhanh (10 bước Euler trong benchmark trên CPU).",
    "Đạt hệ số RTF 0.52 trên CPU thông thường mà không cần GPU.",
    "Phù hợp cho hệ thống Voice Q&A chạy cục bộ trên CPU."
]:
    p = tf_s14_3.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# SLIDE 15
s15_notes = """Về nguyên lý toán học, sự khác biệt lớn nhất giữa Flow Matching và Diffusion nằm ở quỹ đạo xác suất:
Trong Diffusion tiêu chuẩn, quá trình khuếch tán vi phân SDE tạo ra quỹ đạo cong uốn lượn ngẫu nhiên trong không gian vector, buộc mô hình phải bước từng bước rất nhỏ để không lệch hướng, tốn hàng chục bước lặp.
Ngược lại, Matcha-TTS áp dụng lý thuyết Optimal Transport Conditional Flow Matching: ép trường vector đạo hàm di chuyển theo đường thẳng tối ưu nối trực tiếp từ nhiễu Gaussian x0 đến Mel-spectrogram đích x1.
Vì quỹ đạo là đường thẳng tuyến tính, phương trình vi phân ODE có thể giải bằng phương pháp Euler chỉ trong đúng 10 bước lặp. Nhờ đó, Matcha-TTS giữ được độ chi tiết âm thanh của Diffusion nhưng tốc độ suy luận nhanh gấp nhiều lần, hoàn toàn khả thi khi chạy trên CPU."""

s15 = builder.add_content_slide(
    category="Phần 4: Phân hệ TTS Tiên tiến",
    title="Nguyên Lý Toán Học Conditional Flow Matching (OT-CFM)",
    presenter="Trương Hoàng Duy",
    time_str="18:15 - 19:45 (90s)",
    notes_text=s15_notes
)

c_s15_t, tf_s15_t = builder.add_card(s15, Inches(0.8), Inches(1.5), Inches(11.733), Inches(2.2), title="Bản Chất Toán Học Của Optimal-Transport Flow Matching", title_color=PRIMARY_BLUE)
p_ode = tf_s15_t.add_paragraph()
p_ode.text = "Phương trình Vi phân Thường (ODE):   d phi_t(x) / dt = v_t(phi_t(x)),   phi_0(x) = x_0 ~ N(0, I)"
p_ode.font.size = Pt(12)
p_ode.font.bold = True
p_ode.font.color.rgb = TECH_BLUE
p_ode.alignment = PP_ALIGN.CENTER
p_ode.space_before = Pt(4)

p_traj = tf_s15_t.add_paragraph()
p_traj.text = "Quỹ đạo Đường Thẳng Tối Ưu (Straight Line):   psi_t(x) = (1 - (1 - sigma_min)t) * x_0 + t * x_1"
p_traj.font.size = Pt(12)
p_traj.font.bold = True
p_traj.font.color.rgb = TEAL
p_traj.alignment = PP_ALIGN.CENTER
p_traj.space_before = Pt(4)

c_s15_l, tf_s15_l = builder.add_card(s15, Inches(0.8), Inches(3.85), Inches(5.6), Inches(3.0), title="Quỹ Đạo Tuyến Tính vs Quỹ Đạo Cong", title_color=PRIMARY_BLUE)
for b in [
    "Diffusion truyền thống (SDE/ODE): Quỹ đạo cong uốn lượn do quá trình ngẫu nhiên brownian -> Cần 50-100 bước để khử nhiễu.",
    "Optimal Transport Flow Matching: Ép trường vector vận tốc di chuyển thẳng tắp giữa nhiễu Gaussian và Mel-spectrogram đích.",
    "Bộ giải Euler 10 bước (NFE = 10): Tích phân số học theo đường thẳng cho phép bước nhảy lớn mà không tích tụ sai số."
]:
    p = tf_s15_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(6)

c_s15_r, tf_s15_r = builder.add_card(s15, Inches(6.7), Inches(3.85), Inches(5.833), Inches(3.0), title="Hàm Mất Mát CFM Huấn Luyện", title_color=GREEN)
for b in [
    "Hàm mục tiêu hồi quy trường vector (Vector Field Regression):",
    "L_CFM(theta) = E [ || v_t(psi_t(x_0); theta) - (x_1 - (1 - sigma_min)x_0) ||^2 ]",
    "Mạng nơ-ron học cách dự đoán hướng dịch chuyển tức thời của từng hạt âm học.",
    "Hội tụ ổn định, không gặp hiện tượng sụp đổ phân phối (Mode Collapse) như GAN."
]:
    p = tf_s15_r.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(6)

# SLIDE 16
s16_notes = """Đóng góp trọng tâm của nhóm ở phân hệ TTS là đề xuất frontend tách thanh điệu vi_tone_v2:
Tiếng Việt có 6 thanh điệu. Nếu để nguyên nguyên âm có dấu trong từ điển, từ vựng ký tự nở rộng gấp nhiều lần và mô hình coi các biến thể là ký tự rời rạc, rất khó học quy luật biến thiên cao độ F0.
Giải pháp vi_tone_v2 bóc tách thanh điệu thành token độc lập ở cuối mỗi âm tiết: 0 ngang, 1 sắc, 2 huyền, 3 hỏi, 4 ngã, 5 nặng. Ví dụ 'tiếng' tách thành 't i e n g' và token 1; 'hồ' thành 'h ô' và token 2; 'Việt' thành 'v i e t' và token 5.
Nhờ vậy, Text Encoder học tách biệt giữa âm vị và cao độ F0, giảm 70% kích thước từ điển và giảm rõ rệt hiện tượng lẫn lộn dấu hỏi, dấu ngã."""

s16 = builder.add_content_slide(
    category="Phần 4: Phân hệ TTS Tiên tiến",
    title="Đóng Góp Kỹ Thuật: Frontend Tách Thanh Điệu vi_tone_v2",
    presenter="Trương Hoàng Duy",
    time_str="19:45 - 21:00 (75s)",
    notes_text=s16_notes
)

c_s16_l, tf_s16_l = builder.add_card(s16, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Vấn Đề Bùng Nổ Từ Điển Ký Tự Có Dấu", title_color=PRIMARY_BLUE)
for b in [
    "Tiếng Việt có 6 thanh điệu: 0 (Ngang), 1 (Sắc), 2 (Huyền), 3 (Hỏi), 4 (Ngã), 5 (Nặng).",
    "Nếu giữ nguyên nguyên âm mang dấu (a, à, á, ả, ã, ạ, ă, ằ, ắ...): Từ vựng ký tự nở rộng gấp 5 lần.",
    "Mô hình coi 'á' và 'à' là hai âm vị xa lạ, không liên kết được bản chất cùng là âm /a/ khác cao độ.",
    "Hậu quả: Không gian biểu diễn bị phân mảnh, dễ phát âm sai dấu hoặc nuốt thanh điệu khi gặp từ ít phổ biến."
]:
    p = tf_s16_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s16_r, tf_s16_r = builder.add_card(s16, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="Cơ Chế Bóc Tách vi_tone_v2 Của Nhóm", title_color=TEAL)
tone_samples = [
    ("Nguyên lý:", "Tách thanh điệu thành token độc lập đặt ở cuối mỗi âm tiết."),
    ("Ví dụ 1:", "'tiếng'  →  t i e n g 1 (Thanh sắc)"),
    ("Ví dụ 2:", "'hồ'  →  h ô 2 (Thanh huyền)"),
    ("Ví dụ 3:", "'Việt'   →  v i e t 5 (Thanh nặng)"),
    ("Ví dụ 4:", "'Hồ Chí Minh' →  h ô 2   ch i 1   m i n h 0"),
    ("Lợi ích 1:", "Giảm 70% kích thước từ điển ký tự của Text Encoder."),
    ("Lợi ích 2:", "Text Encoder học riêng âm vị (Phoneme) và đường cong cao độ (Pitch Contour F0)."),
    ("Lợi ích 3:", "Giảm rõ rệt hiện tượng nhầm lẫn giữa dấu Hỏi và dấu Ngã.")
]
for title_t, val_t in tone_samples:
    p = tf_s16_r.add_paragraph()
    p.text = f"• {title_t} {val_t}"
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(6)

# SLIDE 17
s17_notes = """Trước khi tổng hợp âm thanh, văn bản câu trả lời đi qua module Text Normalizer chuyên biệt:
Câu trả lời do mô hình sinh ra thường chứa số liệu, ngày tháng lịch sử hoặc ký hiệu viết tắt. Nếu đưa nguyên văn bản thô vào TTS, mô hình sẽ đọc sai hoặc ngắt nghỉ không đúng chỗ.
Module normalizer của nhóm thiết lập 5 bộ quy tắc chuẩn hóa: đọc các định dạng ngày tháng như ngày bảy tháng năm, mở rộng số thập phân, tiền tệ và phần trăm ra chữ tiếng Việt có dấu, đồng thời chuyển đổi các nhãn đáp án dạng ngoặc đơn thành cụm từ rõ ràng.
Ngoài ra, bước hậu xử lý tự động chèn các khoảng nghỉ âm học 150 mili-giây tại dấu phẩy và 400 mili-giây tại dấu chấm, giúp giọng đọc phát ra có nhịp ngắt câu tự nhiên."""

s17 = builder.add_content_slide(
    category="Phần 4: Phân hệ TTS Tiên tiến",
    title="Phân Hệ Chuẩn Hóa Văn Bản Tiếng Việt (Text Normalizer)",
    presenter="Trương Hoàng Duy",
    time_str="21:00 - 22:15 (75s)",
    notes_text=s17_notes
)

rules = [
    ("1. Ngày - Tháng - Năm", "07/05/1954", "ngày bảy tháng năm năm một nghìn chín trăm năm mươi tư"),
    ("2. Số Thập phân & Đơn vị", "3.14  |  50 km/h", "ba phẩy một bốn  |  năm mươi ki-lô-mét trên giờ"),
    ("3. Tiền tệ & Tỷ lệ phần trăm", "100.000 VNĐ  |  85%", "một trăm nghìn đồng  |  tám mươi lăm phần trăm"),
    ("4. Nhãn Đáp án / Liệt kê", "(A) Nguyễn Du  hoặc  B. Hà Nội", "'Đáp án A: Nguyễn Du', 'Đáp án B: Hà Nội' (tránh đọc 'mở ngoặc đóng ngoặc')"),
    ("5. Khoảng Nghỉ Dấu Câu", "Chèn Pause theo cụm dấu câu", "150ms tại dấu phẩy (,), 250ms tại (; :), 400ms tại dấu chấm (. ! ?) tạo nhịp nghỉ")
]

for idx, (head_r, raw_r, out_r) in enumerate(rules):
    ry = Inches(1.5) + idx * Inches(1.08)
    card, tf_r = builder.add_card(s17, Inches(0.8), ry, Inches(11.733), Inches(0.98), title="", border_color=PRIMARY_BLUE)
    p0 = tf_r.paragraphs[0]
    p0.text = head_r.upper()
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = PRIMARY_BLUE
    p1 = tf_r.add_paragraph()
    p1.text = f"Đầu vào thô: {raw_r}   →   Chuẩn hóa: {out_r}"
    p1.font.size = Pt(10.5)
    p1.font.color.rgb = TEXT_DARK
    p1.space_before = Pt(2)

# SLIDE 18
s18_notes = """Nhóm đã thiết lập bộ benchmark âm học định lượng chuẩn quốc tế, so sánh trực tiếp Matcha-TTS với giọng phát thanh viên người thật và hai mô hình nền tảng VITS của Meta và Edge-TTS của Microsoft:
Về độ rõ chữ: khi dùng mô hình nhận dạng ASR PhoWhisper kiểm chứng lại, tỷ lệ lỗi ký tự CER của Matcha-TTS đạt 1,9%, thấp hơn hơn 2 lần so với mức 4,3% của VITS và gần mức trần 0,7% của người thật.
Về độ chuẩn cao độ: sai số log-F0 của Matcha đạt 2,86 bán cung, tiệm cận mô hình thương mại Edge-TTS là 2,69 bán cung và tốt hơn nhiều so với VITS.
Về tốc độ: hệ số RTF trên CPU đạt 0,52, nghĩa là chỉ mất khoảng nửa giây để tổng hợp một câu nói dài một giây, hoàn toàn đáp ứng yêu cầu đàm thoại thời gian thực mà không cần GPU."""

s18 = builder.add_content_slide(
    category="Phần 4: Phân hệ TTS Tiên tiến",
    title="Đánh Giá & Benchmark Định Lượng Âm Học Toàn Diện",
    presenter="Trương Hoàng Duy",
    time_str="22:15 - 23:30 (75s)",
    notes_text=s18_notes
)

headers_s18 = ["Mô Hình TTS", "MCD (dB) ↓", "F0 RMSE (Hz) ↓", "log-F0 RMSE (semitones) ↓", "CER ASR (%) ↓", "RTF (CPU) ↓", "Đặc Điểm Kiến Trúc"]
rows_s18 = [
    ["Giọng Người Thật (Tham chiếu)", "–", "–", "–", "0.7%", "–", "Ngưỡng trần kiểm chứng ASR PhoWhisper"],
    ["Matcha-TTS (Nhóm huấn luyện)", "5.35", "70.4", "2.86", "1.9%", "0.52", "OT-CFM cục bộ, frontend vi_tone_v2"],
    ["VITS MMS (Meta Pretrained)", "4.45", "84.1", "4.31", "4.3%", "0.38", "VAE End-to-End, giọng nam miền Bắc"],
    ["Edge-TTS (Hoài My Neural)", "4.63", "48.3", "2.69", "1.0%", "0.13", "Cloud Neural, phụ thuộc Internet"]
]
col_w_s18 = [Inches(2.8), Inches(1.3), Inches(1.5), Inches(2.2), Inches(1.3), Inches(1.2), Inches(1.433)]
builder.add_table(s18, Inches(0.8), Inches(1.5), Inches(11.733), Inches(2.5), headers_s18, rows_s18, col_w_s18)

c_s18_bot, tf_s18_b = builder.add_card(s18, Inches(0.8), Inches(4.3), Inches(11.733), Inches(2.55), title="Phân Tích Chuyên Sâu 3 Chỉ Số Âm Học Then Chốt", title_color=PRIMARY_BLUE)
for b in [
    "Độ Rõ Âm Vị (CER 1.9%): Matcha-TTS phát âm rõ chữ, tỷ lệ lỗi ký tự thấp hơn VITS hơn 2 lần và gần mức trần 0.7% của người thật.",
    "Độ Chuẩn Thanh Điệu (log-F0 2.86 bán cung): Nhờ frontend vi_tone_v2, sai số cao độ giảm sâu, tiệm cận mô hình thương mại Microsoft (2.69).",
    "Tốc độ TTS (RTF 0.52 CPU): TTS nhanh hơn thời gian thực trên CPU i5/i7, tạo 1 giây âm thanh chỉ mất 0.52 giây."
]:
    p = tf_s18_b.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(6)

# ==============================================================================
# PHẦN 5: KỸ NGHỆ HỆ THỐNG, DEMO & KẾT LUẬN (Slides 19 - 24)
# ==============================================================================

# SLIDE 19
s19_notes = """Về khía cạnh kỹ nghệ phần mềm, nhóm đã tích hợp toàn bộ hệ thống thành một ứng dụng Full-stack hoàn chỉnh:
Phía Backend, nhóm sử dụng FastAPI viết bằng Python 3.11. Toàn bộ 4 phân hệ được chuẩn hóa thành các REST API rõ ràng, hỗ trợ xử lý bất đồng bộ và tự động sinh tài liệu Swagger UI.
Phía Frontend, em xây dựng ứng dụng Angular với kiến trúc Standalone Components hiện đại. Giao diện Chat Voice trực quan hỗ trợ tương tác micro và hiển thị thanh trạng thái Pipeline Flow Indicator theo thời gian thực, giúp người dùng theo dõi minh bạch từng bước xử lý từ nhận dạng giọng nói đến phát âm thanh."""

s19 = builder.add_content_slide(
    category="Phần 5: Kỹ nghệ & Demo",
    title="Kiến Trúc Phần Mềm Full-Stack FastAPI & Angular SPA",
    presenter="Huỳnh Công Lương",
    time_str="23:30 - 24:30 (60s)",
    notes_text=s19_notes
)

c_s19_l, tf_s19_l = builder.add_card(s19, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Backend FastAPI (Python 3.11)", title_color=PRIMARY_BLUE)
for b in [
    "Kiến trúc RESTful Modules hóa cao: Phân tách rõ ràng giữa Engine logic và API Routing.",
    "Xử lý bất đồng bộ (Asynchronous async/await): Tối ưu hóa I/O âm thanh không bị chặn luồng.",
    "Thread-safe Memory Management: Nạp mô hình vào RAM tĩnh, chia sẻ an toàn giữa các tiến trình worker.",
    "Tự động sinh tài liệu OpenAPI / Swagger UI tại đường dẫn /docs phục vụ tích hợp kiểm thử.",
    "Tích hợp Healthcheck endpoint /api/health giám sát tính sẵn sàng của từng phân hệ."
]:
    p = tf_s19_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s19_r, tf_s19_r = builder.add_card(s19, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="Frontend Angular 22 Standalone", title_color=TEAL)
for b in [
    "Giao diện Chat Voice đàm thoại: Trực quan, tối ưu cho cả máy tính để bàn và thiết bị di động.",
    "Thành phần Pipeline Flow Indicator: Hiển thị thanh tiến trình 6 bước (Mic -> STT -> Retrieval -> MRC -> TTS -> Nghe).",
    "Thư viện bài đọc ViMMRC tích hợp: Cho phép người dùng duyệt kho bài đọc, chọn nhanh ngữ cảnh để thử nghiệm câu hỏi.",
    "Web Audio Visualizer: Hiển thị sóng âm thanh động khi người dùng nói vào micro."
]:
    p = tf_s19_r.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# SLIDE 20
s20_notes = """Để đảm bảo tính tái lập và triển khai thuận tiện, nhóm đã đóng gói toàn bộ hệ thống vào container Docker theo kỹ thuật Multi-Stage build:
Stage 1 dùng Node 22 Alpine để biên dịch mã nguồn Angular thành các file tĩnh tối ưu.
Stage 2 dùng image Python 3.11-slim gọn nhẹ, cài đặt ffmpeg, thư viện âm thanh và phiên bản PyTorch CPU-only nặng khoảng 180MB thay vì bản CUDA 2,5GB.
Quá trình triển khai được cấu hình tự động qua docker-compose. Chỉ bằng một lệnh 'docker compose up -d', toàn bộ hệ thống sẽ khởi chạy và sẵn sàng phục vụ trên cổng 8090 kèm theo cơ chế Healthcheck tự động định kỳ giám sát."""

s20 = builder.add_content_slide(
    category="Phần 5: Kỹ nghệ & Demo",
    title="Đóng Gói Triển Khai Docker Multi-Stage & Tự Động Hóa 1 Lệnh",
    presenter="Huỳnh Công Lương",
    time_str="24:30 - 25:30 (60s)",
    notes_text=s20_notes
)

c_s20_l, tf_s20_l = builder.add_card(s20, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Chiến Lược Multi-Stage Build Tối Ưu", title_color=PRIMARY_BLUE)
for b in [
    "Stage 1: node:22-alpine: Biên dịch mã nguồn Angular, áp dụng Tree-shaking và nén tĩnh thư mục dist/.",
    "Stage 2: python:3.11-slim: Image chạy production sạch sẽ, cài đặt ffmpeg và libsndfile1.",
    "Tối ưu PyTorch CPU Wheel: Chỉ cài phiên bản torch cpu-only (~180MB) thay vì bản CUDA (~2.5GB).",
    "Kích thước Image gọn hơn đáng kể, giảm khoảng 70% dung lượng lưu trữ so với build kèm CUDA.",
    "Độc lập với môi trường máy chủ (không phụ thuộc phiên bản Python hay Node cài sẵn trên host)."
]:
    p = tf_s20_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s20_r, tf_s20_r = builder.add_card(s20, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="Vận Hành Với Docker Compose & Healthcheck", title_color=TEAL)
for b in [
    "Triển khai 1 câu lệnh duy nhất: docker compose up -d",
    "Cô lập cổng dịch vụ: Phục vụ duy nhất trên cổng http://localhost:8090.",
    "Cơ chế Healthcheck tự động: Docker gọi curl -f http://localhost:8090/api/health định kỳ mỗi 30s.",
    "Tự động khởi động lại (restart: unless-stopped) nếu có bất kỳ sự cố bất thường nào xảy ra.",
    "Đã kiểm thử và chạy ổn định, container vimmrc-qa-voice chạy ổn định."
]:
    p = tf_s20_r.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# SLIDE 21
s21_notes = """Nhóm áp dụng quy trình kiểm thử tự động toàn diện bằng framework pytest để đảm bảo tính ổn định của toàn bộ mã nguồn.
Trước khi đóng gói phiên bản chính thức, bộ 54 bài kiểm thử tự động đều vượt qua kiểm định (53 passed, 1 skipped cho test accelerate trên CPU).
Bộ test kiểm tra đa tầng từ chuẩn hóa văn bản, giải thuật BM25, mô hình đọc hiểu ViT5, động cơ tổng hợp TTS đến các endpoint API của server. Nhờ kiểm thử chặt chẽ, nhóm phát hiện sớm lỗi hồi quy khi tích hợp mã nguồn giữa các thành viên, giúp hệ thống vận hành ổn định."""

s21 = builder.add_content_slide(
    category="Phần 5: Kỹ nghệ & Demo",
    title="Đảm Bảo Chất Lượng: Bộ 54 Bài Kiểm Thử Tự Động (Pytest)",
    presenter="Ngô Trí Huy (Lead)",
    time_str="25:30 - 26:30 (60s)",
    notes_text=s21_notes
)

headers_s21 = ["Bộ Kiểm Thử (Test Suite)", "Số Lượng Tests", "Phạm Vi Kiểm Định (Test Scope)", "Trạng Thái (Status)"]
rows_s21 = [
    ["text-to-speech_Duy/tests (2 file)", "12 tests", "Matcha/VITS/Edge-TTS fallback, normalizer, tokenizer vi_tone_v2", "12/12 PASSED (100%)"],
    ["retrieval-model_Huy/test_retrieval.py", "15 tests", "BM25 scoring, Bigram boost, Tokenizer, Lập chỉ mục kho bài đọc", "15/15 PASSED (100%)"],
    ["mrc-model_Huy/tests (4 file)", "18 tests", "Dữ liệu MRC, metric EM/F1, context selection, dataset gộp, smoke train", "17 PASSED, 1 SKIPPED (CPU)"],
    ["tests/test_api_server.py", "5 tests", "REST API Endpoints, Healthcheck, phục vụ giao diện web", "5/5 PASSED (100%)"],
    ["tests/test_pipeline.py", "4 tests", "Chuỗi tích hợp retrieval → MRC → TTS", "4/4 PASSED (100%)"],
    ["TỔNG CỘNG TOÀN HỆ THỐNG", "54 TESTS", "Thời gian chạy kiểm thử tự động: ~1–2 phút", "53 PASSED, 1 SKIPPED"]
]
col_w_s21 = [Inches(3.2), Inches(1.8), Inches(4.733), Inches(2.0)]
builder.add_table(s21, Inches(0.8), Inches(1.5), Inches(11.733), Inches(3.2), headers_s21, rows_s21, col_w_s21)

c_s21_bot, tf_s21_b = builder.add_card(s21, Inches(0.8), Inches(4.9), Inches(11.733), Inches(1.95), title="Ý Nghĩa Của Quy Trình Kiểm Thử Tự Động", title_color=PRIMARY_BLUE)
for b in [
    "Chống hồi quy: Phát hiện sớm lỗi hồi quy khi hợp nhất mã nguồn giữa 3 thành viên từ các nhánh git khác nhau.",
    "Tính toàn vẹn (Integrity): Mọi thay đổi về thuật toán đều phải vượt qua bộ kiểm thử chuẩn trước khi triển khai vào Docker.",
    "Có cơ chế dự phòng ở từng phân hệ, được kiểm thử bằng các test fallback."
]:
    p = tf_s21_b.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(4)

# SLIDE 22
s22_notes = """Sau đây, nhóm xin kính mời Thầy Cô và các bạn cùng theo dõi kịch bản chạy thử nghiệm thực tế của hệ thống:
Người dùng bấm giữ nút micro trên giao diện web và hỏi: 'Ai là tác giả của Truyện Kiều?'.
Ngay khi nhả mic, phân hệ STT nhận tín hiệu âm thanh và chuyển thành văn bản trong khoảng 3 giây. Bộ truy xuất lập tức lấy các ứng viên từ BM25 tầng 1, BM25 Wikipedia và dense Wikipedia, sau đó reranker bge-reranker-v2-m3 định vị chính xác đoạn Wikipedia nói về Truyện Kiều.
Mô hình ViT5 tiếp nhận ngữ cảnh và sinh ra câu trả lời 'Nguyễn Du'. Cuối cùng, phân hệ TTS chuẩn hóa văn bản và phát âm thanh câu trả lời bằng giọng đọc nơ-ron tự nhiên qua loa.
Tổng thời gian xử lý toàn chu trình mất khoảng 12 giây khi chạy hoàn toàn trên CPU Docker; nếu tắt reranker thì thời gian phản hồi rút ngắn còn khoảng 6 giây."""

s22 = builder.add_content_slide(
    category="Phần 5: Kỹ nghệ & Demo",
    title="Kịch Bản Live Demonstration: Chu Trình Hỏi Đáp Bằng Giọng Nói",
    presenter="Cả Nhóm (Demo Thực Tế)",
    time_str="26:30 - 28:00 (90s)",
    notes_text=s22_notes
)

demo_cards = [
    ("1. VOICE INPUT", "Micro Browser", "Người dùng hỏi: 'Ai là tác giả của Truyện Kiều?' (câu hỏi tự do)", PRIMARY_BLUE),
    ("2. STT WHISPER", "~3 Giây", "Whisper-small LoRA 50h (CTranslate2 int8) nhận dạng văn bản tiếng Việt có dấu.", TEAL),
    ("3. RETRIEVAL + RERANKER", "~6 Giây", "BM25 + dense ứng viên → reranker chọn đoạn Wikipedia 'Truyện Kiều'.", TECH_BLUE),
    ("4. MRC VIT5", "~1.4 Giây", "ViT5 đọc đoạn văn và sinh câu trả lời 'Nguyễn Du'.", GREEN),
    ("5. TTS SYNTHESIS", "~1.3 Giây", "Normalizer chuyển đổi -> Matcha-TTS tổng hợp câu nói tự nhiên.", AMBER),
    ("6. PLAYBACK AUDIO", "Tổng ~12 Giây", "Trình duyệt tự động phát câu trả lời giọng đọc nơ-ron qua loa.", PRIMARY_BLUE)
]

for idx, (head_d, time_d, desc_d, col_d) in enumerate(demo_cards):
    row_idx = idx // 3
    col_idx = idx % 3
    dx = Inches(0.8) + col_idx * Inches(3.95)
    dy = Inches(1.5) + row_idx * Inches(2.65)
    
    card, ctf = builder.add_card(s22, dx, dy, Inches(3.8), Inches(2.45), title="", border_color=col_d)
    p0 = ctf.paragraphs[0]
    p0.text = head_d
    p0.font.size = Pt(11.5)
    p0.font.bold = True
    p0.font.color.rgb = col_d

    p_t = ctf.add_paragraph()
    p_t.text = "Thời gian: " + time_d
    p_t.font.size = Pt(11)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_DARK
    p_t.space_before = Pt(4)

    p_d = ctf.add_paragraph()
    p_d.text = desc_d
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = TEXT_MUTED
    p_d.space_before = Pt(6)

# SLIDE 23
s23_notes = """Nhóm cũng phân tích các trường hợp lỗi và giới hạn thực tế:
Thứ nhất, ở phân hệ STT, trong môi trường ồn hoặc người nói quá nhỏ, mô hình đôi khi nhận dạng sai phụ âm đầu hoặc mất từ nối.
Thứ hai, ở phân hệ Retrieval, BM25 so khớp từ khóa nên nếu câu hỏi dùng từ đồng nghĩa vắng bóng trong văn bản thì điểm số bị ảnh hưởng; một số câu kiến thức mở còn sai do đoạn tầng 1 lấn át điểm số.
Thứ ba, hệ thống hiện tối ưu cho hội thoại đơn lượt, trả lời từng câu độc lập chứ chưa lưu trữ trạng thái để trò chuyện đa lượt."""

s23 = builder.add_content_slide(
    category="Phần 5: Kỹ nghệ & Demo",
    title="Phân Tích Lỗi Thực Tế (Error Analysis) & Các Giới Hạn Của Hệ Thống",
    presenter="Trương Hoàng Duy",
    time_str="28:00 - 29:00 (60s)",
    notes_text=s23_notes
)

c_s23_l, tf_s23_l = builder.add_card(s23, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.35), title="Phân Tích Các Trường Hợp Lỗi Điển Hình", title_color=AMBER)
for b in [
    "Nhiễu Môi Trường Tạp Âm (STT Error): Trong môi trường ồn ào (tiếng còi xe, quán xá), Whisper có thể nhầm lẫn một số phụ âm đầu gần âm.",
    "Khoảng Trống Từ Vựng (Retrieval Lexical Gap): BM25 dựa trên từ khóa; nếu câu hỏi dùng từ đồng nghĩa hoàn toàn (ví dụ: 'thủ phủ' thay vì 'thủ đô') mà văn bản không chứa từ đó -> Điểm BM25 bị thấp.",
    "Giới hạn ViT5: Đã train thêm 2 epoch: F1 66,02 → 66,55 nhưng dev loss tăng; cải thiện tiếp cần thêm dữ liệu hoặc dò siêu tham số.",
    "Câu hỏi kiến thức chung: Một số câu vẫn sai, ví dụ 'Thủ đô của Việt Nam là gì?' trả về 'Sài Gòn' do đoạn ViQuAD về TP. Hồ Chí Minh ở tầng 1 thắng; F1 kiến thức mở mới ~24.",
    "Lệch giọng địa phương: Mô hình TTS hiện được tối ưu cho giọng chuẩn miền Bắc, chưa đa dạng hóa sang giọng miền Trung và Nam."
]:
    p = tf_s23_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s23_r, tf_s23_r = builder.add_card(s23, Inches(6.7), Inches(1.5), Inches(5.833), Inches(5.35), title="Giới Hạn Phạm Vi Của Hệ Thống Hiện Tại", title_color=PRIMARY_BLUE)
for b in [
    "Tương tác Đơn Lượt (Single-Turn Q&A): Hệ thống trả lời dứt điểm từng câu hỏi, chưa có cơ chế Session Memory để nhớ ngữ cảnh của các câu hỏi trước đó.",
    "Cơ sở Tri thức Tĩnh: Kho gồm ViMMRC + ViQuAD và bản Wikipedia tiếng Việt đã tải về, chưa cập nhật tri thức mới từ Internet.",
    "Định dạng Âm thanh Đầu ra: Hiện mặc định xuất tần số lấy mẫu 22.05kHz, chưa nâng cấp lên 44.1kHz Hi-Fi studio."
]:
    p = tf_s23_r.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# SLIDE 24
s24_notes = """Nhìn lại quá trình nghiên cứu, đề tài đã hoàn thành các mục tiêu: xây dựng hệ thống Voice Q&A tiếng Việt khép kín trên ViMMRC và ViQuAD, làm chủ Matcha-TTS Flow Matching với frontend vi_tone_v2, chạy cục bộ ổn định trên CPU và đóng gói Docker 100%.
Định hướng tương lai: nhóm sẽ triển khai trên GPU để giảm độ trễ dưới 2 giây, tinh chỉnh reranker cho câu hỏi kiến thức mở, và thử nghiệm mô hình LLM tiếng Việt để nâng cao năng lực suy luận.
Nhóm em xin chân thành cảm ơn sự hướng dẫn tận tình của Thầy Cô! Rất mong nhận được góp ý quý báu từ Hội đồng. Em xin trân trọng cảm ơn!"""

s24 = builder.add_content_slide(
    category="Phần 5: Kỹ nghệ & Demo",
    title="Tổng Kết Đóng Góp, Định Hướng Phát Triển & Lời Cảm Ơn",
    presenter="Ngô Trí Huy (Lead)",
    time_str="29:00 - 30:00 (60s)",
    notes_text=s24_notes
)

c_s24_l, tf_s24_l = builder.add_card(s24, Inches(0.8), Inches(1.5), Inches(5.6), Inches(4.1), title="Đóng Góp Chính Của Đề Tài", title_color=PRIMARY_BLUE)
for b in [
    "Xây dựng thành công hệ thống Voice Q&A tiếng Việt mã nguồn mở hoàn chỉnh dựa trên ViMMRC 2.0 và UIT-ViQuAD2.0.",
    "Ứng dụng thành công kỹ thuật tiên tiến Flow Matching (Matcha-TTS ICASSP 2024) và đề xuất frontend vi_tone_v2 tách thanh điệu.",
    "Chứng minh tính khả thi của việc chạy cục bộ toàn bộ pipeline AI trên CPU thông thường mà không cần GPU (Edge-TTS/gTTS dự phòng cần Internet).",
    "Chuẩn mực kỹ nghệ phần mềm: Đóng gói Docker đa tầng 1 lệnh, bộ 54 bài kiểm thử tự động (53 passed, 1 skipped trên CPU)."
]:
    p = tf_s24_l.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

c_s24_r, tf_s24_r = builder.add_card(s24, Inches(6.7), Inches(1.5), Inches(5.833), Inches(4.1), title="Định Hướng Phát Triển Tương Lai", title_color=AMBER)
for b in [
    "Chạy GPU: Giảm độ trễ (hiện ~12 giây/câu trên Docker CPU).",
    "Tinh chỉnh reranker và định tuyến cho câu hỏi kiến thức chung (hiện F1 kiến thức mở mới ~24).",
    "Thử LLM tiếng Việt (PhoGPT, Vistral, SeaLLMs) để sinh câu trả lời.",
    "Hội thoại Đa Lượt (Multi-Turn Dialogue): Xây dựng bộ nhớ đệm trạng thái hội thoại để hỗ trợ hỏi đáp nối tiếp tự nhiên.",
    "Ứng dụng thực tiễn: Triển khai thử nghiệm tại Kiosk trường học và các thiết bị hỗ trợ người khiếm thị."
]:
    p = tf_s24_r.add_paragraph()
    p.text = "→ " + b
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_DARK
    p.space_before = Pt(8)

# Thank you banner bottom
c_s24_ty, tf_s24_ty = builder.add_card(s24, Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.05), title="", bg_color=DARK_BG)
pt0_24 = tf_s24_ty.paragraphs[0]
pt0_24.text = "XIN CHÂN THÀNH CẢM ƠN THẦY CÔ VÀ HỘI ĐỒNG ĐÁNH GIÁ!"
pt0_24.font.size = Pt(15)
pt0_24.font.bold = True
pt0_24.font.color.rgb = WHITE
pt0_24.alignment = PP_ALIGN.CENTER

pt1_24 = tf_s24_ty.add_paragraph()
pt1_24.text = "Nhóm chúng em rất mong nhận được những nhận xét và góp ý quý báu từ Thầy Cô!"
pt1_24.font.size = Pt(11)
pt1_24.font.color.rgb = RGBColor(148, 163, 184)
pt1_24.alignment = PP_ALIGN.CENTER
pt1_24.space_before = Pt(2)

# Save
builder.save()
print("All 24 slides built successfully for 30min presentation.")
