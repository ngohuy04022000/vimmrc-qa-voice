"""Chuẩn hóa văn bản cho câu trả lời của tầng hội thoại (không cần torch: nạp thẳng normalizer.py)."""
import importlib.util
import re
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "normalizer_only", Path(__file__).resolve().parents[1] / "src" / "normalizer.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
normalize = _mod.normalize_vietnamese_text


def test_units_after_multiplier_words():
    assert normalize("diện tích khoảng 9 triệu km².") == "diện tích khoảng chín triệu ki-lô-mét vuông."


def test_digits_glued_to_letters():
    assert normalize("Nước có công thức H2O.") == "Nước có công thức H hai O."


def test_number_ranges():
    assert normalize("ngủ 7-9 giờ") == "ngủ bảy đến chín giờ"
    assert "đến một nghìn tám trăm hai mươi" in normalize("Nguyễn Du (1765–1820)")


def test_roman_numerals_and_abbreviations():
    assert normalize("vào thế kỷ thứ XIX") == "vào thế kỷ thứ mười chín"
    assert normalize("TP.HCM có 14 triệu dân") == "Thành phố Hồ Chí Minh có mười bốn triệu dân"


def test_no_digits_or_unit_symbols_left():
    for text in ("Sa mạc Sahara rộng khoảng 9 triệu km², ban ngày hơn 50 °C.",
                 "Mặt Trăng cách Trái Đất khoảng 384.400 km.", "Trục nghiêng 23,5 độ, 71% là nước."):
        assert not re.search(r"\d|[²³°%]", normalize(text)), normalize(text)


def test_slash_read_as_per():
    assert normalize("300.000 km/s") == "ba trăm nghìn ki-lô-mét trên giây"
    assert normalize("GDP/người") == "GDP trên người"
    assert normalize("và/hoặc") == "và hoặc"
    assert normalize("ngày 2/9/1945") == "ngày hai tháng chín năm một nghìn chín trăm bốn mươi lăm"
