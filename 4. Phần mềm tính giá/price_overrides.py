# -*- coding: utf-8 -*-
"""
Runtime price override system.
Loads price_overrides.json and patches the live price_database dicts in-place.
Writes new overrides back to the JSON file and applies them immediately.
"""
import json
from pathlib import Path

OVERRIDES_FILE = Path(__file__).parent / "price_overrides.json"
_applied = False


def load_and_apply():
    """Read override JSON and patch the live dicts in price_database."""
    global _applied
    if _applied:
        return
    _applied = True
    if not OVERRIDES_FILE.exists():
        return
    try:
        import price_database as _pd
        data = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
        for table_name, overrides in data.items():
            table = getattr(_pd, table_name, None)
            if not isinstance(table, dict):
                continue
            _deep_apply(table, overrides)
    except Exception as e:
        print(f"[price_overrides] load error: {e}")


def _deep_apply(target: dict, overrides: dict):
    for str_key, val in overrides.items():
        # Try to match int keys (lengths stored as ints in the dicts)
        int_key = None
        try:
            int_key = int(str_key)
        except (ValueError, TypeError):
            pass

        if isinstance(val, dict):
            # Navigate one level deeper
            real_key = str_key
            if real_key not in target and int_key is not None and int_key in target:
                real_key = int_key
            if real_key not in target:
                target[real_key] = {}
            if isinstance(target[real_key], dict):
                _deep_apply(target[real_key], val)
        else:
            # Leaf value: find the right key
            if str_key in target:
                target[str_key] = val
            elif int_key is not None and int_key in target:
                target[int_key] = val
            else:
                # Key doesn't exist yet — insert with best guess type
                target[int_key if int_key is not None else str_key] = val


def save_override(table_name: str, size_key: str, sub_key, new_price: int):
    """
    Save a single price override and apply it immediately.
    sub_key: the length (int or str) or special key like "ECU","LDP","LDV", or None for flat tables.
    """
    import price_database as _pd

    # Load existing overrides from file
    data: dict = {}
    if OVERRIDES_FILE.exists():
        try:
            data = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    # Write to override structure
    if table_name not in data:
        data[table_name] = {}

    if sub_key is not None:
        str_sub = str(sub_key)
        if size_key not in data[table_name]:
            data[table_name][size_key] = {}
        if isinstance(data[table_name].get(size_key), dict):
            data[table_name][size_key][str_sub] = new_price
        else:
            data[table_name][size_key] = {str_sub: new_price}
    else:
        data[table_name][size_key] = new_price

    # Apply to live dict immediately
    table = getattr(_pd, table_name, None)
    if isinstance(table, dict):
        if sub_key is not None:
            if size_key not in table or not isinstance(table.get(size_key), dict):
                table[size_key] = {}
            # Try int sub_key first (lengths are stored as int)
            try:
                int_sub = int(sub_key)
                if int_sub in table[size_key]:
                    table[size_key][int_sub] = new_price
                    sub_key = int_sub
                else:
                    table[size_key][sub_key] = new_price
            except (ValueError, TypeError):
                table[size_key][sub_key] = new_price
        else:
            table[size_key] = new_price

    # Persist to file
    OVERRIDES_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def reset_overrides():
    """Delete all overrides (requires app restart to take full effect)."""
    if OVERRIDES_FILE.exists():
        OVERRIDES_FILE.unlink()


# Apply at import time
load_and_apply()
