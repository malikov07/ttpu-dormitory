"""All keyboard builders for the bot."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from data.regions import FACULTIES, REASONS, REGIONS
from texts import t


def language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            ]
        ]
    )


def oferta_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Oferta agreement keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn_oferta_agree", lang), callback_data="oferta:agree")]
        ]
    )


def main_menu_keyboard(lang: str, is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Main menu reply keyboard. Admins get an extra 'Publish results' button."""
    keyboard = [
        [KeyboardButton(text=t("btn_apply", lang))],
        [
            KeyboardButton(text=t("btn_change_lang", lang)),
            KeyboardButton(text=t("btn_faq", lang)),
        ],
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text=t("btn_publish_results", lang))])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def publish_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Confirm / cancel keyboard for publishing admission results."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("btn_publish_confirm", lang), callback_data="publish:confirm"),
                InlineKeyboardButton(text=t("btn_publish_cancel", lang), callback_data="publish:cancel"),
            ]
        ]
    )


def cancel_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Back + Cancel buttons during application."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("btn_back", lang)),
                KeyboardButton(text=t("btn_cancel", lang)),
            ]
        ],
        resize_keyboard=True,
    )


def sex_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Gender selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("btn_male", lang), callback_data="sex:male"),
                InlineKeyboardButton(text=t("btn_female", lang), callback_data="sex:female"),
            ],
            [InlineKeyboardButton(text=t("btn_back", lang), callback_data="back")],
        ]
    )


def level_keyboard(lang: str) -> InlineKeyboardMarkup:
    """University level selection (1-4)."""
    buttons = []
    row = []
    for i in range(1, 5):
        row.append(
            InlineKeyboardButton(
                text=t("level_year", lang, n=i), callback_data=f"level:{i}"
            )
        )
    buttons.append(row)
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def faculty_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Faculty/direction selection keyboard — pairs short names side-by-side."""
    buttons = []
    i = 0
    while i < len(FACULTIES):
        name = FACULTIES[i][lang]
        if i + 1 < len(FACULTIES):
            next_name = FACULTIES[i + 1][lang]
            if len(name) <= 24 and len(next_name) <= 24:
                buttons.append([
                    InlineKeyboardButton(text=name, callback_data=f"faculty:{i}"),
                    InlineKeyboardButton(text=next_name, callback_data=f"faculty:{i + 1}"),
                ])
                i += 2
                continue
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"faculty:{i}")])
        i += 1
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def region_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Region selection keyboard (all 14 regions + Foreign, 2 per row)."""
    buttons = []
    row = []
    for i, reg in enumerate(REGIONS):
        row.append(
            InlineKeyboardButton(text=reg["name"][lang], callback_data=f"reg:{i}")
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text=t("region_foreign", lang), callback_data="reg:foreign")])
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def town_keyboard(region_idx: int, lang: str) -> InlineKeyboardMarkup:
    """Town/district selection for a specific region + Other option."""
    region = REGIONS[region_idx]
    buttons = []
    row = []
    for i, town in enumerate(region["towns"]):
        row.append(
            InlineKeyboardButton(text=town[lang], callback_data=f"town:{i}")
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append(
        [InlineKeyboardButton(text=t("other", lang), callback_data="town:other")]
    )
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def reason_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Reason selection keyboard + Other option."""
    buttons = []
    for i, reason in enumerate(REASONS):
        buttons.append(
            [InlineKeyboardButton(text=reason[lang], callback_data=f"reason:{i}")]
        )
    buttons.append(
        [InlineKeyboardButton(text=t("other", lang), callback_data="reason:other")]
    )
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Phone number sharing keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_share_phone", lang), request_contact=True)],
            [
                KeyboardButton(text=t("btn_back", lang)),
                KeyboardButton(text=t("btn_cancel", lang)),
            ],
        ],
        resize_keyboard=True,
    )


def additional_phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Additional phone number keyboard — type only, no contact share."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("btn_back", lang)),
                KeyboardButton(text=t("btn_cancel", lang)),
            ],
        ],
        resize_keyboard=True,
    )


def preview_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Confirm / Edit inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_confirm", lang), callback_data="preview:confirm"
                ),
                InlineKeyboardButton(
                    text=t("btn_edit", lang), callback_data="preview:edit"
                ),
            ]
        ]
    )


def edit_field_keyboard(lang: str, data: dict = None) -> InlineKeyboardMarkup:
    """Keyboard to select which field to edit."""
    data = data or {}
    fields = [
        ("edit_name", "editf:full_name"),
        ("edit_sex", "editf:sex"),
        ("edit_level", "editf:level"),
        ("edit_faculty", "editf:faculty"),
        ("edit_region", "editf:region"),
        ("edit_town", "editf:town"),
        ("edit_reason", "editf:reason"),
    ]
    if data.get("needs_official_doc"):
        fields.append(("edit_official_doc", "editf:official_doc"))
    fields += [
        ("edit_passport", "editf:passport"),
        ("edit_photo", "editf:photo_3x4"),
        ("edit_phone", "editf:phone"),
        ("edit_additional_phone", "editf:additional_phone"),
    ]
    buttons = []
    row = []
    for text_key, cb_data in fields:
        row.append(
            InlineKeyboardButton(text=t(text_key, lang), callback_data=cb_data)
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="edit:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
