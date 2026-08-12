"""Letting an applicant send a corrected official document after applying.

Some applicants attached the wrong file to their application — the wrong page,
a screenshot of a chat, a copy from no official source. The application itself
stays closed to editing, so this is a one-way errand rather than a re-open: the
applicant attaches the right document, the bot posts it to the documents channel
under their application number, and the tutors work through them there.

The application number is what makes the post useful, so nothing is sent until
the applicant's row has been found in the spreadsheet.
"""

import html
import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import DOCS_CHANNEL_ID, is_admin, now_tashkent
from keyboards import main_menu_keyboard, reupload_keyboard
from states import DocumentReupload
from texts import TEXTS, t
from utils.google_api import find_application
from utils.lang_store import get_user_lang
from utils.preview import _send_items

router = Router()
logger = logging.getLogger(__name__)

# Telegram puts at most 10 items in one media group, and a submission longer
# than that is a misunderstanding rather than a document.
MAX_FILES = 10


def _labels(key: str) -> list:
    """The same button in every language — reply keyboards send back their text."""
    return [TEXTS[lang][key] for lang in TEXTS]


def _esc(value) -> str:
    """Escape a sheet value for an HTML caption."""
    return html.escape(str(value), quote=False)


async def _lang(state: FSMContext, user_id: int) -> str:
    """This session's language, or the one the applicant applied in.

    The FSM lives in memory, so an applicant coming back days later has no
    language in state; the one saved when they applied is the better guess than
    falling back to English.
    """
    data = await state.get_data()
    return data.get("lang") or get_user_lang(user_id)


async def _back_to_menu(message: Message, state: FSMContext, lang: str, text: str) -> None:
    """Answer, drop the re-upload state, and put the main menu back."""
    await state.clear()
    await state.update_data(lang=lang, oferta_agreed=True)
    await message.answer(
        text,
        reply_markup=main_menu_keyboard(lang, is_admin(message.from_user.id)),
        parse_mode="HTML",
    )


@router.message(F.text.in_(_labels("btn_reupload_doc")))
async def start_reupload(message: Message, state: FSMContext) -> None:
    """Open a re-upload session for an applicant who is already in the sheet."""
    lang = await _lang(state, message.from_user.id)

    if not DOCS_CHANNEL_ID:
        logger.error(
            "DOCS_CHANNEL_ID is not set — the re-upload button has nowhere to post."
        )
        await message.answer(t("reupload_unavailable", lang), parse_mode="HTML")
        return

    try:
        application = await find_application(message.from_user.id)
    except Exception as e:
        # A sheet that cannot be read is not the same as an applicant who never
        # applied, and must not be reported to them as one.
        logger.exception(
            "Could not look up the application of %s: %s", message.from_user.id, e
        )
        await message.answer(t("reupload_unavailable", lang), parse_mode="HTML")
        return

    if application is None:
        # No keyboard on purpose: someone who typed this text mid-application
        # keeps the form's own keyboard instead of being dropped into the menu.
        await message.answer(
            t("reupload_no_application", lang, apply=t("btn_apply", lang)),
            parse_mode="HTML",
        )
        return

    await state.set_state(DocumentReupload.collecting)
    await state.update_data(
        lang=lang,
        reupload_app=application,
        reupload_files=[],
        _reupload_sending=False,
    )
    await message.answer(
        t(
            "reupload_intro",
            lang,
            id=_esc(application["app_id"]),
            send=t("btn_reupload_send", lang),
        ),
        reply_markup=reupload_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(DocumentReupload.collecting, F.text.in_(_labels("btn_cancel")))
async def cancel_reupload(message: Message, state: FSMContext) -> None:
    """Leave without sending. Handled here rather than by the application
    router's cancel, whose "your application is cancelled" would frighten
    someone who only backed out of attaching a file."""
    lang = await _lang(state, message.from_user.id)
    await _back_to_menu(message, state, lang, t("reupload_cancelled", lang))


@router.message(DocumentReupload.collecting, F.photo | F.document)
async def collect_file(message: Message, state: FSMContext) -> None:
    """Hold on to one file. Albums arrive a message at a time and stack up here."""
    lang = await _lang(state, message.from_user.id)
    data = await state.get_data()
    files = list(data.get("reupload_files") or [])

    if len(files) >= MAX_FILES:
        await message.answer(
            t(
                "reupload_limit",
                lang,
                max=MAX_FILES,
                send=t("btn_reupload_send", lang),
            ),
            parse_mode="HTML",
        )
        return

    if message.photo:
        files.append([message.photo[-1].file_id, False])
    else:
        files.append([message.document.file_id, True])

    await state.update_data(reupload_files=files)
    await message.answer(t("reupload_added", lang, count=len(files)), parse_mode="HTML")


@router.message(DocumentReupload.collecting, F.text.in_(_labels("btn_reupload_send")))
async def send_documents(message: Message, state: FSMContext, bot: Bot) -> None:
    """Post everything attached to the documents channel, under one caption."""
    lang = await _lang(state, message.from_user.id)
    data = await state.get_data()
    files = data.get("reupload_files") or []
    application = data.get("reupload_app") or {}
    app_id = application.get("app_id", "?")

    if not files:
        await message.answer(
            t("reupload_empty", lang, send=t("btn_reupload_send", lang)),
            parse_mode="HTML",
        )
        return

    if data.get("_reupload_sending"):
        return  # double tap — the first press is still uploading
    await state.update_data(_reupload_sending=True)

    caption = t(
        "reupload_channel_caption",
        "uz",
        id=_esc(app_id),
        name=_esc(application.get("name", "")) or "-",
        reason=_esc(application.get("reason", "")) or "-",
        count=len(files),
        username=_esc(message.from_user.username or "N/A"),
        user_id=message.from_user.id,
        at=now_tashkent().strftime("%Y-%m-%d %H:%M"),
    )

    # Telegram will not mix photos and files in one media group, so a submission
    # holding both goes as two posts. The second carries the application number
    # too — the pair can be separated by anything else posted in between.
    photos = [item for item in files if not item[1]]
    documents = [item for item in files if item[1]]

    try:
        lead = caption
        for group in (photos, documents):
            if not group:
                continue
            await _send_items(bot, DOCS_CHANNEL_ID, group, lead)
            lead = t("reupload_channel_more", "uz", id=_esc(app_id))
    except Exception as e:
        logger.exception(
            "Could not post the re-uploaded document(s) of application %s: %s", app_id, e
        )
        # The files stay in state, so pressing send again retries them.
        await state.update_data(_reupload_sending=False)
        await message.answer(
            t("reupload_error", lang),
            reply_markup=reupload_keyboard(lang),
            parse_mode="HTML",
        )
        return

    logger.info("Application %s re-uploaded %d document(s).", app_id, len(files))
    await _back_to_menu(
        message,
        state,
        lang,
        t("reupload_sent", lang, id=_esc(app_id), count=len(files)),
    )


@router.message(DocumentReupload.collecting)
async def reupload_invalid(message: Message, state: FSMContext) -> None:
    """Anything that is not a file, and not one of the two buttons."""
    lang = await _lang(state, message.from_user.id)
    await message.answer(
        t("reupload_invalid", lang, send=t("btn_reupload_send", lang)),
        parse_mode="HTML",
    )
