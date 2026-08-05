# -*- coding: utf-8 -*-
"""PDF quote generator – uses fpdf2 with Windows Arial for Vietnamese support."""

from pathlib import Path
from datetime import date as _date

try:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    _OK = True
except ImportError:
    _OK = False

_WIN_FONTS = Path("C:/Windows/Fonts")

_BD = (31,  78,  121)   # blue dark
_BM = (46,  117, 182)   # blue mid
_BL = (217, 225, 242)   # blue light
_WH = (255, 255, 255)
_BK = (0,   0,   0)
_GR = (110, 110, 110)


def _fmt(n) -> str:
    if not n:
        return "—"
    return f"{int(n):,}".replace(",", ".")


def _find_font(name: str):
    for fname in {
        "regular": ["arial.ttf", "Arial.ttf"],
        "bold":    ["arialbd.ttf", "ArialBd.ttf"],
    }.get(name, []):
        p = _WIN_FONTS / fname
        if p.exists():
            return str(p)
    return None


class _PDF(FPDF):
    _fam = "Arial"

    def footer(self):
        self.set_y(-11)
        self.set_font(self._fam, size=7.5)
        self.set_text_color(*_GR)
        self.cell(0, 4, "Công ty TNHH Vật tư Công nghiệp Nam An  |  bulongnaman.vn", align="C")
        self.set_text_color(*_BK)


def _fit_text(pdf: _PDF, text: str, max_w: float, sizes=(8, 7, 6.5, 6)) -> tuple[str, float]:
    """Return (text, font_size) that fits in max_w. Truncates if necessary."""
    for sz in sizes:
        pdf.set_font(pdf._fam, size=sz)
        if pdf.get_string_width(text) <= max_w:
            return text, sz
    # Still too wide at smallest size — truncate
    pdf.set_font(pdf._fam, size=sizes[-1])
    t = text
    while len(t) > 4 and pdf.get_string_width(t + "…") > max_w:
        t = t[:-1]
    return t + "…", sizes[-1]


def _party_box(pdf: _PDF, x: float, y: float, w: float, title: str, rows: list):
    fam  = pdf._fam
    lw   = 22   # label width
    rh   = 5.8  # row height

    pdf.set_xy(x, y)
    pdf.set_fill_color(*_BD)
    pdf.set_text_color(*_WH)
    pdf.set_font(fam, style="B", size=8)
    pdf.cell(w, 7, title, border=1, align="C", fill=True, new_x=XPos.LEFT, new_y=YPos.NEXT)

    for lbl, val in rows:
        cy = pdf.get_y()
        pdf.set_xy(x, cy)
        pdf.set_fill_color(*_BL)
        pdf.set_text_color(*_BD)
        pdf.set_font(fam, style="B", size=7.5)
        pdf.cell(lw, rh, lbl + ":", border=1, fill=True)
        val_txt, _ = _fit_text(pdf, val, w - lw - 2)
        pdf.set_font(fam, size=7.5)
        pdf.set_text_color(*_BK)
        pdf.cell(w - lw, rh, val_txt, border=1, new_x=XPos.LEFT, new_y=YPos.NEXT)


def _tbl_header(pdf: _PDF, cw: dict):
    fam = pdf._fam
    pdf.set_fill_color(*_BD)
    pdf.set_text_color(*_WH)
    pdf.set_font(fam, style="B", size=8)
    for txt, key in [
        ("STT",            "stt"),
        ("Sản phẩm",       "name"),
        ("Chất liệu",      "mat"),
        ("ĐVT",            "dvt"),
        ("SL",             "qty"),
        ("Đơn giá (₫)",    "price"),
        ("Thành tiền (₫)", "total"),
    ]:
        pdf.cell(cw[key], 7, txt, border=1, align="C", fill=True)
    pdf.ln()


def _item_row(pdf: _PDF, idx: int, qi, cw: dict, fill: bool):
    """Draw one product row — wraps product name across multiple lines if needed."""
    fam   = pdf._fam
    r     = qi.result
    name  = r.product_name   or "—"
    mat   = r.material_display or "—"
    price = r.unit_price or 0
    qty   = qi.qty or 1
    total = price * qty
    line_h = 6   # mm per line

    fill_c = _BL if fill else _WH

    # Estimate number of lines for name column (size 8)
    pdf.set_font(fam, size=8)
    avail = cw["name"] - 2
    words, lines_est, cur = name.split(' '), [], ''
    for word in words:
        cand = (cur + ' ' + word).strip()
        if pdf.get_string_width(cand) <= avail:
            cur = cand
        else:
            if cur:
                lines_est.append(cur)
            cur = word
    if cur:
        lines_est.append(cur)
    n_lines = max(1, len(lines_est))
    row_h   = max(line_h, n_lines * line_h)

    # Page break check
    y0 = pdf.get_y()
    if y0 + row_h > pdf.h - pdf.b_margin:
        pdf.add_page()
        _tbl_header(pdf, cw)
        y0 = pdf.get_y()

    lm = pdf.l_margin
    pdf.set_fill_color(*fill_c)
    pdf.set_text_color(*_BK)

    # STT
    pdf.set_font(fam, size=8)
    pdf.set_xy(lm, y0)
    pdf.cell(cw["stt"], row_h, str(idx), border=1, align="C", fill=True)

    # Name — multi_cell wraps text automatically
    pdf.set_font(fam, size=8)
    pdf.set_xy(lm + cw["stt"], y0)
    pdf.multi_cell(cw["name"], line_h, name, border=1, align="L", fill=True,
                   new_x=XPos.RIGHT, new_y=YPos.TOP)

    # Remaining cells — positioned explicitly at y0 with full row_h
    mat_txt, mat_sz = _fit_text(pdf, mat, cw["mat"] - 2, sizes=(7.5, 7, 6.5, 6))
    x = lm + cw["stt"] + cw["name"]
    for txt, w, align, sz, style in [
        (mat_txt,       cw["mat"],   "C", mat_sz, ""),
        ("Cái",         cw["dvt"],   "C", 8,      ""),
        (str(qty),      cw["qty"],   "C", 8,      ""),
        (_fmt(price),   cw["price"], "R", 8,      ""),
        (_fmt(total),   cw["total"], "R", 8,      "B"),
    ]:
        pdf.set_font(fam, style=style, size=sz)
        pdf.set_xy(x, y0)
        pdf.cell(w, row_h, txt, border=1, align=align, fill=True)
        x += w

    pdf.set_xy(lm, y0 + row_h)


def generate_quote_pdf(
    items,
    output_path: str,
    quote_number: str = "",
    receiver_name: str = "",
    receiver_address: str = "",
    receiver_tel: str = "",
    quote_date=None,
    vat_rate: int = 8,
) -> None:
    if not _OK:
        raise RuntimeError("Chưa cài fpdf2. Chạy: pip install fpdf2")

    if quote_date is None:
        quote_date = _date.today()

    pdf = _PDF(orientation="P", unit="mm", format="A4")

    reg  = _find_font("regular")
    bold = _find_font("bold")
    if reg:
        pdf.add_font("Arial", fname=reg)
        if bold:
            pdf.add_font("Arial", style="B", fname=bold)
        pdf._fam = "Arial"
    else:
        pdf._fam = "Helvetica"

    LM, RM = 13, 13
    pdf.set_margins(LM, 14, RM)
    pdf.set_auto_page_break(auto=False)
    pdf.b_margin = 20   # 20mm bottom: leaves room for footer on all pages
    pdf.add_page()

    W = pdf.w - LM - RM   # ≈ 184 mm

    # ── Company header ──────────────────────────────────────────────
    pdf.set_font(pdf._fam, style="B", size=11)
    pdf.set_text_color(*_BD)
    pdf.cell(0, 7, "CÔNG TY TNHH VẬT TƯ CÔNG NGHIỆP NAM AN",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font(pdf._fam, size=7.5)
    pdf.set_text_color(*_GR)
    pdf.cell(0, 4.5, "Số 68 khu đất DV Vân Canh, KĐT mới Vân Canh, Hoài Đức, Hà Nội",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 4.5,
             "Tel: 098 334 41 63 – 098 350 63 89  |  Email: bulongocvitnaman@gmail.com  |  Web: bulongnaman.vn",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(2)
    pdf.set_draw_color(*_BM)
    pdf.set_line_width(0.6)
    pdf.line(LM, pdf.get_y(), pdf.w - RM, pdf.get_y())
    pdf.ln(3)

    # ── Title ───────────────────────────────────────────────────────
    pdf.set_font(pdf._fam, style="B", size=15)
    pdf.set_text_color(*_BD)
    pdf.cell(0, 9, "THƯ BÁO GIÁ", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if quote_number:
        pdf.set_font(pdf._fam, size=9.5)
        pdf.set_text_color(*_BM)
        pdf.cell(0, 5, quote_number, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    d = quote_date
    pdf.set_font(pdf._fam, size=8.5)
    pdf.set_text_color(*_GR)
    pdf.cell(0, 5, f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # ── Parties ─────────────────────────────────────────────────────
    gap   = 4
    col_w = (W - gap) / 2
    y0    = pdf.get_y()

    _party_box(pdf, LM,               y0, col_w, "BÊN GIAO", [
        ("Đại diện", "Lê Ngọc Dũng"),
        ("Địa chỉ",  "68 khu đất DV Vân Canh, Hoài Đức, HN"),
        ("Tel",      "098 334 41 63"),
    ])
    _party_box(pdf, LM + col_w + gap, y0, col_w, "BÊN NHẬN", [
        ("Tên",     receiver_name    or "—"),
        ("Địa chỉ", receiver_address or "—"),
        ("Tel",     receiver_tel     or "—"),
    ])

    # Advance past party boxes (header 7mm + 3 rows × 5.8mm)
    pdf.set_y(y0 + 7 + 3 * 5.8 + 5)

    # ── Items table ──────────────────────────────────────────────────
    cw = {"stt": 11, "name": 72, "mat": 27, "dvt": 12,
          "qty": 12, "price": 25, "total": 25}
    cw["name"] += W - sum(cw.values())   # absorb any rounding

    pdf.set_draw_color(*_BM)
    pdf.set_line_width(0.3)
    _tbl_header(pdf, cw)

    sub = 0
    for idx, qi in enumerate(items, 1):
        _item_row(pdf, idx, qi, cw, fill=(idx % 2 == 0))
        sub += (qi.result.unit_price or 0) * (qi.qty or 1)

    # ── Totals ───────────────────────────────────────────────────────
    vat   = round(sub * vat_rate / 100)
    grand = sub + vat
    span  = sum(cw[k] for k in ("stt", "name", "mat", "dvt", "qty"))

    pdf.set_font(pdf._fam, style="B", size=8.5)
    for label, amount, bg in [
        ("Tổng chưa VAT",     sub,   _BL),
        (f"VAT ({vat_rate}%)", vat,   _BL),
        ("TỔNG GỒM VAT",      grand, _BD),
    ]:
        tc  = _WH if bg == _BD else _BD
        rh2 = 7 if bg == _BD else 6
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*tc)
        pdf.cell(span,                       rh2, label,              border=1, align="R", fill=True)
        pdf.cell(cw["price"] + cw["total"],  rh2, _fmt(amount) + " ₫", border=1, align="R", fill=True)
        pdf.ln()

    pdf.ln(6)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)

    # ── Conditions ──────────────────────────────────────────────────
    pdf.set_font(pdf._fam, size=8)
    pdf.set_text_color(*_BK)
    for line in [
        "Tình trạng hàng hóa: Chưa qua sử dụng, đầy đủ phụ kiện",
        "Thanh toán: Thanh toán 100% trước khi nhận hàng.",
        "Thời gian giao hàng: 20–25 ngày kể từ khi có xác nhận đơn hàng.",
        "Thời gian bảo hành: 30 ngày khi có lỗi từ bên cung cấp.",
        "Giao hàng tại: Tại kho Nam An",
    ]:
        pdf.cell(0, 5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(10)

    # ── Signatures ──────────────────────────────────────────────────
    half = W / 2
    pdf.set_font(pdf._fam, style="B", size=9)
    pdf.set_text_color(*_BK)
    pdf.cell(half, 6, "Đại diện bên giao", align="C")
    pdf.cell(half, 6, "Đại diện bên nhận", align="C")
    pdf.ln()

    pdf.set_font(pdf._fam, size=8)
    pdf.set_text_color(*_GR)
    pdf.cell(half, 5, "Công Ty TNHH Vật Tư Công Nghiệp Nam An", align="C")
    pdf.cell(half, 5, receiver_name or "", align="C")
    pdf.ln(22)

    pdf.set_font(pdf._fam, style="B", size=9)
    pdf.set_text_color(*_BK)
    pdf.cell(half, 6, "Lê Ngọc Dũng", align="C")
    pdf.cell(half, 6, "", align="C")
    pdf.ln()

    pdf.output(output_path)
