"""Preview builder and channel sender utilities."""

import html
import json
from pathlib import Path

from aiogram import Bot
from aiogram.types import BufferedInputFile, InputMediaDocument, InputMediaPhoto

from texts import t


def _esc(value) -> str:
    """Escape a value for safe inclusion in an HTML-parsed caption."""
    return html.escape(str(value), quote=False)

COUNTER_FILE = Path(__file__).parent.parent / "app_counter.json"


def _make_media_item(file_id: str, is_doc: bool, **kwargs):
    if is_doc:
        return InputMediaDocument(media=file_id, **kwargs)
    return InputMediaPhoto(media=file_id, **kwargs)


def format_phone(phone: str) -> str:
    """Format +998XXXXXXXXX as XX XXX XX XX."""
    if not phone:
        return phone
    digits = phone.lstrip("+")
    if digits.startswith("998") and len(digits) == 12:
        local = digits[3:]
        return f"{local[0:2]} {local[2:5]} {local[5:7]} {local[7:9]}"
    return phone


def _read_counter() -> int:
    """Return the last issued application id, or 0 if there is no usable record."""
    if not COUNTER_FILE.exists():
        return 0
    try:
        data = json.loads(COUNTER_FILE.read_text())
        return int(data.get("count", 0))
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return 0


def _get_next_id() -> int:
    count = _read_counter() + 1
    COUNTER_FILE.write_text(json.dumps({"count": count}))
    return count


def seed_counter(highest_id: int) -> bool:
    """Raise the counter to highest_id when the local file lags behind the sheet.

    The counter lives only on disk, so a lost or fresh host would restart ids at 1
    and collide with applications already recorded in the spreadsheet. Seeding from
    the sheet at startup makes the id sequence survive a host migration.

    Only ever moves the counter forward — an id is never reissued.
    """
    if highest_id <= _read_counter():
        return False
    COUNTER_FILE.write_text(json.dumps({"count": int(highest_id)}))
    return True


def _caption_args(data: dict, lang: str) -> dict:
    sex_internal = data.get("sex", "")
    additional_phone = data.get("additional_phone", "") or ""
    return dict(
        name=_esc(data.get("full_name", "")),
        sex=_esc(t(f"sex_{sex_internal}", lang)) if sex_internal else "",
        level=_esc(data.get("level", "")),
        faculty=_esc(data.get("faculty_name", "")),
        region=_esc(data.get("region_name", "")),
        town=_esc(data.get("town_name", "")),
        reason=_esc(data.get("reason_name", "")),
        phone=_esc(format_phone(data.get("phone", ""))),
        additional_phone=_esc(format_phone(additional_phone)) if additional_phone else "-",
        username=_esc(data.get("username", "N/A")),
        user_id=_esc(data.get("user_id", "N/A")),
    )


def build_preview_caption(data: dict, lang: str) -> str:
    """Preview caption in the user's language — same layout as the channel message."""
    return t("preview_caption", lang, **_caption_args(data, lang))


async def _send_items(
    bot: Bot,
    chat_id: int,
    items: list[tuple[str, bool]],
    caption: str = "",
) -> list:
    """Send a list of (file_id, is_doc) items.

    Groups same-type items together (Telegram forbids mixing photos and documents
    in one media_group). The caption goes on the very first item sent.
    Groups with a single item fall back to send_photo / send_document.
    """
    photos = [fid for fid, is_doc in items if not is_doc]
    docs   = [fid for fid, is_doc in items if is_doc]
    msgs: list = []
    cap_remaining = caption  # used once, on the first item of the first group

    for group, is_doc in [(photos, False), (docs, True)]:
        if not group:
            continue
        cap = cap_remaining
        cap_remaining = ""  # consumed after first group

        if len(group) >= 2:
            media = []
            for i, fid in enumerate(group):
                kw = {"caption": cap, "parse_mode": "HTML"} if i == 0 and cap else {}
                media.append(_make_media_item(fid, is_doc, **kw))
            result = await bot.send_media_group(chat_id=chat_id, media=media)
            msgs.extend(result)
        else:
            fid = group[0]
            kw = {"caption": cap, "parse_mode": "HTML"} if cap else {}
            if is_doc:
                msg = await bot.send_document(chat_id=chat_id, document=fid, **kw)
            else:
                msg = await bot.send_photo(chat_id=chat_id, photo=fid, **kw)
            msgs.append(msg)

    return msgs


async def _as_photo_media(bot: Bot, file_id: str, is_doc: bool, **kwargs) -> InputMediaPhoto:
    """Always return InputMediaPhoto. If file was stored as a document, download and re-wrap."""
    if not is_doc:
        return InputMediaPhoto(media=file_id, **kwargs)
    file_info = await bot.get_file(file_id)
    buf = await bot.download_file(file_info.file_path)
    return InputMediaPhoto(media=BufferedInputFile(buf.read(), filename="image.jpg"), **kwargs)


async def send_to_channel(bot: Bot, channel_id: int, data: dict, lang: str) -> tuple[int, int]:
    """Send the application to the channel (always Uzbek). Returns (app_id, msg_id).

    Passport and 3x4 are always sent as photos. The official document is sent as a
    photo when it is an image, or as a separate document (PDF/Word/presentation/etc.)
    when it is not.
    """
    app_id = _get_next_id()
    caption = t("channel_caption", "uz", id=app_id, **_caption_args(data, "uz"))

    passport_id = data.get("passport_photo")
    photo_3x4_id = data.get("photo_3x4")
    official_doc_id = data.get("official_doc")
    passport_is_doc = data.get("passport_photo_is_doc", False)
    photo_3x4_is_doc = data.get("photo_3x4_is_doc", False)
    official_doc_is_doc = data.get("official_doc_is_doc", False)
    official_doc_is_image = data.get("official_doc_is_image", not official_doc_is_doc)

    if not (passport_id and photo_3x4_id):
        msg = await bot.send_message(chat_id=channel_id, text=caption, parse_mode="HTML")
        return app_id, msg.message_id

    # Photo group: passport, the official doc if it's an image, then the 3x4 photo.
    photo_items = [(passport_id, passport_is_doc)]
    if official_doc_id and official_doc_is_image:
        photo_items.append((official_doc_id, official_doc_is_doc))
    photo_items.append((photo_3x4_id, photo_3x4_is_doc))

    media = []
    for i, (fid, is_doc) in enumerate(photo_items):
        kw = {"caption": caption, "parse_mode": "HTML"} if i == 0 else {}
        media.append(await _as_photo_media(bot, fid, is_doc, **kw))

    msgs = await bot.send_media_group(chat_id=channel_id, media=media)
    msg_id = msgs[0].message_id if msgs else 0

    # Non-image official document (PDF/Word/presentation) goes as a separate file.
    if official_doc_id and not official_doc_is_image:
        await bot.send_document(
            chat_id=channel_id,
            document=official_doc_id,
            caption="📄 Rasmiy hujjat",
        )

    return app_id, msg_id
