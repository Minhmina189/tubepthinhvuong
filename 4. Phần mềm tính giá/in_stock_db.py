# -*- coding: utf-8 -*-
"""
Cơ sở dữ liệu tồn kho Nam An.
Ô xanh lá trong bảng giá = có sẵn (True)
Ô trắng = không có sẵn / theo yêu cầu (False)
Chưa có dữ liệu = None
"""
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# INOX 201 — BU LÔNG INOX 201
# Ô xanh = có sẵn  |  ô trắng = theo yêu cầu
# ─────────────────────────────────────────────────────────────────────────────
_BULONG_201 = {
    "M4":  {10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 60},
    "M5":  {10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 60, 65, 70},
    "M6":  {10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100},
    "M8":  {10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100},
    "M10": {16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100},
    "M12": {20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100},
    "M14": {30, 35, 40, 45, 50, 55, 60, 65, 70},
    "M16": {30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 90, 100},
    "M20": {40, 45, 50, 60, 70, 80, 90, 100},
}

# ─────────────────────────────────────────────────────────────────────────────
# INOX 201 — LỤC GIÁC CHÌM TRỤ DIN912
# ─────────────────────────────────────────────────────────────────────────────
_LGC_TRU_201 = {
    "M3":  {6, 8, 10, 12, 16, 20, 25},
    "M4":  {6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50},
    "M5":  {8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55},
    "M6":  {10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60},
    "M8":  {12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 100},
    "M10": {16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80},
    "M12": {20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 100},
    "M14": {25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80},
    "M16": {30, 35, 40, 45, 50, 55, 60, 65, 70, 80},
}

# ─────────────────────────────────────────────────────────────────────────────
# INOX 201 — VÍT TRÍ DIN913
# ─────────────────────────────────────────────────────────────────────────────
_VIT_TRI_201 = {
    "M3":  {6, 8, 10, 12, 16, 20},
    "M4":  {6, 8, 10, 12, 16, 20, 25, 30},
    "M5":  {6, 8, 10, 12, 16, 20, 25, 30, 35, 40},
    "M6":  {6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 50},
    "M8":  {8, 10, 12, 16, 20, 25, 30},
    "M10": {10, 12, 16, 20, 25, 30},
    "M12": {12, 16, 20, 25, 30},
    "M14": {20, 25, 30, 35},
    "M16": {20, 25, 30, 35, 40},
    "M20": {25, 30, 40, 50, 60, 70},
}

# ─────────────────────────────────────────────────────────────────────────────
# INOX 201 — ECU, LDP, LDV, THANH REN (không có chiều dài)
# ─────────────────────────────────────────────────────────────────────────────
_ECU_201         = {"M4", "M5", "M6", "M8", "M10", "M12"}
_LDP_201         = {"M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M20"}
_LDV_201         = {"M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M20"}
_ECU_MU_201      = {"M4", "M5", "M6", "M8", "M10", "M12"}
_ECU_KHOA_201    = {"M4", "M5", "M6", "M8", "M10", "M12"}
_ECU_FLANGE_201  = {"M4", "M5", "M6", "M8", "M10", "M12"}
_THANH_REN_201   = {
    "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18",
    "M20", "M22", "M24", "M27", "M30", "M36",
}

# ─────────────────────────────────────────────────────────────────────────────
# INOX 316 — LỤC GIÁC CHÌM TRỤ DIN912
# ─────────────────────────────────────────────────────────────────────────────
_LGC_TRU_316 = {
    "M3":  {6, 8, 10, 12, 16, 20, 25, 30, 35, 40},
    "M4":  {6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 50},
    "M5":  {8, 10, 12, 16, 20, 25, 30, 35, 40, 50, 60, 65, 70, 75, 80},
    "M6":  {10, 12, 16, 20, 25, 30, 35, 40, 50, 60, 65, 70, 75, 80},
    "M8":  {12, 16, 20, 25, 30, 35, 40, 50, 60, 65, 70, 80},
    "M10": {16, 20, 25, 30, 35, 40, 50, 60, 65, 70, 75, 80},
    "M12": {20, 25, 30, 35, 40, 50, 60},
}

# ─────────────────────────────────────────────────────────────────────────────
# INOX 316 — BU LÔNG DIN933
# ─────────────────────────────────────────────────────────────────────────────
_BULONG_316 = {
    "M3":  {8, 10, 12, 16, 20, 25},
    "M4":  {8, 10, 12, 16, 20, 25, 30, 40},
    "M5":  {8, 10, 12, 16, 20, 25, 30, 40, 50},
    "M6":  {10, 12, 16, 20, 25, 30, 40, 50, 60},
    "M8":  {10, 12, 16, 20, 25, 30, 35, 40, 50, 60, 70, 80, 100},
    "M10": {16, 20, 25, 30, 40, 50, 60, 70, 80, 100},
    "M12": {20, 25, 30, 40, 50, 60, 70, 80, 100, 120},
    "M14": {30, 40, 50, 60, 70, 80},
    "M16": {30, 40, 50, 60, 70, 80, 100},
    "M18": {40, 50, 60, 70, 80},
    "M20": {40, 50, 60, 70, 80, 100, 120},
    "M22": {50, 60, 70, 80, 100},
    "M24": {50, 60, 70, 80, 100, 120},
    "M27": {60, 70, 80, 100},
    "M30": {60, 70, 80, 100, 120},
}

# ─────────────────────────────────────────────────────────────────────────────
# INOX 316 — ECU, LDP, LDV, THANH REN, ECU MŨ, ECU KHÓA, ELLD
# ─────────────────────────────────────────────────────────────────────────────
_ECU_316 = {
    "M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16",
    "M18", "M20", "M22", "M24", "M27", "M30", "M36", "M42", "M48",
}
_LDP_316 = {
    "M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16",
    "M18", "M20", "M22", "M24", "M27", "M30", "M36", "M42", "M48", "M56", "M64",
}
_LDV_316         = _LDP_316.copy()
_ECU_KHOA_316    = {"M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18", "M20", "M22", "M24"}
_ECU_MU_316      = {"M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18", "M20", "M24"}
_THANH_REN_316   = {
    "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18",
    "M20", "M22", "M24", "M27", "M30", "M33", "M36",
}

# ─────────────────────────────────────────────────────────────────────────────
# INOX 304 — ước tính (không có PDF riêng, dùng mẫu tương tự 201)
# ─────────────────────────────────────────────────────────────────────────────
_BULONG_304 = {
    "M3":  {8, 10, 12, 14, 16, 18, 20, 22, 25, 30, 35, 40},
    "M4":  {10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 60},
    "M5":  {10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 60, 70},
    "M6":  {10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100},
    "M8":  {10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100},
    "M10": {16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100},
    "M12": {20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100},
    "M14": {30, 35, 40, 45, 50, 55, 60, 65, 70},
    "M16": {30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 90, 100},
    "M18": {35, 40, 45, 50, 55, 60, 65, 70},
    "M20": {40, 45, 50, 60, 70, 80, 90, 100},
    "M22": {50, 60, 70, 80},
    "M24": {50, 60, 70, 80, 100},
    "M27": {60, 70, 80, 100},
    "M30": {60, 70, 80, 100},
    "M33": {60, 70},
    "M36": {70, 80, 100},
}

_LGC_TRU_304 = {
    "M3":  {6, 8, 10, 12, 16, 20, 25},
    "M4":  {6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50},
    "M5":  {8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55},
    "M6":  {10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60},
    "M8":  {12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 100},
    "M10": {16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80},
    "M12": {20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 100},
    "M14": {25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80},
    "M16": {30, 35, 40, 45, 50, 55, 60, 65, 70, 80},
}

_LGC_CHOM_CAU_304 = {
    "M2":   {3, 4, 5, 6, 8, 10, 12},
    "M2.5": {3, 4, 5, 6, 8, 10, 12},
    "M3":   {3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30, 35, 40, 45, 50},
    "M4":   {5, 6, 8, 10, 12, 14, 16, 18, 20, 25, 30, 35, 40, 45, 50},
    "M5":   {6, 8, 10, 12, 14, 16, 18, 20, 25, 30, 35, 40, 45, 50},
    "M6":   {8, 10, 12, 14, 16, 18, 20, 25, 30, 35, 40, 45, 50, 60},
    "M8":   {10, 12, 16, 20, 25, 30, 35, 40, 50, 60, 70, 80},
    "M10":  {12, 16, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100},
    "M12":  {25, 30, 35, 40, 45, 50},
    # M14, M16, M20: white = not in stock
}

# BULONG NỞ stock — full key format "MXxL" matching BULONG_NO_304 dict keys
_BULONG_NO_304_STOCK = {
    "M6x50", "M6x60", "M6x80",
    "M8x60", "M8x80", "M8x120",
    "M10x60", "M10x80", "M10x100", "M10x150",
    "M12x80", "M12x100",
    "M14x80", "M14x100",
    "M16x80", "M16x150",
    "M18x100",
    "M20x150", "M20x200",
}

# LGC ĐẦU BẰNG DIN7991 stock
_LGC_DAU_BANG_304 = {
    "M3":  {20, 25, 30},
    "M4":  {6, 10, 12, 16, 20, 25, 30},
    "M5":  {6, 8, 10, 12, 16, 20, 25, 30},
    "M6":  {8, 10, 12, 16, 20, 25, 30},
    "M8":  {10, 12, 16, 20, 25, 30},
    "M10": {20, 25, 30},
    "M12": {25, 30},
}

# BULONG TAI HỒNG DIN316 stock
_BULONG_TAI_HONG_304 = {
    "M6": {50},
    "M8": {10, 16, 50},
    "M10": {10, 16},
}

# ECU TAI HỒNG DIN316 stock — white = in stock, yellow = not in stock
_ECU_TAI_HONG_304 = {"M3", "M4", "M5", "M6", "M8", "M10", "M12"}

_ECU_304      = {
    "M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18",
    "M20", "M22", "M24", "M27", "M30", "M36",
}
_LDP_304      = _ECU_304.copy()
_LDV_304      = _ECU_304.copy()
_THANH_REN_304 = {
    "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M18", "M20",
    # M22+ and all 2m/3m lengths: white = not in stock
}
_ECU_MU_304   = {"M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M20", "M24"}
_ECU_KHOA_304 = {"M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16"}
_ECU_FLANGE_304 = {"M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16"}
_NOR_DAN_304  = {"M6", "M8", "M10"}  # M12/M14/M16: white = not in stock
_VIT_TRI_304  = {
    "M3":  {6, 8, 10, 12, 16, 20},
    "M4":  {6, 8, 10, 12, 16, 20, 25, 30},
    "M5":  {6, 8, 10, 12, 16, 20, 25, 30, 35, 40},
    "M6":  {6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 50},
    "M8":  {8, 10, 12, 16, 20, 25, 30},
    "M10": {10, 12, 16, 20, 25},
    "M12": {12, 16, 20, 25},
}


# ─────────────────────────────────────────────────────────────────────────────
# LOOKUP FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def _bolt_stock(table: dict, size: str, length) -> Optional[bool]:
    lengths = table.get(size)
    if lengths is None:
        return False
    if length is None:
        return True
    try:
        return int(length) in lengths
    except (TypeError, ValueError):
        return None


def is_in_stock(ptype: str, material: str, size: str, length=None) -> Optional[bool]:
    """
    Trả về True (có sẵn), False (theo yêu cầu), None (không rõ).
    ptype:    product type từ MatchResult.ptype
    material: material key — chấp nhận cả "inox304" và "inox_304"
    size:     "M10"
    length:   int mm hoặc None
    """
    mat = (material or "").lower()
    pt  = (ptype   or "").lower()

    # Normalize: product_matcher dùng "inox304", price catalog dùng "inox_304"
    if mat == "inox304": mat = "inox_304"
    elif mat == "inox201": mat = "inox_201"
    elif mat == "inox316": mat = "inox_316"

    # Thép đen / mạ kẽm: chưa có dữ liệu tồn kho
    if mat.startswith("thep"):
        return None

    # User override takes priority over hardcoded DB
    try:
        from stock_overrides import get_stock_override
        override = get_stock_override(pt, mat, size, length)
        if override is not None:
            return override
    except Exception:
        pass

    # ── INOX 201 ──────────────────────────────
    if mat == "inox_201":
        if pt == "bulong":
            return _bolt_stock(_BULONG_201, size, length)
        if pt in ("lgc_tru", "lgc"):
            return _bolt_stock(_LGC_TRU_201, size, length)
        if pt == "vit_tri":
            return _bolt_stock(_VIT_TRI_201, size, length)
        if pt == "ecu":
            return size in _ECU_201
        if pt == "ldp":
            return size in _LDP_201
        if pt == "ldv":
            return size in _LDV_201
        if pt == "ecu_mu":
            return size in _ECU_MU_201
        if pt == "ecu_khoa":
            return size in _ECU_KHOA_201
        if pt == "ecu_flange":
            return size in _ECU_FLANGE_201
        if pt == "thanh_ren":
            return size in _THANH_REN_201

    # ── INOX 316 ──────────────────────────────
    if mat == "inox_316":
        if pt == "bulong":
            return _bolt_stock(_BULONG_316, size, length)
        if pt in ("lgc_tru", "lgc"):
            return _bolt_stock(_LGC_TRU_316, size, length)
        if pt == "ecu":
            return size in _ECU_316
        if pt == "ldp":
            return size in _LDP_316
        if pt == "ldv":
            return size in _LDV_316
        if pt == "ecu_mu":
            return size in _ECU_MU_316
        if pt == "ecu_khoa":
            return size in _ECU_KHOA_316
        if pt == "thanh_ren":
            return size in _THANH_REN_316

    # ── INOX 304 ──────────────────────────────
    if mat == "inox_304":
        if pt == "bulong":
            return _bolt_stock(_BULONG_304, size, length)
        if pt in ("lgc_tru", "lgc"):
            return _bolt_stock(_LGC_TRU_304, size, length)
        if pt == "lgc_chom_cau":
            return _bolt_stock(_LGC_CHOM_CAU_304, size, length)
        if pt == "lgc_dau_bang":
            return _bolt_stock(_LGC_DAU_BANG_304, size, length)
        if pt == "bulong_tai_hong":
            return _bolt_stock(_BULONG_TAI_HONG_304, size, length)
        if pt == "ecu_tai_hong":
            return size in _ECU_TAI_HONG_304
        if pt == "bulong_no":
            # Called from prices view with "M6x50" key, or from match_product with size+length
            if size and 'x' in size:
                return size in _BULONG_NO_304_STOCK
            elif length is not None:
                return f"{size}x{length}" in _BULONG_NO_304_STOCK
            return any(k.startswith(f"{size}x") for k in _BULONG_NO_304_STOCK)
        if pt == "vit_tri":
            return _bolt_stock(_VIT_TRI_304, size, length)
        if pt == "ecu":
            return size in _ECU_304
        if pt == "ldp":
            return size in _LDP_304
        if pt == "ldv":
            return size in _LDV_304
        if pt == "ecu_mu":
            return size in _ECU_MU_304
        if pt == "ecu_khoa":
            return size in _ECU_KHOA_304
        if pt == "ecu_flange":
            return size in _ECU_FLANGE_304
        if pt == "thanh_ren":
            # THANH_REN key format is "MXxYm" — only 1m lengths are in stock
            if size and 'x' in size:
                bare, length_part = size.split('x', 1)
                if length_part != "1m":
                    return False
                return bare in _THANH_REN_304
            return size in _THANH_REN_304
        if pt == "nor_dan":
            return size in _NOR_DAN_304

    return None
