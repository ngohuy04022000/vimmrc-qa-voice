import sys
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Reconfigure stdout to utf-8 just in case
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Palette
DARK_BG = RGBColor(15, 23, 42)       # #0F172A
LIGHT_BG = RGBColor(248, 250, 252)   # #F8FAFC
WHITE = RGBColor(255, 255, 255)
PRIMARY_BLUE = RGBColor(30, 58, 138) # #1E3A8A
TECH_BLUE = RGBColor(37, 99, 235)    # #2563EB
TEAL = RGBColor(13, 148, 136)        # #0D9488
AMBER = RGBColor(217, 119, 6)        # #D97706
TEXT_DARK = RGBColor(30, 41, 59)     # #1E293B
TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
BORDER_COLOR = RGBColor(226, 232, 240)
CARD_BG = RGBColor(255, 255, 255)
CARD_ACCENT_BG = RGBColor(241, 245, 249)
PILL_BG = RGBColor(224, 231, 255)
PILL_TEXT = RGBColor(55, 48, 163)
GREEN = RGBColor(22, 101, 52)

class SlideDeckBuilder:
    def __init__(self, output_path):
        self.output_path = output_path
        self.prs = pptx.Presentation()
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)
        self.blank_layout = self.prs.slide_layouts[6]
        self.slide_count = 0

    def add_title_slide(self, title, subtitle, metadata_items, duration_tag, notes_text):
        slide = self.prs.slides.add_slide(self.blank_layout)
        self.slide_count += 1

        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = DARK_BG
        bg.line.fill.background()

        # Accent Bar Top
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = TEAL
        bar.line.fill.background()

        # Duration Tag Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.1), Inches(3.2), Inches(0.45))
        pill.fill.solid()
        pill.fill.fore_color.rgb = TEAL
        pill.line.fill.background()
        tf = pill.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = duration_tag.upper()
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        # Title
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.733), Inches(1.8))
        tf = tx_box.text_frame
        tf.word_wrap = True
        for t_idx, t_line in enumerate(title.split("\n")):
            p = tf.paragraphs[0] if t_idx == 0 else tf.add_paragraph()
            p.text = t_line
            p.font.size = Pt(28)
            p.font.bold = True
            p.font.color.rgb = WHITE
            if t_idx > 0:
                p.space_before = Pt(4)

        # Subtitle
        if subtitle:
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.size = Pt(16)
            p2.font.color.rgb = RGBColor(148, 163, 184) # slate-400
            p2.space_before = Pt(8)

        # Member Cards: Ch? nu tn thnh vin, khng b? vai tr v khng c phn cng chi ti?t
        card_w = Inches(3.64)
        card_h = Inches(1.6)
        card_y = Inches(4.7)

        for i, item in enumerate(metadata_items):
            cx = Inches(0.8) + i * Inches(3.9)
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, card_y, card_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(30, 41, 59) # slate-800
            card.line.color.rgb = RGBColor(51, 65, 85)
            card.line.width = Pt(1)

            ctf = card.text_frame
            ctf.word_wrap = True
            ctf.margin_left = Inches(0.2)
            ctf.margin_right = Inches(0.2)
            ctf.margin_top = Inches(0.25)

            name = item if isinstance(item, str) else item.get("name", "")

            cp0 = ctf.paragraphs[0]
            cp0.text = "THÀNH VIÊN THỰC HIỆN"
            cp0.font.size = Pt(9.5)
            cp0.font.bold = True
            cp0.font.color.rgb = TEAL
            cp0.alignment = PP_ALIGN.CENTER

            cp1 = ctf.add_paragraph()
            cp1.text = name
            cp1.font.size = Pt(17)
            cp1.font.bold = True
            cp1.font.color.rgb = WHITE
            cp1.alignment = PP_ALIGN.CENTER
            cp1.space_before = Pt(6)

        # Notes
        slide.notes_slide.notes_text_frame.text = notes_text
        return slide

    def add_content_slide(self, category, title, presenter, time_str, notes_text):
        """
        Content slide:
        Khng hi?n th? tn ngu?i trnh by trn slide theo yu c?u c?a ngu?i dng.
        Ch? hi?n th? th?i gian/th?i lu?ng ? gc trn ph?i.
        """
        slide = self.prs.slides.add_slide(self.blank_layout)
        self.slide_count += 1

        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = LIGHT_BG
        bg.line.fill.background()

        # Top Banner bar
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.15))
        banner.fill.solid()
        banner.fill.fore_color.rgb = WHITE
        banner.line.color.rgb = BORDER_COLOR
        banner.line.width = Pt(1)

        # Category Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.18), Inches(3.0), Inches(0.32))
        pill.fill.solid()
        pill.fill.fore_color.rgb = PILL_BG
        pill.line.fill.background()
        tf = pill.text_frame
        p = tf.paragraphs[0]
        p.text = category.upper()
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = PILL_TEXT
        p.alignment = PP_ALIGN.CENTER

        # Slide Title
        tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.48), Inches(8.8), Inches(0.6))
        tf = tx_title.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK

        # Top Right: Time duration ONLY (No presenter name on slide!)
        if time_str:
            tx_time = slide.shapes.add_textbox(Inches(9.2), Inches(0.32), Inches(3.3), Inches(0.55))
            tf = tx_time.text_frame
            p = tf.paragraphs[0]
            p.text = time_str
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = PRIMARY_BLUE
            p.alignment = PP_ALIGN.RIGHT

        # Footer
        tx_foot = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.35))
        tf = tx_foot.text_frame
        p = tf.paragraphs[0]
        p.text = f"ViMMRC Voice Q&A System | Đồ án Học máy tiên tiến và ứng dụng | Slide {self.slide_count}"
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_MUTED

        # Notes
        slide.notes_slide.notes_text_frame.text = notes_text
        return slide

    def add_card(self, slide, left, top, width, height, title="", title_color=PRIMARY_BLUE, bg_color=CARD_BG, border_color=BORDER_COLOR):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)

        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.2)

        if title:
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = title_color
        return shape, tf

    def add_image(self, slide, image_path, left, top, width, height):
        if not os.path.exists(image_path):
            print(f"Warning: image path does not exist: {image_path}")
            return None
        return slide.shapes.add_picture(str(image_path), left, top, width, height)

    def add_table(self, slide, left, top, width, height, headers, rows, col_widths=None):
        num_rows = len(rows) + 1
        num_cols = len(headers)
        table_shape = slide.shapes.add_table(num_rows, num_cols, left, top, width, height)
        table = table_shape.table

        if col_widths and len(col_widths) == num_cols:
            for idx, w in enumerate(col_widths):
                table.columns[idx].width = w

        # Headers
        for col_idx, header in enumerate(headers):
            cell = table.cell(0, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = PRIMARY_BLUE
            cell.text_frame.margin_left = Inches(0.1)
            cell.text_frame.margin_right = Inches(0.1)
            p = cell.text_frame.paragraphs[0]
            p.text = header
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER

        # Rows
        for row_idx, row in enumerate(rows):
            is_even = (row_idx % 2 == 0)
            for col_idx, val in enumerate(row):
                cell = table.cell(row_idx + 1, col_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = WHITE if is_even else CARD_ACCENT_BG
                cell.text_frame.margin_left = Inches(0.1)
                cell.text_frame.margin_right = Inches(0.1)
                p = cell.text_frame.paragraphs[0]
                p.text = str(val)
                p.font.size = Pt(10)
                p.font.color.rgb = TEXT_DARK
                if col_idx == 0:
                    p.font.bold = True
                    p.alignment = PP_ALIGN.LEFT
                else:
                    p.alignment = PP_ALIGN.CENTER
        return table_shape

    def save(self):
        self.prs.save(self.output_path)
        print(f"Saved {self.slide_count} slides to: {self.output_path}")

print("SlideDeckBuilder framework ready.")
