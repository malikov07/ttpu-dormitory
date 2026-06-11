"""Lightweight persistence of user_id → language preference."""

import json
from pathlib import Path

_FILE = Path(__file__).parent.parent / "user_langs.json"


def save_user_lang(user_id: int, lang: str) -> None:
    data: dict = {}
    if _FILE.exists():
        try:
            data = json.loads(_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    data[str(user_id)] = lang
    _FILE.write_text(json.dumps(data), encoding="utf-8")


def get_user_lang(user_id: int, default: str = "uz") -> str:
    if not _FILE.exists():
        return default
    try:
        data = json.loads(_FILE.read_text(encoding="utf-8"))
        lang = data.get(str(user_id), default)
        return lang if lang in ("uz", "en", "ru") else default
    except Exception:
        return default
