"""Module tiền xử lý và chuẩn hóa văn bản tiếng Việt cho TTS (Vietnamese Text Normalization).

Hỗ trợ:
- Loại bỏ định dạng Markdown.
- Chuẩn hóa nhãn trắc nghiệm (A, B, C, D).
- Xử lý ngày tháng, tỷ lệ phần trăm, đơn vị đo lường.
- Chuyển đổi số nguyên và số thập phân sang chữ tiếng Việt tự nhiên.
"""

import re

DIGITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
UNITS_3 = ["", "nghìn", "triệu", "tỷ"]


def _read_3_digits(n: int, is_highest_group: bool = False) -> str:
    """Đọc nhóm 3 chữ số (0 - 999)."""
    hundred = n // 100
    ten = (n % 100) // 10
    unit = n % 10
    words = []

    if hundred > 0 or not is_highest_group:
        words.append(f"{DIGITS[hundred]} trăm")

    if ten > 1:
        words.append(f"{DIGITS[ten]} mươi")
        if unit == 1:
            words.append("mốt")
        elif unit == 4:
            words.append("tư")
        elif unit == 5:
            words.append("lăm")
        elif unit > 0:
            words.append(DIGITS[unit])
    elif ten == 1:
        words.append("mười")
        if unit == 5:
            words.append("lăm")
        elif unit > 0:
            words.append(DIGITS[unit])
    elif ten == 0:
        if unit > 0:
            if hundred > 0 or not is_highest_group:
                words.append(f"lẻ {DIGITS[unit]}")
            else:
                words.append(DIGITS[unit])

    return " ".join(words)


def read_integer(n: int) -> str:
    """Chuyển số nguyên thành chữ tiếng Việt."""
    if n == 0:
        return "không"

    prefix = ""
    if n < 0:
        prefix = "âm "
        n = abs(n)

    groups = []
    temp = n
    while temp > 0:
        groups.append(temp % 1000)
        temp //= 1000

    result = []
    num_groups = len(groups)
    for i in reversed(range(num_groups)):
        group_val = groups[i]
        if group_val == 0:
            continue
        is_highest = (i == num_groups - 1)
        group_text = _read_3_digits(group_val, is_highest_group=is_highest)
        unit_name = UNITS_3[i % 4]
        if i >= 4:
            unit_name = "tỷ " + UNITS_3[i % 4]
        if unit_name:
            result.append(f"{group_text} {unit_name}".strip())
        else:
            result.append(group_text.strip())

    return prefix + " ".join(result).strip()


def read_number_token(match: re.Match) -> str:
    """Callback chuyển đổi chuỗi số (xử lý số hàng nghìn và số thập phân)."""
    raw = match.group(0).strip()

    # Trường hợp số có dấu chấm ngăn cách hàng nghìn: e.g. 500.000 hoặc 1.250.000
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", raw):
        val = int(raw.replace(".", ""))
        return read_integer(val)

    # Trường hợp số có dấu phẩy ngăn cách hàng nghìn (kiểu Anh): 1,000,000
    if re.fullmatch(r"\d{1,3}(,\d{3})+", raw):
        val = int(raw.replace(",", ""))
        return read_integer(val)

    # Trường hợp số thập phân: e.g. 99.5, 3.14 hoặc 3,5 (không phải dạng nghìn)
    if ("," in raw or "." in raw) and not re.search(r"[.,]{2,}", raw):
        sep = "," if "," in raw else "."
        parts = raw.split(sep)
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            int_part = read_integer(int(parts[0]))
            # Đọc từng chữ số phần thập phân
            dec_part = " ".join(DIGITS[int(d)] for d in parts[1])
            return f"{int_part} phẩy {dec_part}"

    # Trường hợp số nguyên thông thường
    if raw.isdigit():
        return read_integer(int(raw))

    return raw


def normalize_vietnamese_text(text: str) -> str:
    """Tiền xử lý và chuẩn hóa chuỗi văn bản trước khi đưa vào TTS engine."""
    if not text or not text.strip():
        return ""

    s = text.strip()

    # 1. Loại bỏ định dạng Markdown
    s = re.sub(r"\*\*(.*?)\*\*", r"\1", s)
    s = re.sub(r"\*(.*?)\*", r"\1", s)
    s = re.sub(r"`(.*?)`", r"\1", s)
    s = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", s)

    # 2. Chuẩn hóa định dạng câu trả lời trắc nghiệm ViMMRC
    # Ví dụ: "Đáp án: (B)" -> "Đáp án B: ", "(B)" -> "Đáp án B: ", "B." -> "Đáp án B: "
    s = re.sub(r"(?i)\bđáp\s+án\s*[:\s]*\(?([ABCD])\)?(?:\.|\:)?\s*", r"Đáp án \1: ", s)
    s = re.sub(r"(?:^|(?<=[.!?]\s))\(([ABCD])\)\s*", r"Đáp án \1: ", s)
    s = re.sub(r"(?:^|(?<=[.!?]\s))([ABCD])\.\s*", r"Đáp án \1: ", s)
    s = re.sub(r"(?i)\b(đáp án\s+)+", "Đáp án ", s)

    # 3. Chuẩn hóa ngày tháng (dd/mm/yyyy hoặc dd/mm)
    def _replace_date(m):
        prefix = m.group(1) or ""
        day = int(m.group(2))
        month = int(m.group(3))
        year = m.group(4)
        has_ngay_prefix = bool(re.search(r"ngày\s*$", prefix, re.IGNORECASE))
        date_str = "" if has_ngay_prefix else "ngày "
        date_str += f"{day} tháng {month}"
        if year:
            date_str += f" năm {int(year)}"
        return f"{prefix}{date_str}"

    s = re.sub(r"(\bngày\s+)?(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b", _replace_date, s, flags=re.IGNORECASE)

    # 4. Ký hiệu phổ biến & đơn vị đo lường (hỗ trợ cả số hàng nghìn và số thập phân)
    num_re = r"(\d+(?:[.,]\d+)?)"
    s = re.sub(num_re + r"\s*%", r"\1 phần trăm", s)
    s = re.sub(num_re + r"\s*(?:USD|\$)", r"\1 đô la", s)
    s = re.sub(num_re + r"\s*(?:\bVND\b|\bđồng\b|\bđ\b|₫)", r"\1 đồng", s)
    s = re.sub(num_re + r"\s*km/h\b", r"\1 ki-lô-mét trên giờ", s)
    s = re.sub(num_re + r"\s*km2\b", r"\1 ki-lô-mét vuông", s)
    s = re.sub(num_re + r"\s*km²", r"\1 ki-lô-mét vuông", s)
    s = re.sub(num_re + r"\s*km\b", r"\1 ki-lô-mét", s)
    s = re.sub(num_re + r"\s*kg\b", r"\1 ki-lô-gam", s)
    s = re.sub(num_re + r"\s*m²", r"\1 mét vuông", s)
    s = re.sub(num_re + r"\s*m2\b", r"\1 mét vuông", s)
    s = re.sub(num_re + r"\s*m³", r"\1 mét khối", s)
    s = re.sub(num_re + r"\s*m3\b", r"\1 mét khối", s)
    s = re.sub(num_re + r"\s*m\b", r"\1 mét", s)
    s = re.sub(num_re + r"\s*°C\b", r"\1 độ C", s)

    # 5. Thay thế các con số đứng độc lập thành chữ tiếng Việt
    # Pattern khớp số nguyên hoặc số thập phân
    number_pattern = re.compile(r"\b\d+(?:[.,]\d+)?\b")
    s = number_pattern.sub(read_number_token, s)

    # 6. Ký hiệu toán học/nối câu
    s = s.replace("&", " và ")
    s = s.replace("+", " cộng ")
    s = s.replace("=", " bằng ")

    # 7. Xóa khoảng trắng thừa và chuẩn hóa dấu ngắt câu
    s = re.sub(r"\s+", " ", s).strip()

    return s
