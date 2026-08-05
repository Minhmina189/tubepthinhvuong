# -*- coding: utf-8 -*-
"""
Phân tích và khớp tên sản phẩm khách hàng → sản phẩm Nam An
"""
import re
import unicodedata
from typing import Optional

from in_stock_db import is_in_stock

from price_database import (
    BULONG_304_DIN933, BULONG_201, BULONG_316_DIN933, BULONG_88_DEN, BULONG_109_DEN,
    BULONG_109_DEN_REN_LUNG,
    LGC_304_DIN912, LGC_201_DIN912, LGC_316_DIN912,
    LGC_CHOM_CAU_304_DIN7380, LGC_CHOM_CAU_109_DIN7380,
    LGC_DAU_BANG_304_DIN7991, LGC_BANG_88_DIN7991, LGC_BANG_109_DIN7991,
    LGC_TRU_DIN912_129,
    VIT_TRI_304, VIT_TRI_201, VIT_TRI_DEN_DIN916,
    ECU_304,
    ECU_88_DEN, LDP_THEP, LDV_THEP,
    ECU_FLANGE_304, ECU_MU_304, ECU_KHOA_201, ECU_MU_201, ECU_FLANGE_201,
    ECU_KHOA_316, ECU_MU_316,
    ECU_109_DEN, ECU_129_DEN, ECU_MU_MA, ECU_KHOA_MA,
    TAN_RUT_304, TAN_RUT_THEP, LONG_DEN_XUOC_THEP, LONG_DEN_XUOC_304,
    THANH_REN_304, THANH_REN_201, THANH_REN_316, THANH_REN_88_DEN, THANH_REN_109_DEN,
    MOC_CAU_DUONG_304, MOC_CAU_88_MA,
    BULONG_88_MA_KEM, BULONG_109_MA_KEM,
    ECU_88_MA_KEM, ECU_109_MA_KEM, ECU_129_MA_KEM,
    LDP_MA_KEM, LDV_MA_KEM,
    BULONG_NO_304, NOR_DAN_304, BULONG_TAI_HONG_304, ECU_TAI_HONG_304,
    VIT_BAN_TON_304,
    UBOLT_MA_KEM, UBOLT_MA_KEM_NHUNG_NHUA, UBOLT_BOC_NHUA,
)

# ─────────────────────────────────────────────
# BẢNG PHÂN LOẠI SẢN PHẨM
# ─────────────────────────────────────────────

PRODUCT_TYPES = {
    # --- UBOLT (U-BOLT / KẸP ỐNG CHỮ U) ---
    "ubolt": {
        "keywords": [
            "ubolt","u-bolt","u bolt","u lông","ulông","kẹp ống","kep ong",
            "u clamp","kẹp u","kep u",
        ],
        "exclude": ["bu lông", "bulong", "bulông", "bu long", "lục giác"],
    },
    # --- BU LÔNG / BOLT ---
    "bulong": {
        "keywords": [
            "bu lông","bulong","bulông","bu long","bolt","bldc","blcc","blcv","blld",
            "lục giác ngoài","hex bolt","hex head","đầu lục giác ngoài","đầu 6 cạnh ngoài",
        ],
        "exclude": ["chìm","lgc","lục giác chìm","socket","din912","din7380","din7991","nở","ubolt"],
    },
    # --- LỤC GIÁC CHÌM TRỤ (socket head cap screw) ---
    "lgc_tru": {
        "keywords": [
            "lục giác chìm","lgc","socket head","din 912","din912","lục giác trụ",
            "chìm trụ","socket cap","luc giac chim",
        ],
        "exclude": ["chỏm cầu","đầu bằng","bằng","button","flat","countersunk","din7380","din7991"],
    },
    # --- LỤC GIÁC CHÌM CHỎM CẦU (button head) ---
    "lgc_chom_cau": {
        "keywords": [
            "chỏm cầu","button head","din 7380","din7380","lgc chỏm","dome head","round head socket",
        ],
    },
    # --- LỤC GIÁC CHÌM ĐẦU BẰNG (flat/countersunk) ---
    "lgc_dau_bang": {
        "keywords": [
            "đầu bằng","countersunk","flat head","din 7991","din7991","lgc bằng","chìm bằng",
        ],
    },
    # --- VÍT TRÍ (set screw / grub screw) ---
    "vit_tri": {
        "keywords": [
            "vít trí","vit tri","set screw","grub screw","vít không đầu","không đầu","din913","din916",
        ],
    },
    # --- VÍT BẮN TÔN (self-tapping/drilling) ---
    "vit_ban_ton": {
        "keywords": [
            "bắn tôn","vít tôn","tôn","self-tapping","self-drilling","vtkd","vtkdt","vtkb","vtkcc",
        ],
    },
    # --- ECU / ĐAI ỐC (hex nut) ---
    "ecu": {
        "keywords": [
            "ecu","đai ốc","nut","đai oc","ê cu","êcu",
        ],
        "exclude": ["mũ","liền long","khóa","flange","nyloc"],
    },
    # --- ECU MŨ (dome/acorn nut) ---
    "ecu_mu": {
        "keywords": ["ecu mũ","đai ốc mũ","acorn nut","cap nut","dome nut","din1587"],
    },
    # --- ECU KHÓA / NYLOC (lock nut) ---
    "ecu_khoa": {
        "keywords": ["ecu khóa","lock nut","nyloc","din985","khóa ren","đai ốc khóa"],
    },
    # --- ECU LIỀN LONG ĐEN / FLANGE NUT ---
    "ecu_flange": {
        "keywords": ["liền long đen","flange nut","din6923","ecu flange","đai ốc liền"],
    },
    # --- ECU TAI HỒNG / WING NUT ---
    "ecu_tai_hong": {
        "keywords": ["ecu tai hồng","ecu tai hong","đai ốc tai hồng","tai hồng ecu","wing nut","butterfly nut"],
    },
    # --- LONG ĐEN PHẲNG / FLAT WASHER ---
    "ldp": {
        "keywords": [
            "long đen phẳng","đệm phẳng","long phẳng","flat washer","washer flat",
            "ldp","lđp","l.đ.p","đệm dẹt","vòng đệm phẳng",
            # ASCII fallback
            "dem phang","long den phang","long phang","dem det",
        ],
    },
    # --- LONG ĐEN VÊNH / SPRING WASHER ---
    "ldv": {
        "keywords": [
            "long đen vênh","đệm vênh","long vênh","spring washer","đệm lò xo",
            "ldv","lđv","l.đ.v","vòng đệm vênh",
            # ASCII fallback
            "dem venh","long den venh","long venh",
        ],
    },
    # --- LONG ĐEN XƯỚC / TOOTHED LOCK WASHER ---
    "long_xuc": {
        "keywords": ["long đen xước","long xước","toothed washer","đệm xước","lock washer xước"],
    },
    # --- THANH REN (threaded rod) ---
    "thanh_ren": {
        "keywords": ["thanh ren","ren suốt","threaded rod","all thread","din975","ty ren","bar ren"],
    },
    # --- NỞ ĐẠN (bullet anchor sleeve) ---
    "nor_dan": {
        "keywords": ["nở đạn","no dan","đầu đạn","dau dan","nor dan"],
    },
    # --- BULONG TAI HỒNG (flange bolt with ear) ---
    "bulong_tai_hong": {
        "keywords": ["tai hồng","tai hong","bulong tai","flange bolt din316","din316"],
        "exclude": ["ecu tai","đai ốc tai"],
    },
    # --- BULONG NỞ (anchor bolt) ---
    "bulong_no": {
        "keywords": ["nở","anchor bolt","bulong nở","bolt anchor","fisher"],
        "exclude": ["3 cánh","nở đạn","no dan","đầu đạn"],
    },
    # --- TÁN RÚT (pop rivet / blind rivet) ---
    "tan_rut": {
        "keywords": ["tán rút","tan rut","pop rivet","blind rivet","đinh rút","dinh rut","rivet"],
        "exclude": ["lục giác"],
    },
    # --- MÓC CẨU (lifting eye bolt) ---
    "moc_cau": {
        "keywords": ["móc cẩu","moc cau","lifting eye","eye bolt","tai cẩu"],
    },
}

# ─────────────────────────────────────────────
# PHÂN TÍCH CHẤT LIỆU
# ─────────────────────────────────────────────

MATERIAL_PATTERNS = {
    "inox316": [
        r"316", r"inox\s*316", r"ss\s*316", r"sus\s*316", r"stainless\s*316", r"316l",
    ],
    "inox201": [
        r"201", r"inox\s*201", r"sus\s*201", r"ss\s*201",
    ],
    "inox304": [
        r"304", r"inox\s*304", r"ss\s*304", r"sus\s*304", r"stainless", r"inox", r"ss304", r"không gỉ",
    ],
    "thep_129": [
        r"12\.9", r"cap\s*12\.9", r"cb\s*12\.9", r"class\s*12", r"cấp\s*12",
    ],
    "thep_109": [
        r"10\.9", r"cap\s*10\.9", r"cb\s*10\.9", r"class\s*10", r"cấp\s*10", r"10\.9\s*đen",
    ],
    "thep_109_ma": [
        r"10\.9\s*mạ", r"mạ\s*10\.9", r"thép\s*mạ\s*kẽm\s*10", r"ma\s*kem\s*10\.9",
        r"thep\s*ma\s*kem\s*10", r"thep ma kem 10",
    ],
    "thep_129_ma": [
        r"12\.9\s*mạ", r"mạ\s*12\.9", r"thép\s*mạ\s*kẽm\s*12", r"ma\s*kem\s*12\.9",
    ],
    "thep_88_ma": [
        r"8\.8\s*mạ", r"mạ\s*8\.8", r"mạ\s*kẽm", r"mạ\s*k[eê]m", r"galvanized",
        r"ma\s*kẽm", r"ma\s*kem", r"thép\s*mạ", r"cb\s*8[,.]?8\s*mạ", r"thep\s*ma",
        r"\bkẽm\b", r"\bmạ\b",
        r"mã\s*kẽm", r"mã\s*kem",
    ],
    "thep_88": [
        r"8\.8", r"cap\s*8\.8", r"cb\s*8\.8", r"class\s*8", r"cấp\s*8",
        r"thép\s*đen", r"thep\s*den", r"\bđen\b", r"\bblack\b", r"\bthep\b", r"\bthép\b",
    ],
}

MATERIAL_DISPLAY = {
    "inox304": "Inox 304",
    "inox201": "Inox 201",
    "inox316": "Inox 316",
    "thep_88":     "Thép 8.8 đen",
    "thep_88_ma":  "Thép 8.8 mạ kẽm",
    "thep_109":    "Thép 10.9 đen",
    "thep_109_ma": "Thép 10.9 mạ kẽm",
    "thep_129":    "Thép 12.9 đen",
    "thep_129_ma": "Thép 12.9 mạ kẽm",
    "ubolt_ma_kem":     "Thép mạ kẽm",
    "ubolt_nhung_nhua": "Thép mạ kẽm nhúng nhựa",
    "ubolt_boc_nhua":   "Thép mạ kẽm bọc nhựa",
}

# Valid bolt thread sizes (M-series standard)
_BOLT_SIZES = {
    "1","1.4","1.6","2","2.5","3","3.5","4","5","6","7","8","10","12","14","16",
    "18","20","22","24","27","30","33","36","39","42","48","52","56","64","72","80","100",
}
# Numbers that are material grades, not sizes or lengths
_MATERIAL_NUMS = {"201","304","316","88","109","129","8.8","10.9","12.9"}

# ─────────────────────────────────────────────
# HÀM PHÂN TÍCH
# ─────────────────────────────────────────────

def normalize(text: str) -> str:
    """Chuẩn hóa text: NFC, chữ thường, dấu phẩy thập phân → chấm."""
    text = unicodedata.normalize('NFC', text)
    text = text.lower().strip()
    text = re.sub(r'(\d),(\d)', r'\1.\2', text)   # "10,9" → "10.9"
    text = re.sub(r"[_\-–]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def extract_size(text: str) -> Optional[str]:
    """Trích xuất kích thước ren: M4, M8, M10 ...
    Chỉ lấy size hợp lệ (trong bảng chuẩn), bỏ qua số chất liệu 201/304/316.
    """
    for m in re.finditer(r"\bm\s*(\d+\.?\d*)", text, re.IGNORECASE):
        num = m.group(1).rstrip(".")
        if num in _BOLT_SIZES:
            return f"M{num}"
    return None


def extract_length(text: str) -> Optional[int]:
    """Trích xuất chiều dài mm.
    Ví dụ: M8x30, M10×55, M8 30mm → 30.
    Không lấy số chất liệu (201, 304, 316).
    """
    # Dạng MXxL – đáng tin nhất
    m = re.search(r"m\s*\d+\.?\d*\s*[x×*]\s*(\d+)", text, re.IGNORECASE)
    if m:
        val = int(m.group(1))
        if str(val) not in _MATERIAL_NUMS and val <= 500:
            return val
    # Dạng "Lmm"
    m = re.search(r"(\d+)\s*mm\b", text, re.IGNORECASE)
    if m:
        val = int(m.group(1))
        if str(val) not in _MATERIAL_NUMS and val <= 500:
            return val
    # Dạng "x L" độc lập (không đứng sau M...)
    for m in re.finditer(r"[x×]\s*(\d+)\b", text, re.IGNORECASE):
        # Bỏ qua nếu đứng ngay sau M+số (đã xử lý ở trên)
        start = m.start()
        before = text[max(0, start-6):start]
        if re.search(r"m\s*\d", before, re.IGNORECASE):
            continue
        val = int(m.group(1))
        if str(val) not in _MATERIAL_NUMS and val <= 500:
            return val
    return None


def extract_dn_size(text: str) -> Optional[str]:
    """Trích xuất kích thước ống dưới dạng key tra bảng.
    'DN65' → 'DN65', 'Ø125' → 'Ø125'.
    Trả về full key string để tra đúng bảng (Ø125 ≠ DN125).
    """
    m = re.search(r'\bdn\s*(\d+)', text, re.IGNORECASE)
    if m:
        return f"DN{m.group(1)}"
    m = re.search(r'[øφΦ]\s*(\d+)', text)
    if m:
        return f"Ø{m.group(1)}"
    return None


def detect_material(text: str) -> str:
    """Phát hiện chất liệu từ text, trả về key nội bộ."""
    t = normalize(text)
    # Mạ kẽm + cấp độ bền phải check TRƯỚC khi check grade riêng lẻ
    _MA = r'mạ\s*kẽm|mạ\s*k[eê]m|\bkẽm\b|\bkem\b|zinc|galvanized'
    if re.search(_MA, t, re.IGNORECASE):
        if re.search(r'12[.,]9', t): return 'thep_129_ma'
        if re.search(r'10[.,]9', t): return 'thep_109_ma'
        return 'thep_88_ma'
    # Ưu tiên theo thứ tự từ cụ thể → chung
    for mat_key, patterns in MATERIAL_PATTERNS.items():
        if mat_key in ('thep_88_ma', 'thep_109_ma', 'thep_129_ma'):
            continue  # đã xử lý ở trên
        for pat in patterns:
            if re.search(pat, t, re.IGNORECASE):
                return mat_key
    # Mặc định: thép 8.8 đen nếu không rõ
    return "thep_88"


def detect_product_type(text: str) -> Optional[str]:
    """Phát hiện loại sản phẩm từ text."""
    t = normalize(text)
    for ptype, conf in PRODUCT_TYPES.items():
        keywords = conf.get("keywords", [])
        excludes = conf.get("exclude", [])
        matched = any(k in t for k in keywords)
        excluded = any(e in t for e in excludes)
        if matched and not excluded:
            return ptype
    return None


# ─────────────────────────────────────────────
# TRA GIÁ
# ─────────────────────────────────────────────

def _pick_from_dict(d: dict, key):
    """Tra bảng giá đơn giản (key → price)."""
    if d is None:
        return None
    return d.get(key)


def lookup_price(ptype: str, material: str, size: str, length: Optional[int] = None):
    """
    Tra giá theo loại, chất liệu, size, chiều dài.
    Trả về (đơn_giá, tên_hiển_thị_sản_phẩm, chất_liệu_hiển_thị, ghi_chú)
    """
    price = None
    product_name = ""
    mat_display = MATERIAL_DISPLAY.get(material, material)
    note = ""

    # Mạ kẽm: các ptype hỗ trợ mạ kẽm
    _MA_KEM_SUPPORTED = {"bulong", "ubolt", "ecu", "ldp", "ldv"}
    if material in ("thep_88_ma", "thep_109_ma", "thep_129_ma"):
        if ptype not in _MA_KEM_SUPPORTED:
            # Không có hàng mạ → fallback về thép đen cùng cấp
            _fallback = {"thep_88_ma": "thep_88", "thep_109_ma": "thep_109", "thep_129_ma": "thep_129"}
            material = _fallback[material]
            mat_display = MATERIAL_DISPLAY.get(material, material)
            note = "Thép đen (không có hàng mạ kẽm)"

    # ── LỤC GIÁC CHÌM TRỤ ──────────────────────────
    if ptype == "lgc_tru":
        if material == "inox304":
            product_name = "Lục giác chìm SUS 304 DIN912"
            price = _bolt_lookup(LGC_304_DIN912, size, length)
        elif material == "inox201":
            product_name = "Lục giác chìm SUS 201 DIN912"
            price = _bolt_lookup(LGC_201_DIN912, size, length)
        elif material == "inox316":
            product_name = "Lục giác chìm SUS 316 DIN912"
            price = _bolt_lookup(LGC_316_DIN912, size, length)
        elif material == "thep_129":
            product_name = "LGC trụ DIN912 CB 12.9 đen"
            price = _bolt_lookup(LGC_TRU_DIN912_129, size, length)
        elif material in ("thep_88", "thep_88_ma", "thep_109"):
            # Thép 8.8 thường không có LGC trụ riêng → dùng 12.9 hoặc báo không có
            product_name = "LGC trụ DIN912 CB 12.9 đen"
            price = _bolt_lookup(LGC_TRU_DIN912_129, size, length)
            mat_display = "Thép 12.9 đen"

    # ── BU LÔNG ─────────────────────────────────────
    elif ptype == "bulong":
        if material == "inox304":
            product_name = "Bu lông Inox 304 DIN933"
            price = _bolt_lookup(BULONG_304_DIN933, size, length)
        elif material == "inox201":
            product_name = "Bu lông Inox 201"
            price = _bolt_lookup(BULONG_201, size, length)
        elif material == "inox316":
            product_name = "Bu lông Inox 316 DIN933"
            price = _bolt_lookup(BULONG_316_DIN933, size, length)
        elif material == "thep_88":
            product_name = "Bu lông 8.8 đen"
            price = _bolt_lookup(BULONG_88_DEN, size, length)
        elif material == "thep_88_ma":
            product_name = "Bu lông 8.8 mạ kẽm"
            price = _bolt_lookup(BULONG_88_MA_KEM, size, length)
        elif material == "thep_109":
            price = _bolt_lookup(BULONG_109_DEN, size, length)
            rl_data = BULONG_109_DEN_REN_LUNG.get(size, {}) if size else {}
            if length and length in rl_data:
                product_name = "Bu lông 10.9 đen ren lửng"
            else:
                product_name = "Bu lông 10.9 đen"
        elif material == "thep_109_ma":
            product_name = "Bu lông 10.9 mạ kẽm"
            price = _bolt_lookup(BULONG_109_MA_KEM, size, length)
        elif material == "thep_129":
            product_name = "Bu lông 8.8 đen"
            price = _bolt_lookup(BULONG_88_DEN, size, length)
            note = "Dùng hàng 8.8 đen"

    # ── LỤC GIÁC CHÌM CHỎM CẦU ─────────────────────
    elif ptype == "lgc_chom_cau":
        if material == "inox304":
            product_name = "LGC chỏm cầu SUS 304 DIN7380"
            price = _bolt_lookup(LGC_CHOM_CAU_304_DIN7380, size, length)
        elif material in ("thep_109", "thep_88"):
            product_name = "LGC chỏm cầu 10.9 DIN7380"
            price = _bolt_lookup(LGC_CHOM_CAU_109_DIN7380, size, length)
            mat_display = "Thép 10.9 đen"
        else:
            product_name = "LGC chỏm cầu SUS 304 DIN7380"
            price = _bolt_lookup(LGC_CHOM_CAU_304_DIN7380, size, length)

    # ── LỤC GIÁC CHÌM ĐẦU BẰNG ────────────────────
    elif ptype == "lgc_dau_bang":
        if material == "inox304":
            product_name = "LGC đầu bằng SUS 304 DIN7991"
            price = _bolt_lookup(LGC_DAU_BANG_304_DIN7991, size, length)
        elif material in ("thep_88", "thep_88_ma"):
            product_name = "LGC bằng 8.8 DIN7991"
            key = f"{size}x{length}" if length else None
            price = LGC_BANG_88_DIN7991.get(key) if key else None
            mat_display = "Thép 8.8 đen"
        elif material == "thep_109":
            product_name = "LGC bằng 10.9 DIN7991"
            price = _bolt_lookup(LGC_BANG_109_DIN7991, size, length)
        else:
            product_name = "LGC đầu bằng SUS 304 DIN7991"
            price = _bolt_lookup(LGC_DAU_BANG_304_DIN7991, size, length)

    # ── VÍT TRÍ ────────────────────────────────────
    elif ptype == "vit_tri":
        if material == "inox304":
            product_name = "Vít trí SUS 304 DIN913"
            price = _bolt_lookup(VIT_TRI_304, size, length)
        elif material == "inox201":
            product_name = "Vít trí SUS 201 DIN913"
            price = _bolt_lookup(VIT_TRI_201, size, length)
        else:
            product_name = "Vít trí DIN916 đen"
            price = _bolt_lookup(VIT_TRI_DEN_DIN916, size, length)
            mat_display = "Thép đen"

    # ── VÍT BẮN TÔN ────────────────────────────────
    elif ptype == "vit_ban_ton":
        product_name = "Vít bắn tôn SUS 304"
        mat_display = "Inox 304"
        key = f"{size}x{length}" if length else None
        price = VIT_BAN_TON_304.get(key) if key else None
        if material not in ("inox304", "inox201", "inox316"):
            note = "Chỉ có hàng Inox 304"

    # ── ECU HEX NUT ────────────────────────────────
    elif ptype == "ecu":
        if material == "inox304":
            product_name = "ECU Inox 304"
            price = ECU_304.get(size)
        elif material == "inox201":
            product_name = "ECU Inox 201"
            price = BULONG_201.get(size, {}).get("ECU")
        elif material == "inox316":
            product_name = "ECU Inox 316"
            price = BULONG_316_DIN933.get(size, {}).get("ECU")
        elif material == "thep_88":
            product_name = "ECU 8.8 đen"
            price = ECU_88_DEN.get(size)
        elif material == "thep_88_ma":
            product_name = "ECU 8.8 mạ kẽm"
            price = ECU_88_MA_KEM.get(size)
        elif material == "thep_109":
            product_name = "ECU 10.9 đen"
            price = ECU_109_DEN.get(size)
        elif material == "thep_109_ma":
            product_name = "ECU 10.9 mạ kẽm"
            price = ECU_109_MA_KEM.get(size)
        elif material == "thep_129":
            product_name = "ECU 12.9 đen"
            price = ECU_129_DEN.get(size)
        elif material == "thep_129_ma":
            product_name = "ECU 12.9 mạ kẽm"
            price = ECU_129_MA_KEM.get(size)
        else:
            product_name = "ECU 8.8 đen"
            price = ECU_88_DEN.get(size)
            mat_display = "Thép 8.8 đen"

    # ── ECU MŨ ─────────────────────────────────────
    elif ptype == "ecu_mu":
        if material == "inox304":
            product_name = "ECU mũ DIN1587 SUS304"
            price = ECU_MU_304.get(size)
        elif material == "inox201":
            product_name = "ECU mũ DIN1587 Inox 201"
            price = ECU_MU_201.get(size)
        elif material == "inox316":
            product_name = "ECU mũ Inox 316"
            price = ECU_MU_316.get(size)
        else:
            product_name = "ECU mũ mạ"
            price = ECU_MU_MA.get(size)
            mat_display = "Thép mạ"

    # ── ECU KHÓA ───────────────────────────────────
    elif ptype == "ecu_khoa":
        if material == "inox201":
            product_name = "ECU khóa Inox 201 DIN985"
            price = ECU_KHOA_201.get(size)
        elif material == "inox316":
            product_name = "ECU khóa Inox 316 DIN985"
            price = ECU_KHOA_316.get(size)
        else:
            product_name = "ECU khóa mạ"
            price = ECU_KHOA_MA.get(size)
            mat_display = "Thép mạ"

    # ── ECU FLANGE ─────────────────────────────────
    elif ptype == "ecu_flange":
        if material == "inox304":
            product_name = "ECU liền long đen DIN6923 SUS304"
            price = ECU_FLANGE_304.get(size)
        elif material == "inox201":
            product_name = "ECU liền long đen DIN6923 Inox 201"
            price = ECU_FLANGE_201.get(size)
        else:
            product_name = "ECU liền long đen DIN6923 SUS304"
            price = ECU_FLANGE_304.get(size)
            mat_display = "Inox 304"

    # ── LONG ĐEN PHẲNG ─────────────────────────────
    elif ptype == "ldp":
        if material in ("inox304", "inox316", "inox201"):
            product_name = "Long đen phẳng " + mat_display
            tbl = BULONG_304_DIN933 if material == "inox304" else (
                  BULONG_316_DIN933 if material == "inox316" else BULONG_201)
            price = tbl.get(size, {}).get("LDP")
        elif material in ("thep_88_ma", "thep_109_ma", "thep_129_ma"):
            product_name = "Long đen phẳng mạ kẽm"
            price = LDP_MA_KEM.get(size)
        else:
            product_name = "Long đen phẳng thép đen"
            price = LDP_THEP.get(size)
            mat_display = "Thép đen"

    # ── LONG ĐEN VÊNH ──────────────────────────────
    elif ptype == "ldv":
        if material in ("inox304", "inox316", "inox201"):
            product_name = "Long đen vênh " + mat_display
            tbl = BULONG_304_DIN933 if material == "inox304" else (
                  BULONG_316_DIN933 if material == "inox316" else BULONG_201)
            price = tbl.get(size, {}).get("LDV")
        elif material in ("thep_88_ma", "thep_109_ma", "thep_129_ma"):
            product_name = "Long đen vênh mạ kẽm"
            price = LDV_MA_KEM.get(size)
        else:
            product_name = "Long đen vênh thép đen"
            price = LDV_THEP.get(size)
            mat_display = "Thép đen"

    # ── LONG ĐEN XƯỚC ──────────────────────────────
    elif ptype == "long_xuc":
        if material in ("inox304",):
            product_name = "Long đen xước Inox 304"
            price = LONG_DEN_XUOC_304.get(size)
        else:
            product_name = "Long đen xước thép"
            price = LONG_DEN_XUOC_THEP.get(size)
            mat_display = "Thép đen"

    # ── THANH REN ──────────────────────────────────
    elif ptype == "thanh_ren":
        key = f"{size}x1m"
        if material == "inox304":
            product_name = "Thanh ren SUS 304 DIN975"
            price = THANH_REN_304.get(key)
        elif material == "inox201":
            product_name = "Thanh ren Inox 201"
            price = THANH_REN_201.get(key)
        elif material == "inox316":
            product_name = "Thanh ren SS316 DIN975"
            price = THANH_REN_316.get(key)
        elif material in ("thep_109", "thep_88_ma"):
            product_name = "Thanh ren 10.9 đen"
            price = THANH_REN_109_DEN.get(key)
            mat_display = "Thép 10.9 đen"
        else:
            product_name = "Thanh ren 8.8 đen DIN975"
            price = THANH_REN_88_DEN.get(key)
            mat_display = "Thép 8.8 đen"

    # ── NỞ ĐẠN ─────────────────────────────────────
    elif ptype == "nor_dan":
        product_name = "Nở đạn SUS 304"
        price = NOR_DAN_304.get(size)
        mat_display = "Inox 304"

    # ── BULONG TAI HỒNG ─────────────────────────────
    elif ptype == "bulong_tai_hong":
        product_name = "Bulong tai hồng SUS 304 DIN316"
        price = _bolt_lookup(BULONG_TAI_HONG_304, size, length)
        mat_display = "Inox 304"

    # ── ECU TAI HỒNG ────────────────────────────────
    elif ptype == "ecu_tai_hong":
        product_name = "ECU tai hồng SUS 304"
        price = ECU_TAI_HONG_304.get(size)
        mat_display = "Inox 304"

    # ── BULONG NỞ ──────────────────────────────────
    elif ptype == "bulong_no":
        product_name = "Bulong nở Inox 304"
        key = f"{size}x{length}" if length else None
        price = BULONG_NO_304.get(key) if key else None
        mat_display = "Inox 304"

    # ── TÁN RÚT ────────────────────────────────────
    elif ptype == "tan_rut":
        if material == "inox304":
            product_name = "Tán rút Inox 304"
            price = TAN_RUT_304.get(size)
        else:
            product_name = "Tán rút thép"
            price = TAN_RUT_THEP.get(size)
            mat_display = "Thép đen"

    # ── MÓC CẨU ────────────────────────────────────
    elif ptype == "moc_cau":
        if material == "inox304":
            product_name = "Móc cẩu dương Inox 304"
            price = MOC_CAU_DUONG_304.get(size)
        else:
            product_name = "Móc cẩu 8.8 mạ"
            price = MOC_CAU_88_MA.get(size)
            mat_display = "Thép 8.8 mạ"

    # ── UBOLT ──────────────────────────────────────
    elif ptype == "ubolt":
        dn_key = f"DN{length}" if length else None
        dn_alt = f"Ø{length}"  if length else None
        if material == "ubolt_boc_nhua":
            table = UBOLT_BOC_NHUA
            mat_display = "Thép mạ kẽm bọc nhựa"
        elif material == "ubolt_nhung_nhua":
            table = UBOLT_MA_KEM_NHUNG_NHUA
            mat_display = "Thép mạ kẽm nhúng nhựa"
        else:
            table = UBOLT_MA_KEM
            mat_display = "Thép mạ kẽm"
        product_name = "Ubolt"
        subtable = table.get(size) if size else None
        if subtable and dn_key:
            price = subtable.get(dn_key) or subtable.get(dn_alt)

    if price is not None:
        price = round(price)

    # Replace product name with clean descriptive name — no material (material in separate column)
    _BASE_NAMES = {
        "bulong":       "Bu lông lục giác ngoài",
        "lgc_tru":      "Lục giác chìm trụ",
        "lgc_chom_cau": "Lục giác chìm chỏm cầu",
        "lgc_dau_bang": "Lục giác chìm đầu bằng",
        "vit_tri":      "Vít trí",
        "vit_ban_ton":  "Vít bắn tôn",
        "ecu":          "ECU",
        "ecu_mu":       "ECU mũ",
        "ecu_khoa":     "ECU khóa",
        "ecu_flange":   "ECU liền long đen",
        "ldp":          "Long đen phẳng",
        "ldv":          "Long đen vênh",
        "long_xuc":     "Long đen xước",
        "thanh_ren":    "Thanh ren",
        "nor_dan":         "Nở đạn",
        "bulong_tai_hong": "Bulong tai hồng",
        "ecu_tai_hong":    "ECU tai hồng",
        "bulong_no":    "Bulong nở",
        "tan_rut":      "Tán rút",
        "moc_cau":      "Móc cẩu dương",
        "ubolt":        "Ubolt",
    }
    if ptype in _BASE_NAMES and product_name:
        product_name = _BASE_NAMES[ptype]

    # Append size (and length/DN for bolt-type items) to product name
    _PTYPE_WITH_LEN = {"bulong", "lgc_tru", "lgc_chom_cau", "lgc_dau_bang",
                       "vit_tri", "vit_ban_ton", "bulong_no", "bulong_tai_hong"}
    if product_name and size:
        if ptype == "thanh_ren":
            product_name = f"{product_name} {size}x1m"
        elif ptype == "ubolt" and length:
            product_name = f"{product_name} {size}-DN{length}"
        elif ptype in _PTYPE_WITH_LEN and length:
            product_name = f"{product_name} {size}x{length}"
        else:
            product_name = f"{product_name} {size}"

    return price, product_name, mat_display, note


def _bolt_lookup(table: dict, size: str, length: Optional[int]) -> Optional[float]:
    """Tra giá bulong/vít từ bảng 2D."""
    row = table.get(size)
    if row is None:
        return None
    if not isinstance(row, dict):
        return None
    if length is not None:
        return row.get(length)
    # Nếu không có length, trả None
    return None


# ─────────────────────────────────────────────
# HÀM CHÍNH
# ─────────────────────────────────────────────

PRODUCT_TYPE_NAMES = {
    "ubolt":        "Ubolt (kẹp ống chữ U)",
    "bulong":       "Bu lông lục giác ngoài",
    "lgc_tru":      "Lục giác chìm trụ DIN912",
    "lgc_chom_cau": "Lục giác chìm chỏm cầu DIN7380",
    "lgc_dau_bang": "Lục giác chìm đầu bằng DIN7991",
    "vit_tri":      "Vít trí DIN916",
    "vit_ban_ton":  "Vít bắn tôn",
    "ecu":          "Đai ốc (ECU)",
    "ecu_mu":       "ECU mũ DIN1587",
    "ecu_khoa":     "ECU khóa nylon DIN985",
    "ecu_flange":   "ECU liền long đen DIN6923",
    "ldp":          "Long đen phẳng",
    "ldv":          "Long đen vênh",
    "long_xuc":     "Long đen xước",
    "thanh_ren":    "Thanh ren DIN975",
    "nor_dan":         "Nở đạn Inox 304",
    "bulong_tai_hong": "Bulong tai hồng Inox 304 DIN316",
    "ecu_tai_hong":    "ECU tai hồng SUS 304",
    "bulong_no":    "Bulong nở",
    "tan_rut":      "Tán rút",
    "moc_cau":      "Móc cẩu",
}

# Map (ptype, material_key) → price table for size/length lookup
_PTYPE_MAT_TABLE = {
    ("bulong",       "inox304"):    "BULONG_304_DIN933",
    ("bulong",       "inox201"):    "BULONG_201",
    ("bulong",       "inox316"):    "BULONG_316_DIN933",
    ("bulong",       "thep_88"):    "BULONG_88_DEN",
    ("bulong",       "thep_88_ma"): "BULONG_88_DEN",
    ("bulong",       "thep_109"):   "BULONG_109_DEN",
    ("bulong",       "thep_129"):   "BULONG_88_DEN",
    ("lgc_tru",      "inox304"):    "LGC_304_DIN912",
    ("lgc_tru",      "inox201"):    "LGC_201_DIN912",
    ("lgc_tru",      "inox316"):    "LGC_316_DIN912",
    ("lgc_tru",      "thep_129"):   "LGC_TRU_DIN912_129",
    ("lgc_tru",      "thep_88"):    "LGC_TRU_DIN912_129",
    ("lgc_tru",      "thep_109"):   "LGC_TRU_DIN912_129",
    ("lgc_chom_cau", "inox304"):    "LGC_CHOM_CAU_304_DIN7380",
    ("lgc_chom_cau", "thep_109"):   "LGC_CHOM_CAU_109_DIN7380",
    ("lgc_chom_cau", "thep_88"):    "LGC_CHOM_CAU_109_DIN7380",
    ("lgc_dau_bang",    "inox304"):  "LGC_DAU_BANG_304_DIN7991",
    ("lgc_dau_bang",    "thep_109"): "LGC_BANG_109_DIN7991",
    ("lgc_dau_bang",    "thep_88"):  "LGC_BANG_88_DIN7991",
    ("bulong_tai_hong", "inox304"):  "BULONG_TAI_HONG_304",
    ("ecu_tai_hong",    "inox304"):  "ECU_TAI_HONG_304",
    ("vit_tri",      "inox304"):    "VIT_TRI_304",
    ("vit_tri",      "inox201"):    "VIT_TRI_201",
    ("vit_tri",      "thep_88"):    "VIT_TRI_DEN_DIN916",
    ("ecu",          "inox304"):    "ECU_304",
    ("ecu",          "inox201"):    "BULONG_201",
    ("ecu",          "inox316"):    "BULONG_316_DIN933",
    ("ecu",          "thep_88"):    "ECU_88_DEN",
    ("ecu",          "thep_88_ma"): "ECU_88_DEN",
    ("ecu",          "thep_109"):   "ECU_109_DEN",
    ("ecu",          "thep_129"):   "ECU_129_DEN",
    ("ecu_mu",       "inox304"):    "ECU_MU_304",
    ("ecu_mu",       "inox201"):    "ECU_MU_201",
    ("ecu_mu",       "inox316"):    "ECU_MU_316",
    ("ecu_mu",       "thep_88"):    "ECU_MU_MA",
    ("ecu_mu",       "thep_88_ma"): "ECU_MU_MA",
    ("ecu_khoa",     "inox201"):    "ECU_KHOA_201",
    ("ecu_khoa",     "inox316"):    "ECU_KHOA_316",
    ("ecu_khoa",     "thep_88"):    "ECU_KHOA_MA",
    ("ecu_khoa",     "thep_88_ma"): "ECU_KHOA_MA",
    ("ecu_flange",   "inox304"):    "ECU_FLANGE_304",
    ("ecu_flange",   "inox201"):    "ECU_FLANGE_201",
    ("ldp",          "inox304"):    "BULONG_304_DIN933",
    ("ldp",          "inox316"):    "BULONG_316_DIN933",
    ("ldp",          "inox201"):    "BULONG_201",
    ("ldp",          "thep_88"):    "LDP_THEP",
    ("ldv",          "inox304"):    "BULONG_304_DIN933",
    ("ldv",          "inox316"):    "BULONG_316_DIN933",
    ("ldv",          "inox201"):    "BULONG_201",
    ("ldv",          "thep_88"):    "LDV_THEP",
    ("long_xuc",     "inox304"):    "LONG_DEN_XUOC_304",
    ("long_xuc",     "thep_88"):    "LONG_DEN_XUOC_THEP",
    ("thanh_ren",    "inox304"):    "THANH_REN_304",
    ("thanh_ren",    "inox201"):    "THANH_REN_201",
    ("thanh_ren",    "inox316"):    "THANH_REN_316",
    ("thanh_ren",    "thep_88"):    "THANH_REN_88_DEN",
    ("thanh_ren",    "thep_109"):   "THANH_REN_109_DEN",
    ("tan_rut",      "inox304"):    "TAN_RUT_304",
    ("tan_rut",      "thep_88"):    "TAN_RUT_THEP",
    ("moc_cau",      "inox304"):    "MOC_CAU_DUONG_304",
    ("moc_cau",      "thep_88"):    "MOC_CAU_88_MA",
    ("nor_dan",      "inox304"):    "NOR_DAN_304",
    ("bulong_no",    "inox304"):    "BULONG_NO_304",
    ("ubolt", "ubolt_ma_kem"):      "UBOLT_MA_KEM",
    ("ubolt", "ubolt_nhung_nhua"):  "UBOLT_MA_KEM_NHUNG_NHUA",
    ("ubolt", "ubolt_boc_nhua"):    "UBOLT_BOC_NHUA",
}

def _resolve_table(name: str):
    import price_database as _pd
    return getattr(_pd, name, None)


def get_available_sizes(ptype: str, material_key: str) -> list:
    """Trả về danh sách size có trong bảng giá cho loại + chất liệu đã cho."""
    tname = _PTYPE_MAT_TABLE.get((ptype, material_key))
    if not tname:
        return []
    table = _resolve_table(tname)
    if not table:
        return []
    def _num(s):
        try: return float(s[1:])
        except: return 9999
    return sorted([k for k in table.keys() if isinstance(k, str) and k.upper().startswith("M")], key=_num)


def get_available_lengths(ptype: str, material_key: str, size: str) -> list:
    """Trả về danh sách chiều dài có trong bảng giá cho size đã cho."""
    tname = _PTYPE_MAT_TABLE.get((ptype, material_key))
    if not tname:
        return []
    table = _resolve_table(tname)
    if not table:
        return []
    row = table.get(size)
    if not isinstance(row, dict):
        return []
    return sorted([k for k in row.keys() if isinstance(k, int)])


def get_suggestions(ptype, material_key, size, length, confidence) -> list:
    """Trả về danh sách gợi ý cho sản phẩm không khớp hoàn toàn."""
    if confidence == "high":
        return []

    suggs = []
    ptype_label = PRODUCT_TYPE_NAMES.get(ptype) if ptype else None
    mat_label = MATERIAL_DISPLAY.get(material_key, material_key or "")

    if not ptype:
        suggs.append(
            "Không nhận diện được loại sản phẩm. "
            "Thử các từ khóa: bu lông, lục giác chìm, đệm phẳng, đệm vênh, ecu, thanh ren..."
        )
        return suggs

    if not size:
        suggs.append(
            f"Nhận diện: {ptype_label}{' – ' + mat_label if mat_label else ''}. "
            "Thiếu kích thước ren (VD: M8, M10x30). Chỉnh sửa tên sản phẩm để thêm kích thước."
        )
        return suggs

    sizes = get_available_sizes(ptype, material_key)
    if not sizes:
        suggs.append(
            f"Nhận diện: {ptype_label} {mat_label}. "
            "Tổ hợp loại + chất liệu này chưa có trong bảng giá Nam An. Nhập đơn giá thủ công."
        )
        return suggs

    if size not in sizes:
        suggs.append(
            f"Nhận diện: {ptype_label} {mat_label} – nhưng size {size} không có trong bảng giá. "
            f"Có sẵn: {', '.join(sizes)}"
        )
        return suggs

    # size found but no price
    if length is not None:
        lengths = get_available_lengths(ptype, material_key, size)
        if lengths:
            suggs.append(
                f"Nhận diện: {ptype_label} {mat_label} {size}. "
                f"Không có chiều dài {length}mm. "
                f"Chiều dài có sẵn (mm): {', '.join(str(l) for l in lengths)}"
            )
        else:
            suggs.append(
                f"Nhận diện: {ptype_label} {mat_label} {size}. Không tìm được giá. Nhập thủ công."
            )
    else:
        suggs.append(
            f"Nhận diện: {ptype_label} {mat_label} {size}. "
            "Thiếu chiều dài (VD: x30, x50mm). Nhập đơn giá thủ công hoặc bổ sung chiều dài."
        )
    return suggs


def _parse_set_components(desc: str) -> Optional[dict]:
    """Phát hiện thành phần bộ từ mô tả kỹ thuật.
    Trả về dict hoặc None nếu không phải bộ."""
    t = desc.lower()
    has_flat   = any(k in t for k in ["đệm phẳng","dem phang","long phẳng","long phang"])
    has_spring = any(k in t for k in ["đệm vênh","dem venh","long vênh","long venh"])
    has_nut    = any(k in t for k in ["ê cu","đai ốc","dai oc","ecu","e cu"])
    if not has_flat and not has_spring and not has_nut:
        return None
    flat_n = 1
    m = re.search(r'(\d+)\s*(?:đệm\s*phẳng|dem\s*phang|long\s*phẳng)', t)
    if m:
        flat_n = int(m.group(1))
    elif not has_flat:
        flat_n = 0
    return {
        "flat_washer":   flat_n,
        "spring_washer": 1 if has_spring else 0,
        "nut":           1 if has_nut else 0,
    }


def _calculate_set_price(ptype: str, material: str, size: str, length: Optional[int],
                          components: dict) -> tuple:
    """Tính giá bộ = bulong + đệm + đai ốc.
    Trả về (tổng_giá, tên_bộ, ghi_chú, breakdown_list) hoặc (None, None, None, None)."""
    total = 0
    parts = []
    breakdown = []

    bolt_price, bolt_name, _, _ = lookup_price(ptype, material, size, length)
    if bolt_price is None:
        return None, None, None, None
    total += bolt_price
    bolt_display = bolt_name or f"Bu lông {size}"
    parts.append(f"1× {bolt_display}")
    breakdown.append({"name": bolt_display, "qty": 1, "price": bolt_price})

    flat_n = components.get("flat_washer", 0)
    if flat_n > 0:
        ldp_p, ldp_name, _, _ = lookup_price("ldp", material, size, None)
        if ldp_p:
            total += ldp_p * flat_n
            dname = ldp_name or f"Đệm phẳng {size}"
            parts.append(f"{flat_n}× {dname}")
            breakdown.append({"name": dname, "qty": flat_n, "price": ldp_p})

    spring_n = components.get("spring_washer", 0)
    if spring_n > 0:
        ldv_p, ldv_name, _, _ = lookup_price("ldv", material, size, None)
        if ldv_p:
            total += ldv_p * spring_n
            dname = ldv_name or f"Đệm vênh {size}"
            parts.append(f"{spring_n}× {dname}")
            breakdown.append({"name": dname, "qty": spring_n, "price": ldv_p})

    nut_n = components.get("nut", 0)
    if nut_n > 0:
        nut_p, nut_name, _, _ = lookup_price("ecu", material, size, None)
        if nut_p:
            total += nut_p * nut_n
            dname = nut_name or f"ECU {size}"
            parts.append(f"{nut_n}× {dname}")
            breakdown.append({"name": dname, "qty": nut_n, "price": nut_p})

    if len(breakdown) <= 1:
        # Chỉ có bulong, không có thành phần bộ → không phải bộ
        return None, None, None, None

    set_name = f"Bộ {bolt_name}" if bolt_name else f"Bộ Bu lông {size}"
    return int(total), set_name, " + ".join(parts), breakdown


class MatchResult:
    def __init__(self):
        self.product_name = ""
        self.material_display = ""
        self.size = ""
        self.length = None
        self.unit_price = None
        self.note = ""
        self.matched = False
        # For review page
        self.ptype = None        # loại sản phẩm nhận diện được
        self.material_key = None # chất liệu nhận diện được
        self.confidence = "none" # "high" | "medium" | "low" | "none"
        self.set_detail = None   # list[dict] breakdown cho bộ: [{"name","qty","price"}]
        self.in_stock: Optional[bool] = None  # True=có sẵn, False=theo yêu cầu, None=không rõ

    def __repr__(self):
        return (f"MatchResult({self.product_name} | {self.material_display} | "
                f"{self.size} L={self.length} | giá={self.unit_price} | conf={self.confidence})")


def match_product(raw_name: str, raw_material: str = "", raw_desc: str = "") -> MatchResult:
    """
    Phân tích tên sản phẩm và chất liệu từ khách hàng → tra giá Nam An.
    raw_name:     tên sản phẩm khách đưa
    raw_material: chất liệu khách ghi (hoặc hint từ _extract_material_hint)
    raw_desc:     mô tả kỹ thuật / cấu hình (dùng để phát hiện bộ + chất liệu)
    """
    result = MatchResult()

    norm_name = normalize(raw_name)
    norm_mat  = normalize(raw_material) if raw_material else ""
    norm_desc = normalize(raw_desc)     if raw_desc     else ""
    combined  = f"{norm_name} {norm_mat} {norm_desc}".strip()

    # Phát hiện chất liệu: cột chất liệu > mô tả kỹ thuật > tên sản phẩm
    if norm_mat:
        material = detect_material(norm_mat)
    elif norm_desc:
        material = detect_material(norm_desc)
    else:
        material = detect_material(norm_name)
    result.material_key = material

    # 1. Trích xuất kích thước (tên > mô tả > toàn bộ text)
    size = extract_size(norm_name) or extract_size(norm_desc) or extract_size(combined)
    result.size = size or ""

    # 2. Trích xuất chiều dài
    length = extract_length(norm_name) or extract_length(norm_desc) or extract_length(combined)
    result.length = length

    # 3. Phân loại sản phẩm
    ptype = detect_product_type(combined)
    result.ptype = ptype

    if not size:
        result.note = "Không tìm được kích thước (M?)"
        result.confidence = "none"
        return result

    if not ptype:
        result.note = "Không nhận diện được loại sản phẩm"
        result.confidence = "low"
        return result

    # Override + direct lookup cho ubolt (early return)
    if ptype == "ubolt":
        if any(k in combined for k in ["bọc nhựa", "boc nhua"]):
            material = "ubolt_boc_nhua"
            table    = UBOLT_BOC_NHUA
        elif any(k in combined for k in ["nhúng nhựa", "nhung nhua"]):
            material = "ubolt_nhung_nhua"
            table    = UBOLT_MA_KEM_NHUNG_NHUA
        else:
            material = "ubolt_ma_kem"
            table    = UBOLT_MA_KEM
        mat_disp = MATERIAL_DISPLAY.get(material, "Thép mạ kẽm")
        result.material_key     = material
        result.material_display = mat_disp

        dn_key = extract_dn_size(combined)  # e.g. "DN65" or "Ø125"
        if dn_key:
            # Extract numeric part for display in result.length
            m_num = re.search(r'\d+', dn_key)
            result.length = int(m_num.group()) if m_num else None

        subtable = table.get(size) if size else None
        price = subtable.get(dn_key) if subtable and dn_key else None
        # Fallback: if exact key not found, try DN↔Ø swap
        if price is None and dn_key and subtable:
            if dn_key.startswith("Ø"):
                price = subtable.get(f"DN{dn_key[1:]}")
            elif dn_key.startswith("DN"):
                price = subtable.get(f"Ø{dn_key[2:]}")

        result.unit_price    = round(price) if price is not None else None
        dn_label = dn_key or "?"
        result.product_name  = f"Ubolt {size}-{dn_label}" if size else "Ubolt"
        result.note          = ""
        result.matched       = size is not None
        result.confidence    = "high" if price is not None else ("medium" if size else "none")
        if price is None and not dn_key:
            result.note = "Thiếu kích thước ống DN (VD: DN65, DN100)"
        elif price is None:
            result.note = f"Không có giá cho {size}-{dn_label}"
        return result

    # 4. Phát hiện và tính giá BỘ (set) nếu mô tả có đệm + đai ốc
    if ptype == "bulong" and norm_desc:
        components = _parse_set_components(norm_desc)
        if components:
            set_price, set_name, set_note, set_detail = _calculate_set_price(
                ptype, material, size, length, components
            )
            if set_price is not None:
                result.unit_price    = set_price
                result.product_name  = set_name or f"Bộ Bu lông {size}x{length}"
                result.material_display = MATERIAL_DISPLAY.get(material, material)
                result.note          = f"Bộ: {set_note}"
                result.set_detail    = set_detail
                result.matched       = True
                result.confidence    = "high"
                return result

    # 5. Tra giá đơn lẻ
    price, product_name, mat_display, note = lookup_price(ptype, material, size, length)

    result.unit_price = price
    result.product_name = product_name
    result.material_display = mat_display
    result.note = note
    result.matched = product_name != ""

    if price is not None:
        result.confidence = "high"
    elif product_name:
        result.confidence = "medium"
        if not result.note:
            result.note = "Không có giá cho size/chiều dài này"
    else:
        result.confidence = "low"

    # Tra tình trạng tồn kho
    result.in_stock = is_in_stock(ptype, material, size, length)

    return result


# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("Đệm phẳng M14", "Inox 304"),
        ("Đệm vênh M10", "Inox 304"),
        ("Bu lông M14x40", "Thép mạ cb 8.8 ren suốt"),
        ("Bu lông m10x55", "Thép mạ cb 8.8"),
        ("Ecu M10", "Thép mạ cb 8.8 ren suốt"),
        ("Lục giác chìm M8x30", ""),
        ("Đệm phẳng M8", "Inox 304"),
        ("Đệm vênh M8", "Inox 304"),
        ("Thanh ren M12", "Inox 304"),
        ("Bulong M8x20 inox 316", ""),
        ("Vít trí M6x10", "Inox 304"),
        ("Long đen phẳng M30", "Inox 304"),
    ]
    for name, mat in tests:
        r = match_product(name, mat)
        print(f"[{name}] [{mat}] → {r.product_name} | {r.material_display} | "
              f"size={r.size} L={r.length} | giá={r.unit_price} | {r.note}")
