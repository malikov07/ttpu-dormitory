"""Admin handlers — publishing admission results, unblocking re-applications."""

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import RESULT_QUIET_SECONDS, is_admin
from keyboards import main_menu_keyboard, publish_confirm_keyboard
from texts import TEXTS, t
from utils.applied_store import clear_applied
from utils.results import clear_sent, deliver_ready_results
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
        t("publish_prompt", lang, minutes=max(1, RESULT_QUIET_SECONDS // 60)),
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


@router.message(Command("resend"))
async def handle_resend(message: Message, state: FSMContext, command: CommandObject) -> None:
    """Admin: send an applicant their result again, e.g. after a corrected reason.

    A result is delivered once and only once on its own; this re-arms a single
    application id. The current text still has to settle before it goes out, so a
    correction being typed right now is not what gets sent.
    """
    lang = await _get_lang(state)
    if not is_admin(message.from_user.id):
        await message.answer(t("not_admin", lang), parse_mode="HTML")
        return

    app_id = (command.args or "").strip()
    if not app_id:
        await message.answer(t("resend_usage", lang), parse_mode="HTML")
        return

    key = "resend_done" if clear_sent(app_id) else "resend_not_found"
    await message.answer(t(key, lang, id=app_id), parse_mode="HTML")


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
        counts = await deliver_ready_results(bot)
    finally:
        _publishing.discard(uid)

    await safe_delete(status_msg)
    await callback.message.answer(
        t(
            "publish_done",
            lang,
            accepted=counts["accepted"],
            interview=counts["interview"],
            rejected=counts["rejected"],
            failed=counts["failed"],
            waiting=counts["waiting"],
            pending=counts["pending"],
            undecided=counts["undecided"],
        ),
        reply_markup=main_menu_keyboard(lang, is_admin=True),
        parse_mode="HTML",
    )
