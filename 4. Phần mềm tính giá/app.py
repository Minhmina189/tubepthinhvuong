# -*- coding: utf-8 -*-
"""
Phần mềm báo giá Nam An - Flask Web App
"""
import json
import uuid
from datetime import date
from pathlib import Path

# Load .env file if present (ANTHROPIC_API_KEY etc.)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from flask import (Flask, flash, redirect, render_template,
                   request, send_file, session, url_for)

from flask import jsonify

from product_matcher import match_product, get_suggestions, MatchResult
from quote_generator import QuoteItem, generate_quote_excel
from pdf_generator import generate_quote_pdf
from input_parser import parse_input_file
import price_overrides  # applies overrides at startup

# ─────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
UPLOAD_DIR  = BASE_DIR / "uploads"
OUTPUT_DIR  = BASE_DIR / "outputs"
TEMPLATE_DIR = BASE_DIR / "templates"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
HISTORY_FILE = BASE_DIR / "quote_history.json"


def _append_history(entry: dict):
    history = []
    if HISTORY_FILE.exists():
        try:
            history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            history = []
    history.insert(0, entry)
    HISTORY_FILE.write_text(
        json.dumps(history[:200], ensure_ascii=False, indent=2), encoding="utf-8"
    )

ALLOWED_EXT = {
    ".xlsx", ".xls", ".csv",
    ".docx", ".doc",
    ".pdf",
    ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp",
}

app = Flask(__name__, template_folder=str(TEMPLATE_DIR))
app.secret_key = "naman-baogia-2026"
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024  # 30 MB (PDF/image support)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXT


def fmt_currency(value) -> str:
    if value is None:
        return "—"
    return f"{int(value):,}".replace(",", ".")


app.jinja_env.filters["currency"] = fmt_currency


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f or f.filename == "":
        flash("Vui lòng chọn file Excel hoặc CSV.", "error")
        return redirect(url_for("index"))

    if not allowed_file(f.filename):
        flash("Định dạng không được hỗ trợ. Vui lòng dùng Excel, CSV, Word, PDF hoặc ảnh.", "error")
        return redirect(url_for("index"))

    ext = Path(f.filename).suffix.lower()
    uid = uuid.uuid4().hex[:8]
    upload_path = UPLOAD_DIR / f"{uid}{ext}"
    f.save(str(upload_path))

    # Parse customer file (all formats)
    try:
        raw_items = parse_input_file(str(upload_path))
    except Exception as e:
        flash(f"Lỗi đọc file: {e}", "error")
        return redirect(url_for("index"))

    if not raw_items:
        flash("Không tìm thấy sản phẩm nào trong file. "
              "Kiểm tra file có cột tên hàng (ví dụ: 'Tên hàng', 'Tên sản phẩm', 'Vật tư') "
              "và cột số lượng ('Số lượng', 'SL', 'Qty'). "
              "Hoặc dùng chức năng Nhập Tay để điền thủ công.", "error")
        return redirect(url_for("index"))

    # Match products and compute confidence + suggestions
    quote_items_data = []
    for i, raw in enumerate(raw_items, 1):
        result = match_product(raw["name"], raw["material"], raw.get("raw_desc", ""))
        suggs  = get_suggestions(result.ptype, result.material_key,
                                 result.size, result.length, result.confidence)
        quote_items_data.append({
            "stt":              i,
            "raw_name":         raw["name"],
            "raw_mat":          raw["material"],
            "qty":              raw["qty"],
            "note_in":          raw.get("note_in", ""),
            "product_name":     result.product_name or raw["name"],
            "material_display": result.material_display or raw["material"],
            "size":             result.size,
            "length":           result.length,
            "unit_price":       result.unit_price,
            "total":            (result.unit_price * raw["qty"]) if result.unit_price else None,
            "note":             result.note,
            "matched":          result.matched,
            "confidence":       result.confidence,
            "ptype":            result.ptype,
            "material_key":     result.material_key,
            "suggestions":      suggs,
            "set_detail":       result.set_detail,
            "in_stock":         result.in_stock,
        })

    session["uid"]         = uid
    session["items"]       = quote_items_data
    session["upload_path"] = str(upload_path)
    return redirect(url_for("review"))


@app.route("/review", methods=["GET"])
def review():
    items = session.get("items", [])
    if not items:
        flash("Phiên làm việc đã hết hạn. Vui lòng upload lại.", "error")
        return redirect(url_for("index"))

    # Always re-compute in_stock from current DB so old sessions stay accurate
    from in_stock_db import is_in_stock as _is_in_stock
    for it in items:
        it["in_stock"] = _is_in_stock(
            it.get("ptype"),
            it.get("material_key"),
            it.get("size"),
            it.get("length"),
        )

    prefill = session.pop("prefill", None)  # consume once so refresh doesn't re-apply

    high   = sum(1 for it in items if it.get("confidence") == "high")
    medium = sum(1 for it in items if it.get("confidence") == "medium")
    low    = sum(1 for it in items if it.get("confidence") in ("low", "none"))

    subtotal = sum(it["total"] or 0 for it in items)
    vat      = round(subtotal * 0.08)
    total    = subtotal + vat

    return render_template(
        "review.html",
        items=items,
        high=high, medium=medium, low=low,
        subtotal=subtotal, vat=vat, total=total,
        prefill=prefill,
    )


def _parse_quote_form():
    """Parse shared quote form fields. Returns (meta_dict, quote_items, vat_rate) or raises."""
    quote_number     = request.form.get("quote_number", "").strip()
    receiver_name    = request.form.get("receiver_name", "").strip()
    receiver_address = request.form.get("receiver_address", "").strip()
    receiver_tel     = request.form.get("receiver_tel", "").strip()
    try:
        vat_rate = int(request.form.get("vat_rate", "8"))
    except ValueError:
        vat_rate = 8
    try:
        item_count = int(request.form.get("item_count", 0))
    except ValueError:
        item_count = 0

    quote_items = []
    for i in range(1, item_count + 1):
        pname    = request.form.get(f"pname_{i}", "").strip()
        mat      = request.form.get(f"mat_{i}", "").strip()
        note     = request.form.get(f"note_{i}", "").strip()
        raw_name = request.form.get(f"raw_name_{i}", pname)
        raw_mat  = request.form.get(f"raw_mat_{i}", mat)
        try:
            qty = max(1, int(float(request.form.get(f"qty_{i}", "1") or "1")))
        except ValueError:
            qty = 1
        try:
            price_str = (request.form.get(f"price_{i}", "") or "").strip()
            price = int(float(price_str)) if price_str else None
        except ValueError:
            price = None
        if not pname:
            continue
        r = MatchResult()
        r.product_name     = pname
        r.material_display = mat
        r.unit_price       = price
        r.note             = note
        r.matched          = True
        quote_items.append(QuoteItem(stt=i, raw_name=raw_name, raw_mat=raw_mat,
                                     qty=qty, result=r, note_in=""))

    meta = dict(quote_number=quote_number, receiver_name=receiver_name,
                receiver_address=receiver_address, receiver_tel=receiver_tel)
    return meta, quote_items, vat_rate


@app.route("/generate", methods=["POST"])
def generate():
    uid = session.get("uid", uuid.uuid4().hex[:8])

    meta, quote_items, vat_rate = _parse_quote_form()
    quote_number     = meta["quote_number"]
    receiver_name    = meta["receiver_name"]
    receiver_address = meta["receiver_address"]
    receiver_tel     = meta["receiver_tel"]

    if not quote_items:
        flash("Không có sản phẩm hợp lệ để tạo báo giá.", "error")
        return redirect(url_for("review"))

    output_filename = f"BaoGia_{uid}_{quote_number or 'NAM-AN'}.xlsx"
    output_path     = OUTPUT_DIR / output_filename

    try:
        generate_quote_excel(
            items=quote_items,
            output_path=str(output_path),
            quote_number=quote_number,
            receiver_name=receiver_name,
            receiver_address=receiver_address,
            receiver_tel=receiver_tel,
            quote_date=date.today(),
            vat_rate=vat_rate,
        )
    except Exception as e:
        flash(f"Lỗi tạo file Excel: {e}", "error")
        return redirect(url_for("review"))

    # Save to history
    try:
        sub = sum((qi.result.unit_price or 0) * qi.qty for qi in quote_items)
        _append_history({
            "id":           str(uuid.uuid4()),
            "date":         date.today().isoformat(),
            "quote_number": quote_number or "—",
            "customer":     receiver_name or "—",
            "address":      receiver_address or "",
            "tel":          receiver_tel or "",
            "vat_rate":     vat_rate,
            "item_count":   len(quote_items),
            "subtotal":     sub,
            "file":         output_filename,
            "items": [
                {
                    "stt":   qi.stt,
                    "pname": qi.result.product_name or "",
                    "mat":   qi.result.material_display or "",
                    "qty":   qi.qty,
                    "price": qi.result.unit_price or 0,
                    "total": (qi.result.unit_price or 0) * qi.qty,
                }
                for qi in quote_items
            ],
        })
    except Exception:
        pass

    return send_file(
        str(output_path),
        as_attachment=True,
        download_name=output_filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    uid = session.get("uid", uuid.uuid4().hex[:8])

    meta, quote_items, vat_rate = _parse_quote_form()
    quote_number     = meta["quote_number"]
    receiver_name    = meta["receiver_name"]
    receiver_address = meta["receiver_address"]
    receiver_tel     = meta["receiver_tel"]

    if not quote_items:
        flash("Không có sản phẩm hợp lệ để tạo báo giá.", "error")
        return redirect(url_for("review"))

    pdf_filename = f"BaoGia_{uid}_{quote_number or 'NAM-AN'}.pdf"
    pdf_path     = OUTPUT_DIR / pdf_filename

    try:
        generate_quote_pdf(
            items=quote_items,
            output_path=str(pdf_path),
            quote_number=quote_number,
            receiver_name=receiver_name,
            receiver_address=receiver_address,
            receiver_tel=receiver_tel,
            quote_date=date.today(),
            vat_rate=vat_rate,
        )
    except Exception as e:
        flash(f"Lỗi tạo file PDF: {e}", "error")
        return redirect(url_for("review"))

    # Save to history (PDF does not overwrite Excel entry)
    try:
        sub = sum((qi.result.unit_price or 0) * qi.qty for qi in quote_items)
        _append_history({
            "id":           str(uuid.uuid4()),
            "date":         date.today().isoformat(),
            "quote_number": quote_number or "—",
            "customer":     receiver_name or "—",
            "address":      receiver_address or "",
            "tel":          receiver_tel or "",
            "vat_rate":     vat_rate,
            "item_count":   len(quote_items),
            "subtotal":     sub,
            "file":         pdf_filename,
            "format":       "pdf",
            "items": [
                {
                    "stt":   qi.stt,
                    "pname": qi.result.product_name or "",
                    "mat":   qi.result.material_display or "",
                    "qty":   qi.qty,
                    "price": qi.result.unit_price or 0,
                    "total": (qi.result.unit_price or 0) * qi.qty,
                }
                for qi in quote_items
            ],
        })
    except Exception:
        pass

    return send_file(
        str(pdf_path),
        as_attachment=True,
        download_name=pdf_filename,
        mimetype="application/pdf",
    )


@app.route("/manual", methods=["GET"])
def manual():
    """Nhập đơn hàng thủ công (không upload file)."""
    return render_template("manual.html")


@app.route("/manual_submit", methods=["POST"])
def manual_submit():
    """Xử lý đơn hàng nhập thủ công."""
    names     = request.form.getlist("name[]")
    materials = request.form.getlist("material[]")
    qtys      = request.form.getlist("qty[]")
    notes_in  = request.form.getlist("note_in[]")

    raw_items = []
    for i, (n, m, q, ni) in enumerate(zip(names, materials, qtys, notes_in)):
        n = n.strip()
        if not n:
            continue
        try:
            qty = max(1, int(float(q))) if q.strip() else 1
        except ValueError:
            qty = 1
        raw_items.append({"name": n, "material": m.strip(), "qty": qty, "note_in": ni.strip()})

    if not raw_items:
        flash("Vui lòng nhập ít nhất một sản phẩm.", "error")
        return redirect(url_for("manual"))

    quote_items_data = []
    for i, raw in enumerate(raw_items, 1):
        result = match_product(raw["name"], raw["material"], raw.get("raw_desc", ""))
        suggs  = get_suggestions(result.ptype, result.material_key,
                                 result.size, result.length, result.confidence)
        quote_items_data.append({
            "stt":              i,
            "raw_name":         raw["name"],
            "raw_mat":          raw["material"],
            "qty":              raw["qty"],
            "note_in":          raw.get("note_in", ""),
            "product_name":     result.product_name or raw["name"],
            "material_display": result.material_display or raw["material"],
            "size":             result.size,
            "length":           result.length,
            "unit_price":       result.unit_price,
            "total":            (result.unit_price * raw["qty"]) if result.unit_price else None,
            "note":             result.note,
            "matched":          result.matched,
            "confidence":       result.confidence,
            "ptype":            result.ptype,
            "material_key":     result.material_key,
            "suggestions":      suggs,
            "set_detail":       result.set_detail,
        })

    uid = uuid.uuid4().hex[:8]
    session["uid"]   = uid
    session["items"] = quote_items_data
    return redirect(url_for("review"))


@app.route("/lookup", methods=["GET", "POST"])
def lookup():
    """Tra giá đơn lẻ."""
    result = None
    if request.method == "POST":
        name     = request.form.get("name", "")
        material = request.form.get("material", "")
        r = match_product(name, material)
        result = {
            "product_name": r.product_name,
            "material_display": r.material_display,
            "size": r.size,
            "length": r.length,
            "unit_price": r.unit_price,
            "note": r.note,
        }
    return render_template("lookup.html", result=result)


# ─────────────────────────────────────────────
# PRICE CATALOG STRUCTURE
# ─────────────────────────────────────────────

# Maps price-table name → (ptype, material) for is_in_stock lookup
_TABLE_STOCK_META = {
    "BULONG_304_DIN933":  ("bulong",     "inox_304"),
    "BULONG_201":         ("bulong",     "inox_201"),
    "BULONG_316_DIN933":  ("bulong",     "inox_316"),
    "LGC_304_DIN912":     ("lgc_tru",    "inox_304"),
    "LGC_201_DIN912":     ("lgc_tru",    "inox_201"),
    "LGC_316_DIN912":     ("lgc_tru",    "inox_316"),
    "VIT_TRI_304":        ("vit_tri",    "inox_304"),
    "VIT_TRI_201":        ("vit_tri",    "inox_201"),
    "ECU_304":            ("ecu",        "inox_304"),
    "ECU_MU_304":         ("ecu_mu",     "inox_304"),
    "ECU_MU_201":         ("ecu_mu",     "inox_201"),
    "ECU_MU_316":         ("ecu_mu",     "inox_316"),
    "ECU_KHOA_201":       ("ecu_khoa",   "inox_201"),
    "ECU_KHOA_316":       ("ecu_khoa",   "inox_316"),
    "ECU_FLANGE_304":     ("ecu_flange", "inox_304"),
    "ECU_FLANGE_201":     ("ecu_flange", "inox_201"),
    "THANH_REN_304":           ("thanh_ren",    "inox_304"),
    "THANH_REN_201":           ("thanh_ren",    "inox_201"),
    "THANH_REN_316":           ("thanh_ren",    "inox_316"),
    "NOR_DAN_304":             ("nor_dan",      "inox_304"),
    "LGC_CHOM_CAU_304_DIN7380":  ("lgc_chom_cau",    "inox_304"),
    "LGC_DAU_BANG_304_DIN7991":  ("lgc_dau_bang",    "inox_304"),
    "BULONG_TAI_HONG_304":       ("bulong_tai_hong", "inox_304"),
    "ECU_TAI_HONG_304":          ("ecu_tai_hong",    "inox_304"),
    "BULONG_NO_304":             ("bulong_no",       "inox_304"),
}

PRICE_CATALOG_GROUPS = [
    {"group": "Bu lông lục giác đầu ngoài", "icon": "🔩", "tables": [
        {"name": "BULONG_304_DIN933",        "label": "Bu lông Inox 304 DIN933"},
        {"name": "BULONG_201",               "label": "Bu lông Inox 201"},
        {"name": "BULONG_316_DIN933",        "label": "Bu lông Inox 316 DIN933"},
        {"name": "BULONG_88_DEN",            "label": "Bu lông 8.8 đen"},
        {"name": "BULONG_88_MA_KEM",         "label": "Bu lông 8.8 mạ kẽm"},
        {"name": "BULONG_109_DEN",           "label": "Bu lông 10.9 đen"},
        {"name": "BULONG_109_MA_KEM",        "label": "Bu lông 10.9 mạ kẽm"},
        {"name": "BULONG_109_DEN_REN_LUNG",  "label": "Bu lông 10.9 đen ren lửng (DIN 931)"},
    ]},
    {"group": "Lục giác chìm trụ DIN912", "icon": "🔩", "tables": [
        {"name": "LGC_304_DIN912",     "label": "LGC trụ Inox 304"},
        {"name": "LGC_201_DIN912",     "label": "LGC trụ Inox 201"},
        {"name": "LGC_316_DIN912",     "label": "LGC trụ Inox 316"},
        {"name": "LGC_TRU_DIN912_129", "label": "LGC trụ 12.9 đen"},
    ]},
    {"group": "Lục giác chìm chỏm cầu DIN7380", "icon": "🔩", "tables": [
        {"name": "LGC_CHOM_CAU_304_DIN7380", "label": "LGC chỏm cầu Inox 304"},
        {"name": "LGC_CHOM_CAU_109_DIN7380", "label": "LGC chỏm cầu 10.9 đen"},
    ]},
    {"group": "Lục giác chìm đầu bằng DIN7991", "icon": "🔩", "tables": [
        {"name": "LGC_DAU_BANG_304_DIN7991", "label": "LGC đầu bằng Inox 304"},
        {"name": "LGC_BANG_88_DIN7991",      "label": "LGC đầu bằng 8.8 đen"},
        {"name": "LGC_BANG_109_DIN7991",      "label": "LGC đầu bằng 10.9 đen"},
    ]},
    {"group": "Vít trí DIN916", "icon": "🔩", "tables": [
        {"name": "VIT_TRI_304",        "label": "Vít trí Inox 304"},
        {"name": "VIT_TRI_201",        "label": "Vít trí Inox 201"},
        {"name": "VIT_TRI_DEN_DIN916", "label": "Vít trí đen DIN916"},
    ]},
    {"group": "Đai ốc (ECU)", "icon": "⚙", "tables": [
        {"name": "ECU_304",       "label": "ECU Inox 304"},
        {"name": "ECU_88_DEN",    "label": "ECU 8.8 đen"},
        {"name": "ECU_88_MA_KEM", "label": "ECU 8.8 mạ kẽm"},
        {"name": "ECU_109_DEN",   "label": "ECU 10.9 đen"},
        {"name": "ECU_109_MA_KEM","label": "ECU 10.9 mạ kẽm"},
        {"name": "ECU_129_DEN",   "label": "ECU 12.9 đen"},
        {"name": "ECU_129_MA_KEM","label": "ECU 12.9 mạ kẽm"},
    ]},
    {"group": "ECU đặc biệt", "icon": "⚙", "tables": [
        {"name": "ECU_MU_304",     "label": "ECU mũ Inox 304 DIN1587"},
        {"name": "ECU_MU_201",     "label": "ECU mũ Inox 201"},
        {"name": "ECU_MU_316",     "label": "ECU mũ Inox 316"},
        {"name": "ECU_MU_MA",      "label": "ECU mũ mạ"},
        {"name": "ECU_KHOA_201",   "label": "ECU khóa Inox 201 DIN985"},
        {"name": "ECU_KHOA_316",   "label": "ECU khóa Inox 316"},
        {"name": "ECU_KHOA_MA",    "label": "ECU khóa mạ"},
        {"name": "ECU_FLANGE_304", "label": "ECU liền long đen Inox 304 DIN6923"},
        {"name": "ECU_FLANGE_201", "label": "ECU liền long đen Inox 201"},
    ]},
    {"group": "Long đen / Đệm", "icon": "⭕", "tables": [
        {"name": "LDP_THEP",           "label": "Long đen phẳng thép đen"},
        {"name": "LDP_MA_KEM",         "label": "Long đen phẳng mạ kẽm"},
        {"name": "LDV_THEP",           "label": "Long đen vênh thép đen"},
        {"name": "LDV_MA_KEM",         "label": "Long đen vênh mạ kẽm"},
        {"name": "LONG_DEN_XUOC_THEP", "label": "Long đen xước thép"},
        {"name": "LONG_DEN_XUOC_304",  "label": "Long đen xước Inox 304"},
    ]},
    {"group": "Thanh ren DIN975", "icon": "📏", "tables": [
        {"name": "THANH_REN_304",     "label": "Thanh ren Inox 304"},
        {"name": "THANH_REN_201",     "label": "Thanh ren Inox 201"},
        {"name": "THANH_REN_316",     "label": "Thanh ren Inox 316"},
        {"name": "THANH_REN_88_DEN",  "label": "Thanh ren 8.8 đen"},
        {"name": "THANH_REN_109_DEN", "label": "Thanh ren 10.9 đen"},
    ]},
    {"group": "Tán rút / Móc cẩu / Khác", "icon": "🔗", "tables": [
        {"name": "TAN_RUT_304",       "label": "Tán rút Inox 304"},
        {"name": "TAN_RUT_THEP",      "label": "Tán rút thép đen"},
        {"name": "MOC_CAU_DUONG_304", "label": "Móc cẩu dương Inox 304"},
        {"name": "MOC_CAU_88_MA",     "label": "Móc cẩu 8.8 mạ"},
        {"name": "VIT_BAN_TON_304",   "label": "Vít bắn tôn Inox 304"},
        {"name": "BULONG_NO_304",       "label": "Bulong nở Inox 304"},
        {"name": "NOR_DAN_304",         "label": "Nở đạn Inox 304"},
        {"name": "BULONG_TAI_HONG_304", "label": "Bulong tai hồng Inox 304 DIN316"},
        {"name": "ECU_TAI_HONG_304",    "label": "ECU tai hồng SUS 304"},
    ]},
    {"group": "Ubolt mạ kẽm (kẹp ống chữ U)", "icon": "🔗", "tables": [
        {"name": "UBOLT_MA_KEM",            "label": "Ubolt mạ kẽm – đơn giá chiếc"},
        {"name": "UBOLT_MA_KEM_BO",         "label": "Ubolt mạ kẽm – đơn giá bộ (T+2E+2P)"},
        {"name": "UBOLT_MA_KEM_NHUNG_NHUA", "label": "Ubolt mạ kẽm nhúng nhựa – chiếc"},
        {"name": "UBOLT_BOC_NHUA",          "label": "Ubolt mạ kẽm bọc nhựa – tiêu chuẩn (T+2E+2P)"},
        {"name": "DEM_NHUA_UBOLT",          "label": "Đệm nhựa (phụ kiện bọc nhựa)"},
    ]},
]


def _build_price_catalog():
    """Build structured catalog with table data for the price viewer."""
    import price_database as pd
    from in_stock_db import is_in_stock
    catalog = []
    for group in PRICE_CATALOG_GROUPS:
        tables = []
        for t in group["tables"]:
            tbl = getattr(pd, t["name"], None)
            if not tbl:
                continue
            first_val = next(iter(tbl.values()), None)
            is_2d = isinstance(first_val, dict)
            # Collect all columns for 2D tables
            cols = None
            if is_2d:
                seen, cols = set(), []
                for row_data in tbl.values():
                    for col in row_data:
                        if col not in seen:
                            seen.add(col)
                            cols.append(col)
                def _col_key(c):
                    import re as _re
                    m = _re.match(r'(?:dn|[øφΦ])\s*(\d+)', str(c).lower())
                    return (1, int(m.group(1)), str(c)) if m else (0, 0, str(c))
                str_cols = sorted([c for c in cols if isinstance(c, str)], key=_col_key)
                int_cols = sorted([c for c in cols if isinstance(c, int)])
                cols = str_cols + int_cols
            # Pre-compute in_stock status for each cell
            in_stock = None
            meta = _TABLE_STOCK_META.get(t["name"])
            if meta:
                ptype, material = meta
                in_stock = {}
                if is_2d:
                    for size, row_data in tbl.items():
                        in_stock[size] = {col: is_in_stock(ptype, material, size, col)
                                          for col in row_data}
                else:
                    for size in tbl:
                        in_stock[size] = is_in_stock(ptype, material, size, None)
            tables.append({
                "name":     t["name"],
                "label":    t["label"],
                "data":     tbl,
                "is_2d":    is_2d,
                "cols":     cols,
                "in_stock": in_stock,
            })
        if tables:
            catalog.append({
                "group":  group["group"],
                "icon":   group["icon"],
                "tables": tables,
            })
    return catalog


@app.route("/prices", methods=["GET"])
def prices():
    """Xem và sửa bảng giá hệ thống."""
    import stock_overrides as _so
    catalog = _build_price_catalog()
    return render_template(
        "prices.html",
        catalog=catalog,
        has_overrides=(BASE_DIR / "price_overrides.json").exists(),
        has_stock_overrides=_so.has_any_overrides(),
    )


@app.route("/prices/save", methods=["POST"])
def prices_save():
    """AJAX: lưu một ô giá đã sửa."""
    data = request.get_json(force=True)
    try:
        price_overrides.save_override(
            data["table_name"],
            data["size_key"],
            data.get("sub_key") or None,
            int(data["new_price"]),
        )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/prices/reset", methods=["POST"])
def prices_reset():
    """Xóa toàn bộ bảng giá đã sửa (cần restart để có hiệu lực đầy đủ)."""
    price_overrides.reset_overrides()
    flash("Đã xóa bảng giá tùy chỉnh. Khởi động lại phần mềm để hoàn tất.", "info")
    return redirect(url_for("prices"))


@app.route("/prices/stock-save", methods=["POST"])
def prices_stock_save():
    """AJAX: lưu trạng thái tồn kho của một ô (server-side persistence)."""
    import stock_overrides as _so
    data = request.get_json(force=True)
    try:
        val_str = data.get("value", "")
        if val_str == "yes":
            value = True
        elif val_str == "no":
            value = False
        else:
            value = None  # "auto" → xóa override, về giá trị gốc
        _so.save_stock_override(
            data["table_name"],
            data["size_key"],
            data.get("sub_key") or None,
            value,
        )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/prices/stock-reset", methods=["POST"])
def prices_stock_reset():
    """Xóa toàn bộ tồn kho đã sửa, về giá trị gốc."""
    import stock_overrides as _so
    _so.reset_all()
    flash("Đã đặt lại toàn bộ tồn kho về mặc định.", "info")
    return redirect(url_for("prices"))


# ─────────────────────────────────────────────
# DIN MAPPING ROUTES
# ─────────────────────────────────────────────

DIN_MAP_FILE = BASE_DIR / "din_mapping.json"


def _load_din_mapping() -> dict:
    if not DIN_MAP_FILE.exists():
        return {}
    try:
        raw = json.loads(DIN_MAP_FILE.read_text(encoding="utf-8"))
        return {k: v for k, v in raw.items() if not k.startswith("_")}
    except Exception:
        return {}


@app.route("/din-mapping", methods=["GET"])
def din_mapping_page():
    mapping = _load_din_mapping()
    # Sort numerically for display
    sorted_map = dict(sorted(mapping.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 9999))
    return render_template("din_mapping.html", mapping=sorted_map)


@app.route("/din-mapping/save", methods=["POST"])
def din_mapping_save():
    """AJAX: thêm hoặc cập nhật một dòng trong bảng DIN."""
    data = request.get_json(force=True)
    din_num = str(data.get("din", "")).strip()
    ten     = str(data.get("ten", "")).strip()
    if not din_num or not ten:
        return jsonify({"ok": False, "error": "Thiếu mã DIN hoặc tên sản phẩm"})
    mapping = _load_din_mapping()
    mapping[din_num] = {
        "ten":         ten,
        "co_chieu_dai": bool(data.get("co_chieu_dai", False)),
        "ghi_chu":     str(data.get("ghi_chu", "")).strip(),
        "ky_hieu":     str(data.get("ky_hieu", "")).strip(),
    }
    try:
        out = {"_comment": "Bảng tra mã DIN/ISO → tên sản phẩm Nam An"}
        out.update(mapping)
        DIN_MAP_FILE.write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/din-mapping/delete", methods=["POST"])
def din_mapping_delete():
    """AJAX: xóa một dòng DIN."""
    data    = request.get_json(force=True)
    din_num = str(data.get("din", "")).strip()
    mapping = _load_din_mapping()
    mapping.pop(din_num, None)
    try:
        out = {"_comment": "Bảng tra mã DIN/ISO → tên sản phẩm Nam An"}
        out.update(mapping)
        DIN_MAP_FILE.write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# ─────────────────────────────────────────────
# QUOTE HISTORY
# ─────────────────────────────────────────────

@app.route("/history", methods=["GET"])
def history():
    entries = []
    if HISTORY_FILE.exists():
        try:
            entries = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            entries = []
    return render_template("history.html", entries=entries)


@app.route("/history/download/<filename>")
def history_download(filename):
    # Security: only allow filenames that match expected pattern
    import re as _re
    if not _re.match(r'^BaoGia_[a-zA-Z0-9_\-\.]+\.(xlsx|pdf)$', filename):
        flash("Tên file không hợp lệ.", "error")
        return redirect(url_for("history"))
    path = OUTPUT_DIR / filename
    if not path.exists():
        flash("File không còn tồn tại trên máy chủ.", "error")
        return redirect(url_for("history"))
    return send_file(
        str(path), as_attachment=True, download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.route("/history/view/<entry_id>")
def history_view(entry_id):
    entries = []
    if HISTORY_FILE.exists():
        try:
            entries = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            entries = []
    entry = next((e for e in entries if e.get("id") == entry_id), None)
    if not entry:
        flash("Không tìm thấy báo giá này trong lịch sử.", "error")
        return redirect(url_for("history"))
    sub      = entry.get("subtotal", 0) or 0
    vat_rate = entry.get("vat_rate", 8) or 8
    vat      = round(sub * vat_rate / 100)
    grand    = sub + vat
    return render_template("history_view.html", entry=entry, vat=vat, grand=grand)


@app.route("/history/copy/<entry_id>")
def history_copy(entry_id):
    entries = []
    if HISTORY_FILE.exists():
        try:
            entries = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            entries = []
    entry = next((e for e in entries if e.get("id") == entry_id), None)
    if not entry:
        flash("Không tìm thấy báo giá này trong lịch sử.", "error")
        return redirect(url_for("history"))

    raw_items = entry.get("items", [])
    if not raw_items:
        flash("Báo giá này không có sản phẩm để sao chép.", "error")
        return redirect(url_for("history_view", entry_id=entry_id))

    quote_items_data = []
    for i, it in enumerate(raw_items, 1):
        pname = it.get("pname", "")
        mat   = it.get("mat", "")
        price = it.get("price") or None
        qty   = it.get("qty", 1)
        quote_items_data.append({
            "stt":              i,
            "raw_name":         pname,
            "raw_mat":          mat,
            "qty":              qty,
            "note_in":          "",
            "product_name":     pname,
            "material_display": mat,
            "size":             None,
            "length":           None,
            "unit_price":       price,
            "total":            price * qty if price else None,
            "note":             "",
            "matched":          True,
            "confidence":       "high" if price else "low",
            "ptype":            None,
            "material_key":     None,
            "suggestions":      [],
        })

    uid = uuid.uuid4().hex[:8]
    session["uid"]     = uid
    session["items"]   = quote_items_data
    session["prefill"] = {
        "quote_number":     "",
        "receiver_name":    entry.get("customer", ""),
        "receiver_address": entry.get("address", ""),
        "receiver_tel":     entry.get("tel", ""),
        "vat_rate":         entry.get("vat_rate", 8),
    }
    flash("Đã sao chép báo giá vào form. Điều chỉnh và tải xuống báo giá mới.", "info")
    return redirect(url_for("review"))


@app.route("/history/clear", methods=["POST"])
def history_clear():
    if HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")
    flash("Đã xóa toàn bộ lịch sử.", "info")
    return redirect(url_for("history"))


# ─────────────────────────────────────────────
# SET / BUNDLE PRICING
# ─────────────────────────────────────────────

@app.route("/api/lookup-price", methods=["POST"])
def api_lookup_price():
    """AJAX: tra giá theo tên + chất liệu nhập tay."""
    data = request.get_json(force=True)
    name = str(data.get("name", "")).strip()
    mat  = str(data.get("material", "")).strip()
    if not name:
        return jsonify({"ok": False, "error": "Thiếu tên sản phẩm"})
    r = match_product(name, mat)
    return jsonify({
        "ok":           True,
        "product_name": r.product_name or name,
        "material":     r.material_display or mat,
        "unit_price":   r.unit_price,
        "confidence":   r.confidence,
        "note":         r.note or "",
        "in_stock":     r.in_stock,   # True / False / None
    })


@app.route("/api/set-price", methods=["POST"])
def api_set_price():
    """AJAX: tra giá linh kiện bộ (ECU, đệm vênh, đệm phẳng)."""
    data  = request.get_json(force=True)
    comps = data.get("components", [])
    results = []
    for comp in comps:
        name = str(comp.get("name", "")).strip()
        mat  = str(comp.get("material", "")).strip()
        try:
            qty = max(1, int(comp.get("qty") or 1))
        except (TypeError, ValueError):
            qty = 1
        if not name:
            continue
        r = match_product(name, mat)
        results.append({
            "name":       r.product_name or name,
            "material":   r.material_display or mat,
            "qty":        qty,
            "unit_price": r.unit_price,
            "total":      (r.unit_price * qty) if r.unit_price else None,
            "confidence": r.confidence,
        })
    return jsonify({"ok": True, "items": results})


# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("=" * 50)
    print("  PHAN MEM BAO GIA NAM AN")
    print("  Truy cap: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
