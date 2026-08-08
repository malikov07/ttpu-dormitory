"""Lightweight persistence of Telegram IDs that already submitted an application.

One application per Telegram account. The file is the bot's own record; it is
seeded from the spreadsheet at startup (see utils.google_api.sync_applied_users)
so students who applied before this record existed are still recognised.
"""

import json
import logging
from pathlib import Path

from config import now_tashkent

logger = logging.getLogger(__name__)

_FILE = Path(__file__).parent.parent / "applied_users.json"


def _load() -> dict:
    if not _FILE.exists():
        return {}
    try:
        data = json.loads(_FILE.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("applied_users.json is unreadable — treating it as empty.")
        return {}
    return data if isinstance(data, dict) else {}


def _save(data: dict) -> None:
    _FILE.write_text(json.dumps(data), encoding="utf-8")


def get_application(user_id: int):
    """Return the stored record for a previous application, or None."""
    return _load().get(str(user_id))


def has_applied(user_id: int) -> bool:
    return str(user_id) in _load()


def mark_applied(user_id: int, app_id) -> None:
    data = _load()
    data[str(user_id)] = {
        "app_id": app_id,
        "at": now_tashkent().isoformat(timespec="seconds"),
    }
    _save(data)


def clear_applied(user_id: int) -> bool:
    """Let a user apply again. Returns False if they had no application on record."""
    data = _load()
    if str(user_id) not in data:
        return False
    del data[str(user_id)]
    _save(data)
    return True


def seed(user_ids) -> int:
    """Record ids that are missing locally. Existing entries are left untouched.

    Returns how many ids were newly added.
    """
    data = _load()
    added = 0
    for uid in user_ids:
        key = str(uid)
        if key not in data:
            data[key] = {"app_id": None, "at": None, "source": "sheet"}
            added += 1
    if added:
        _save(data)
    return added


def already_applied_text(user_id: int, lang: str) -> str:
    """Message shown when someone who already applied tries to apply again."""
    from texts import t

    app_id = (get_application(user_id) or {}).get("app_id")
    if app_id:
        return t("already_applied_with_id", lang, id=app_id)
    return t("already_applied", lang)
