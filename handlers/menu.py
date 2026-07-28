"""Main menu handler — Apply, Change Language, FAQ."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import is_admin
from keyboards import cancel_keyboard, language_keyboard, main_menu_keyboard
from states import ApplicationForm
from texts import TEXTS, t
from utils.applied_store import already_applied_text, has_applied

router = Router()


async def _get_lang(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get("lang", "en")


@router.message(F.text.in_([TEXTS[la]["btn_apply"] for la in TEXTS]))
async def handle_apply(message: Message, state: FSMContext) -> None:
    """Start the application process — one application per Telegram account."""
    lang = await _get_lang(state)
    uid = message.from_user.id
    if has_applied(uid):
        await message.answer(
            already_applied_text(uid, lang),
            reply_markup=main_menu_keyboard(lang, is_admin(uid)),
            parse_mode="HTML",
        )
        return
    await state.set_state(ApplicationForm.full_name)
    await message.answer(
        t("ask_full_name", lang),
        reply_markup=cancel_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(F.text.in_([TEXTS[la]["btn_change_lang"] for la in TEXTS]))
async def handle_change_lang(message: Message, state: FSMContext) -> None:
    """Show language selection again."""
    await message.answer(
        t("welcome", "en"),
        reply_markup=language_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text.in_([TEXTS[la]["btn_faq"] for la in TEXTS]))
async def handle_faq(message: Message, state: FSMContext) -> None:
    """Show FAQ."""
    lang = await _get_lang(state)
    text = t("faq_title", lang) + "\n" + t("faq_content", lang)
    await message.answer(text, parse_mode="HTML")
