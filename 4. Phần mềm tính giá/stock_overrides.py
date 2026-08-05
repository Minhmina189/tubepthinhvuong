# -*- coding: utf-8 -*-
"""
Runtime stock override system.
Saves user-edited stock status per cell to stock_overrides.json.
is_in_stock() checks this file first before hardcoded DB values.
"""
import json
from pathlib import Path
from typing import Optional

OVERRIDES_FILE = Path(__file__).parent / "stock_overrides.json"

# Reverse lookup: (ptype, normalised_material) → table_name
# Must stay in sync with _TABLE_STOCK_META in app.py
_TABLE_BY_PTYPE_MAT = {
    ("bulong",          "inox_304"): "BULONG_304_DIN933",
    ("bulong",          "inox_201"): "BULONG_201",
    ("bulong",          "inox_316"): "BULONG_316_DIN933",
    ("lgc_tru",         "inox_304"): "LGC_304_DIN912",
    ("lgc_tru",         "inox_201"): "LGC_201_DIN912",
    ("lgc_tru",         "inox_316"): "LGC_316_DIN912",
    ("lgc_chom_cau",    "inox_304"): "LGC_CHOM_CAU_304_DIN7380",
    ("lgc_dau_bang",    "inox_304"): "LGC_DAU_BANG_304_DIN7991",
    ("vit_tri",         "inox_304"): "VIT_TRI_304",
    ("vit_tri",         "inox_201"): "VIT_TRI_201",
    ("ecu",             "inox_304"): "ECU_304",
    ("ecu_mu",          "inox_304"): "ECU_MU_304",
    ("ecu_mu",          "inox_201"): "ECU_MU_201",
    ("ecu_mu",          "inox_316"): "ECU_MU_316",
    ("ecu_khoa",        "inox_201"): "ECU_KHOA_201",
    ("ecu_khoa",        "inox_316"): "ECU_KHOA_316",
    ("ecu_flange",      "inox_304"): "ECU_FLANGE_304",
    ("ecu_flange",      "inox_201"): "ECU_FLANGE_201",
    ("thanh_ren",       "inox_304"): "THANH_REN_304",
    ("thanh_ren",       "inox_201"): "THANH_REN_201",
    ("thanh_ren",       "inox_316"): "THANH_REN_316",
    ("nor_dan",         "inox_304"): "NOR_DAN_304",
    ("bulong_tai_hong", "inox_304"): "BULONG_TAI_HONG_304",
    ("ecu_tai_hong",    "inox_304"): "ECU_TAI_HONG_304",
    ("bulong_no",       "inox_304"): "BULONG_NO_304",
}

_cache: Optional[dict] = None
_cache_mtime: float = -1.0


def _load() -> dict:
    global _cache, _cache_mtime
    try:
        if not OVERRIDES_FILE.exists():
            _cache, _cache_mtime = {}, 0.0
            return _cache
        mtime = OVERRIDES_FILE.stat().st_mtime
        if _cache is not None and _cache_mtime == mtime:
            return _cache
        _cache = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
        _cache_mtime = mtime
        return _cache
    except Exception:
        return _cache or {}


def _save(data: dict):
    global _cache, _cache_mtime
    OVERRIDES_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _cache = data
    try:
        _cache_mtime = OVERRIDES_FILE.stat().st_mtime
    except Exception:
        _cache_mtime = -1.0


def get_stock_override(ptype: str, material: str, size: str, sub_key) -> Optional[bool]:
    """
    Return True (in stock) / False (not in stock) if user has overridden this cell.
    Return None if no override exists (caller should use hardcoded DB value).
    """
    table_name = _TABLE_BY_PTYPE_MAT.get((ptype, material))
    if not table_name:
        return None

    # BULONG_NO uses "M6x50" keys — normalise if called with separate size+length
    if ptype == "bulong_no" and sub_key is not None and "x" not in str(size):
        size = f"{size}x{sub_key}"
        sub_key = None

    data = _load()
    tbl  = data.get(table_name, {})

    if sub_key is not None:
        sz_data = tbl.get(size)
        if isinstance(sz_data, dict):
            val = sz_data.get(str(sub_key))
            if isinstance(val, bool):
                return val
        return None

    val = tbl.get(size)
    if isinstance(val, bool):
        return val
    return None


def save_stock_override(table_name: str, size: str, sub_key, value: Optional[bool]):
    """
    Persist stock override for one cell.
    value = True (in stock) | False (not in stock) | None (remove override, revert to DB).
    """
    data = dict(_load())

    if table_name not in data:
        data[table_name] = {}

    if sub_key is not None:
        str_sub = str(sub_key)
        if size not in data[table_name] or not isinstance(data[table_name][size], dict):
            data[table_name][size] = {}
        sz = data[table_name][size]
        if value is None:
            sz.pop(str_sub, None)
            if not sz:
                data[table_name].pop(size, None)
        else:
            sz[str_sub] = value
    else:
        if value is None:
            data[table_name].pop(size, None)
        else:
            data[table_name][size] = value

    if not data.get(table_name):
        data.pop(table_name, None)

    _save(data)


def has_any_overrides() -> bool:
    return bool(_load())


def reset_all():
    global _cache, _cache_mtime
    if OVERRIDES_FILE.exists():
        OVERRIDES_FILE.unlink()
    _cache, _cache_mtime = {}, 0.0
