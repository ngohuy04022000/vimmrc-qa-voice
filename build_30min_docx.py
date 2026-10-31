# -*- coding: utf-8 -*-
"""
Script to generate docs/ViMMRC_KichBan_30phut.docx.
Matches the professional landscape A4 layout of ViMMRC_KichBan_5phut.docx:
- Table 0: Overview table (Slide, Title, Time, Speaker, Word count, Est. speaking time)
- Table 1: Detailed script table (Slide & Time & Speaker, Slide bullet contents, Verbatim speech)
- Table 2: Benchmark & quantitative appendix
"""
import os
import re
import sys
from pathlib import Path

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

DOCX_OUT = Path("docs/ViMMRC_KichBan_30phut.docx")
MD_PATH = Path("docs/presentation-30min.md")

# ==============================================================================
# 1. PARSE PRESENTATION-30MIN.MD
# ==============================================================================
with open(MD_PATH, "r", encoding="utf-8") as f:
    md_text = f.read()

slide_pattern = (
    r'### SLIDE (\d+):\s*([^\n]+)\n'
    r'\* \*\*Thời lượng:\*\*\s*([^\n]+)\n'
    r'\* \*\*Người trình bày:\*\*\s*([^\n]+)\n'
    r'\* \*\*Nội dung hiển thị:\*\*\n'
    r'(.*?)\n'
    r'\* \*\*Kịch bản thuyết trình \(Speaker Script\):\*\*\n'
    r'(.*?)(?=\n---\n|\Z)'
)

slides_data = []
for m in re.finditer(slide_pattern, md_text, re.DOTALL):
    num = int(m.group(1))
    title = m.group(2).strip()
    dur = m.group(3).strip()
    speaker = m.group(4).strip()
    bullets_raw = m.group(5).strip()
    script_raw = m.group(6).strip()

    # Clean script lines
    script_lines = []
    for line in script_raw.split('\n'):
        l = line.strip()
        l = re.sub(r'^\s*>\s*"?', '', l)
        l = re.sub(r'"?\s*$', '', l)
        if l:
            script_lines.append(l)
    script_clean = '\n\n'.join(script_lines)
    wc = len(script_clean.split())

    # Format est speaking time at ~2.2 - 2.4 words/second
    est_sec = int(round(wc / 2.1))
    if est_sec >= 60:
        est_min = est_sec // 60
        rem_sec = est_sec % 60
        est_str = f"~{est_min}m{rem_sec:02d}s"
    else:
        est_str = f"~{est_sec}s"

    slides_data.append({
        'num': num,
        'title': title,
        'dur': dur,
        'speaker': speaker,
        'bullets': bullets_raw,
        'script': script_clean,
        'wc': wc,
        'est_str': est_str
    })

print(f"Parsed {len(slides_data)} slides from {MD_PATH}")
assert len(slides_data) == 24, f"Expected 24 slides, got {len(slides_data)}"

# ==============================================================================
# 2. HELPER FUNCTIONS FOR DOCX FORMATTING
# ==============================================================================
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    # Remove existing shading if any
    for existing in tcPr.findall(qn('w:shd')):
        tcPr.remove(existing)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=70, bottom=70, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def set_table_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def format_cell_text(cell, text, font_size=9.5, bold=False, color_rgb=None, space_after=40, line_spacing=1.05):
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after / 20.0)
    p.paragraph_format.line_spacing = line_spacing
    run = p.runs[0] if p.runs else p.add_run()
    run.text = text
    run.font.name = "Calibri"
    run.font.size = Pt(font_size)
    run.font.bold = bold
    if color_rgb:
        run.font.color.rgb = color_rgb

# ==============================================================================
# 3. BUILD DOCUMENT
# ==============================================================================
doc = Document()

# Set Page to A4 Landscape
section = doc.sections[0]
section.page_width = Inches(11.69)
section.page_height = Inches(8.27)
section.top_margin = Inches(0.63)
section.bottom_margin = Inches(0.63)
section.left_margin = Inches(0.63)
section.right_margin = Inches(0.63)

# Configure default Normal style
style_normal = doc.styles['Normal']
style_normal.font.name = 'Calibri'
style_normal.font.size = Pt(10.5)
style_normal.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

# Document Header
p_title = doc.add_paragraph()
p_title.paragraph_format.space_before = Pt(0)
p_title.paragraph_format.space_after = Pt(2)
run_title = p_title.add_run("KỊCH BẢN THUYẾT TRÌNH 30 PHÚT (VIDEO BÁO CÁO TOÀN DIỆN ĐỒ ÁN)")
run_title.font.name = "Calibri"
run_title.font.size = Pt(18)
run_title.font.bold = True
run_title.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)

p_sub1 = doc.add_paragraph()
p_sub1.paragraph_format.space_before = Pt(0)
p_sub1.paragraph_format.space_after = Pt(2)
run_sub1 = p_sub1.add_run("Hệ thống Hỏi - Đáp bằng giọng nói tiếng Việt dựa trên bộ dữ liệu ViMMRC 2.0 (ViMMRC Voice Q&A)")
run_sub1.font.name = "Calibri"
run_sub1.font.size = Pt(12)
run_sub1.font.bold = True
run_sub1.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)

p_sub2 = doc.add_paragraph()
p_sub2.paragraph_format.space_before = Pt(0)
p_sub2.paragraph_format.space_after = Pt(10)
run_sub2 = p_sub2.add_run("Môn: Học máy tiên tiến và ứng dụng · Học viên thực hiện: Ngô Trí Huy, Huỳnh Công Lương, Trương Hoàng Duy · Thời lượng: 30:00")
run_sub2.font.name = "Calibri"
run_sub2.font.size = Pt(10)
run_sub2.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

# ------------------------------------------------------------------------------
# SECTION 1: OVERVIEW TABLE (TABLE 0)
# ------------------------------------------------------------------------------
h2_1 = doc.add_paragraph()
h2_1.paragraph_format.space_before = Pt(8)
h2_1.paragraph_format.space_after = Pt(4)
run_h2_1 = h2_1.add_run("1. Tổng quan phân công & phân bổ thời lượng 24 Slide (Tổng: 30:00)")
run_h2_1.font.name = "Calibri"
run_h2_1.font.size = Pt(12.5)
run_h2_1.font.bold = True
run_h2_1.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)

t0_headers = ["Slide", "Nội dung", "Thời gian", "Người trình bày", "Số chữ lời thoại", "Ước tính nói (2,4 chữ/s)"]
t0_widths = [Inches(0.55), Inches(3.54), Inches(1.34), Inches(2.05), Inches(1.18), Inches(1.77)]

t0 = doc.add_table(rows=1 + len(slides_data) + 1, cols=6)
t0.style = "Table Grid"
t0.alignment = WD_TABLE_ALIGNMENT.CENTER

# Header row
set_table_header(t0.rows[0])
set_row_cant_split(t0.rows[0])
for ci, h in enumerate(t0_headers):
    cell = t0.rows[0].cells[ci]
    cell.width = t0_widths[ci]
    set_cell_background(cell, "1F3A5F")
    set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
    format_cell_text(cell, h, font_size=9.5, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))

# Data rows
total_wc = 0
for i, s in enumerate(slides_data):
    row = t0.rows[i + 1]
    set_row_cant_split(row)
    total_wc += s['wc']
    bg_color = "F2F2F2" if (i % 2 == 1) else "FFFFFF"

    cells_text = [
        str(s['num']),
        s['title'],
        s['dur'],
        s['speaker'],
        str(s['wc']),
        s['est_str']
    ]

    for ci, txt in enumerate(cells_text):
        cell = row.cells[ci]
        cell.width = t0_widths[ci]
        if bg_color != "FFFFFF":
            set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
        is_center = ci in [0, 4, 5]
        format_cell_text(cell, txt, font_size=9.0, bold=(ci == 0))
        if is_center:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

# Total row
row_tot = t0.rows[-1]
set_row_cant_split(row_tot)
set_cell_background(row_tot.cells[0], "E2E8F0")
set_cell_background(row_tot.cells[1], "E2E8F0")
set_cell_background(row_tot.cells[2], "E2E8F0")
set_cell_background(row_tot.cells[3], "E2E8F0")
set_cell_background(row_tot.cells[4], "E2E8F0")
set_cell_background(row_tot.cells[5], "E2E8F0")

for ci in range(6):
    row_tot.cells[ci].width = t0_widths[ci]
    set_cell_margins(row_tot.cells[ci], top=70, bottom=70, left=80, right=80)

format_cell_text(row_tot.cells[0], "", font_size=9.5, bold=True)
format_cell_text(row_tot.cells[1], "TỔNG TOÀN BỘ 24 SLIDE", font_size=9.5, bold=True)
format_cell_text(row_tot.cells[2], "30:00 (1.800s)", font_size=9.5, bold=True)
row_tot.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
format_cell_text(row_tot.cells[3], "Cả Nhóm 3 thành viên", font_size=9.5, bold=True)
format_cell_text(row_tot.cells[4], f"{total_wc} từ", font_size=9.5, bold=True)
row_tot.cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
format_cell_text(row_tot.cells[5], f"~{total_wc/125:.1f} phút (120 wpm)", font_size=9.5, bold=True)
row_tot.cells[5].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

# ------------------------------------------------------------------------------
# SECTION 2: DETAILED SCRIPT TABLE (TABLE 1)
# ------------------------------------------------------------------------------
doc.add_page_break()

h2_2 = doc.add_paragraph()
h2_2.paragraph_format.space_before = Pt(8)
h2_2.paragraph_format.space_after = Pt(4)
run_h2_2 = h2_2.add_run("2. Kịch bản chi tiết từng slide (24 Slide - Lời thoại & Nội dung trình chiếu)")
run_h2_2.font.name = "Calibri"
run_h2_2.font.size = Pt(12.5)
run_h2_2.font.bold = True
run_h2_2.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)

t1_headers = [
    "Slide · Thời gian · Người nói",
    "Nội dung hiển thị trên slide",
    "Lời thoại (đọc thành tiếng - Verbatim Script)"
]
t1_widths = [Inches(1.81), Inches(3.70), Inches(4.92)]

t1 = doc.add_table(rows=1 + len(slides_data), cols=3)
t1.style = "Table Grid"
t1.alignment = WD_TABLE_ALIGNMENT.CENTER

# Header row
set_table_header(t1.rows[0])
set_row_cant_split(t1.rows[0])
for ci, h in enumerate(t1_headers):
    cell = t1.rows[0].cells[ci]
    cell.width = t1_widths[ci]
    set_cell_background(cell, "1F3A5F")
    set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
    format_cell_text(cell, h, font_size=9.5, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))

# Data rows for Table 1
for i, s in enumerate(slides_data):
    row = t1.rows[i + 1]
    set_row_cant_split(row)
    bg_color = "F8FAFC" if (i % 2 == 1) else "FFFFFF"

    # Col 0: Slide · Thời gian · Người nói
    cell_0 = row.cells[0]
    cell_0.width = t1_widths[0]
    if bg_color != "FFFFFF":
        set_cell_background(cell_0, bg_color)
    set_cell_margins(cell_0, top=70, bottom=70, left=80, right=80)
    p0 = cell_0.paragraphs[0]
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(2)
    p0.paragraph_format.line_spacing = 1.1

    r0_title = p0.add_run(f"Slide {s['num']}:\n")
    r0_title.font.name = "Calibri"
    r0_title.font.size = Pt(9.5)
    r0_title.font.bold = True
    r0_title.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)

    r0_tname = p0.add_run(f"{s['title']}\n\n")
    r0_tname.font.name = "Calibri"
    r0_tname.font.size = Pt(9.0)
    r0_tname.font.bold = True

    r0_time = p0.add_run(f"⏱ {s['dur']}\n\n")
    r0_time.font.name = "Calibri"
    r0_time.font.size = Pt(9.0)
    r0_time.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)

    r0_spk = p0.add_run(f"🎤 {s['speaker']}\n\n")
    r0_spk.font.name = "Calibri"
    r0_spk.font.size = Pt(9.0)
    r0_spk.font.bold = True
    r0_spk.font.color.rgb = RGBColor(0x05, 0x96, 0x69)

    r0_wc = p0.add_run(f"📝 {s['wc']} từ ({s['est_str']})")
    r0_wc.font.name = "Calibri"
    r0_wc.font.size = Pt(8.5)
    r0_wc.font.color.rgb = RGBColor(0x6B, 0x72, 0x80)

    # Col 1: Nội dung hiển thị trên slide
    cell_1 = row.cells[1]
    cell_1.width = t1_widths[1]
    if bg_color != "FFFFFF":
        set_cell_background(cell_1, bg_color)
    set_cell_margins(cell_1, top=70, bottom=70, left=80, right=80)
    p1 = cell_1.paragraphs[0]
    p1.paragraph_format.space_before = Pt(0)
    p1.paragraph_format.space_after = Pt(2)
    p1.paragraph_format.line_spacing = 1.05

    # Clean markdown bullets for Col 1
    bullet_lines = s['bullets'].split('\n')
    for b_idx, bl in enumerate(bullet_lines):
        bl_str = bl.rstrip()
        if not bl_str.strip():
            continue
        p_b = cell_1.add_paragraph() if b_idx > 0 else p1
        p_b.paragraph_format.space_before = Pt(0)
        p_b.paragraph_format.space_after = Pt(1.5)
        p_b.paragraph_format.line_spacing = 1.05

        indent_level = len(bl_str) - len(bl_str.lstrip())
        clean_bl = bl_str.strip()
        # strip markdown bold / bullet marks
        if clean_bl.startswith('* ') or clean_bl.startswith('- '):
            clean_bl = '• ' + clean_bl[2:]
        elif re.match(r'^\d+\.\s', clean_bl):
            pass # keep numbered lists

        run_b = p_b.add_run(('    ' if indent_level >= 2 else '') + clean_bl)
        run_b.font.name = "Calibri"
        run_b.font.size = Pt(8.5)
        if clean_bl.startswith('• **') or ':**' in clean_bl or clean_bl.startswith('**'):
            run_b.font.bold = False # keep standard
        run_b.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    # Col 2: Lời thoại (đọc thành tiếng)
    cell_2 = row.cells[2]
    cell_2.width = t1_widths[2]
    if bg_color != "FFFFFF":
        set_cell_background(cell_2, bg_color)
    set_cell_margins(cell_2, top=70, bottom=70, left=80, right=80)

    script_paragraphs = s['script'].split('\n\n')
    for p_idx, sp in enumerate(script_paragraphs):
        p2 = cell_2.paragraphs[0] if p_idx == 0 else cell_2.add_paragraph()
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(3)
        p2.paragraph_format.line_spacing = 1.15
        run_p2 = p2.add_run(sp.strip())
        run_p2.font.name = "Calibri"
        run_p2.font.size = Pt(9.0)
        run_p2.font.color.rgb = RGBColor(0x11, 0x18, 0x27)

# ------------------------------------------------------------------------------
# SECTION 3: BENCHMARK & QUANTITATIVE APPENDIX (TABLE 2)
# ------------------------------------------------------------------------------
doc.add_page_break()

h2_3 = doc.add_paragraph()
h2_3.paragraph_format.space_before = Pt(8)
h2_3.paragraph_format.space_after = Pt(4)
run_h2_3 = h2_3.add_run("3. Phụ lục: Bảng tổng hợp số liệu thực nghiệm & Benchmark toàn hệ thống")
run_h2_3.font.name = "Calibri"
run_h2_3.font.size = Pt(12.5)
run_h2_3.font.bold = True
run_h2_3.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)

p_app_note = doc.add_paragraph()
p_app_note.paragraph_format.space_before = Pt(0)
p_app_note.paragraph_format.space_after = Pt(6)
run_app_note = p_app_note.add_run("Bảng số liệu đối sánh thực nghiệm toàn diện các phân hệ: Nhận dạng giọng nói (STT), Truy xuất thông tin (Retrieval), Đọc hiểu máy (MRC), Tổng hợp tiếng nói (TTS) và Hiệu năng triển khai hệ thống (Docker CPU).")
run_app_note.font.name = "Calibri"
run_app_note.font.size = Pt(9.5)
run_app_note.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

t2_headers = ["Phân hệ / Mô hình", "Chỉ số then chốt", "Giá trị đạt được", "So sánh Baseline", "Ý nghĩa thực tiễn & Bối cảnh kỹ thuật"]
t2_widths = [Inches(1.97), Inches(1.65), Inches(1.69), Inches(2.36), Inches(2.76)]

appendix_data = [
    (
        "Phân hệ STT\n(Whisper-small LoRA 50h VietSpeech)",
        "Tỷ lệ lỗi từ (WER) /\nTỷ lệ lỗi ký tự (CER)",
        "WER: 13.77%\nCER: 6.67%\n(Test 1.802 mẫu VietSpeech)",
        "Whisper-small gốc (zero-shot):\nWER: 36.76%\nCER: 19.43%",
        "Fine-tune LoRA 50h giúp giảm hơn 22,9% WER trên tiếng Việt âm học thực tế; nhận dạng chuẩn xác dấu thanh điệu."
    ),
    (
        "Tối ưu STT\n(CTranslate2 INT8 vs PyTorch FP32)",
        "Tốc độ suy luận CPU &\nDung lượng RAM",
        "Nhanh gấp 4.1 lần\nRAM: ~450 MB (CT2 int8)",
        "PyTorch gốc FP32:\nThời gian ~12.5s / câu\nRAM: ~1.2 GB",
        "Lượng hóa INT8 cho phép STT chạy mượt mà ngay trên Docker CPU, giải mã câu hỏi giọng nói ~3 giây."
    ),
    (
        "Lọc khoảng lặng STT\n(Silero VAD - faster-whisper)",
        "Tỷ lệ cắt khoảng lặng &\nNgăn lặp hallucination",
        "vad_filter=True\nCắt bỏ 100% khoảng lặng vô nghĩa",
        "Không dùng VAD:\nWhisper dễ bị hallucination lặp câu khi có nhiễu nền",
        "Giúp phân hệ STT hoạt động ổn định trong môi trường thực tế, loại bỏ nhiễu micro và âm thanh thừa trước khi giải mã."
    ),
    (
        "Retrieval BM25 Tinh chỉnh\n(Kho ViMMRC 552 bài đọc)",
        "Recall@1 / Recall@5 /\nMRR (Dev 564 câu)",
        "Recall@1: 71.45%\nRecall@5: 86.88%\nMRR: 0.7719",
        "BM25 mặc định (k1=1.2, b=0.75):\nRecall@1: 64.18%\nRecall@5: 79.96%\nMRR: 0.7042",
        "Tinh chỉnh k1=2.1, b=1.0 kết hợp Bigram Phrase Boost (+0.4) giúp tăng vượt bậc +7.27% Recall@1."
    ),
    (
        "Kho Tri thức Hai Tầng RAG\n(Two-Tier Knowledge Base)",
        "Quy mô kho tài liệu &\nĐộ phủ tri thức",
        "Tầng 1: 5.869 đoạn (ViMMRC + ViQuAD)\nTầng 2: 1.481.873 đoạn Wikipedia",
        "Kho đơn tầng:\nChỉ trả lời được câu hỏi thuộc bài đọc đóng",
        "Cho phép hệ thống vừa trả lời câu hỏi chuyên biệt trong tập dữ liệu, vừa mở rộng trả lời kiến thức bách khoa mở."
    ),
    (
        "Retrieval Kho Hai Tầng\n(BM25 hai tầng - 2.545 câu test)",
        "Recall@1 / Recall@5\n(Test 2.545 câu)",
        "Recall@1: 71.1%\nRecall@5: 85.9%",
        "Baseline 1 tầng:\nChỉ đo trên tập đóng",
        "Tìm đúng đoạn văn trả lời ngay ở Top 1 đạt hơn 71% và Top 5 đạt gần 86% trên toàn bộ tập test."
    ),
    (
        "Pipeline cuối RAG\n(bge-reranker-v2-m3 + ưu tiên tầng 1)",
        "Answer F1 (ViT5):\n200 câu trong kho /\n200 câu kiến thức mở",
        "F1 tầng 1: 60.7%\nF1 kiến thức mở: 24.3%",
        "BM25 thuần (không reranker):\nF1 tầng 1: 58.0%\nF1 kiến thức mở: 15.4%",
        "Reranker giúp cải thiện rõ rệt ở câu kiến thức mở (+8.9% F1), định vị chính xác đoạn Wikipedia liên quan."
    ),
    (
        "Đọc hiểu MRC (ViT5-base)\n(Tập gộp 27.164 câu)",
        "Exact Match (EM) &\nToken F1 (Test 2.716 câu)",
        "Exact Match: 41.05%\nToken F1: 66.55%\n(Dev: EM 42.62%, F1 67.92%)",
        "Trích câu khớp nhất (Lexical Extractive fallback):\nEM: ~21.5%, F1: ~43.2%",
        "ViT5 sinh câu trả lời tự do ngắn gọn, đúng trọng tâm thay vì trích xuất cả câu dài; không cần đáp án trắc nghiệm sẵn."
    ),
    (
        "Tổng hợp Tiếng nói (TTS)\n(Matcha-TTS Flow Matching)",
        "Tỷ lệ lỗi chữ (CER) &\nĐộ biến thiên cao độ (F0)",
        "CER: 1.9%\nlog-F0: 2.86 semitones\nMCD: 6.12 dB",
        "VITS: CER 4.3% / log-F0 4.31\nEdge-TTS thương mại: log-F0 2.69\nNgười thật: CER 0.7%",
        "Matcha-TTS phát âm rõ chữ hơn VITS gấp hơn 2 lần; thanh điệu tự nhiên, tiệm cận mô hình thương mại Edge-TTS."
    ),
    (
        "Tốc độ Tổng hợp TTS\n(Matcha-TTS trên Docker CPU)",
        "Real-Time Factor (RTF)\n(10 bước Euler ODE)",
        "RTF: 0.52\n(CPU Intel Core i5/i7)",
        "Yêu cầu Real-Time chuẩn: RTF < 1.0\nFastSpeech 2: RTF ~0.45",
        "Tổng hợp âm thanh nhanh gấp 2 lần thời gian thực trên CPU, chỉ mất ~1.3 giây cho câu trả lời trung bình."
    ),
    (
        "Độ trễ toàn chu trình\n(Voice-to-Voice Latency)",
        "Thời gian từ khi nhả mic\nđến khi nghe loa",
        "Toàn trình: ~12 giây (Docker CPU)\n(Tắt reranker: ~6 giây)",
        "Yêu cầu chạy cục bộ CPU:\nKhông dùng GPU rời, không API đám mây trả phí",
        "STT ~3s, Truy xuất + Reranker ~6s, ViT5 sinh đáp án ~1.4s, TTS phát âm ~1.3s. Hoạt động độc lập, bảo mật dữ liệu."
    ),
    (
        "Kiểm thử Phần mềm\n(Automated Test Suites)",
        "Tỷ lệ Test Pass &\nBao phủ phân hệ",
        "54/54 passed (100%)\n(1 skipped accelerate CPU)",
        "Dự án không có kiểm thử tự động",
        "Bao phủ toàn diện REST API, Audio Normalizer, Text Normalizer, Thread-Safe Lazy Loading, Cơ chế Fallback đa tầng."
    )
]

t2 = doc.add_table(rows=1 + len(appendix_data), cols=5)
t2.style = "Table Grid"
t2.alignment = WD_TABLE_ALIGNMENT.CENTER

# Header row
set_table_header(t2.rows[0])
set_row_cant_split(t2.rows[0])
for ci, h in enumerate(t2_headers):
    cell = t2.rows[0].cells[ci]
    cell.width = t2_widths[ci]
    set_cell_background(cell, "1F3A5F")
    set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
    format_cell_text(cell, h, font_size=9.5, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))

# Data rows for Table 2
for i, (m_sys, m_metric, m_val, m_base, m_mean) in enumerate(appendix_data):
    row = t2.rows[i + 1]
    set_row_cant_split(row)
    bg_color = "F2F2F2" if (i % 2 == 1) else "FFFFFF"

    cells_text = [m_sys, m_metric, m_val, m_base, m_mean]
    for ci, txt in enumerate(cells_text):
        cell = row.cells[ci]
        cell.width = t2_widths[ci]
        if bg_color != "FFFFFF":
            set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        format_cell_text(cell, txt, font_size=8.5, bold=(ci == 0))

# Save Document
doc.save(DOCX_OUT)
print(f"Successfully generated {DOCX_OUT} ({os.path.getsize(DOCX_OUT)} bytes)")
