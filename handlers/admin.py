"""Admin handlers — publishing admission results, unblocking re-applications."""

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import is_admin
from keyboards import main_menu_keyboard, publish_confirm_keyboard
from texts import TEXTS, t
from utils.applied_store import clear_applied
from utils.google_api import publish_results
from utils.tg import safe_delete

router = Router()

# Guards against a double-tap / re-entry running the publish job more than once.
_publishing: set[int] = set()


async def _get_lang(state: FSMContext) -> str:
    data = await state.get_data()
    return data.get("lang", "uz")


@router.message(F.text.in_([TEXTS[la]["btn_publish_results"] for la in TEXTS]))
async def handle_publish_button(message: Message, state: FSMContext) -> None:
    """Admin pressed 'Publish results' — ask for confirmation."""
    lang = await _get_lang(state)
    if not is_admin(message.from_user.id):
        await message.answer(t("not_admin", lang), parse_mode="HTML")
        return
    await message.answer(
        t("publish_prompt", lang),
        reply_markup=publish_confirm_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(Command("allow_reapply"))
async def handle_allow_reapply(
    message: Message, state: FSMContext, command: CommandObject
) -> None:
    """Admin: clear a user's application record so they can submit a new one.

    The old application stays in the channel and the sheet — remove it there by hand
    if it should not be considered.
    """
    lang = await _get_lang(state)
    if not is_admin(message.from_user.id):
        await message.answer(t("not_admin", lang), parse_mode="HTML")
        return

    try:
        target_id = int((command.args or "").strip())
    except ValueError:
        await message.answer(t("reapply_usage", lang), parse_mode="HTML")
        return

    key = "reapply_done" if clear_applied(target_id) else "reapply_not_found"
    await message.answer(t(key, lang, id=target_id), parse_mode="HTML")


@router.callback_query(F.data == "publish:cancel")
async def handle_publish_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _get_lang(state)
    await callback.answer()
    await safe_delete(callback.message)
    await callback.message.answer(t("publish_cancelled", lang), parse_mode="HTML")


@router.callback_query(F.data == "publish:confirm")
async def handle_publish_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    lang = await _get_lang(state)
    uid = callback.from_user.id
    await callback.answer()

    if not is_admin(uid):
        await callback.message.answer(t("not_admin", lang), parse_mode="HTML")
        return

    if uid in _publishing:
        return  # a publish job is already running for this admin
    _publishing.add(uid)

    await safe_delete(callback.message)
    status_msg = await callback.message.answer(t("publishing", lang), parse_mode="HTML")

    try:
        counts = await publish_results(bot)
    finally:
        _publishing.discard(uid)

    await safe_delete(status_msg)
    await callback.message.answer(
        t(
            "publish_done",
            lang,
            success=counts["success"],
            failure=counts["failure"],
            failed=counts["failed"],
        ),
        reply_markup=main_menu_keyboard(lang, is_admin=True),
        parse_mode="HTML",
    )
