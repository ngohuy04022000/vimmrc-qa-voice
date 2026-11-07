"""Trích / ghi lại văn bản của một deck .pptx (hộp văn bản, bảng, ghi chú diễn giả, nhãn biểu đồ), giữ nguyên định dạng.

  python scripts/pptx_i18n.py extract deck.pptx units.json
  python scripts/pptx_i18n.py apply   deck.pptx map.json out.pptx     # map.json: {unit_id: văn bản mới}, chỉ cần các đơn vị muốn đổi

Mỗi đơn vị có id ổn định: s{slide}:sh{chỉ số hình}[:g{con}]:p{đoạn} | ...:r{hàng}c{cột}:p{đoạn} | s{slide}:notes:p{đoạn} |
s{slide}:sh{hình}:cat{i} | s{slide}:sh{hình}:ser{j}. Đoạn có nhiều run: giữ định dạng run đầu, xoá các run còn lại
(các deck của dự án tô đậm cả đoạn bằng một run; đoạn trộn đậm/thường sẽ mất phần trộn).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData


def _paragraphs_of_shape(shape, sid):
    if shape.shape_type == 6:  # group
        for k, child in enumerate(shape.shapes):
            yield from _paragraphs_of_shape(child, f"{sid}:g{k}")
        return
    if getattr(shape, "has_text_frame", False) and shape.has_text_frame:
        for i, p in enumerate(shape.text_frame.paragraphs):
            yield f"{sid}:p{i}", p
    if getattr(shape, "has_table", False) and shape.has_table:
        for r, row in enumerate(shape.table.rows):
            for c, cell in enumerate(row.cells):
                for i, p in enumerate(cell.text_frame.paragraphs):
                    yield f"{sid}:r{r}c{c}:p{i}", p


def iter_units(prs):
    """Yield (id, kind, obj, text): kind in {'p', 'cat', 'ser'}."""
    for n, slide in enumerate(prs.slides, 1):
        for k, shape in enumerate(slide.shapes):
            sid = f"s{n}:sh{k}"
            for uid, p in _paragraphs_of_shape(shape, sid):
                text = "".join(r.text for r in p.runs)
                if text.strip():
                    yield uid, "p", p, text
            if getattr(shape, "has_chart", False) and shape.has_chart:
                if shape.chart.has_title and shape.chart.chart_title.text_frame.paragraphs[0].runs:
                    yield f"{sid}:ctitle", "ctitle", shape.chart, shape.chart.chart_title.text_frame.text
                plot = shape.chart.plots[0]
                for i, cat in enumerate(plot.categories):
                    yield f"{sid}:cat{i}", "cat", shape.chart, str(cat)
                for j, ser in enumerate(plot.series):
                    yield f"{sid}:ser{j}", "ser", shape.chart, ser.name
        if slide.has_notes_slide:
            for i, p in enumerate(slide.notes_slide.notes_text_frame.paragraphs):
                text = "".join(r.text for r in p.runs)
                if text.strip():
                    yield f"s{n}:notes:p{i}", "p", p, text


def set_paragraph_text(p, text: str) -> None:
    runs = p.runs
    if not runs:
        p.add_run().text = text
        return
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def extract(src: Path, out: Path) -> None:
    prs = Presentation(str(src))
    units = {uid: text for uid, _, _, text in iter_units(prs)}
    out.write_text(json.dumps(units, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(units)} units, {sum(len(t) for t in units.values())} chars -> {out}")


def apply(src: Path, mapping: Path, out: Path) -> None:
    prs = Presentation(str(src))
    new = json.loads(mapping.read_text(encoding="utf-8"))
    chart_edits: dict[int, dict] = {}
    done = 0
    for uid, kind, obj, text in iter_units(prs):
        if uid not in new or new[uid] == text:
            continue
        if kind == "p":
            set_paragraph_text(obj, new[uid])
        elif kind == "ctitle":
            set_paragraph_text(obj.chart_title.text_frame.paragraphs[0], new[uid])
        else:
            chart_edits.setdefault(id(obj), {"chart": obj, "cat": {}, "ser": {}})[kind][int(uid.rsplit(kind, 1)[1])] = new[uid]
        done += 1
    for e in chart_edits.values():
        chart = e["chart"]
        plot = chart.plots[0]
        cats = [e["cat"].get(i, str(c)) for i, c in enumerate(plot.categories)]
        data = CategoryChartData()
        data.categories = cats
        for j, ser in enumerate(plot.series):
            vals = []
            for idx in range(len(cats)):
                try:
                    vals.append(ser.values[idx])
                except Exception:
                    vals.append(None)
            data.add_series(e["ser"].get(j, ser.name), vals)
        chart.replace_data(data)
    prs.save(str(out))
    missing = [k for k in new if k not in {u for u, *_ in iter_units(prs)}]
    print(f"applied {done} edits -> {out}; ids not found: {missing[:10]}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "extract":
        extract(Path(sys.argv[2]), Path(sys.argv[3]))
    elif cmd == "apply":
        apply(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
    else:
        sys.exit(__doc__)
