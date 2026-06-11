"""/start command, language selection, and oferta handlers."""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import OFERTA_URL, is_admin
from keyboards import language_keyboard, main_menu_keyboard, oferta_keyboard
from texts import t
from utils.tg import safe_delete

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Handle /start — show language selection."""
    await state.clear()
    await message.answer(
        t("welcome", "en"),
        reply_markup=language_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("lang:"))
async def process_language(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle language selection — show oferta if not yet agreed."""
    lang = callback.data.split(":")[1]
    data = await state.get_data()
    already_agreed = data.get("oferta_agreed", False)

    await state.update_data(lang=lang)
    await callback.answer()
    await safe_delete(callback.message)

    await callback.message.answer(t("lang_set", lang), parse_mode="HTML")

    if already_agreed:
        await callback.message.answer(
            t("main_menu", lang),
            reply_markup=main_menu_keyboard(lang, is_admin(callback.from_user.id)),
            parse_mode="HTML",
        )
        return

    text = t("oferta_message", lang)
    if OFERTA_URL:
        link_label = t("oferta_link", lang)
        text += f'\n\n🔗 <a href="{OFERTA_URL}">{link_label}</a>'

    await callback.message.answer(
        text,
        reply_markup=oferta_keyboard(lang),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "oferta:agree")
async def process_oferta_agree(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle oferta agreement — show main menu."""
    data = await state.get_data()
    lang = data.get("lang", "en")

    await state.update_data(oferta_agreed=True)
    await callback.answer()
    await safe_delete(callback.message)

    await callback.message.answer(
        t("main_menu", lang),
        reply_markup=main_menu_keyboard(lang, is_admin(callback.from_user.id)),
        parse_mode="HTML",
    )
