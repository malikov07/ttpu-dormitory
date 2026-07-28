"""Application form FSM handlers — full step-by-step flow."""

import asyncio
import logging
import re

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from config import CHANNEL_ID, is_admin
from data.regions import FACULTIES, REASONS, REASONS_REQUIRING_DOC, REGIONS
from utils.tg import safe_delete

# Length limits for free-text input (keeps captions under Telegram's 1024-char cap).
MAX_NAME_LEN = 100
MAX_TOWN_LEN = 100
MAX_REASON_LEN = 200
from keyboards import (
    additional_phone_keyboard,
    cancel_keyboard,
    edit_field_keyboard,
    faculty_keyboard,
    level_keyboard,
    main_menu_keyboard,
    phone_keyboard,
    preview_keyboard,
    reason_keyboard,
    region_keyboard,
    sex_keyboard,
    town_keyboard,
)
from states import ApplicationForm
from texts import TEXTS, t
from utils.google_api import process_and_save_application
from utils.preview import _send_items, build_preview_caption, send_to_channel

router = Router()
logger = logging.getLogger(__name__)

# International (E.164) number: country code + subscriber number, 8–15 digits total.
PHONE_RE = re.compile(r"^\+[1-9]\d{7,14}$")
PHONE_SEPARATORS_RE = re.compile(r"[\s\-().]")
UZ_LOCAL_LEN = 9  # Uzbek subscriber number without the 998 country code


def normalize_phone(raw: str):
    """Return the number as +<country code><subscriber>, or None if it isn't valid.

    Bare digits are only accepted when they are unambiguously Uzbek (998XXXXXXXXX or
    a 9-digit local number); any other country must be typed with a leading "+".
    """
    phone = PHONE_SEPARATORS_RE.sub("", raw.strip())
    if not phone.startswith("+"):
        if phone.startswith("998"):
            phone = "+" + phone
        elif len(phone) == UZ_LOCAL_LEN and phone.isdigit():
            phone = "+998" + phone
        else:
            return None
    if not PHONE_RE.match(phone):
        return None
    # Uzbek numbers stay strictly validated so ordinary typos are still caught.
    if phone.startswith("+998") and len(phone) != len("+998") + UZ_LOCAL_LEN:
        return None
    return phone


async def _get_lang(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get("lang", "en")


def _safe_int(value: str):
    """Parse an int from callback data; return None if it's not a valid integer."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


async def _show_preview(message_or_cb, state: FSMContext, lang: str) -> None:
    """Send photos as album then caption text + inline buttons as a separate message."""
    data = await state.get_data()
    text = build_preview_caption(data, lang)

    if isinstance(message_or_cb, CallbackQuery):
        chat_id = message_or_cb.message.chat.id
        bot = message_or_cb.message.bot
    else:
        chat_id = message_or_cb.chat.id
        bot = message_or_cb.bot

    passport_id = data.get("passport_photo")
    photo_3x4_id = data.get("photo_3x4")
    official_doc_id = data.get("official_doc")
    passport_is_doc = data.get("passport_photo_is_doc", False)
    photo_3x4_is_doc = data.get("photo_3x4_is_doc", False)
    official_doc_is_doc = data.get("official_doc_is_doc", False)

    items = [(passport_id, passport_is_doc)]
    if official_doc_id:
        items.append((official_doc_id, official_doc_is_doc))
    items.append((photo_3x4_id, photo_3x4_is_doc))

    await _send_items(bot, chat_id, items)
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=preview_keyboard(lang),
        parse_mode="HTML",
    )
    await state.set_state(ApplicationForm.preview)


# ─── Cancel handler ───────────────────────────────────────────────────────

@router.message(F.text.in_([TEXTS[la]["btn_cancel"] for la in TEXTS]))
async def handle_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    lang = await _get_lang(state)
    await state.clear()
    await state.update_data(lang=lang, oferta_agreed=True)
    await message.answer(
        t("cancelled", lang),
        reply_markup=main_menu_keyboard(lang, is_admin(message.from_user.id)),
        parse_mode="HTML",
    )


# ─── Unified back navigation (works for inline and reply keyboards) ───────

async def _go_back(bot, chat_id: int, user_id: int, state: FSMContext, lang: str) -> None:
    """Move one step back from the current state. Used by both back buttons."""
    current = await state.get_state()
    if current is None:
        return
    data = await state.get_data()

    async def send(text, markup):
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode="HTML")

    if current == ApplicationForm.full_name:
        await state.clear()
        await state.update_data(lang=lang, oferta_agreed=True)
        await send(t("main_menu", lang), main_menu_keyboard(lang, is_admin(user_id)))

    elif current == ApplicationForm.sex:
        await send(t("ask_full_name", lang), cancel_keyboard(lang))
        await state.set_state(ApplicationForm.full_name)

    elif current == ApplicationForm.level:
        await send(t("ask_sex", lang), sex_keyboard(lang))
        await state.set_state(ApplicationForm.sex)

    elif current == ApplicationForm.faculty:
        await send(t("ask_level", lang), level_keyboard(lang))
        await state.set_state(ApplicationForm.level)

    elif current == ApplicationForm.region:
        await send(t("ask_faculty", lang), faculty_keyboard(lang))
        await state.set_state(ApplicationForm.faculty)

    elif current == ApplicationForm.town:
        await send(t("ask_region", lang), region_keyboard(lang))
        await state.set_state(ApplicationForm.region)

    elif current == ApplicationForm.town_custom:
        region_idx = data.get("region_idx", 0)
        region_name = data.get("region_name", "")
        await send(t("ask_town", lang, region=region_name), town_keyboard(region_idx, lang))
        await state.set_state(ApplicationForm.town)

    elif current == ApplicationForm.reason:
        if data.get("is_foreign"):
            await send(t("ask_region", lang), region_keyboard(lang))
            await state.set_state(ApplicationForm.region)
        else:
            region_idx = data.get("region_idx", 0)
            region_name = data.get("region_name", "")
            await send(t("ask_town", lang, region=region_name), town_keyboard(region_idx, lang))
            await state.set_state(ApplicationForm.town)

    elif current in (ApplicationForm.reason_custom, ApplicationForm.official_doc):
        await send(t("ask_reason", lang), reason_keyboard(lang))
        await state.set_state(ApplicationForm.reason)

    elif current == ApplicationForm.passport_photo:
        if data.get("needs_official_doc"):
            await send(t("ask_official_doc", lang), cancel_keyboard(lang))
            await state.set_state(ApplicationForm.official_doc)
        else:
            await send(t("ask_reason", lang), reason_keyboard(lang))
            await state.set_state(ApplicationForm.reason)

    elif current == ApplicationForm.photo_3x4:
        await send(t("ask_passport", lang), cancel_keyboard(lang))
        await state.set_state(ApplicationForm.passport_photo)

    elif current == ApplicationForm.phone_number:
        await send(t("ask_photo_3x4", lang), cancel_keyboard(lang))
        await state.set_state(ApplicationForm.photo_3x4)

    elif current == ApplicationForm.additional_phone:
        await send(t("ask_phone", lang), phone_keyboard(lang))
        await state.set_state(ApplicationForm.phone_number)


@router.callback_query(F.data == "back")
async def handle_inline_back(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    await callback.answer()
    await safe_delete(callback.message)
    await _go_back(callback.message.bot, callback.message.chat.id, callback.from_user.id, state, lang)


@router.message(F.text.in_([TEXTS[la]["btn_back"] for la in TEXTS]))
async def handle_text_back(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        return
    lang = await _get_lang(state)
    await _go_back(message.bot, message.chat.id, message.from_user.id, state, lang)


# ─── Step 1: Full Name ───────────────────────────────────────────────────

@router.message(ApplicationForm.full_name, F.text)
async def process_full_name(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    name = message.text.strip()

    if len(name) < 5 or len(name) > MAX_NAME_LEN:
        await message.answer(t("invalid_name", lang), parse_mode="HTML")
        return

    data = await state.get_data()
    editing = data.get("editing")
    await state.update_data(full_name=name)

    if editing:
        await state.update_data(editing=False)
        await _show_preview(message, state, lang)
        return

    await message.answer(t("ask_sex", lang), reply_markup=sex_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.sex)


# ─── Step 2: Sex ─────────────────────────────────────────────────────────

@router.callback_query(ApplicationForm.sex, F.data.startswith("sex:"))
async def process_sex(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    sex_value = callback.data.split(":")[1]  # "male" or "female"
    await callback.answer()
    await safe_delete(callback.message)

    sex_uz = "Erkak" if sex_value == "male" else "Ayol"
    data = await state.get_data()
    editing = data.get("editing")

    await state.update_data(sex=sex_value, sex_uz=sex_uz)

    if editing:
        await state.update_data(editing=False)
        await _show_preview(callback, state, lang)
        return

    await callback.message.answer(t("ask_level", lang), reply_markup=level_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.level)


# ─── Step 3: Level ────────────────────────────────────────────────────────

@router.callback_query(ApplicationForm.level, F.data.startswith("level:"))
async def process_level(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    level = callback.data.split(":")[1]
    await callback.answer()
    await safe_delete(callback.message)

    data = await state.get_data()
    editing = data.get("editing")
    await state.update_data(level=level)

    if editing:
        await state.update_data(editing=False)
        await _show_preview(callback, state, lang)
        return

    await callback.message.answer(t("ask_faculty", lang), reply_markup=faculty_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.faculty)


# ─── Step 4: Faculty ──────────────────────────────────────────────────────

@router.callback_query(ApplicationForm.faculty, F.data.startswith("faculty:"))
async def process_faculty(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    idx = _safe_int(callback.data.split(":")[1])
    if idx is None or not (0 <= idx < len(FACULTIES)):
        await callback.answer()
        return
    await callback.answer()
    await safe_delete(callback.message)

    faculty_name = FACULTIES[idx][lang]
    data = await state.get_data()
    editing = data.get("editing")

    await state.update_data(faculty_idx=idx, faculty_name=faculty_name, faculty_uz=FACULTIES[idx]["uz"])

    if editing:
        await state.update_data(editing=False)
        await _show_preview(callback, state, lang)
        return

    await callback.message.answer(t("ask_region", lang), reply_markup=region_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.region)


# ─── Step 5: Region ───────────────────────────────────────────────────────

@router.callback_query(ApplicationForm.region, F.data.startswith("reg:"))
async def process_region(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    value = callback.data.split(":")[1]
    await callback.answer()
    await safe_delete(callback.message)

    if value == "foreign":
        foreign_name = t("region_foreign", lang)
        await state.update_data(
            region_idx=-1,
            region_name=foreign_name,
            region_uz="Xorijiy davlat",
            is_foreign=True,
            town_name=foreign_name,
            town_uz="Xorijiy davlat",
        )
        data = await state.get_data()
        editing = data.get("editing")
        if editing:
            await state.update_data(editing=False)
            await _show_preview(callback, state, lang)
            return
        await callback.message.answer(t("ask_reason", lang), reply_markup=reason_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.reason)
        return

    idx = _safe_int(value)
    if idx is None or not (0 <= idx < len(REGIONS)):
        return
    region_name = REGIONS[idx]["name"][lang]
    await state.update_data(
        region_idx=idx,
        region_name=region_name,
        region_uz=REGIONS[idx]["name"]["uz"],
        is_foreign=False,
    )
    await callback.message.answer(
        t("ask_town", lang, region=region_name),
        reply_markup=town_keyboard(idx, lang),
        parse_mode="HTML",
    )
    await state.set_state(ApplicationForm.town)


# ─── Step 6: Town ─────────────────────────────────────────────────────────

@router.callback_query(ApplicationForm.town, F.data.startswith("town:"))
async def process_town(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    value = callback.data.split(":")[1]
    await callback.answer()
    await safe_delete(callback.message)

    if value == "other":
        await callback.message.answer(t("ask_town_custom", lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.town_custom)
        return

    data = await state.get_data()
    editing = data.get("editing")
    region_idx = data.get("region_idx", 0)
    town_idx = _safe_int(value)
    if region_idx is None or not (0 <= region_idx < len(REGIONS)):
        return
    towns = REGIONS[region_idx]["towns"]
    if town_idx is None or not (0 <= town_idx < len(towns)):
        return
    town_name = towns[town_idx][lang]
    town_uz = towns[town_idx]["uz"]

    await state.update_data(town_name=town_name, town_uz=town_uz)

    if editing:
        await state.update_data(editing=False)
        await _show_preview(callback, state, lang)
        return

    await callback.message.answer(t("ask_reason", lang), reply_markup=reason_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.reason)


@router.message(ApplicationForm.town_custom, F.text)
async def process_town_custom(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    data = await state.get_data()
    editing = data.get("editing")

    town = message.text.strip()[:MAX_TOWN_LEN]
    await state.update_data(town_name=town, town_uz=town)

    if editing:
        await state.update_data(editing=False)
        await _show_preview(message, state, lang)
        return

    await message.answer(t("ask_reason", lang), reply_markup=reason_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.reason)


# ─── Step 7: Reason ───────────────────────────────────────────────────────

def _needs_doc(reason_idx: int) -> bool:
    return reason_idx in REASONS_REQUIRING_DOC


@router.callback_query(ApplicationForm.reason, F.data.startswith("reason:"))
async def process_reason(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    value = callback.data.split(":")[1]
    await callback.answer()
    await safe_delete(callback.message)

    if value == "other":
        await callback.message.answer(t("ask_reason_custom", lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.reason_custom)
        return

    reason_idx = _safe_int(value)
    if reason_idx is None or not (0 <= reason_idx < len(REASONS)):
        return
    reason_name = REASONS[reason_idx][lang]
    reason_uz = REASONS[reason_idx]["uz"]
    needs_doc = _needs_doc(reason_idx)
    data = await state.get_data()
    editing = data.get("editing")

    await state.update_data(reason_name=reason_name, reason_uz=reason_uz, needs_official_doc=needs_doc)

    if editing:
        if not needs_doc:
            # Switched to a reason that needs no document — drop any previously uploaded one.
            await state.update_data(
                official_doc=None, official_doc_is_doc=False, official_doc_is_image=False
            )
            await state.update_data(editing=False)
            await _show_preview(callback, state, lang)
            return
        # Now requires a document: ask for it instead of returning straight to preview.
        await state.update_data(editing=True)
        await callback.message.answer(
            t("ask_official_doc", lang), reply_markup=cancel_keyboard(lang), parse_mode="HTML"
        )
        await state.set_state(ApplicationForm.official_doc)
        return

    if needs_doc:
        await callback.message.answer(t("ask_official_doc", lang), reply_markup=cancel_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.official_doc)
    else:
        await state.update_data(official_doc=None)
        await callback.message.answer(t("ask_passport", lang), reply_markup=cancel_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.passport_photo)


@router.message(ApplicationForm.reason_custom, F.text)
async def process_reason_custom(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    data = await state.get_data()
    editing = data.get("editing")

    reason = message.text.strip()[:MAX_REASON_LEN]
    await state.update_data(reason_name=reason, reason_uz=reason, needs_official_doc=False, official_doc=None)

    if editing:
        await state.update_data(editing=False)
        await _show_preview(message, state, lang)
        return

    await message.answer(t("ask_passport", lang), reply_markup=cancel_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.passport_photo)


# ─── Step 8: Official Document (conditional) ─────────────────────────────

@router.message(ApplicationForm.official_doc, F.photo)
async def process_official_doc(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    data = await state.get_data()
    editing = data.get("editing")
    await state.update_data(
        official_doc=message.photo[-1].file_id,
        official_doc_is_doc=False,
        official_doc_is_image=True,
    )
    if editing:
        await state.update_data(editing=False)
        await _show_preview(message, state, lang)
        return
    await message.answer(t("ask_passport", lang), reply_markup=cancel_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.passport_photo)


@router.message(ApplicationForm.official_doc, F.document)
async def process_official_doc_document(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    # Official document accepts any file: images, PDF, Word, presentations, etc.
    mime = message.document.mime_type or ""
    data = await state.get_data()
    editing = data.get("editing")
    await state.update_data(
        official_doc=message.document.file_id,
        official_doc_is_doc=True,
        official_doc_is_image=mime.startswith("image/"),
    )
    if editing:
        await state.update_data(editing=False)
        await _show_preview(message, state, lang)
        return
    await message.answer(t("ask_passport", lang), reply_markup=cancel_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.passport_photo)


@router.message(ApplicationForm.official_doc)
async def process_official_doc_invalid(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    await message.answer(t("ask_official_doc_invalid", lang), parse_mode="HTML")


# ─── Step 9: Passport Photo ──────────────────────────────────────────────

@router.message(ApplicationForm.passport_photo, F.photo)
async def process_passport_photo(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    data = await state.get_data()
    editing = data.get("editing")
    await state.update_data(passport_photo=message.photo[-1].file_id, passport_photo_is_doc=False)
    if editing:
        await state.update_data(editing=False)
        await _show_preview(message, state, lang)
        return
    await message.answer(t("ask_photo_3x4", lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.photo_3x4)


@router.message(ApplicationForm.passport_photo, F.document)
async def process_passport_photo_document(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    if not (message.document.mime_type or "").startswith("image/"):
        await message.answer(t("send_photo_only", lang), parse_mode="HTML")
        return
    data = await state.get_data()
    editing = data.get("editing")
    await state.update_data(passport_photo=message.document.file_id, passport_photo_is_doc=True)
    if editing:
        await state.update_data(editing=False)
        await _show_preview(message, state, lang)
        return
    await message.answer(t("ask_photo_3x4", lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.photo_3x4)


@router.message(ApplicationForm.passport_photo)
async def process_passport_photo_invalid(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    await message.answer(t("send_photo_only", lang), parse_mode="HTML")


# ─── Step 10: 3x4 Photo ──────────────────────────────────────────────────

@router.message(ApplicationForm.photo_3x4, F.photo)
async def process_photo_3x4(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    data = await state.get_data()
    editing = data.get("editing")
    await state.update_data(photo_3x4=message.photo[-1].file_id, photo_3x4_is_doc=False)
    if editing:
        await state.update_data(editing=False)
        await _show_preview(message, state, lang)
        return
    await message.answer(t("ask_phone", lang), reply_markup=phone_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.phone_number)


@router.message(ApplicationForm.photo_3x4, F.document)
async def process_photo_3x4_document(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    if not (message.document.mime_type or "").startswith("image/"):
        await message.answer(t("send_photo_only", lang), parse_mode="HTML")
        return
    data = await state.get_data()
    editing = data.get("editing")
    await state.update_data(photo_3x4=message.document.file_id, photo_3x4_is_doc=True)
    if editing:
        await state.update_data(editing=False)
        await _show_preview(message, state, lang)
        return
    await message.answer(t("ask_phone", lang), reply_markup=phone_keyboard(lang), parse_mode="HTML")
    await state.set_state(ApplicationForm.phone_number)


@router.message(ApplicationForm.photo_3x4)
async def process_photo_3x4_invalid(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    await message.answer(t("send_photo_only", lang), parse_mode="HTML")


# ─── Step 11: Phone Number ────────────────────────────────────────────────

@router.message(ApplicationForm.phone_number, F.contact)
async def process_phone_contact(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    data = await state.get_data()
    editing = data.get("editing")
    await state.update_data(
        phone=phone,
        username=message.from_user.username or "N/A",
        user_id=message.from_user.id,
        editing=False,
    )
    if editing:
        await _show_preview(message, state, lang)
        return

    await message.answer(
        t("ask_additional_phone", lang),
        reply_markup=additional_phone_keyboard(lang),
        parse_mode="HTML",
    )
    await state.set_state(ApplicationForm.additional_phone)


@router.message(ApplicationForm.phone_number, F.text)
async def process_phone_text(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)

    if message.text in [TEXTS[la]["btn_cancel"] for la in TEXTS]:
        return
    if message.text in [TEXTS[la]["btn_back"] for la in TEXTS]:
        return

    phone = normalize_phone(message.text)
    if phone is None:
        await message.answer(t("invalid_phone", lang), parse_mode="HTML")
        return

    data = await state.get_data()
    editing = data.get("editing")
    await state.update_data(
        phone=phone,
        username=message.from_user.username or "N/A",
        user_id=message.from_user.id,
        editing=False,
    )
    if editing:
        await _show_preview(message, state, lang)
        return

    await message.answer(
        t("ask_additional_phone", lang),
        reply_markup=additional_phone_keyboard(lang),
        parse_mode="HTML",
    )
    await state.set_state(ApplicationForm.additional_phone)


# ─── Step 12: Additional Phone ────────────────────────────────────────────

@router.message(ApplicationForm.additional_phone, F.contact)
async def process_additional_phone_contact(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    data = await state.get_data()
    if phone == data.get("phone", ""):
        await message.answer(t("same_phone_error", lang), parse_mode="HTML")
        return

    await state.update_data(additional_phone=phone, editing=False)
    await _show_preview(message, state, lang)


@router.message(ApplicationForm.additional_phone, F.text)
async def process_additional_phone_text(message: Message, state: FSMContext) -> None:
    lang = await _get_lang(state)

    if message.text in [TEXTS[la]["btn_cancel"] for la in TEXTS]:
        return
    if message.text in [TEXTS[la]["btn_back"] for la in TEXTS]:
        return

    phone = normalize_phone(message.text)
    if phone is None:
        await message.answer(t("invalid_phone", lang), parse_mode="HTML")
        return

    data = await state.get_data()
    if phone == data.get("phone", ""):
        await message.answer(t("same_phone_error", lang), parse_mode="HTML")
        return

    await state.update_data(additional_phone=phone, editing=False)
    await _show_preview(message, state, lang)


# ─── Preview: Confirm / Edit ─────────────────────────────────────────────

@router.callback_query(ApplicationForm.preview, F.data == "preview:confirm")
async def process_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    lang = await _get_lang(state)
    data = await state.get_data()
    await callback.answer()

    # Guard against double-tap producing duplicate channel posts / sheet rows.
    if data.get("_submitting"):
        return
    await state.update_data(_submitting=True)

    await safe_delete(callback.message)

    admin = is_admin(callback.from_user.id)
    try:
        app_id, msg_id = await send_to_channel(bot, CHANNEL_ID, data, lang)
        asyncio.create_task(process_and_save_application(bot, data, app_id, msg_id))
        await callback.message.answer(
            t("confirmed", lang, id=app_id),
            reply_markup=main_menu_keyboard(lang, admin),
            parse_mode="HTML",
        )
    except Exception as e:
        logger.exception("Failed to send application to channel: %s", e)
        await callback.message.answer(
            t("submit_error", lang),
            reply_markup=main_menu_keyboard(lang, admin),
            parse_mode="HTML",
        )

    await state.clear()
    await state.update_data(lang=lang, oferta_agreed=True)


@router.callback_query(ApplicationForm.preview, F.data == "preview:edit")
async def process_edit(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    data = await state.get_data()
    await callback.answer()
    await safe_delete(callback.message)

    await callback.message.answer(
        t("edit_select", lang),
        reply_markup=edit_field_keyboard(lang, data),
        parse_mode="HTML",
    )
    await state.set_state(ApplicationForm.select_edit_field)


@router.callback_query(ApplicationForm.select_edit_field, F.data == "edit:back")
async def process_edit_back(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    await callback.answer()
    await safe_delete(callback.message)
    await _show_preview(callback, state, lang)


# ─── Edit field selection ─────────────────────────────────────────────────

@router.callback_query(ApplicationForm.select_edit_field, F.data.startswith("editf:"))
async def process_edit_field(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    field = callback.data.split(":")[1]
    await callback.answer()
    await safe_delete(callback.message)

    await state.update_data(editing=True)

    if field == "full_name":
        await callback.message.answer(t("ask_full_name", lang), reply_markup=cancel_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.full_name)

    elif field == "sex":
        await callback.message.answer(t("ask_sex", lang), reply_markup=sex_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.sex)

    elif field == "level":
        await callback.message.answer(t("ask_level", lang), reply_markup=level_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.level)

    elif field == "faculty":
        await callback.message.answer(t("ask_faculty", lang), reply_markup=faculty_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.faculty)

    elif field == "region":
        await callback.message.answer(t("ask_region", lang), reply_markup=region_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.region)

    elif field == "town":
        data = await state.get_data()
        if data.get("is_foreign"):
            # Foreign users don't have town — redirect to region edit
            await callback.message.answer(t("ask_region", lang), reply_markup=region_keyboard(lang), parse_mode="HTML")
            await state.set_state(ApplicationForm.region)
        else:
            region_idx = data.get("region_idx", 0)
            region_name = data.get("region_name", "")
            await callback.message.answer(
                t("ask_town", lang, region=region_name),
                reply_markup=town_keyboard(region_idx, lang),
                parse_mode="HTML",
            )
            await state.set_state(ApplicationForm.town)

    elif field == "reason":
        await callback.message.answer(t("ask_reason", lang), reply_markup=reason_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.reason)

    elif field == "official_doc":
        await callback.message.answer(t("ask_official_doc", lang), reply_markup=cancel_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.official_doc)

    elif field == "passport":
        await callback.message.answer(t("ask_passport", lang), reply_markup=cancel_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.passport_photo)

    elif field == "photo_3x4":
        await callback.message.answer(t("ask_photo_3x4", lang), reply_markup=cancel_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.photo_3x4)

    elif field == "phone":
        await callback.message.answer(t("ask_phone", lang), reply_markup=phone_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.phone_number)

    elif field == "additional_phone":
        await callback.message.answer(t("ask_additional_phone", lang), reply_markup=additional_phone_keyboard(lang), parse_mode="HTML")
        await state.set_state(ApplicationForm.additional_phone)
